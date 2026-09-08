#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge HD team spec HTML files into one PDF with jump links and embedded images.

Source of truth: NN-*.html + 规范总览.html (images via relative paths under images/).
Build artifact: 柴油日常开发规范_YYYYMMDD_HHMMSS.pdf  and  build/bundle.html
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import html as htmlmod
import mimetypes
import os
import re
import shutil
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import unquote, urlparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CHAPTER_NAME_RE = re.compile(r"^(\d{2})-.+\.html$", re.I)
INDEX_NAME = "规范总览.html"
DEFAULT_PDF_STEM = "柴油日常开发规范"
BACKUP_DIRNAME = "backup"
DOC_TITLE = "汽车诊断软件开发团队规范知识库"

SHARED_CSS = r"""
:root{
  --primary:#0b5cad; --primary-dark:#073d75; --bg:#f6f8fb;
  --card:#ffffff; --border:#dde3ec; --text:#1f2d3d; --muted:#6b7a90;
  --warn:#d98014; --ok:#1a8a3f; --danger:#c0392b;
}
*{box-sizing:border-box}
body{margin:0;font-family:"Microsoft YaHei","PingFang SC","Segoe UI",Arial,sans-serif;
     color:var(--text);background:var(--bg);line-height:1.75;font-size:15px}
header{background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;
       padding:20px 40px;box-shadow:0 2px 8px rgba(0,0,0,.1);
       -webkit-print-color-adjust:exact;print-color-adjust:exact}
.cover > header, section.cover header{padding:32px 40px}
header .crumb{font-size:12px;opacity:.85}
header .crumb a{color:#fff;text-decoration:underline}
header h1{margin:6px 0 0;font-size:22px}
.cover header h1{margin:0 0 8px;font-size:26px}
header .meta{opacity:.9;font-size:13px;margin-top:4px}
main{max-width:1000px;margin:20px auto;padding:0 24px}
.cover main{max-width:1100px;margin:24px auto}
.card{background:var(--card);border:1px solid var(--border);border-radius:8px;
      padding:24px 28px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
h2{color:var(--primary-dark);border-bottom:2px solid var(--primary);padding-bottom:8px;
   margin-top:0;font-size:19px}
h3{color:var(--primary-dark);font-size:16px;margin-top:22px;margin-bottom:6px}
h4{color:var(--text);font-size:15px;margin:14px 0 4px}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}
th,td{border:1px solid var(--border);padding:8px 12px;text-align:left;vertical-align:top}
th{background:#eef3fb;color:var(--primary-dark)}
tr:nth-child(even) td{background:#fafbfd}
ul,ol{margin:8px 0 8px 24px;padding:0}
li{margin:5px 0}
code{background:#eef3fb;padding:2px 6px;border-radius:3px;
     font-family:Consolas,Monaco,monospace;font-size:13px;color:var(--primary-dark)}
pre{background:#1f2d3d;color:#e6e6e6;padding:14px;border-radius:6px;overflow-x:auto;font-size:13px;
    white-space:pre-wrap;word-break:break-word}
pre code{background:transparent;color:inherit;padding:0}
a{color:var(--primary);text-decoration:none}
a:hover{text-decoration:underline}
.note{background:#eef5ff;border-left:4px solid var(--primary);padding:12px 16px;
      margin:12px 0;border-radius:0 4px 4px 0;font-size:14px}
.warn{background:#fff4e0;border-left:4px solid var(--warn);padding:12px 16px;
      margin:12px 0;border-radius:0 4px 4px 0;font-size:14px}
.danger{background:#fdecea;border-left:4px solid var(--danger);padding:12px 16px;
        margin:12px 0;border-radius:0 4px 4px 0;font-size:14px}
.ok{background:#e6f4ec;border-left:4px solid var(--ok);padding:12px 16px;
    margin:12px 0;border-radius:0 4px 4px 0;font-size:14px}
.purpose{background:#fff8ec;border-left:4px solid var(--warn);padding:12px 16px;
         border-radius:4px;margin:16px 0;color:#7a4a00}
.empty{display:flex;flex-direction:column;align-items:center;justify-content:center;
       height:200px;color:var(--muted);text-align:center}
.empty .icon{font-size:38px;margin-bottom:10px;opacity:.5}
.empty .t{font-size:15px;color:var(--warn);font-weight:600}
.empty .s{font-size:13px;margin-top:6px}
footer{text-align:center;color:var(--muted);font-size:12px;padding:20px}
figure{margin:16px 0;text-align:center}
figure img{max-width:100%;height:auto;border:1px solid var(--border);border-radius:6px}
figure.placeholder{background:#fff7e6;border:2px dashed #f0b429;border-radius:8px;padding:20px}
figure.placeholder .img-tip{color:var(--warn);font-weight:600;font-size:13px}
figure figcaption{margin-top:8px;font-size:13px;color:var(--muted)}
.toc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}
.toc-item{display:block;padding:14px 16px;border:1px solid var(--border);border-radius:8px;
          background:#fbfcfe;text-decoration:none;color:inherit}
.toc-item:hover{border-color:var(--primary);background:#fff;text-decoration:none}
.toc-item .n{color:var(--muted);font-size:12px;font-weight:bold}
.toc-item .t{font-weight:600;color:var(--text);margin-top:2px}
.toc-item .s{font-size:12px;margin-top:4px;display:inline-block;padding:2px 8px;
             border-radius:10px;background:#eef3fb;color:var(--primary-dark)}
.toc-item .s.wip{background:#fff4e0;color:var(--warn)}
.legend{margin-top:14px;font-size:13px;color:var(--muted)}
.legend .s{font-size:12px;display:inline-block;padding:2px 8px;border-radius:10px;
           background:#eef3fb;color:var(--primary-dark)}
.legend .s.wip{background:#fff4e0;color:var(--warn)}
.core-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0}
.core-item{border:1px solid var(--border);border-radius:6px;padding:12px 14px;background:#fbfcfe}
.core-item .k{font-size:12px;color:var(--muted);font-weight:700}
.core-item .v{margin-top:4px;font-weight:600;color:var(--primary-dark)}

@page{size:A4;margin:12mm 10mm 16mm 10mm}
@media print{
  html,body{background:#fff}
  header{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  .note,.warn,.danger,.ok,.purpose,th,pre,code,.toc-item,.card,.core-item{
    -webkit-print-color-adjust:exact;print-color-adjust:exact}
  .chapter{break-before:page}
  .chapter.cover{break-before:auto}
  h2,h3,h4,header{break-after:avoid}
  figure,pre,table,.core-grid{break-inside:avoid}
  figure img{max-height:170mm;object-fit:contain}
  a.toc-item{text-decoration:none}
}
""".strip()


