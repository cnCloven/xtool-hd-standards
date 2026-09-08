#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Encode local <img src="..."> in an HTML file as data-URI, or restore them.

Default workflow: keep relative paths in source HTML (images/NN-slug.png).
This script is only needed when a standalone HTML must display images without
the images/ folder (for example sending a single file).

  python tools/embed_images.py 04-版本发布.html          # bake in
  python tools/embed_images.py --extract 04-版本发布.html  # data-URI -> images/
"""
from __future__ import annotations

import argparse
import base64
import mimetypes
import re
import sys
from pathlib import Path
from urllib.parse import unquote

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA_RE = re.compile(
    r'(<img\b[^>]*?\bsrc=["\'])(data:image/([^;]+);base64,([A-Za-z0-9+/=]+))(["\'])',
    re.I,
)
SRC_RE = re.compile(r'(<img\b[^>]*?\bsrc=["\'])([^"\']+)(["\'])', re.I)
ALT_RE = re.compile(r'\balt=["\']([^"\']*)["\']', re.I)


def slug(text: str, fallback: str) -> str:
    text = re.sub(r"[^\w一-鿿\-]+", "-", text).strip("-")
    return (text[:40] or fallback)


def embed(path: Path) -> int:
    html = path.read_text(encoding="utf-8")
    n = 0
    missing = []

    def repl(m: re.Match) -> str:
        nonlocal n
        src = m.group(2).strip()
        if src.startswith(("data:", "http://", "https://", "//")):
            return m.group(0)
        img = (path.parent / unquote(src).replace("\\", "/")).resolve()
        if not img.is_file():
            missing.append(src)
            return m.group(0)
        mime = mimetypes.guess_type(str(img))[0] or "image/png"
        b64 = base64.b64encode(img.read_bytes()).decode("ascii")
        n += 1
        return f"{m.group(1)}data:{mime};base64,{b64}{m.group(3)}"

    new = SRC_RE.sub(repl, html)
    if missing:
        print("缺失图片:")
        for s in missing:
            print("  -", s)
        return 1
    path.write_text(new, encoding="utf-8", newline="\n")
    print(f"已写入 {n} 张 data-URI 到 {path}  (现 {path.stat().st_size} bytes)")
    if n:
        print("提示: 源 HTML 会变大且不便编辑。日常请保持相对路径，打包 PDF 时由 build_pdf.py 自动编码。")
    return 0


def extract(path: Path) -> int:
    html = path.read_text(encoding="utf-8")
    out_dir = path.parent / "images"
    out_dir.mkdir(exist_ok=True)
    stem = path.stem.split("-")[0]
    idx = 0

    def repl(m: re.Match) -> str:
        nonlocal idx
        idx += 1
        mime, b64 = m.group(3).lower(), m.group(4)
        ext = {"jpeg": "jpg", "svg+xml": "svg"}.get(mime, mime)
        alt_m = ALT_RE.search(m.group(0))
        name = slug(alt_m.group(1) if alt_m else "", f"img{idx}")
        fname = f"{stem}-{name}.{ext}"
        dest = out_dir / fname
        dest.write_bytes(base64.b64decode(b64))
        print(f"写出 {dest} ({dest.stat().st_size} bytes)")
        return f"{m.group(1)}images/{fname}{m.group(5)}"

    new, n = DATA_RE.subn(repl, html)
    path.write_text(new, encoding="utf-8", newline="\n")
    print(f"从 {path} 抽出 {n} 张图")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html", help="要处理的 HTML 文件")
    ap.add_argument("--extract", action="store_true", help="把 data-URI 抽成 images/ 相对路径")
    args = ap.parse_args()
    path = Path(args.html)
    if not path.is_file():
        print("文件不存在:", path)
        return 1
    return extract(path) if args.extract else embed(path)


if __name__ == "__main__":
    raise SystemExit(main())
