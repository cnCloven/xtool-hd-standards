# 规范打包

HTML 是源文件，PDF 是产物。

```bat
tools\build_pdf.bat
```

或：

```bash
python tools/build_pdf.py
```

依赖：Python 3、`playwright`、`pypdf`，以及 `python -m playwright install chromium`。

每次打包生成 `柴油日常开发规范_YYYYMMDD_HHMMSS.pdf`，并把根目录里其余往期 PDF 移入 `backup/`。截图请放到 `images/` 并用相对路径引用，不要把 base64 写进 HTML。
