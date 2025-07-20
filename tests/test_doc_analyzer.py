"""招标文件分析器测试套件"""

import os
import pytest
import pandas as pd
from pathlib import Path
from src.doc_analyzer import DocumentAnalyzer

# 测试文件路径
TEST_FILES_DIR = Path(__file__).parent / "test_files"

def test_doc_analyzer_initialization():
    """测试DocumentAnalyzer类的初始化"""
    analyzer = DocumentAnalyzer()
    assert analyzer is not None

def test_pdf_file_processing():
    """测试PDF文件处理"""
    analyzer = DocumentAnalyzer()
    pdf_file = TEST_FILES_DIR / "test.pdf"
    keywords = ["测试", "关键词"]
    
    # 确保测试文件存在
    assert pdf_file.exists(), "测试PDF文件不存在"
    
    results = analyzer.process_file(str(pdf_file), keywords)
    assert isinstance(results, pd.DataFrame)
    assert "关键词" in results.columns
    assert "出现次数" in results.columns

def test_docx_file_processing():
    """测试DOCX文件处理"""
    analyzer = DocumentAnalyzer()
    docx_file = TEST_FILES_DIR / "test.docx"
    keywords = ["测试", "关键词"]
    
    # 确保测试文件存在
    assert docx_file.exists(), "测试DOCX文件不存在"
    
    results = analyzer.process_file(str(docx_file), keywords)
    assert isinstance(results, pd.DataFrame)
    assert "关键词" in results.columns
    assert "出现次数" in results.columns

def test_invalid_file():
    """测试处理无效文件"""
    analyzer = DocumentAnalyzer()
    invalid_file = TEST_FILES_DIR / "invalid.txt"
    keywords = ["测试"]
    
    with pytest.raises(ValueError):
        analyzer.process_file(str(invalid_file), keywords)

def test_empty_keywords():
    """测试空关键词列表"""
    analyzer = DocumentAnalyzer()
    pdf_file = TEST_FILES_DIR / "test.pdf"
    
    with pytest.raises(ValueError):
        analyzer.process_file(str(pdf_file), [])

def test_keyword_file_loading():
    """测试关键词文件加载"""
    analyzer = DocumentAnalyzer()
    keyword_file = TEST_FILES_DIR / "keywords.txt"
    
    # 创建测试关键词文件
    with open(keyword_file, "w", encoding="utf-8") as f:
        f.write("关键词1,关键词2,关键词3\n")
    
    keywords = analyzer.load_keywords(str(keyword_file))
    assert len(keywords) == 3
    assert "关键词1" in keywords
    assert "关键词2" in keywords
    assert "关键词3" in keywords
    
    # 清理测试文件
    os.remove(keyword_file)

def test_results_export():
    """测试结果导出"""
    analyzer = DocumentAnalyzer()
    pdf_file = TEST_FILES_DIR / "test.pdf"
    keywords = ["测试", "关键词"]
    output_file = TEST_FILES_DIR / "test_output.xlsx"
    
    results = analyzer.process_file(str(pdf_file), keywords)
    analyzer.export_results(results, str(output_file))
    
    assert output_file.exists()
    
    # 验证导出的Excel文件
    df = pd.read_excel(str(output_file))
    assert "关键词" in df.columns
    assert "出现次数" in df.columns
    
    # 清理测试文件
    os.remove(output_file)

if __name__ == "__main__":
    pytest.main(["-v", __file__])
