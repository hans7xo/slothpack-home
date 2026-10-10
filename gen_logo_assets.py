# -*- coding: utf-8 -*-
"""从 brand/ 下的母版生成站点实际使用的 Logo、favicon 与 touch icon。

母版（都是 v6 品牌插画的派生件，透明底）：
- brand/logo-mark-master.png   站点 Logo 用图 —— **完整插画**（长边 480px，够 3 倍图用）
- brand/logo-head-master.png   头部裁切 —— 已清除装饰弧线碎片与椅子角，单一连通域 → favicon / touch icon
- brand/logo-glyph-master.png  </> 符号（备用，当前未使用）

运行：python gen_logo_assets.py

输出（写入 public/，构建时原样拷进 dist/）：
- logo-mark.png         页面按 24px 高显示，72px 为 3 倍图
- favicon.ico           16 / 32 / 48 三帧，燕麦色圆角底 + 头像
- apple-touch-icon.png  180x180

两个踩过的坑：
1. PIL 保存 ICO 带 append_images 只会写出一帧 → 这里手写 ICONDIR，逐帧内嵌 PNG。
2. 位图缩放（LANCZOS）会在边缘留下极低透明度的"毛边"像素，24px 显示时是若有若无的脏点 →
   缩放后必须做阈值清理；头像这类"应该只有一个主体"的图还要去小连通域，并对成品自检。
   注意：完整插画里的装饰弧线、烟气是**正常内容**，所以对它只做阈值、不做连通域删除。
"""
import io
import os
import struct
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.join(ROOT, "brand")
PUBLIC = os.path.join(ROOT, "public")
OAT = (245, 241, 232, 255)


def components(alpha):
    """4 邻域连通域标记，返回 (标签图, 区块数)。"""
    h, w = alpha.shape
    lab = np.zeros((h, w), np.int32)
    cur = 0
    for y in range(h):
        for x in range(w):
            if alpha[y, x] and lab[y, x] == 0:
                cur += 1
                q = deque([(y, x)])
                lab[y, x] = cur
                while q:
                    cy, cx = q.popleft()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and alpha[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = cur
                            q.append((ny, nx))
    return lab, cur


def clean_alpha(img, min_alpha=25, min_area=0):
    """阈值清理半透明毛边；min_area>0 时再删掉面积不足的孤立碎片。"""
    arr = np.array(img.convert("RGBA")).copy()
    arr[:, :, 3] = np.where(arr[:, :, 3] < min_alpha, 0, arr[:, :, 3])
    lab, cur = components(arr[:, :, 3] > 0)
    areas = []
    if cur:
        sizes = sorted(((int((lab == i).sum()), i) for i in range(1, cur + 1)), reverse=True)
        if min_area > 0:
            for area, idx in sizes:
                if area < min_area:
                    arr[lab == idx] = 0
        lab2, cur2 = components(arr[:, :, 3] > 0)
        areas = sorted((int((lab2 == i).sum()) for i in range(1, cur2 + 1)), reverse=True)
    return Image.fromarray(arr, "RGBA"), areas


def build_ico(frames):
    """frames: [(size, RGBAImage)] -> ICO bytes（每帧以 PNG 形式内嵌）。"""
    blobs = []
    for _, img in frames:
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        blobs.append(buf.getvalue())
    header = struct.pack("<HHH", 0, 1, len(frames))
    entries = b""
    offset = 6 + 16 * len(frames)
    for (size, _), blob in zip(frames, blobs):
        dim = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
    return header + entries + b"".join(blobs)


def rounded_tile(art, size, pad_ratio, radius_ratio=0.22):
    """把图形放进一块燕麦色圆角方块，保证在深色/浅色浏览器主题下都看得见。"""
    tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(tile).rounded_rectangle(
        [0, 0, size - 1, size - 1], radius=max(int(size * radius_ratio), 2), fill=OAT
    )
    avail = size * (1 - 2 * pad_ratio)
    g = art.resize(
        (max(int(round(art.width * avail / art.height)), 1), max(int(round(avail)), 1)),
        Image.LANCZOS,
    )
    if g.width > avail:
        g = art.resize(
            (max(int(round(avail)), 1), max(int(round(art.height * avail / art.width)), 1)),
            Image.LANCZOS,
        )
    tile.alpha_composite(g, ((size - g.width) // 2, (size - g.height) // 2))
    return tile


def report(path, expect_single=None):
    im = Image.open(path).convert("RGBA")
    lab, cur = components(np.array(im)[:, :, 3] > 0)
    areas = sorted((int((lab == i).sum()) for i in range(1, cur + 1)), reverse=True)
    flag = ""
    if expect_single is True:
        flag = "OK" if len(areas) == 1 else "!! 期望单一连通域，实际 %d 个" % len(areas)
    print(
        "  %-22s %sx%s  %6d bytes  连通域=%d 各块=%s  %s"
        % (os.path.basename(path), im.width, im.height, os.path.getsize(path), len(areas), areas, flag)
    )
    return areas


def main():
    illustration = Image.open(os.path.join(BRAND, "logo-mark-master.png")).convert("RGBA")
    head = Image.open(os.path.join(BRAND, "logo-head-master.png")).convert("RGBA")

    # --- 站点 Logo：完整插画，页面按 48px 高显示，144px 为 3 倍图 ---
    h = 144
    w = max(int(round(illustration.width * h / illustration.height)), 1)
    small, areas = clean_alpha(illustration.resize((w, h), Image.LANCZOS), min_alpha=12, min_area=0)
    out = os.path.join(PUBLIC, "logo-mark.png")
    pal = small.quantize(colors=256, method=Image.FASTOCTREE)
    pal.save(out, optimize=True)
    full_size = 0
    buf = io.BytesIO()
    small.save(buf, format="PNG", optimize=True)
    full_size = buf.tell()
    report(out, expect_single=None)
    print("       （PNG32 未压缩版为 %d bytes；已选用 256 色调色板版）" % full_size)

    # --- favicon / touch icon：干净头像，必须是单一连通域 ---
    head_clean, head_areas = clean_alpha(head, min_alpha=25, min_area=40)
    if len(head_areas) != 1:
        raise SystemExit("头像母版连通域不是 1（实际 %d），请检查母版" % len(head_areas))
    frames = [
        (16, rounded_tile(head_clean, 16, 0.05)),
        (32, rounded_tile(head_clean, 32, 0.10)),
        (48, rounded_tile(head_clean, 48, 0.13)),
    ]
    out = os.path.join(PUBLIC, "favicon.ico")
    with open(out, "wb") as f:
        f.write(build_ico(frames))
    print("  %-22s 16+32+48  %6d bytes" % ("favicon.ico", os.path.getsize(out)))

    out = os.path.join(PUBLIC, "apple-touch-icon.png")
    rounded_tile(head_clean, 180, 0.14).save(out, optimize=True)
    print("  %-22s 180x180  %6d bytes" % ("apple-touch-icon.png", os.path.getsize(out)))
    print("自检通过：头像链路的 favicon/touch icon 均基于单一连通域母版")


if __name__ == "__main__":
    main()
