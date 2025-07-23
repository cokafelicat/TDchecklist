"""数据库管理模块"""
import sqlite3
from pathlib import Path
import logging
from typing import List, Dict, Optional, Union
import json

class DatabaseManager:
    """数据库管理器类"""
    
    def update_keyword(self, old_keyword: str, new_keyword: str, category: str = None, description: str = None) -> bool:
        """
        更新关键词
        
        Args:
            old_keyword: 原关键词
            new_keyword: 新关键词
            category: 分类
            description: 描述
            
        Returns:
            bool: 是否更新成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE keywords 
                    SET keyword = ?, category = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE keyword = ?
                    """,
                    (new_keyword, category, description, old_keyword)
                )
                conn.commit()
                self.logger.info(f"关键词更新成功: {old_keyword} -> {new_keyword}")
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"更新关键词失败: {e}")
            return False

    def delete_keyword(self, keyword: str) -> bool:
        """
        删除关键词
        
        Args:
            keyword: 要删除的关键词
            
        Returns:
            bool: 是否删除成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM keywords WHERE keyword = ?",
                    (keyword,)
                )
                conn.commit()
                self.logger.info(f"关键词删除成功: {keyword}")
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"删除关键词失败: {e}")
            return False
    
    def __init__(self, db_path: Union[str, Path] = None):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径，如果为None则使用默认路径
        """
        if db_path is None:
            db_path = Path.home() / '.biaoshuchecklist' / 'analysis.db'
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建关键词表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT UNIQUE NOT NULL,
                    category TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # 创建项目分析摘要表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT NOT NULL,
                    file_path TEXT,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    keyword_stats JSON,
                    total_keywords INTEGER,
                    file_type TEXT,
                    file_size INTEGER,
                    status TEXT,
                    notes TEXT
                )
                """)
                
                conn.commit()
                self.logger.info("数据库表初始化完成")
                
        except sqlite3.Error as e:
            self.logger.error(f"数据库初始化失败: {e}")
            raise
    
    def add_keyword(self, keyword: str, category: str = None, description: str = None) -> bool:
        """
        添加关键词
        
        Args:
            keyword: 关键词
            category: 关键词类别
            description: 关键词描述
            
        Returns:
            bool: 是否添加成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO keywords (keyword, category, description)
                    VALUES (?, ?, ?)
                    """,
                    (keyword, category, description)
                )
                conn.commit()
                self.logger.info(f"关键词添加成功: {keyword}")
                return True
        except sqlite3.IntegrityError:
            self.logger.warning(f"关键词已存在: {keyword}")
            return False
        except sqlite3.Error as e:
            self.logger.error(f"添加关键词失败: {e}")
            return False
    
    def get_all_keywords(self) -> List[Dict]:
        """
        获取所有关键词
        
        Returns:
            List[Dict]: 关键词列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM keywords ORDER BY category, keyword")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            self.logger.error(f"获取关键词失败: {e}")
            return []
    
    def add_project_summary(self, 
                          project_name: str,
                          file_path: str,
                          keyword_stats: Dict,
                          file_type: str,
                          file_size: int,
                          status: str = "completed",
                          notes: str = None) -> Optional[int]:
        """
        添加项目分析摘要
        
        Args:
            project_name: 项目名称
            file_path: 文件路径
            keyword_stats: 关键词统计数据
            file_type: 文件类型
            file_size: 文件大小
            status: 分析状态
            notes: 备注
            
        Returns:
            Optional[int]: 项目ID，如果添加失败则返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO project_summaries 
                    (project_name, file_path, keyword_stats, total_keywords,
                     file_type, file_size, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project_name,
                        file_path,
                        json.dumps(keyword_stats, ensure_ascii=False),
                        len(keyword_stats),
                        file_type,
                        file_size,
                        status,
                        notes
                    )
                )
                conn.commit()
                self.logger.info(f"项目摘要添加成功: {project_name}")
                return cursor.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"添加项目摘要失败: {e}")
            return None
    
    def get_project_summaries(self, 
                            limit: int = 100,
                            offset: int = 0,
                            status: str = None) -> List[Dict]:
        """
        获取项目分析摘要列表
        
        Args:
            limit: 返回记录数限制
            offset: 起始位置偏移
            status: 分析状态过滤
            
        Returns:
            List[Dict]: 项目摘要列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM project_summaries"
                params = []
                
                if status:
                    query += " WHERE status = ?"
                    params.append(status)
                
                query += " ORDER BY analysis_date DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                
                results = []
                for row in cursor.fetchall():
                    record = dict(row)
                    record['keyword_stats'] = json.loads(record['keyword_stats'])
                    results.append(record)
                
                return results
                
        except sqlite3.Error as e:
            self.logger.error(f"获取项目摘要失败: {e}")
            return []
    
    def search_projects(self, keyword: str) -> List[Dict]:
        """
        搜索项目
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            List[Dict]: 匹配的项目列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    """
                    SELECT * FROM project_summaries
                    WHERE project_name LIKE ? OR notes LIKE ?
                    ORDER BY analysis_date DESC
                    """,
                    (f"%{keyword}%", f"%{keyword}%")
                )
                
                results = []
                for row in cursor.fetchall():
                    record = dict(row)
                    record['keyword_stats'] = json.loads(record['keyword_stats'])
                    results.append(record)
                
                return results
                
        except sqlite3.Error as e:
            self.logger.error(f"搜索项目失败: {e}")
            return []
    
    def get_project_detail(self, project_id: int) -> Optional[Dict]:
        """
        获取项目详细信息
        
        Args:
            project_id: 项目ID
            
        Returns:
            Optional[Dict]: 项目详细信息
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT * FROM project_summaries WHERE id = ?",
                    (project_id,)
                )
                
                row = cursor.fetchone()
                if row:
                    record = dict(row)
                    record['keyword_stats'] = json.loads(record['keyword_stats'])
                    return record
                
                return None
                
        except sqlite3.Error as e:
            self.logger.error(f"获取项目详情失败: {e}")
            return None
