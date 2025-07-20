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
├── src/                    # 源代码目录
│   ├── doc_analyzer.py     # 核心分析模块
│   ├── doc_analyzer_gui.py # 图形界面程序
│   └── icon_data.py       # 程序图标数据
├── tests/                  # 测试目录
│   ├── test_doc_analyzer.py # 核心模块测试
│   └── test_files/        # 测试用文件
├── docs/                   # 文档目录
├── data/                   # 数据目录
├── logs/                   # 日志目录
├── install.py             # 安装脚本
├── setup.py              # 项目配置文件
├── requirements.txt      # 项目依赖
├── requirements-dev.txt  # 开发依赖
├── tox.ini              # 测试配置
└── README.md            # 项目说明文档
```

## 开发说明

### 开发环境设置

1. 克隆仓库：
   ```bash
   git clone https://github.com/cofecatrj/biaoshuchecklist.git
   cd biaoshuchecklist
   ```

2. 创建虚拟环境：
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. 安装开发依赖：
   ```bash
   pip install -r requirements-dev.txt
   ```

### 运行测试

```bash
pytest
```

或使用tox运行完整测试套件：

```bash
tox
```

## 作者

cofecatrj (renjun.eric@gmail.com)

## 更新日志

### 2025-07-20
- 初始版本发布
- 实现基本的文档分析功能
- 添加安装程序
