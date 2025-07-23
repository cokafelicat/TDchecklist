@echo off
REM 一键安装脚本 for TDchecklist
cd /d %~dp0

REM 创建虚拟环境
python -m venv venv
call venv\Scripts\activate

REM 升级pip
python -m pip install --upgrade pip

REM 安装依赖
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo 未找到 requirements.txt，跳过依赖安装
)

REM 启动主程序
python doc_analyzer_gui.py --gui
