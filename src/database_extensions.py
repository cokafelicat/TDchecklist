"""关键词管理数据库操作扩展"""
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
