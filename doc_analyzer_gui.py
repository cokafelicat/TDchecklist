#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
招标文件分析器 (Tender Document Analyzer)

这是一个用于分析招标文件中关键词的工具，支持PDF和DOCX格式文件。

功能特点:
    - 支持PDF和DOCX格式文件的分析
    - 关键词批量导入（支持TXT文件，使用逗号或换行符分隔）
    - 结果导出为Excel格式
    - 完整的日志记录系统
    - 支持GUI和命令行两种操作模式

使用方法:
    GUI模式:
        python doc_analyzer_gui.py
        或
        python doc_analyzer_gui.py --gui

    命令行模式:
        python doc_analyzer_gui.py -k 关键词文件.txt -d 招标文件.pdf -o 输出结果.xlsx

版本: 1.0.0
作者: cofecatrj
日期: 2025-07-20
许可: MIT License
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import pandas as pd
from doc_analyzer import DocumentAnalyzer
import sys
import logging
from datetime import datetime
import traceback

# 版本信息
__version__ = '1.0.0'
__author__ = 'cofecatrj'
__date__ = '2025-07-20'

# 配置日志记录
def setup_logger():
    # 创建logs目录（如果不存在）
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # 设置日志文件名（使用当前日期）
    log_file = os.path.join('logs', f'tender_analyzer_{datetime.now().strftime("%Y%m%d")}.log')
    
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

# 创建logger实例
logger = setup_logger()

class TenderAnalyzerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f'招标文件分析器 v{__version__}')
        self.root.geometry('1200x800')
        
        logger.info(f"启动招标文件分析器 v{__version__}")
        
        try:
            self.analyzer = DocumentAnalyzer()
            
            # 创建状态标签（在setup_gui之前）
            self.status_label = ttk.Label(self.root, text="就绪", anchor=tk.W)
            
            self.setup_gui()
            
            # 在setup_gui之后放置状态标签
            self.status_label.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
            
            # 显示版本信息
            self.show_version_info()
            
        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            logger.error(traceback.format_exc())
            messagebox.showerror("错误", f"程序初始化失败：{str(e)}")

    def show_version_info(self):
        """显示版本信息"""
        version_frame = ttk.Frame(self.root)
        version_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        version_label = ttk.Label(
            version_frame,
            text=f"版本: {__version__} | 作者: {__author__} | 日期: {__date__}",
            anchor=tk.E
        )
        version_label.pack(side=tk.RIGHT)

    def setup_gui(self):
        """创建GUI界面"""
        logger.debug("开始设置GUI界面")
        
        # 创建主布局
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # 左侧面板 - 关键词管理
        left_frame = ttk.LabelFrame(main_frame, text="关键词管理", padding="5")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        # 关键词输入区域
        keyword_frame = ttk.Frame(left_frame)
        keyword_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        keyword_frame.columnconfigure(0, weight=1)
        
        self.keyword_var = tk.StringVar()
        keyword_entry = ttk.Entry(keyword_frame, textvariable=self.keyword_var)
        keyword_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        add_btn = ttk.Button(keyword_frame, text="添加关键词", command=self.add_keyword)
        add_btn.grid(row=0, column=1, padx=5)

        # 关键词列表
        self.keyword_list = tk.Listbox(left_frame, selectmode=tk.EXTENDED)
        self.keyword_list.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 为关键词列表添加滚动条
        keyword_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.keyword_list.yview)
        keyword_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.keyword_list.configure(yscrollcommand=keyword_scrollbar.set)
        
        self.update_keyword_list()

        # 关键词操作按钮
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        remove_btn = ttk.Button(btn_frame, text="删除选中", command=self.remove_keywords)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(btn_frame, text="清空所有", command=self.clear_keywords)
        clear_btn.pack(side=tk.LEFT, padx=5)

        import_btn = ttk.Button(btn_frame, text="导入关键词", command=self.import_keywords)
        import_btn.pack(side=tk.LEFT, padx=5)

        # 右侧面板 - 文档处理
        right_frame = ttk.LabelFrame(main_frame, text="招标文件处理", padding="5")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        main_frame.columnconfigure(1, weight=3)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        # 文件选择区域
        file_frame = ttk.Frame(right_frame)
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        file_frame.columnconfigure(0, weight=1)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state='readonly')
        file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        browse_btn = ttk.Button(file_frame, text="浏览文件", command=self.browse_file)
        browse_btn.grid(row=0, column=1, padx=5)
        
        analyze_btn = ttk.Button(file_frame, text="分析文档", command=self.analyze_document)
        analyze_btn.grid(row=0, column=2, padx=5)

        # 结果显示表格
        self.result_tree = ttk.Treeview(right_frame, columns=('no', 'section', 'page', 'keyword', 'content'),
                                      show='headings', height=20)
        self.result_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # 设置列标题
        self.result_tree.heading('no', text='序号')
        self.result_tree.heading('section', text='章节')
        self.result_tree.heading('page', text='页码')
        self.result_tree.heading('keyword', text='关键词')
        self.result_tree.heading('content', text='内容')

        # 设置列宽
        self.result_tree.column('no', width=50, minwidth=50)
        self.result_tree.column('section', width=100, minwidth=100)
        self.result_tree.column('page', width=50, minwidth=50)
        self.result_tree.column('keyword', width=100, minwidth=100)
        self.result_tree.column('content', width=500, minwidth=300)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.result_tree.configure(yscrollcommand=scrollbar.set)

        # 导出按钮
        export_btn = ttk.Button(right_frame, text="导出结果", command=self.export_results)
        export_btn.grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        
        logger.debug("GUI界面设置完成")

    def update_status(self, message):
        """更新状态栏信息"""
        logger.debug(f"状态更新: {message}")
        self.status_label.config(text=message)
        self.root.update()

    def update_keyword_list(self):
        """更新关键词列表显示"""
        self.keyword_list.delete(0, tk.END)
        keywords = sorted(self.analyzer.keywords)
        for keyword in keywords:
            self.keyword_list.insert(tk.END, keyword)
        self.update_status(f"当前共有 {len(keywords)} 个关键词")
        logger.debug(f"更新关键词列表，共 {len(keywords)} 个")

    def add_keyword(self):
        """添加关键词"""
        keyword = self.keyword_var.get().strip()
        if keyword:
            logger.info(f"添加关键词: {keyword}")
            self.analyzer.add_keywords([keyword])
            self.keyword_var.set('')
            self.update_keyword_list()
            self.update_status(f"已添加关键词: {keyword}")

    def remove_keywords(self):
        """删除选中的关键词"""
        selected = self.keyword_list.curselection()
        if selected:
            keywords = [self.keyword_list.get(i) for i in selected]
            logger.info(f"删除关键词: {', '.join(keywords)}")
            self.analyzer.remove_keywords(keywords)
            self.update_keyword_list()
            self.update_status(f"已删除 {len(keywords)} 个关键词")

    @staticmethod
    def process_keywords_file(file_path):
        """处理关键词文件，支持逗号和换行符分隔"""
        keywords = set()  # 使用集合去重
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            # 首先按换行符分割
            lines = content.split('\n')
            for line in lines:
                # 对每一行按逗号分割
                if line.strip():
                    words = line.split('，')  # 使用中文逗号分割
                    # 处理每个关键词
                    for word in words:
                        word = word.strip()
                        if word:
                            keywords.add(word)
            
            return list(keywords)
        except Exception as e:
            raise Exception(f"处理关键词文件失败: {str(e)}")

    def import_keywords(self):
        """从文本文件导入关键词"""
        file_path = filedialog.askopenfilename(
            title='选择关键词文件',
            filetypes=[('文本文件', '*.txt'), ('所有文件', '*.*')]
        )
        if not file_path:
            return

        try:
            logger.info(f"开始从文件导入关键词: {file_path}")
            self.update_status("正在导入关键词...")
            
            # 处理关键词文件
            keywords = self.process_keywords_file(file_path)
            
            if not keywords:
                messagebox.showwarning('警告', '文件中没有找到有效的关键词！')
                return
            
            # 添加关键词
            self.analyzer.add_keywords(keywords)
            self.update_keyword_list()
            
            logger.info(f"成功导入 {len(keywords)} 个关键词")
            self.update_status(f"成功导入 {len(keywords)} 个关键词")
            messagebox.showinfo('成功', f'已成功导入 {len(keywords)} 个关键词！')
            
        except Exception as e:
            error_msg = f"导入关键词失败：{str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.update_status(error_msg)
            messagebox.showerror('错误', error_msg)

    def clear_keywords(self):
        """清空所有关键词"""
        if messagebox.askyesno('确认', '确定要删除所有关键词吗？'):
            count = len(self.analyzer.keywords)
            logger.info(f"清空所有关键词，共 {count} 个")
            self.analyzer.keywords.clear()
            self.analyzer.save_keywords([])
            self.update_keyword_list()
            self.update_status(f"已清空所有关键词，共 {count} 个")

    def browse_file(self):
        """浏览并选择文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[('招标文档', '*.pdf;*.docx'), ('所有文件', '*.*')]
        )
        if file_path:
            logger.info(f"选择文件: {file_path}")
            self.file_path_var.set(file_path)
            self.update_status(f"已选择文件: {os.path.basename(file_path)}")

    def analyze_document(self):
        """分析文档并显示结果"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning('警告', '请先选择要分析的招标文件！')
            return

        if not self.analyzer.keywords:
            messagebox.showwarning('警告', '请先添加关键词！')
            return

        try:
            logger.info(f"开始分析文档: {file_path}")
            self.update_status("正在分析文档...")
            # 清空现有结果
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)

            # 分析文档
            results = self.analyzer.process_document(file_path)
            
            # 显示结果
            for i, result in enumerate(results, 1):
                self.result_tree.insert('', tk.END, values=(
                    i,
                    result.get('section', ''),
                    result['page'],
                    result['keyword'],
                    result['text']
                ))
            
            logger.info(f"分析完成，找到 {len(results)} 个匹配结果")
            self.update_status(f"分析完成，找到 {len(results)} 个匹配结果")
            
        except Exception as e:
            error_msg = f"处理文档时出错：{str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.update_status(f"错误：{str(e)}")
            messagebox.showerror('错误', error_msg)

    def export_results(self):
        """导出结果到Excel文件"""
        if not self.result_tree.get_children():
            messagebox.showwarning('警告', '没有可导出的结果！')
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[('Excel文件', '*.xlsx'), ('所有文件', '*.*')]
        )
        if not file_path:
            return

        try:
            logger.info(f"开始导出结果到: {file_path}")
            self.update_status("正在导出结果...")
            # 获取所有结果
            data = []
            for item in self.result_tree.get_children():
                values = self.result_tree.item(item)['values']
                data.append({
                    '序号': values[0],
                    '章节': values[1],
                    '页码': values[2],
                    '关键词': values[3],
                    '内容': values[4]
                })

            # 导出到Excel
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            
            logger.info("导出完成")
            self.update_status("导出完成")
            messagebox.showinfo('成功', '结果已成功导出！')
        except Exception as e:
            error_msg = f"导出失败：{str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.update_status(f"导出失败：{str(e)}")
            messagebox.showerror('错误', error_msg)

    def run(self):
        """运行GUI程序"""
        logger.info("启动主循环")
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"主循环异常: {str(e)}")
            logger.error(traceback.format_exc())
        finally:
            logger.info("程序结束")

