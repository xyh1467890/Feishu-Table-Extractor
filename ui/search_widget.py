from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt


class SearchWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setObjectName("search_container")
        self.setFixedWidth(320)
        
        self.search_input = None
        self.match_label = None
        self.prev_button = None
        self.next_button = None
        
        self.search_matches = []
        self.current_match_index = -1
        
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet("""
            QFrame#search_container {
                background-color: #ffffff;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
            }
            QFrame#search_container:focus-within {
                border: 1px solid #409eff;
            }
            QLineEdit {
                border: none;
                background: transparent;
                font-size: 13px;
                padding: 0;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #606266;
                font-size: 12px;
                border-radius: 4px;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #f5f7fa;
                color: #409eff;
            }
            QPushButton:pressed {
                background-color: #e4e7ed;
            }
            QPushButton:disabled {
                color: #c0c4cc;
                background-color: transparent;
            }
        """)
        
        search_layout = QHBoxLayout(self)
        search_layout.setContentsMargins(8, 2, 8, 2)
        search_layout.setSpacing(6)
        self.setFixedHeight(34)
        
        search_label = QLabel("🔍")
        search_label.setStyleSheet("font-size: 13px; color: #909399; border: none;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("在结果中搜索...")
        self.search_input.textChanged.connect(
            self.parent_window.on_search_text_changed if self.parent_window else lambda x: None
        )
        
        self.match_label = QLabel("")
        self.match_label.setStyleSheet("font-size: 12px; color: #909399; border: none;")
        self.match_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.match_label.setMinimumWidth(35)
        
        # 分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("color: #e4e7ed; border: none; background-color: #e4e7ed;")
        separator.setFixedSize(1, 16)
        
        # 使用更精美的图标字符
        self.prev_button = QPushButton("▲")
        self.prev_button.setCursor(Qt.PointingHandCursor)
        self.prev_button.clicked.connect(
            self.parent_window.on_prev_match if self.parent_window else lambda: None
        )
        self.prev_button.setEnabled(False)
        self.prev_button.setFixedSize(26, 26)
        self.prev_button.setToolTip("上一条")
        self.prev_button.setStyleSheet("font-size: 10px; font-family: 'Segoe UI Symbol', 'Microsoft YaHei', sans-serif;")
        
        self.next_button = QPushButton("▼")
        self.next_button.setCursor(Qt.PointingHandCursor)
        self.next_button.clicked.connect(
            self.parent_window.on_next_match if self.parent_window else lambda: None
        )
        self.next_button.setEnabled(False)
        self.next_button.setFixedSize(26, 26)
        self.next_button.setToolTip("下一条")
        self.next_button.setStyleSheet("font-size: 10px; font-family: 'Segoe UI Symbol', 'Microsoft YaHei', sans-serif;")
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.match_label)
        search_layout.addWidget(separator)
        search_layout.addWidget(self.prev_button)
        search_layout.addWidget(self.next_button)
