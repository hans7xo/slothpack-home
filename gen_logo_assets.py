# -*- coding: utf-8 -*-
"""从 brand/ 下的母版生成站点实际使用的 Logo 与 favicon 资产。

母版来源：v6 品牌插画（用户锁定版）的裁切派生件，不含烟草元素。
- brand/logo-mark-master.png  ：头像标记母版（含透明通道）
- brand/logo-glyph-master.png ：</> 符号母版（从插画笔记本屏幕上提取）

运行：python gen_logo_assets.py

输出（写入 public/，构建时原样拷进 dist/）：
- logo-mark.png         127x72（页面按 24px 高显示，3 倍图，调色板压缩）
- favicon.ico           16 / 32 / 48 三尺寸，逐帧内嵌 PNG
- apple-touch-icon.png  180x180

注意：PIL 的 ICO 保存器在带 append_images 时只写出一帧，因此这里手写 ICONDIR。
"""
import io
import os
import struct

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.join(ROOT, "brand")
PUBLIC = os.path.join(ROOT, "public")
OAT = (245, 241, 232, 255)


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


def glyph_tile(glyph, size, pad_ratio, radius_ratio=0.22):
    """把 </> 符号放进一块燕麦色圆角方块，保证在深色/浅色浏览器主题下都看得见。"""
    tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(tile).rounded_rectangle(
        [0, 0, size - 1, size - 1], radius=max(int(size * radius_ratio), 2), fill=OAT
    )
    avail = size * (1 - 2 * pad_ratio)
    g = glyph.resize(
        (max(int(round(glyph.width * avail / glyph.height)), 1), max(int(round(avail)), 1)),
        Image.LANCZOS,
    )
    if g.width > avail:  # 符号较宽时改以宽度为准
        g = glyph.resize(
            (max(int(round(avail)), 1), max(int(round(glyph.height * avail / glyph.width)), 1)),
            Image.LANCZOS,
        )
    tile.alpha_composite(g, ((size - g.width) // 2, (size - g.height) // 2))
    return tile


def main():
    mark = Image.open(os.path.join(BRAND, "logo-mark-master.png")).convert("RGBA")
    glyph = Image.open(os.path.join(BRAND, "logo-glyph-master.png")).convert("RGBA")

    # 页面里标记高度固定 24px，72px 正好是 3 倍图；调色板压缩后约 4KB
    h = 72
    w = int(round(mark.width * h / mark.height))
    mark72 = mark.resize((w, h), Image.LANCZOS)
    out = os.path.join(PUBLIC, "logo-mark.png")
    mark72.quantize(colors=192, method=Image.FASTOCTREE).save(out, optimize=True)
    print("logo-mark.png     %dx%d  %d bytes" % (w, h, os.path.getsize(out)))

    # 16px 下留白必须收窄，否则 </> 只有几个像素
    frames = [
        (16, glyph_tile(glyph, 16, 0.05)),
        (32, glyph_tile(glyph, 32, 0.10)),
        (48, glyph_tile(glyph, 48, 0.13)),
    ]
    out = os.path.join(PUBLIC, "favicon.ico")
    with open(out, "wb") as f:
        f.write(build_ico(frames))
    print("favicon.ico       16+32+48  %d bytes" % os.path.getsize(out))

    out = os.path.join(PUBLIC, "apple-touch-icon.png")
    glyph_tile(glyph, 180, 0.14).save(out, optimize=True)
    print("apple-touch-icon.png 180x180  %d bytes" % os.path.getsize(out))


if __name__ == "__main__":
    main()
