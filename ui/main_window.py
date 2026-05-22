import sys
import os
import json
import webbrowser
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QFileDialog, QMessageBox,
    QLineEdit
)
from PyQt5.QtCore import Qt

from ui.styles import APP_STYLE
from ui.sidebar_panel import SidebarPanel, resource_path
from ui.result_panel import ResultPanel
from ui.search_logic import SearchLogic
from workers.oauth_worker import OAuthTokenThread
from workers.cookie_worker import GetCookieThread
from workers.fetch_worker import FetchDataThread


class FeishuBitableApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("飞书多维表格元数据工具")
        self.resize(1200, 900)
        self.setMinimumSize(1000, 700)
        
        self.current_result = None
        self.original_json = ""
        self.oauth_thread = None
        self.get_cookie_thread = None
        
        self.sidebar = None
        self.result_panel = None
        self.search_logic = None
        
        self.init_ui()
    
    def init_ui(self):
        # 基础样式设置
        QApplication.instance().setStyle('Fusion')
        self.setStyleSheet(APP_STYLE)
        
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        
        # 整体采用左右分栏布局
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 左侧控制面板
        self.sidebar = SidebarPanel(self)
        self.sidebar.tabs.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.sidebar)
        
        # 右侧结果面板
        self.result_panel = ResultPanel(self)
        main_layout.addWidget(self.result_panel)
        
        # 搜索逻辑
        self.search_logic = SearchLogic(
            self.result_panel.result_text,
            self.result_panel.search_widget
        )
    
    def on_tab_changed(self, index):
        """标签页切换时的处理"""
        tab_text = self.sidebar.tabs.tabText(index)
        if "Cookie" in tab_text:
            # Cookie 标签页：弹框提示
            QMessageBox.warning(
                self,
                "提示",
                "注意：Cookie 方式仅可提取当前数据表 JSON 数据，无法批量提取全表 JSON，也不支持读取数据表内记录内容。"
            )
            self.sidebar.fetch_records_checkbox.setEnabled(False)
            self.sidebar.fetch_records_checkbox.setChecked(False)
            self.sidebar.fetch_records_checkbox.setToolTip("Cookie 方式不支持获取记录内容")
        else:
            self.sidebar.fetch_records_checkbox.setEnabled(True)
            self.sidebar.fetch_records_checkbox.setChecked(True)
            self.sidebar.fetch_records_checkbox.setToolTip("")
    
    def on_manual_info_link_clicked(self, link):
        """处理 Token 标签页链接点击"""
        if link == "help:token":
            # 播放视频
            video_path = resource_path("get_user_access_token.mp4")
            if os.path.exists(video_path):
                if sys.platform == "win32":
                    os.startfile(video_path)
                elif sys.platform == "darwin":
                    subprocess.call(["open", video_path])
                else:
                    subprocess.call(["xdg-open", video_path])
            else:
                QMessageBox.warning(self, "提示", f"视频文件不存在：{video_path}")
        elif link.startswith("http"):
            webbrowser.open(link)
    
    def toggle_token_visibility(self, checked):
        if checked:
            self.sidebar.token_input.setEchoMode(QLineEdit.Normal)
            self.sidebar.show_token_btn.setText("隐藏")
            self.sidebar.show_token_btn.setStyleSheet("background-color: #409eff; color: white;")
        else:
            self.sidebar.token_input.setEchoMode(QLineEdit.Password)
            self.sidebar.show_token_btn.setText("显示")
            self.sidebar.show_token_btn.setStyleSheet("")
    
    def start_get_cookie(self):
        """开始获取 Cookie"""
        self.sidebar.get_cookie_btn.setEnabled(False)
        self.sidebar.cookie_status_label.setText("正在准备...")
        
        self.get_cookie_thread = GetCookieThread()
        self.get_cookie_thread.cookie_received.connect(self.on_cookie_received)
        self.get_cookie_thread.error.connect(self.on_get_cookie_error)
        self.get_cookie_thread.progress.connect(self.update_cookie_status)
        self.get_cookie_thread.start()
    
    def confirm_get_cookie(self):
        """确认登录完成，获取 Cookie"""
        if self.get_cookie_thread:
            self.sidebar.confirm_login_btn.setEnabled(False)
            self.get_cookie_thread.get_cookie_after_login()
    
    def update_cookie_status(self, message):
        """更新 Cookie 状态"""
        self.sidebar.cookie_status_label.setText(message)
        if "请在浏览器中登录" in message:
            self.sidebar.confirm_login_btn.setEnabled(True)
    
    def on_cookie_received(self, cookie):
        """获取到 Cookie"""
        self.sidebar.cookie_input.setText(cookie)
        self.sidebar.cookie_status_label.setText("✓ Cookie 已自动填入")
        self.sidebar.get_cookie_btn.setEnabled(True)
        self.sidebar.confirm_login_btn.setEnabled(False)
        QMessageBox.information(self, "成功", "Cookie 获取成功，已自动填入！")
    
    def on_get_cookie_error(self, error_msg):
        """获取 Cookie 出错"""
        self.sidebar.cookie_status_label.setText(f"✗ 错误：{error_msg}")
        self.sidebar.get_cookie_btn.setEnabled(True)
        self.sidebar.confirm_login_btn.setEnabled(False)
        QMessageBox.critical(self, "错误", error_msg)
    
    def start_oauth_flow(self):
        app_id = self.sidebar.app_id_input.text().strip()
        app_secret = self.sidebar.app_secret_input.text().strip()
        
        if not app_id:
            QMessageBox.warning(self, "提示", "请输入 App ID")
            return
        if not app_secret:
            QMessageBox.warning(self, "提示", "请输入 App Secret")
            return
        
        self.sidebar.login_button.setEnabled(False)
        self.sidebar.oauth_status_label.setText("正在打开浏览器进行授权...")
        
        self.oauth_thread = OAuthTokenThread(app_id, app_secret)
        self.oauth_thread.token_received.connect(self.on_token_received)
        self.oauth_thread.error.connect(self.on_oauth_error)
        self.oauth_thread.start()
    
    def on_token_received(self, token):
        self.sidebar.token_input.setText(token)
        self.sidebar.oauth_status_label.setText("✓ 登录成功！Token 已自动填充")
        self.sidebar.login_button.setEnabled(True)
        QMessageBox.information(self, "成功", "登录成功！Token 已自动填充到输入框中。")
    
    def on_oauth_error(self, error_msg):
        self.sidebar.oauth_status_label.setText(f"✗ 错误：{error_msg}")
        self.sidebar.login_button.setEnabled(True)
        QMessageBox.critical(self, "错误", error_msg)
    
    def fetch_data(self):
        current_tab_index = self.sidebar.tabs.currentIndex()
        feishu_url = self.sidebar.url_input.text().strip()
        fetch_records = self.sidebar.fetch_records_checkbox.isChecked()
        
        auth_type = None
        auth_data = None
        
        if current_tab_index == 0 or current_tab_index == 1:
            # Token 或 OAuth 标签页
            user_token = self.sidebar.token_input.text().strip()
            if not user_token:
                QMessageBox.warning(self, "提示", "请输入用户 Token")
                return
            auth_type = "token"
            auth_data = user_token
        elif current_tab_index == 2:
            # Cookie 标签页
            cookie = self.sidebar.cookie_input.text().strip()
            if not cookie:
                QMessageBox.warning(self, "提示", "请输入飞书 Cookie")
                return
            auth_type = "cookie"
            auth_data = cookie
        
        if not feishu_url:
            QMessageBox.warning(self, "提示", "请输入多维表格链接")
            return
        
        self.sidebar.fetch_button.setEnabled(False)
        self.result_panel.export_button.setEnabled(False)
        self.result_panel.result_text.clear()
        self.sidebar.progress_label.setStyleSheet("color: #409eff;")
        
        self.thread = FetchDataThread(auth_type, auth_data, feishu_url, fetch_records)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_fetch_finished)
        self.thread.error.connect(self.on_fetch_error)
        self.thread.start()
    
    def update_progress(self, message):
        self.sidebar.progress_label.setText(message)
    
    def on_fetch_finished(self, result):
        self.current_result = result
        self.original_json = json.dumps(result, ensure_ascii=False, indent=2)
        self.result_panel.result_text.setText(self.original_json)
        self.search_logic.set_original_text(self.original_json)
        self.result_panel.export_button.setEnabled(True)
        self.sidebar.fetch_button.setEnabled(True)
        self.sidebar.progress_label.setStyleSheet("color: #67c23a;")
        self.sidebar.progress_label.setText("✓ 获取成功！")
    
    def on_search_text_changed(self, search_text):
        self.search_logic.on_search_text_changed(search_text)
    
    def on_prev_match(self):
        self.search_logic.on_prev_match()
    
    def on_next_match(self):
        self.search_logic.on_next_match()
    
    def on_fetch_error(self, error_msg):
        self.result_panel.result_text.setText(f"错误：{error_msg}")
        self.sidebar.fetch_button.setEnabled(True)
        self.sidebar.progress_label.setStyleSheet("color: #f56c6c;")
        self.sidebar.progress_label.setText("✗ 获取失败")
        QMessageBox.critical(self, "错误", f"获取数据失败：{error_msg}")
    
    def export_json(self):
        if not self.current_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存 JSON 文件",
            "",
            "JSON 文件 (*.json);;所有文件 (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_result, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "成功", f"文件已保存到：{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存文件失败：{str(e)}")
