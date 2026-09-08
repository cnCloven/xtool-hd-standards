@echo off
setlocal
set SCRIPT=%~dp0build_pdf.py
where py >nul 2>&1 && (
  py -3 "%SCRIPT%" %*
  exit /b %ERRORLEVEL%
)
where python >nul 2>&1 && (
  python "%SCRIPT%" %*
  exit /b %ERRORLEVEL%
)
echo 未找到 Python。请安装 Python 3 并确保 py 或 python 在 PATH 中。
exit /b 1
