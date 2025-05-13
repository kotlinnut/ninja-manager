from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class NinjaCard(QWidget):
    deleted = Signal(str)
    checked = Signal(str, bool)  # 新增信号用于复选框状态

    def __init__(self, name, rank, parent=None):
        super().__init__(parent)
        self.name = name
        self.rank = rank
        self.is_checkbox_mode = False
        self.setup_ui()
        self.setProperty("class", "NinjaCard")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # 顶部容器用于放置复选框和名称
        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        # 复选框（初始隐藏）
        self.checkbox = QCheckBox()
        self.checkbox.setVisible(False)
        self.checkbox.setFixedSize(13, 13)  # 固定复选框大小
        self.checkbox.stateChanged.connect(
            lambda state: self.checked.emit(self.name, state == Qt.Checked)
        )

        # 忍者名称
        name_label = QLabel(self.name)
        name_label.setStyleSheet("font-size: 13px; font-weight : bold ;padding: 0px; margin: 0px;")
        name_label.setFixedHeight(13)  # 固定高度

        # 创建一个水平布局容器专门用于复选框和名称
        checkbox_name_container = QWidget()
        checkbox_name_layout = QHBoxLayout(checkbox_name_container)
        checkbox_name_layout.setContentsMargins(1, 0, 0, 0)  # 只保留左边一个像素的边距
        checkbox_name_layout.setSpacing(1)  # 复选框和文字之间保留1像素间距
        checkbox_name_layout.addWidget(self.checkbox)
        checkbox_name_layout.addWidget(name_label)
        checkbox_name_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        top_layout.addWidget(checkbox_name_container)
        top_layout.setAlignment(checkbox_name_container, Qt.AlignLeft | Qt.AlignVCenter)

        # 删除按钮
        self.delete_btn = QPushButton("删除")
        self.delete_btn.setObjectName("deleteButton")
        self.delete_btn.setFixedHeight(16)  # 固定高度
        self.delete_btn.clicked.connect(lambda: self.deleted.emit(self.name))

        layout.addWidget(top_container)
        layout.addWidget(self.delete_btn)

    def set_checkbox_mode(self, enabled):
        self.is_checkbox_mode = enabled
        self.delete_btn.setVisible(not enabled)
        self.checkbox.setVisible(enabled)
        if not enabled:
            self.checkbox.setChecked(False)

    def delete_ninja(self):
        self.deleted.emit(self.name)