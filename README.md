# 招标文件分析器

一个用于分析和处理招标文件的桌面应用程序。

## 功能特点

- 支持多种文件格式（PDF、Word、Excel）的文档分析
- 自动提取关键信息
- 用户友好的图形界面
- 支持导出分析结果
- 批量处理功能

## 系统要求

- Python 3.6 或更高版本
- Windows 操作系统

## 依赖项

- pandas：数据处理
- openpyxl：Excel文件处理
- python-docx：Word文件处理
- PyPDF2：PDF文件处理
- PyInstaller：打包可执行文件

## 安装说明

1. 确保您的系统已安装 Python 3.6 或更高版本
2. 运行安装程序：
   ```bash
   python install.py
   ```
3. 安装程序会自动：
   - 安装所需的依赖包
   - 创建必要的目录结构
   - 在桌面创建快捷方式

## 使用方法

1. 双击桌面上的"招标文件分析器.exe"启动程序
2. 或在命令行中运行：
   ```bash
   python doc_analyzer_gui.py
   ```

## 目录结构

```
biaoshuchecklist/
├── install.py          # 安装脚本
├── doc_analyzer_gui.py # 主程序
├── icon_data.py       # 程序图标数据
├── README.md          # 项目说明文档
├── data/              # 数据目录
└── logs/              # 日志目录
```

## 作者

cofecatrj

## 更新日志

### 2025-07-20
- 初始版本发布
- 实现基本的文档分析功能
- 添加安装程序
