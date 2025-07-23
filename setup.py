from setuptools import setup, find_packages

setup(
    name="biaoshuchecklist",
    version="1.0.0",
    author="cofecatrj",
    author_email="renjun.eric@gmail.com",
    description="招标文件分析工具",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cofecatrj/biaoshuchecklist",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas",
        "python-docx",
        "PyPDF2",
        "openpyxl",
    ],
    entry_points={
        "console_scripts": [
            "biaoshuchecklist=biaoshuchecklist.doc_analyzer_gui:main",
        ],
    },
)