def process_command_line(doc_file=None, keywords_file=None, output_file=None):
    """处理命令行操作"""
    try:
        analyzer = DocumentAnalyzer()
        
        # 如果提供了关键词文件，导入关键词
        if keywords_file:
            logger.info(f"从文件导入关键词: {keywords_file}")
            keywords = TenderAnalyzerGUI.process_keywords_file(keywords_file)
            if keywords:
                analyzer.add_keywords(keywords)
                logger.info(f"成功导入 {len(keywords)} 个关键词")
            else:
                logger.error("关键词文件中没有找到有效的关键词")
                return False

        # 如果提供了文档文件，进行分析
        if doc_file:
            if not analyzer.keywords:
                logger.error("没有可用的关键词，请先提供关键词文件")
                return False
                
            logger.info(f"开始分析文档: {doc_file}")
            results = analyzer.process_document(doc_file)
            logger.info(f"分析完成，找到 {len(results)} 个匹配结果")
            
            # 如果提供了输出文件，导出结果
            if output_file:
                logger.info(f"开始导出结果到: {output_file}")
                data = []
                for i, result in enumerate(results, 1):
                    data.append({
                        '序号': i,
                        '章节': result.get('section', ''),
                        '页码': result['page'],
                        '关键词': result['keyword'],
                        '内容': result['text']
                    })
                df = pd.DataFrame(data)
                df.to_excel(output_file, index=False)
                logger.info("导出完成")
                
        return True
            
    except Exception as e:
        logger.error(f"命令行处理出错: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def main():
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='招标文件分析器')
    parser.add_argument('-d', '--doc', help='要分析的招标文档路径')
    parser.add_argument('-k', '--keywords', help='关键词文件路径')
    parser.add_argument('-o', '--output', help='分析结果输出文件路径')
    parser.add_argument('-g', '--gui', action='store_true', help='启动图形界面')
    
    args = parser.parse_args()
    
    try:
        # 如果指定了GUI模式或没有提供任何参数，启动GUI
        if args.gui or (not args.doc and not args.keywords and not args.output):
            logger.info("创建应用实例")
            app = TenderAnalyzerGUI()
            app.run()
        else:
            # 命令行模式
            if process_command_line(args.doc, args.keywords, args.output):
                logger.info("命令行处理完成")
            else:
                logger.error("命令行处理失败")
                sys.exit(1)
                
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        logger.error(traceback.format_exc())
        if args.gui:
            messagebox.showerror("错误", f"程序运行出错：{str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
