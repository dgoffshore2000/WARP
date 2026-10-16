@echo off
rem WARP V1.0 便携启动脚本（Windows）
rem 依赖已安装后双击即可；浏览器访问 http://127.0.0.1:8300
cd /d "%~dp0"
python warp_web.py
pause
