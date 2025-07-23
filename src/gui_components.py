"""SQLite数据库管理界面"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

class DatabaseManagerFrame(ttk.Frame):
    """数据库管理界面框架"""
    
    def __init__(self, parent, db_manager):
        """初始化数据库管理界面"""
        super().__init__(parent)
        self.db = db_manager
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建notebook用于切换不同视图
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建关键词管理标签页
        self.keywords_frame = KeywordsManagerFrame(self.notebook, self.db)
        self.notebook.add(self.keywords_frame, text="关键词管理")
        
        # 创建项目摘要标签页
        self.projects_frame = ProjectSummaryFrame(self.notebook, self.db)
        self.notebook.add(self.projects_frame, text="项目摘要")
        
        # 创建统计摘要标签页
        self.stats_frame = StatisticsFrame(self.notebook, self.db)
        self.notebook.add(self.stats_frame, text="统计摘要")

class KeywordsManagerFrame(ttk.Frame):
    """关键词管理界面"""
    
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 工具栏
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="添加关键词", command=self.add_keyword).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="编辑关键词", command=self.edit_keyword).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除关键词", command=self.delete_keyword).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="导入关键词", command=self.import_keywords).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="导出关键词", command=self.export_keywords).pack(side=tk.LEFT, padx=2)
        
        # 搜索框
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 关键词列表
        self.tree = ttk.Treeview(
            self,
            columns=("keyword", "category", "description", "created_at"),
            show="headings"
        )
        
        # 设置列
        self.tree.heading("keyword", text="关键词")
        self.tree.heading("category", text="分类")
        self.tree.heading("description", text="描述")
        self.tree.heading("created_at", text="创建时间")
        
        # 设置列宽
        self.tree.column("keyword", width=150)
        self.tree.column("category", width=100)
        self.tree.column("description", width=200)
        self.tree.column("created_at", width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置组件
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 加载关键词
        self.load_keywords()
    
    def load_keywords(self):
        """加载关键词列表"""
        # 清空现有内容
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 从数据库加载关键词
        keywords = self.db.get_all_keywords()
        for keyword in keywords:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    keyword["keyword"],
                    keyword["category"],
                    keyword["description"],
                    keyword["created_at"]
                )
            )
    
    def on_search(self, *args):
        """搜索关键词"""
        search_term = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            if (
                search_term in str(values[0]).lower() or  # 关键词
                search_term in str(values[1]).lower() or  # 分类
                search_term in str(values[2]).lower()     # 描述
            ):
                self.tree.reattach(item, "", tk.END)
            else:
                self.tree.detach(item)
    
    def add_keyword(self):
        """添加新关键词"""
        dialog = KeywordDialog(self, "添加关键词")
        if dialog.result:
            success = self.db.add_keyword(
                keyword=dialog.result["keyword"],
                category=dialog.result["category"],
                description=dialog.result["description"]
            )
            if success:
                self.load_keywords()
    
    def edit_keyword(self):
        """编辑选中的关键词"""
        selected = self.tree.selection()
        if not selected:
            tk.messagebox.showwarning("警告", "请先选择要编辑的关键词")
            return
            
        item = selected[0]
        values = self.tree.item(item)["values"]
        
        dialog = KeywordDialog(
            self,
            "编辑关键词",
            initial={
                "keyword": values[0],
                "category": values[1],
                "description": values[2]
            }
        )
        
        if dialog.result:
            success = self.db.update_keyword(
                old_keyword=values[0],
                new_keyword=dialog.result["keyword"],
                category=dialog.result["category"],
                description=dialog.result["description"]
            )
            if success:
                self.load_keywords()
            else:
                tk.messagebox.showerror("错误", "更新关键词失败")
    
    def delete_keyword(self):
        """删除选中的关键词"""
        selected = self.tree.selection()
        if not selected:
            tk.messagebox.showwarning("警告", "请先选择要删除的关键词")
            return
            
        if tk.messagebox.askyesno("确认", "确定要删除选中的关键词吗？"):
            item = selected[0]
            keyword = self.tree.item(item)["values"][0]
            if self.db.delete_keyword(keyword):
                self.load_keywords()
            else:
                tk.messagebox.showerror("错误", "删除关键词失败")
    
    def import_keywords(self):
        """从文件导入关键词"""
        file_path = tk.filedialog.askopenfilename(
            title="选择关键词文件",
            filetypes=[
                ("文本文件", "*.txt"),
                ("CSV文件", "*.csv"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        try:
            count = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if not parts[0]:
                        continue
                    
                    keyword = parts[0]
                    category = parts[1] if len(parts) > 1 else ""
                    description = parts[2] if len(parts) > 2 else ""
                    
                    if self.db.add_keyword(keyword, category, description):
                        count += 1
                        
            self.load_keywords()
            tk.messagebox.showinfo("成功", f"成功导入{count}个关键词")
        except Exception as e:
            tk.messagebox.showerror("错误", f"导入关键词失败：{str(e)}")
    
    def export_keywords(self):
        """导出关键词到文件"""
        file_path = tk.filedialog.asksaveasfilename(
            title="保存关键词文件",
            defaultextension=".txt",
            filetypes=[
                ("文本文件", "*.txt"),
                ("CSV文件", "*.csv"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        try:
            keywords = self.db.get_all_keywords()
            with open(file_path, 'w', encoding='utf-8') as f:
                for kw in keywords:
                    f.write(f"{kw['keyword']}\t{kw['category']}\t{kw['description']}\n")
            tk.messagebox.showinfo("成功", "关键词导出完成")
        except Exception as e:
            tk.messagebox.showerror("错误", f"导出关键词失败：{str(e)}")

class ProjectSummaryFrame(ttk.Frame):
    """项目摘要界面"""
    
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 工具栏
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="刷新", command=self.refresh_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="导出列表", command=self.export_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="查看详情", command=self.show_detail).pack(side=tk.LEFT, padx=2)
        
        # 搜索框
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 项目列表
        self.tree = ttk.Treeview(
            self,
            columns=("id", "project_name", "analysis_date", "total_keywords", "status"),
            show="headings"
        )
        
        # 设置列
        self.tree.heading("id", text="ID")
        self.tree.heading("project_name", text="项目名称")
        self.tree.heading("analysis_date", text="分析日期")
        self.tree.heading("total_keywords", text="关键词数")
        self.tree.heading("status", text="状态")
        
        # 设置列宽
        self.tree.column("id", width=50)
        self.tree.column("project_name", width=200)
        self.tree.column("analysis_date", width=150)
        self.tree.column("total_keywords", width=100)
        self.tree.column("status", width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置组件
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 加载项目列表
        self.load_projects()
    
    def load_projects(self):
        """加载项目列表"""
        # 清空现有内容
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 从数据库加载项目
        projects = self.db.get_project_summaries()
        for project in projects:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    project["id"],
                    project["project_name"],
                    project["analysis_date"],
                    project["total_keywords"],
                    project["status"]
                )
            )
    
    def on_search(self, *args):
        """搜索项目"""
        search_term = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            if (
                search_term in str(values[1]).lower() or  # 项目名称
                search_term in str(values[4]).lower()     # 状态
            ):
                self.tree.reattach(item, "", tk.END)
            else:
                self.tree.detach(item)
    
    def refresh_list(self):
        """刷新项目列表"""
        self.load_projects()
    
    def export_list(self):
        """导出项目列表"""
        # TODO: 实现导出功能
        pass
    
    def show_detail(self):
        """显示项目详情"""
        selected = self.tree.selection()
        if not selected:
            tk.messagebox.showwarning("警告", "请先选择要查看的项目")
            return
            
        item = selected[0]
        project_id = self.tree.item(item)["values"][0]
        
        project = self.db.get_project_detail(project_id)
        if project:
            ProjectDetailDialog(self, "项目详情", project)

class KeywordDialog:
    """关键词对话框"""
    
    def __init__(self, parent, title, initial=None):
        self.result = None
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        window_width = 400
        window_height = 300
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建表单
        self.create_form(initial or {})
        
        # 等待窗口关闭
        self.dialog.wait_window()
    
    def create_form(self, initial):
        """创建表单"""
        # 关键词
        ttk.Label(self.dialog, text="关键词:").grid(row=0, column=0, padx=5, pady=5)
        self.keyword_var = tk.StringVar(value=initial.get("keyword", ""))
        ttk.Entry(self.dialog, textvariable=self.keyword_var).grid(row=0, column=1, padx=5, pady=5)
        
        # 分类
        ttk.Label(self.dialog, text="分类:").grid(row=1, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar(value=initial.get("category", ""))
        ttk.Entry(self.dialog, textvariable=self.category_var).grid(row=1, column=1, padx=5, pady=5)
        
        # 描述
        ttk.Label(self.dialog, text="描述:").grid(row=2, column=0, padx=5, pady=5)
        self.description_var = tk.StringVar(value=initial.get("description", ""))
        ttk.Entry(self.dialog, textvariable=self.description_var).grid(row=2, column=1, padx=5, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def on_ok(self):
        """确定按钮事件"""
        self.result = {
            "keyword": self.keyword_var.get(),
            "category": self.category_var.get(),
            "description": self.description_var.get()
        }
        self.dialog.destroy()

class ProjectDetailDialog:
    """项目详情对话框"""
    
    def __init__(self, parent, title, project):
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        window_width = 600
        window_height = 400
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 显示项目详情
        self.show_project_detail(project)
        
        # 等待窗口关闭
        self.dialog.wait_window()
    
    def show_project_detail(self, project):
        """显示项目详情"""
        # 项目基本信息
        info_frame = ttk.LabelFrame(self.dialog, text="基本信息")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text=f"项目名称: {project['project_name']}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"分析日期: {project['analysis_date']}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"文件类型: {project['file_type']}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"文件大小: {project['file_size']} 字节").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"状态: {project['status']}").pack(anchor=tk.W, padx=5, pady=2)
        
        # 关键词统计
        stats_frame = ttk.LabelFrame(self.dialog, text="关键词统计")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建表格
        tree = ttk.Treeview(
            stats_frame,
            columns=("keyword", "count"),
            show="headings"
        )
        
        tree.heading("keyword", text="关键词")
        tree.heading("count", text="出现次数")
        
        tree.column("keyword", width=200)
        tree.column("count", width=100)
        
        # 添加数据
        for keyword, count in project['keyword_stats'].items():
            tree.insert("", tk.END, values=(keyword, count))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置组件
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 关闭按钮
        ttk.Button(self.dialog, text="关闭", command=self.dialog.destroy).pack(pady=10)

class StatisticsFrame(ttk.Frame):
    """统计摘要界面"""
    
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 总体统计区域
        overview_frame = ttk.LabelFrame(self, text="总体统计")
        overview_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 统计数据
        self.total_keywords_var = tk.StringVar(value="0")
        self.total_projects_var = tk.StringVar(value="0")
        self.total_matches_var = tk.StringVar(value="0")
        self.avg_keywords_per_project_var = tk.StringVar(value="0")
        
        # 创建统计信息标签
        ttk.Label(overview_frame, text="关键词总数:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(overview_frame, textvariable=self.total_keywords_var).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(overview_frame, text="已分析项目数:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(overview_frame, textvariable=self.total_projects_var).grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(overview_frame, text="关键词匹配总次数:").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(overview_frame, textvariable=self.total_matches_var).grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(overview_frame, text="平均每项目关键词数:").grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(overview_frame, textvariable=self.avg_keywords_per_project_var).grid(row=3, column=1, padx=5, pady=2, sticky=tk.W)
        
        # 关键词使用频率排行
        keyword_stats_frame = ttk.LabelFrame(self, text="关键词使用频率排行")
        keyword_stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建表格
        self.tree = ttk.Treeview(
            keyword_stats_frame,
            columns=("project_name", "analysis_date", "keywords_found", "total_occurrences"),
            show="headings"
        )
        
        # 设置列
        self.tree.heading("project_name", text="项目名称")
        self.tree.heading("analysis_date", text="分析日期")
        self.tree.heading("keywords_found", text="发现关键词数")
        self.tree.heading("total_occurrences", text="关键词总出现次数")
        
        # 设置列宽
        self.tree.column("project_name", width=200)
        self.tree.column("analysis_date", width=150)
        self.tree.column("keywords_found", width=100)
        self.tree.column("total_occurrences", width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(keyword_stats_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置组件
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加刷新按钮
        ttk.Button(self, text="刷新统计", command=self.refresh_stats).pack(pady=5)
        
        # 加载初始数据
        self.refresh_stats()
    
    def refresh_stats(self):
        """刷新统计数据"""
        # 获取数据
        keywords = self.db.get_all_keywords()
        projects = self.db.get_project_summaries(limit=1000)  # 获取所有项目
        
        # 按项目名称合并相同项目的多次分析结果
        project_stats = {}
        unique_projects = set()
        for project in projects:
            project_name = project.get('project_name', '')
            if project_name:
                unique_projects.add(project_name)
                stats = project.get('keyword_stats', {})
                if project_name not in project_stats:
                    project_stats[project_name] = {
                        'keyword_stats': {},
                        'latest_date': project['analysis_date']
                    }
                else:
                    # 如果是同一个项目的多次分析，只保留最新的结果
                    if project['analysis_date'] > project_stats[project_name]['latest_date']:
                        project_stats[project_name] = {
                            'keyword_stats': {},
                            'latest_date': project['analysis_date']
                        }
                
                # 只有是最新分析时才统计关键词
                if project['analysis_date'] == project_stats[project_name]['latest_date']:
                    project_stats[project_name]['keyword_stats'] = stats
        
        # 更新总体统计
        self.total_keywords_var.set(str(len(keywords)))
        self.total_projects_var.set(str(len(unique_projects)))  # 显示唯一项目数
        
        # 计算关键词使用统计
        keyword_stats = {}
        total_matches = 0
        
        for project_name, project_data in project_stats.items():
            stats = project_data['keyword_stats']
            for keyword, count in stats.items():
                if keyword not in keyword_stats:
                    keyword_stats[keyword] = {'usage_count': 0, 'project_count': 0}
                keyword_stats[keyword]['usage_count'] += count
                keyword_stats[keyword]['project_count'] += 1
                total_matches += count
        
        # 更新匹配总次数
        self.total_matches_var.set(str(total_matches))
        
        # 计算平均每项目关键词数
        if unique_projects:
            avg = sum(len(p['keyword_stats']) for p in project_stats.values()) / len(unique_projects)
            self.avg_keywords_per_project_var.set(f"{avg:.2f}")
        else:
            self.avg_keywords_per_project_var.set("0")
        
        # 更新表格数据
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 准备项目统计信息
        project_info = []
        for project_name, project_data in project_stats.items():
            stats = project_data['keyword_stats']
            # 计算该项目的统计信息
            total_occurrences = sum(stats.values())  # 关键词总出现次数
            unique_keywords = len(stats)  # 不同关键词数量
            
            project_info.append({
                'project_name': project_name,
                'analysis_date': project_data['latest_date'],
                'keywords_found': unique_keywords,
                'total_occurrences': total_occurrences
            })
        
        # 按总出现次数降序排序
        project_info.sort(key=lambda x: x['total_occurrences'], reverse=True)
        
        # 填充表格
        for info in project_info:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    info['project_name'],
                    info['analysis_date'],
                    info['keywords_found'],
                    info['total_occurrences']
                )
            )
