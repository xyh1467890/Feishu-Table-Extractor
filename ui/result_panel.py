from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
)
from PyQt5.QtCore import Qt

from ui.search_widget import SearchWidget


class ResultPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setObjectName("right_panel")
        
        self.search_widget = None
        self.result_text = None
        self.export_button = None
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 45, 40, 45)
        layout.setSpacing(20)
        
        result_header = QHBoxLayout()
        result_title = QLabel("解析结果")
        result_title.setObjectName("section_title")
        result_title.setStyleSheet("margin: 0;")
        
        # 搜索区域
        self.search_widget = SearchWidget(self.parent_window)
        
        self.export_button = QPushButton("导出 JSON")
        self.export_button.setCursor(Qt.PointingHandCursor)
        self.export_button.clicked.connect(
            self.parent_window.export_json if self.parent_window else lambda: None
        )
        self.export_button.setEnabled(False)
        self.export_button.setFixedWidth(120)
        self.export_button.setFixedHeight(36)
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #409eff;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #66b1ff;
            }
            QPushButton:pressed {
                background-color: #3a8ee6;
            }
            QPushButton:disabled {
                background-color: #a0cfff;
                color: #ffffff;
            }
        """)
        
        result_header.addWidget(result_title)
        result_header.addStretch()
        result_header.addWidget(self.search_widget)
        
        layout.addLayout(result_header)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("获取到的 JSON 数据将在这里格式化显示...")
        layout.addWidget(self.result_text)
        
        # 底部操作区
        bottom_action_layout = QHBoxLayout()
        bottom_action_layout.addStretch()
        bottom_action_layout.addWidget(self.export_button)
        layout.addLayout(bottom_action_layout)
