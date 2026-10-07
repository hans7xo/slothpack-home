# -*- coding: utf-8 -*-
"""生成 SlothPack 占位 favicon.ico（16px + 32px，纯 #F5F1E8 底，PNG 内嵌格式）。
非正式 Logo，仅为占位文件，供用户后续替换。"""
import struct
import zlib
import os

BG = (245, 241, 232, 255)  # #F5F1E8


def png_chunk(chunk_type, data):
    return (
        struct.pack(">I", len(data))
        + chunk_type
        + data
        + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    )


def make_png(size):
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    row = b"\x00" + bytes(BG) * size
    idat = zlib.compress(row * size, 9)
    return (
        sig
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", idat)
        + png_chunk(b"IEND", b"")
    )


def build_ico(pngs):
    """pngs: list[(size, png_bytes)]，按顺序写入 ICONDIR。"""
    count = len(pngs)
    header = struct.pack("<HHH", 0, 1, count)
    entries = b""
    offset = 6 + 16 * count
    for size, data in pngs:
        w = 0 if size >= 256 else size
        entries += struct.pack(
            "<BBBBHHII", w, w, 0, 0, 1, 32, len(data), offset
        )
        offset += len(data)
    return header + entries + b"".join(d for _, d in pngs)


def main():
    out = os.path.join(os.path.dirname(__file__), "favicon.ico")
    pngs = [(16, make_png(16)), (32, make_png(32))]
    with open(out, "wb") as f:
        f.write(build_ico(pngs))
    print("written:", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