def find_root(start: Optional[Path] = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for p in [cur, *cur.parents]:
        if (p / INDEX_NAME).exists() or any(CHAPTER_NAME_RE.match(x.name) for x in p.glob("*.html")):
            return p
    return cur


def read_html(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_tag_inner(html: str, tag: str) -> str:
    m = re.search(rf"<{tag}\b[^>]*>(.*)</{tag}>", html, re.S | re.I)
    return m.group(1) if m else html


def strip_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return htmlmod.unescape(re.sub(r"\s+", " ", text)).strip()


def chapter_title_from_html(html: str, fallback: str) -> str:
    m = re.search(r"<h1\b[^>]*>(.*?)</h1>", html, re.S | re.I)
    return strip_tags(m.group(1)) if m else fallback


def collect_chapters(root: Path) -> List[Tuple[str, Path]]:
    items = []
    for p in root.iterdir():
        if not p.is_file():
            continue
        m = CHAPTER_NAME_RE.match(p.name)
        if m:
            items.append((m.group(1), p))
    items.sort(key=lambda x: x[0])
    return items


def embed_images(html: str, base_dir: Path, missing: List[str]) -> str:
    pattern = re.compile(r'(<img\b[^>]*?\bsrc=["\'])([^"\']+)(["\'])', re.I)

    def repl(m: re.Match) -> str:
        src = m.group(2).strip()
        if src.startswith(("data:", "http://", "https://", "//", "about:")):
            return m.group(0)
        rel = unquote(src).replace("\\", "/")
        path = (base_dir / rel).resolve()
        if not path.is_file():
            missing.append(str(rel))
            return m.group(0)
        mime = mimetypes.guess_type(str(path))[0] or "image/png"
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"{m.group(1)}data:{mime};base64,{b64}{m.group(3)}"

    return pattern.sub(repl, html)


def rewrite_internal_links(html: str) -> str:
    pattern = re.compile(r'href=["\']([^"\']+)["\']')

    def repl(m: re.Match) -> str:
        href = m.group(1).strip()
        if href.startswith(("http://", "https://", "mailto:", "data:", "javascript:")):
            return m.group(0)
        if href.startswith("#"):
            return m.group(0)
        file, frag = (href.split("#", 1) + [""])[:2]
        file = unquote(file).replace("\\", "/").split("/")[-1]
        if file == INDEX_NAME or file == "":
            return 'href="#top"'
        mm = CHAPTER_NAME_RE.match(file)
        if mm:
            return f'href="#sec-{mm.group(1)}"'
        # 仓库内其它文件（如 templates/*.html）：从 build/bundle.html 出发要先回到仓库根
        orig = href.replace("\\", "/")
        if orig.startswith("../"):
            return f'href="{orig}"'
        return f'href="../{orig}"'

    return pattern.sub(repl, html)


def toc_hrefs(index_html: str) -> List[str]:
    return re.findall(r'href=["\']([^"\']+\.html)["\']', index_html)


def build_bundle(root: Path) -> Tuple[str, List[Tuple[str, str]]]:
    """Return (bundle_html, [(sec_id, title), ...]) including ('top', index title)."""
    index_path = root / INDEX_NAME
    chapters = collect_chapters(root)
    if not chapters:
        raise SystemExit("未找到 NN-*.html 章节文件")

    missing_imgs: List[str] = []
    outline: List[Tuple[str, str]] = []
    parts: List[str] = []

    if index_path.exists():
        raw = read_html(index_path)
        body = extract_tag_inner(raw, "body")
        body = embed_images(body, root, missing_imgs)
        body = rewrite_internal_links(body)
        title = chapter_title_from_html(raw, DOC_TITLE)
        outline.append(("top", title))
        parts.append(
            f'<section class="chapter cover" id="top">\n<a name="top"></a>\n{body}\n</section>'
        )
        listed = toc_hrefs(raw)
        listed_files = {unquote(h).replace("\\", "/").split("/")[-1] for h in listed}
        chapter_files = {p.name for _, p in chapters}
        extra = sorted(chapter_files - listed_files)
        missing_toc = sorted(listed_files - chapter_files)
        if extra:
            print("警告: 以下章节未出现在规范总览索引中:", ", ".join(extra))
        if missing_toc:
            print("警告: 规范总览链接了但不存在的文件:", ", ".join(missing_toc))
    else:
        print("警告: 未找到规范总览.html，将自动生成封面索引")
        cards = []
        for num, path in chapters:
            cards.append(
                f'<a class="toc-item" href="#sec-{num}">'
                f'<div class="n">{num}</div>'
                f'<div class="t">{htmlmod.escape(path.stem[3:])}</div></a>'
            )
        auto = f"""
<header><h1>{htmlmod.escape(DOC_TITLE)}</h1>
<div class="meta">自动生成封面（缺少 {INDEX_NAME}）</div></header>
<main><div class="card"><h2>文档索引</h2>
<div class="toc-grid">{''.join(cards)}</div></div></main>
<footer>© 汽车诊断软件开发团队 · 内部资料 · 请勿外传</footer>
"""
        outline.append(("top", DOC_TITLE))
        parts.append(f'<section class="chapter cover" id="top">\n<a name="top"></a>\n{auto}\n</section>')

    for num, path in chapters:
        raw = read_html(path)
        body = extract_tag_inner(raw, "body")
        body = embed_images(body, root, missing_imgs)
        body = rewrite_internal_links(body)
        title = chapter_title_from_html(raw, path.stem)
        outline.append((f"sec-{num}", title))
        parts.append(
            f'<section class="chapter" id="sec-{num}">\n'
            f'<a name="sec-{num}"></a>\n{body}\n</section>'
        )

    if missing_imgs:
        uniq = sorted(set(missing_imgs))
        raise SystemExit("图片文件缺失，请放到对应路径后再打包:\n  - " + "\n  - ".join(uniq))

    bundle = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{htmlmod.escape(DOC_TITLE)}</title>
<style>
{SHARED_CSS}
</style>
</head>
<body>
{''.join(parts)}
</body>
</html>
"""
    return bundle, outline


def print_pdf(bundle_path: Path, pdf_path: Path, page_format: str) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise SystemExit(
            "未安装 playwright。请执行: python -m pip install playwright && python -m playwright install chromium"
        ) from e

    uri = bundle_path.resolve().as_uri()
    footer = (
        '<div style="font-size:9px;width:100%;text-align:center;color:#6b7a90;'
        "font-family:'Microsoft YaHei',sans-serif;padding-top:2px;\">"
        '汽车诊断软件开发团队 · 内部资料 · 请勿外传 · '
        '<span class="pageNumber"></span> / <span class="totalPages"></span></div>'
    )
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--disable-dev-shm-usage"])
        page = browser.new_page()
        page.goto(uri, wait_until="load", timeout=120000)
        page.evaluate(
            """() => Promise.all([...document.images].map(img => {
                if (img.complete) return Promise.resolve();
                return new Promise(r => { img.onload = img.onerror = r; });
            }))"""
        )
        page.emulate_media(media="print")
        page.pdf(
            path=str(pdf_path),
            format=page_format,
            print_background=True,
            prefer_css_page_size=True,
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=footer,
            outline=True,
            tagged=True,
            margin={"top": "10mm", "bottom": "14mm", "left": "8mm", "right": "8mm"},
        )
        browser.close()


def file_uri_to_path(uri: str) -> Optional[Path]:
    try:
        parsed = urlparse(uri)
    except Exception:
        return None
    if parsed.scheme != "file":
        return None
    path = unquote(parsed.path)
    if os.name == "nt" and re.match(r"^/[A-Za-z]:", path):
        path = path[1:]
    if not path:
        return None
    return Path(path)


def relativize_local_file_links(writer, pdf_path: Path, repo_root: Path) -> List[str]:
    """Turn Chromium's file:///E:/... URIs into paths relative to the PDF file."""
    from pypdf.generic import DictionaryObject, NameObject, create_string_object

    pdf_dir = pdf_path.resolve().parent
    repo_root = repo_root.resolve()
    rewritten = []
    for page in writer.pages:
        annots = page.get("/Annots")
        if not annots:
            continue
        for annot in annots:
            obj = annot.get_object()
            action = obj.get("/A")
            if action is None:
                continue
            action = action.get_object()
            uri = action.get("/URI")
            if not uri:
                continue
            uri_s = str(uri)
            target = file_uri_to_path(uri_s)
            if target is None:
                continue
            try:
                target = target.resolve()
                target.relative_to(repo_root)
                rel = Path(os.path.relpath(target, pdf_dir)).as_posix()
            except (OSError, ValueError):
                continue
            new_action = DictionaryObject()
            new_action[NameObject("/Type")] = NameObject("/Action")
            new_action[NameObject("/S")] = NameObject("/Launch")
            fs = DictionaryObject()
            fs[NameObject("/Type")] = NameObject("/Filespec")
            fs[NameObject("/F")] = create_string_object(rel)
            fs[NameObject("/UF")] = create_string_object(rel)
            new_action[NameObject("/F")] = fs
            obj[NameObject("/A")] = new_action
            rewritten.append(rel)
    return rewritten


def dest_page_index(reader, name: str) -> Optional[int]:
    nd = reader.named_destinations or {}
    dest = nd.get(name) or nd.get("/" + name)
    if dest is None:
        return None
    page = getattr(dest, "page", None)
    if page is None and isinstance(dest, dict):
        page = dest.get("/Page")
    if page is None:
        return None
    try:
        page = page.get_object() if hasattr(page, "get_object") else page
    except Exception:
        pass
    for i, p in enumerate(reader.pages):
        try:
            if p == page or p.indirect_reference == getattr(page, "indirect_reference", None):
                return i
        except Exception:
            continue
        try:
            if p.indirect_reference == page:
                return i
        except Exception:
            continue
    return None


def polish_pdf(pdf_path: Path, outline: List[Tuple[str, str]], repo_root: Path) -> None:
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("提示: 未安装 pypdf，跳过书签/元数据后处理。pip install pypdf")
        return

    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    writer.append(reader)
    rewritten = relativize_local_file_links(writer, pdf_path, repo_root)
    if rewritten:
        print("相对文件跳转:")
        for rel in rewritten:
            print("  ", rel)
    writer.add_metadata(
        {
            "/Title": DOC_TITLE,
            "/Author": "汽车诊断软件开发团队",
            "/Creator": "hd-spec-docs / tools/build_pdf.py",
            "/Subject": "部门日常开发规范（HTML 知识库打包）",
        }
    )

    # Chapter-level bookmarks (Playwright outline=True already adds heading bookmarks;
    # add a clean top-level outline as well if named dests exist).
    try:
        # If Chromium already wrote an outline, keep it and just set metadata.
        existing = bool(reader.outline)
    except Exception:
        existing = False

    if not existing:
        for dest_id, title in outline:
            idx = dest_page_index(reader, dest_id)
            if idx is None:
                # fallback: first page for cover, skip others
                if dest_id == "top":
                    idx = 0
                else:
                    continue
            writer.add_outline_item(title, idx)

    tmp = pdf_path.with_suffix(".tmp.pdf")
    with open(tmp, "wb") as f:
        writer.write(f)
    tmp.replace(pdf_path)

    verify = PdfReader(str(pdf_path))
    n_annot = 0
    n_img = 0
    for p in verify.pages:
        annots = p.get("/Annots")
        if annots:
            n_annot += len(annots)
        try:
            n_img += len(p.images)
        except Exception:
            pass
    dests = list((verify.named_destinations or {}).keys())
    print(f"PDF 页数: {len(verify.pages)}")
    print(f"命名锚点: {dests}")
    print(f"链接注释: {n_annot}")
    print(f"内嵌图片: {n_img}")
    if not any("sec-" in str(d) or str(d).endswith("01") for d in dests) and n_annot == 0:
        print("警告: 未检测到内部跳转锚点/链接，请打开 PDF 检查目录页是否可点击。")


def stamped_pdf_name() -> str:
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{DEFAULT_PDF_STEM}_{ts}.pdf"


def _unique_dest(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    n = 2
    while True:
        cand = dest.with_name(f"{stem}_{n}{suffix}")
        if not cand.exists():
            return cand
        n += 1


def _move_pdf(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        src.replace(dest)
        return
    except PermissionError:
        pass
    shutil.copy2(src, dest)
    for _ in range(6):
        try:
            src.unlink()
            return
        except PermissionError:
            time.sleep(0.4)
    raise PermissionError(str(src))


def archive_previous_pdfs(root: Path, keep: Path) -> None:
    """Move every previous 柴油日常开发规范*.pdf in the repo root into backup/."""
    backup = root / BACKUP_DIRNAME
    backup.mkdir(exist_ok=True)
    keep_res = keep.resolve()
    moved = []
    locked = []
    for p in sorted(root.glob(f"{DEFAULT_PDF_STEM}*.pdf")):
        if not p.is_file():
            continue
        if p.resolve() == keep_res:
            continue
        dest = _unique_dest(backup / p.name)
        try:
            _move_pdf(p, dest)
            moved.append(f"{p.name} → {BACKUP_DIRNAME}/{dest.name}")
        except PermissionError:
            locked.append(p.name)
    if moved:
        print("已归档往期 PDF:")
        for line in moved:
            print("  ", line)
    if locked:
        print("警告: 下列 PDF 正被占用，未能移入 backup/（请关闭预览后再次打包，或手动移动）：")
        for name in locked:
            print("  ", name)
    if not moved and not locked:
        print("无往期 PDF 需要归档")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="将部门规范 HTML 打包为带跳转链接的 PDF")
    ap.add_argument("--root", default="", help="规范根目录（默认自动探测）")
    ap.add_argument(
        "--out",
        default="",
        help="输出 PDF 文件名（默认 柴油日常开发规范_YYYYMMDD_HHMMSS.pdf）",
    )
    ap.add_argument("--format", choices=["A4", "Letter"], default="A4")
    ap.add_argument("--bundle-only", action="store_true", help="只生成 build/bundle.html，不打印 PDF")
    args = ap.parse_args(argv)

    root = find_root(Path(args.root) if args.root else None)
    os.chdir(root)
    print("规范根目录:", root)

    bundle, outline = build_bundle(root)
    build_dir = root / "build"
    build_dir.mkdir(exist_ok=True)
    bundle_path = build_dir / "bundle.html"
    bundle_path.write_text(bundle, encoding="utf-8")
    print("已写入", bundle_path, f"({bundle_path.stat().st_size} bytes)")
    print("章节:")
    for dest_id, title in outline:
        print(f"  #{dest_id}  {title}")

    if args.bundle_only:
        return 0

    out_name = args.out.strip() or stamped_pdf_name()
    pdf_path = root / out_name
    print("正在用 Chromium 打印 PDF …")
    print_pdf(bundle_path, pdf_path, args.format)
    polish_pdf(pdf_path, outline, root)
    print("已生成", pdf_path, f"({pdf_path.stat().st_size} bytes)")
    archive_previous_pdfs(root, pdf_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
