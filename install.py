#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
招标文件分析器安装程序

此程序用于安装招标文件分析器及其依赖项。
完全使用Python实现，确保安全性和跨平台兼容性。

作者: cofecatrj
日期: 2025-07-20
"""

import os
import sys
import site
import shutil
import subprocess
import platform
from pathlib import Path
import logging
from datetime import datetime

def setup_logger():
    """配置日志记录"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f'install_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()

def check_python_version():
    """检查Python版本是否满足要求"""
    logger.info("检查Python版本...")
    if sys.version_info < (3, 6):
        logger.error("Python版本必须是3.6或更高版本")
        return False
    logger.info(f"Python版本检查通过: {platform.python_version()}")
    return True

def install_package(package):
    """安装指定的Python包"""
    logger.info(f"正在安装 {package}...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        logger.info(f"{package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"安装 {package} 失败: {e}")
        return False

def install_requirements():
    """安装所有依赖包"""
    logger.info("开始安装依赖包...")
    requirements = [
        'pandas',
        'openpyxl',
        'python-docx',
        'PyPDF2',
        'pyinstaller'
    ]
    
    all_success = True
    for package in requirements:
        if not install_package(package):
            all_success = False
    
    if all_success:
        logger.info("所有依赖包安装完成")
    else:
        logger.error("部分依赖包安装失败")
    return all_success

def create_directories():
    """创建必要的目录结构"""
    logger.info("创建目录结构...")
    directories = ['logs', 'data']
    
    try:
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logger.info(f"目录 {directory} 创建成功")
        return True
    except Exception as e:
        logger.error(f"创建目录失败: {e}")
        return False

def create_executable():
    """创建可执行文件"""
    logger.info("开始创建可执行文件...")
    try:
        # 创建临时的spec文件
        spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['doc_analyzer_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='招标文件分析器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
'''
        # 创建图标文件
        create_icon()
        
        # 保存spec文件
        with open('analyzer.spec', 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        logger.info("正在编译可执行文件（这可能需要几分钟时间）...")
        # 使用PyInstaller编译
        subprocess.check_call([
            sys.executable,
            '-m',
            'PyInstaller',
            '--clean',
            'analyzer.spec'
        ])
        
        # 复制可执行文件到桌面
        desktop = Path.home() / 'Desktop'
        exe_path = Path('dist') / '招标文件分析器.exe'
        if exe_path.exists():
            shutil.copy2(exe_path, desktop / '招标文件分析器.exe')
            logger.info("可执行文件创建完成")
            return True
        else:
            logger.error("可执行文件未能正确创建")
            return False
            
    except Exception as e:
        logger.error(f"创建可执行文件失败: {e}")
        return False

def create_icon():
    """创建程序图标"""
    try:
        import base64
        from icon_data import ICON_DATA
        
        # 将base64数据转换为图片文件
        icon_data = base64.b64decode(ICON_DATA)
        with open('icon.ico', 'wb') as f:
            f.write(icon_data)
        logger.info("程序图标创建成功")
        return True
    except Exception as e:
        logger.error(f"创建图标失败: {e}")
        return False

def setup():
    """主安装程序"""
    print("=== 招标文件分析器安装程序 ===\n")
    logger.info("开始安装...")

    # 检查Python版本
    if not check_python_version():
        return False

    # 安装依赖包
    if not install_requirements():
        return False

    # 创建目录结构
    if not create_directories():
        return False

    # 创建可执行文件
    if not create_executable():
        return False

    logger.info("安装完成！")
    print("\n=== 安装完成 ===")
    print("您可以通过双击桌面上的'招标文件分析器.exe'来启动程序")
    print("\n如需帮助，请查看程序目录下的日志文件。")
    
    return True

def main():
    """程序入口"""
    try:
        if setup():
            input("\n按回车键退出...")
        else:
            logger.error("安装失败")
            input("\n安装失败，按回车键退出...")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("安装被用户中断")
        print("\n\n安装被用户中断")
    except Exception as e:
        logger.error(f"安装过程中发生错误: {e}")
        print(f"\n安装过程中发生错误: {e}")
        input("按回车键退出...")
        sys.exit(1)

if __name__ == '__main__':
    main()
