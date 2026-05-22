
class SearchLogic:
    def __init__(self, result_text_widget, search_widget):
        self.result_text = result_text_widget
        self.search_widget = search_widget
        self.original_json = ""
        self.search_matches = []
        self.current_match_index = -1
    
    def set_original_text(self, text):
        self.original_json = text
    
    def on_search_text_changed(self, search_text):
        """搜索关键词并高亮显示"""
        if not self.original_json:
            return
        
        if not search_text:
            # 如果搜索框为空，显示原始内容
            self.result_text.setText(self.original_json)
            self.search_matches = []
            self.current_match_index = -1
            self.search_widget.match_label.setText("")
            self.search_widget.prev_button.setEnabled(False)
            self.search_widget.next_button.setEnabled(False)
            return
        
        # 查找所有匹配位置
        text = self.original_json
        self.search_matches = []
        index = 0
        search_len = len(search_text)
        while index < len(text):
            idx = text.find(search_text, index)
            if idx == -1:
                break
            self.search_matches.append(idx)
            index = idx + search_len
        
        # 更新匹配统计
        total = len(self.search_matches)
        if total == 0:
            self.search_widget.match_label.setText("未找到匹配")
            self.current_match_index = -1
            self.search_widget.prev_button.setEnabled(False)
            self.search_widget.next_button.setEnabled(False)
            self.result_text.setText(self.original_json)
            return
        
        self.current_match_index = 0
        self.search_widget.match_label.setText(f"{self.current_match_index + 1}/{total}")
        self.search_widget.prev_button.setEnabled(total > 1)
        self.search_widget.next_button.setEnabled(total > 1)
        
        # 高亮显示
        self.highlight_matches(search_text)
    
    def highlight_matches(self, search_text):
        """高亮显示匹配项，当前项用橙色"""
        text = self.original_json
        highlighted = []
        last_pos = 0
        search_len = len(search_text)
        
        for i, pos in enumerate(self.search_matches):
            # 添加匹配前的文本
            highlighted.append(self.escape_html(text[last_pos:pos]))
            # 添加高亮的匹配文本
            if i == self.current_match_index:
                # 当前匹配用橙色高亮
                highlighted.append(f'<span style="background-color: #ffa500; color: black; font-weight: bold;">{self.escape_html(search_text)}</span>')
            else:
                # 其他匹配用黄色高亮
                highlighted.append(f'<span style="background-color: yellow; color: black;">{self.escape_html(search_text)}</span>')
            last_pos = pos + search_len
        
        # 添加剩余文本
        highlighted.append(self.escape_html(text[last_pos:]))
        
        html_text = f'<pre style="font-family: monospace; font-size: 13px; white-space: pre-wrap;">{"".join(highlighted)}</pre>'
        self.result_text.setHtml(html_text)
        
        # 滚动到当前匹配位置
        if self.search_matches:
            cursor = self.result_text.textCursor()
            cursor.setPosition(self.search_matches[self.current_match_index])
            self.result_text.setTextCursor(cursor)
            self.result_text.ensureCursorVisible()
    
    def escape_html(self, text):
        """转义 HTML 特殊字符"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    
    def on_prev_match(self):
        """上一条匹配"""
        if not self.search_matches:
            return
        
        if self.current_match_index > 0:
            self.current_match_index -= 1
            self.search_widget.match_label.setText(f"{self.current_match_index + 1}/{len(self.search_matches)}")
            self.highlight_matches(self.search_widget.search_input.text())
    
    def on_next_match(self):
        """下一条匹配"""
        if not self.search_matches:
            return
        
        if self.current_match_index < len(self.search_matches) - 1:
            self.current_match_index += 1
            self.search_widget.match_label.setText(f"{self.current_match_index + 1}/{len(self.search_matches)}")
            self.highlight_matches(self.search_widget.search_input.text())
