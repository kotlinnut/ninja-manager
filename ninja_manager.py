import os

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ninja_card import NinjaCard
from scroll_wheel import ScrollWheel
from utils import NinjaData


class QFlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.itemList = []
        self.margin = margin
        self.spacing = spacing


    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.margin, 2 * self.margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x() + self.margin
        y = rect.y() + self.margin
        lineHeight = 0

        for item in self.itemList:
            widget = item.widget()
            spaceX = self.spacing
            spaceY = self.spacing
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x() + self.margin
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y() + self.margin


# 添加秘卷项组件v
class ScrollItem(QWidget):
    deleted = Signal(str)

    def __init__(self, name, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        # 秘卷名称
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setObjectName("deleteButton")
        delete_btn.clicked.connect(lambda: self.deleted.emit(name))

        layout.addWidget(name_label)
        layout.addWidget(delete_btn)

        self.setStyleSheet("""
            ScrollItem {
                background-color: white;
                border-radius: 6px;
                border: 1px solid #ddd;
            }
            ScrollItem:hover {
                border-color: #2196F3;
            }
        """)


class NinjaManager(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ninja_data = NinjaData()
        self.selected_ninjas = set()

        # 检查并创建checkmark.svg文件
        self.ensure_checkmark_file()

        self.setup_ui()
        self.load_ninjas()
        self.load_scrolls()

        # 自动触发所有等级的批量删除按钮
        QTimer.singleShot(300, self.auto_trigger_batch_delete)

    def auto_trigger_batch_delete(self):
        # 为每个等级触发批量删除按钮的点击事件
        for rank in ['S', 'A', 'B', 'C']:
            self.toggle_batch_delete_mode(rank)

    def ensure_checkmark_file(self):
        checkmark_path = "checkmark.svg"
        if not os.path.exists(checkmark_path):
            svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M6.5 10.5L3.5 7.5L2.5 8.5L6.5 12.5L13.5 5.5L12.5 4.5L6.5 10.5Z" fill="white"/>
    </svg>'''
            with open(checkmark_path, 'w') as f:
                f.write(svg_content)

    def setup_ui(self):
        self.setWindowTitle("火影忍者段位赛挑战管理器 by宇宙暴龙大皇帝无敌奇拉比公式大王")
        self.setMinimumSize(1200, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)
        self.load_stylesheet()

    def create_left_panel(self):
        # 创建滚动区域作为最外层容器
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cdcdcd;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #b8b8b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # 创建内容面板
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # 规则说明区域
        rules_widget = QWidget()
        rules_layout = QVBoxLayout(rules_widget)
        rules_layout.setSpacing(8)

        rules_label = QLabel("规则说明")
        rules_label.setObjectName("rulesLabel")

        self.rules_text = QTextEdit()
        self.rules_text.setPlaceholderText("在此输入规则说明...")
        self.rules_text.setMinimumHeight(100)
        self.rules_text.setMaximumHeight(150)

        # 设置字体
        font = self.rules_text.font()
        font.setPointSize(16)
        font.setWeight(QFont.Weight.Bold)
        self.rules_text.setFont(font)

        self.rules_text.setText(self.ninja_data.load_rules())
        self.rules_text.textChanged.connect(self.save_rules)

        rules_layout.addWidget(rules_label)
        rules_layout.addWidget(self.rules_text)

        # 搜索框区域
        search_widget = QWidget()
        search_layout = QVBoxLayout(search_widget)
        search_layout.setSpacing(8)

        search_header = QWidget()
        search_header_layout = QHBoxLayout(search_header)
        search_header_layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入忍者名称...")

        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.search_ninja)

        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear_search)

        search_header_layout.addWidget(self.search_input)
        search_header_layout.addWidget(search_btn)
        search_header_layout.addWidget(clear_btn)

        self.search_result_label = QLabel()
        self.search_result_label.setWordWrap(True)
        self.search_result_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                border-radius: 4px;
                font-size: 13px;
            }
        """)
        self.search_result_label.hide()

        search_layout.addWidget(search_header)
        search_layout.addWidget(self.search_result_label)

        # 等级分类区域
        rank_widget = QWidget()
        rank_widget.setObjectName("rankWidget")
        rank_layout = QVBoxLayout(rank_widget)
        rank_layout.setSpacing(12)

        rank_title = QLabel("忍者等级")
        rank_title.setObjectName("rankTitle")
        rank_layout.addWidget(rank_title)

        for rank in ['S', 'A', 'B', 'C']:
            rank_group = QWidget()
            rank_group_layout = QHBoxLayout(rank_group)
            rank_group_layout.setContentsMargins(0, 0, 0, 0)

            rank_label = QLabel(f"{rank}级")
            rank_label.setObjectName("rankLabel")
            rank_label.setFixedWidth(50)

            add_btn = QPushButton("添加")
            add_btn.setObjectName("addButton")
            add_btn.clicked.connect(lambda checked, r=rank: self.quick_add_ninja(r))

            batch_add_btn = QPushButton("批量添加")
            batch_add_btn.setObjectName("batchAddButton")
            batch_add_btn.clicked.connect(lambda checked, r=rank: self.batch_add_ninja(r))

            rank_group_layout.addWidget(rank_label)
            rank_group_layout.addWidget(add_btn)
            rank_group_layout.addWidget(batch_add_btn)
            rank_group_layout.addStretch()

            rank_layout.addWidget(rank_group)


        # 秘卷转盘区域
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(12)

        scroll_title = QLabel("转盘")
        scroll_title.setObjectName("scrollTitle")

        # 秘卷输入区域
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_input = QLineEdit()
        self.scroll_input.setPlaceholderText("输入名称...")

        add_scroll_btn = QPushButton("添加")
        add_scroll_btn.clicked.connect(self.add_scroll)

        input_layout.addWidget(self.scroll_input)
        input_layout.addWidget(add_scroll_btn)

        # 秘卷列表区域
        self.scroll_list_widget = QWidget()
        self.scroll_list_layout = QFlowLayout()
        self.scroll_list_layout.setSpacing(8)
        self.scroll_list_widget.setLayout(self.scroll_list_layout)

        # 转盘
        self.scroll_wheel = ScrollWheel()

        # 转动按钮
        self.spin_btn = QPushButton("转动")
        self.spin_btn.setObjectName("spinButton")
        self.spin_btn.clicked.connect(self.scroll_wheel.spin)

        scroll_layout.addWidget(scroll_title)
        scroll_layout.addWidget(input_widget)
        scroll_layout.addWidget(self.scroll_list_widget)
        scroll_layout.addWidget(self.scroll_wheel)
        scroll_layout.addWidget(self.spin_btn)

        # 添加所有组件到主布局
        layout.addWidget(rules_widget)
        layout.addWidget(search_widget)
        layout.addWidget(rank_widget)
        layout.addWidget(scroll_widget)

        # 设置面板样式
        panel.setObjectName("leftPanel")

        # 将面板设置为滚动区域的内容
        scroll.setWidget(panel)

        return scroll

    # 修改 toggle_batch_delete_mode 方法，确保切换模式时重置全选按钮状态
    def toggle_batch_delete_mode(self, rank):
        layout = self.rank_areas[rank]
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, NinjaCard):
                widget.set_checkbox_mode(True)

        # 显示删除和全选按钮，并重置全选按钮状态
        self.batch_delete_buttons[rank].show()
        select_all_btn = self.select_all_buttons[rank]
        select_all_btn.show()
        select_all_btn.setText("全选")
        select_all_btn.setProperty("is_all_selected", False)
    def create_right_panel(self):
        container = QWidget()
        container_layout = QVBoxLayout(container)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        self.right_layout = QVBoxLayout(content_widget)
        self.right_layout.setSpacing(1)
        self.right_layout.setContentsMargins(1, 1, 1, 1)

        self.rank_areas = {}
        self.rank_containers = {}  # 存储每个等级的容器
        self.batch_delete_buttons = {}  # 存储每个等级的批量删除按钮
        self.select_all_buttons = {}  # 存储每个等级的全选按钮

        for rank in ['S', 'A', 'B', 'C']:
            rank_container = QWidget()
            rank_container.setObjectName(f"rank_container_{rank}")
            rank_layout = QVBoxLayout(rank_container)

            # 标题栏
            title_bar = QWidget()
            title_layout = QHBoxLayout(title_bar)
            title_layout.setContentsMargins(0, 0, 0, 0)

            title = QLabel(f"{rank}级忍者")
            title.setObjectName("rankTitle")

            batch_delete_btn = QPushButton("批量删除")
            batch_delete_btn.setObjectName("batchClearButton")
            batch_delete_btn.clicked.connect(lambda checked, r=rank: self.toggle_batch_delete_mode(r))

            # 在创建全选按钮时，添加一个属性来跟踪状态
            select_all_btn = QPushButton("全选")
            select_all_btn.setObjectName("selectAllButton")
            select_all_btn.setProperty("is_all_selected", False)  # 添加状态属性
            select_all_btn.clicked.connect(lambda checked, r=rank: self.toggle_select_all_ninjas(r))
            select_all_btn.hide()  # 初始隐藏全选按钮

            title_layout.addWidget(title)
            title_layout.addWidget(batch_delete_btn)
            title_layout.addWidget(select_all_btn)
            title_layout.addStretch()

            rank_layout.addWidget(title_bar)

            # 忍者卡片区域
            cards_widget = QWidget()
            cards_layout = QFlowLayout()  # 使用流式布局
            cards_layout.setSpacing(2)
            cards_layout.margin = 1  # 直接设置 margin 属性
            cards_widget.setLayout(cards_layout)

            self.rank_areas[rank] = cards_layout

            # 批量删除按钮（初始隐藏）
            delete_selected_btn = QPushButton("删除选中")
            delete_selected_btn.setObjectName("deleteSelectedButton")
            delete_selected_btn.clicked.connect(lambda checked, r=rank: self.delete_selected_ninjas(r))
            delete_selected_btn.hide()

            rank_layout.addWidget(cards_widget)
            rank_layout.addWidget(delete_selected_btn)

            self.rank_containers[rank] = rank_container
            self.batch_delete_buttons[rank] = delete_selected_btn
            self.select_all_buttons[rank] = select_all_btn
            self.right_layout.addWidget(rank_container)

        scroll.setWidget(content_widget)
        container_layout.addWidget(scroll)

        return container

    def load_ninjas(self):
        for rank_layout in self.rank_areas.values():
            while rank_layout.count():
                item = rank_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        ninjas = self.ninja_data.get_ninjas()

        rank_ninjas = {'S': [], 'A': [], 'B': [], 'C': []}
        for ninja in ninjas:
            if ninja['rank'] in rank_ninjas:
                rank_ninjas[ninja['rank']].append(ninja)

        for rank, ninjas in rank_ninjas.items():
            layout = self.rank_areas[rank]
            
            for ninja in ninjas:
                card = NinjaCard(
                    ninja["name"],
                    ninja["rank"]
                )
                card.deleted.connect(self.delete_ninja)
                layout.addWidget(card)

    def toggle_select_all_ninjas(self, rank):
        button = self.select_all_buttons[rank]
        is_all_selected = button.property("is_all_selected")

        layout = self.rank_areas[rank]

        # 切换状态
        new_state = not is_all_selected
        button.setProperty("is_all_selected", new_state)

        # 更新按钮文字
        button.setText("取消全选" if new_state else "全选")

        # 更新所有忍者的选中状态
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, NinjaCard):
                widget.checkbox.setChecked(new_state)

    def delete_selected_ninjas(self, rank):
        layout = self.rank_areas[rank]
        selected_names = []

        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, NinjaCard) and widget.checkbox.isChecked():
                selected_names.append(widget.name)

        if selected_names:
            reply = QMessageBox.question(
                self,
                "确认删除",
                f"确定要删除选中的 {len(selected_names)} 个忍者吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                for name in selected_names:
                    self.ninja_data.delete_ninja(name)
                self.load_ninjas()

                # 调整该等级区域的高度
                # container = self.rank_containers[rank]
                # container.setMaximumHeight(100)  # 设置一个合适的最小高度
                # container.adjustSize()
                # QTimer.singleShot(0, container.adjustSize)  # 确保在下一个事件循环中调整大小
                # 自动触发所有等级的批量删除按钮


        # 恢复正常模式
        self.batch_delete_buttons[rank].hide()
        select_all_btn = self.select_all_buttons[rank]
        select_all_btn.hide()
        select_all_btn.setText("全选")  # 重置按钮文字
        select_all_btn.setProperty("is_all_selected", False)  # 重置状态
        QTimer.singleShot(300, self.auto_trigger_batch_delete)
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, NinjaCard):
                widget.set_checkbox_mode(False)

    def select_all_ninjas(self, rank):
        layout = self.rank_areas[rank]
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, NinjaCard):
                widget.checkbox.setChecked(True)

    def add_ninja(self, rank):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"添加{rank}级忍者")
        layout = QVBoxLayout(dialog)

        name_input = QLineEdit()
        name_input.setPlaceholderText("输入忍者名称")

        confirm_btn = QPushButton("确认")

        def on_confirm():
            name = name_input.text().strip()
            if name:
                # 检查是否已存在
                ninjas = self.ninja_data.get_ninjas()
                if any(ninja["name"].lower() == name.lower() for ninja in ninjas):
                    QMessageBox.warning(dialog, "警告", "该忍者已被禁用")
                    return

                self.ninja_data.add_ninja(name, rank)
                self.load_ninjas()
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "警告", "请输入忍者名称")

        confirm_btn.clicked.connect(on_confirm)

        layout.addWidget(QLabel("忍者名称:"))
        layout.addWidget(name_input)
        layout.addWidget(confirm_btn)

        dialog.exec_()

    def quick_add_ninja(self, rank):
        name = self.search_input.text().strip()
        if name:
            # 检查是否已存在
            ninjas = self.ninja_data.get_ninjas()
            if any(ninja["name"].lower() == name.lower() for ninja in ninjas):
                QMessageBox.warning(self, "警告", "该忍者已被禁用")
                return

            self.ninja_data.add_ninja(name, rank)
            self.load_ninjas()
            self.search_input.clear()
            self.search_result_label.hide()
        else:
            self.add_ninja(rank)

    def batch_add_ninja(self, rank):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"批量添加{rank}级忍者")
        dialog.resize(600, 400)  # 设置更大的对话框尺寸
        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)  # 增加边距

        # 说明文本
        hint_label = QLabel("请输入忍者名称，用空格分隔多个忍者")
        hint_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                margin-bottom: 8px;
            }
        """)

        # 输入框
        name_input = QTextEdit()  # 使用QTextEdit替代QLineEdit
        name_input.setPlaceholderText("例如：宇智波斑 千手柱间 宇智波鼬")
        name_input.setMinimumHeight(200)  # 设置最小高度
        font = name_input.font()
        font.setPointSize(14)  # 设置更大的字体
        name_input.setFont(font)

        # 确认按钮
        confirm_btn = QPushButton("确认添加")
        confirm_btn.setMinimumHeight(40)  # 增加按钮高度
        confirm_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
            }
        """)

        def on_confirm():
            names_text = name_input.toPlainText().strip()
            if names_text:
                # 分割文本并过滤空字符串
                names = [name.strip() for name in names_text.split() if name.strip()]

                # 检查重复的忍者
                existing_ninjas = self.ninja_data.get_ninjas()
                existing_names = {ninja["name"].lower() for ninja in existing_ninjas}

                # 记录添加结果
                success_count = 0
                duplicate_names = []

                for name in names:
                    if name.lower() not in existing_names:
                        self.ninja_data.add_ninja(name, rank)
                        success_count += 1
                        existing_names.add(name.lower())
                    else:
                        duplicate_names.append(name)

                # 显示结果消息
                result_message = f"成功添加 {success_count} 个忍者"
                if duplicate_names:
                    result_message += f"\n以下忍者已存在：\n{', '.join(duplicate_names)}"

                QMessageBox.information(dialog, "添加结果", result_message)

                if success_count > 0:
                    self.load_ninjas()
                    dialog.accept()
            else:
                QMessageBox.warning(dialog, "警告", "请输入忍者名称")


        confirm_btn.clicked.connect(on_confirm)

        layout.addWidget(hint_label)
        layout.addWidget(name_input)
        layout.addWidget(confirm_btn)

        # 设置对话框样式
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 12px;
                background-color: white;
            }
            QTextEdit:focus {
                border: 2px solid #2196F3;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)

        dialog.exec_()
        QTimer.singleShot(300, self.auto_trigger_batch_delete)

    def delete_ninja(self, name):
        self.ninja_data.delete_ninja(name)
        self.load_ninjas()

    def clear_search(self):
        self.search_input.clear()
        self.search_result_label.hide()

    def search_ninja(self):
        search_text = self.search_input.text().strip()
        if not search_text:
            self.search_result_label.hide()
            return

        # 在所有忍者中搜索
        ninjas = self.ninja_data.get_ninjas()
        found = any(ninja["name"].lower() == search_text.lower() for ninja in ninjas)

        # 设置搜索结果提示
        if found:
            self.search_result_label.setText(f"忍者「{search_text}」已被禁用")
            self.search_result_label.setStyleSheet("""
                QLabel {
                    background-color: #ffebee;
                    color: #c62828;
                    padding: 8px;
                    border-radius: 4px;
                    font-size: 13px;
                }
            """)
        else:
            self.search_result_label.setText(f"忍者「{search_text}」未被禁用")
            self.search_result_label.setStyleSheet("""
                QLabel {
                    background-color: #e8f5e9;
                    color: #2e7d32;
                    padding: 8px;
                    border-radius: 4px;
                    font-size: 13px;
                }
            """)

        self.search_result_label.show()

    def save_rules(self):
        self.ninja_data.save_rules(self.rules_text.toPlainText())

    def load_scrolls(self):
        # 清除现有的秘卷项
        while self.scroll_list_layout.count():
            item = self.scroll_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 加载秘卷列表
        scrolls = self.ninja_data.load_scrolls()

        # 更新转盘和转动按钮状态
        self.scroll_wheel.set_items(scrolls)

        # 根据是否有秘卷来设置转盘和按钮的可见性
        has_scrolls = len(scrolls) > 0
        self.scroll_wheel.setVisible(has_scrolls)
        self.spin_btn.setVisible(has_scrolls)

        # 添加秘卷项到列表
        for scroll in scrolls:
            scroll_item = ScrollItem(scroll)
            scroll_item.deleted.connect(self.remove_scroll)
            self.scroll_list_layout.addWidget(scroll_item)

    def add_scroll(self):
        name = self.scroll_input.text().strip()
        if name:
            self.ninja_data.add_scroll(name)
            self.load_scrolls()
            self.scroll_input.clear()

            # 确保转盘和按钮可见
            self.scroll_wheel.setVisible(True)
            self.spin_btn.setVisible(True)

    def remove_scroll(self, name):
        self.ninja_data.remove_scroll(name)
        self.load_scrolls()

    def load_stylesheet(self):
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }

        QWidget {
            font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
        }

        QWidget#leftPanel {
            background-color: white;
            border-radius: 8px;
            margin: 8px;
        }

        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #1976D2;
        }

        QPushButton:pressed {
            background-color: #0D47A1;
        }

        QPushButton#deleteButton {
            background-color: #F44336;
            padding: 4px 8px;
        }

        QPushButton#deleteButton:hover {
            background-color: #D32F2F;
        }

        QLineEdit {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
        }

        QLineEdit:focus {
            border: 2px solid #2196F3;
        }

        QLabel#searchLabel, QLabel#rankTitle {
            font-size: 16px;
            font-weight: bold;
            color: #1976D2;
            padding-bottom: 8px;
        }

        QLabel#rankLabel {
            font-size: 14px;
            font-weight: bold;
            color: #333;
        }

        QPushButton#addButton {
            min-width: 80px;
        }

        QWidget#rankWidget {
            background-color: #f8f9fa;
            border-radius: 6px;
            padding: 12px;
        }

        .NinjaCard {
            background-color: white;
            border-radius: 1px;  /* 减小圆角 */
            padding: 0px;
            margin: 0px;
            box-shadow: none;    /* 移除阴影以减少视觉空间 */
        }
        QScrollArea {
            border: none;
            background-color: transparent;
        }

        QWidget[objectName^="rank_container_"] {
            background-color: white;
            border-radius: 4px;  /* 减小圆角 */
            padding: 2px;        /* 进一步减小容器内边距 */
            margin: 2px;         /* 减小容器外边距 */
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }

        QDialog {
            background-color: white;
        }

        QDialog QLabel {
            font-size: 14px;
            color: #333;
            margin-top: 8px;
        }

        QDialog QPushButton {
            margin-top: 16px;
        }

        QLabel#rulesLabel {
            font-size: 16px;
            font-weight: bold;
            color: #1976D2;
            padding-bottom: 8px;
        }

        QTextEdit {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
            font-size: 13px;
        }

        QTextEdit:focus {
            border: 2px solid #2196F3;
        }

        QLabel#scrollTitle {
            font-size: 16px;
            font-weight: bold;
            color: #1976D2;
            padding-bottom: 8px;
        }

        QPushButton#spinButton {
            background-color: #4CAF50;
            font-size: 16px;
            padding: 12px;
            margin-top: 8px;
        }

        QPushButton#spinButton:hover {
            background-color: #388E3C;
        }

        QPushButton#batchClearButton {
            background-color: #FF5722;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: bold;
        }

        QPushButton#batchClearButton:hover {
            background-color: #F4511E;
        }

        QPushButton#deleteSelectedButton {
            background-color: #F44336;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            margin-top: 8px;
        }

        QPushButton#deleteSelectedButton:hover {
            background-color: #D32F2F;
        }

        QPushButton#selectAllButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: bold;
            margin-left: 8px;
        }

        QPushButton#selectAllButton:hover {
            background-color: #1976D2;
        }

        
        QCheckBox {
            spacing: 0px;
            margin: 0px;
            padding: 0px;
        }

        QCheckBox::indicator {
            width: 10px;
            height: 10px;
            margin: 0px;
            padding: 0px;
        }

        QCheckBox::indicator:unchecked {
            border: 1px solid #ddd;
            border-radius: 2px;
            background-color: white;
            margin: 0px;
        }

        QCheckBox::indicator:checked {
            border: 1px solid #2196F3;
            border-radius: 2px;
            background-color: #2196F3;
            image: url(checkmark.svg);
            margin: 0px;
        }

        .NinjaCard {
            background-color: white;
            border-radius: 0px;
            padding: 0px;
            margin: 0px;
            min-height: 20px;    /* 设置最小高度 */
            max-height: 20px;    /* 设置最大高度 */
        }

        /* 添加水平布局容器的样式 */
        .NinjaCard QWidget {
            margin: 0px;
            padding: 0px;
        }

        /* 确保标签没有额外的边距 */
        .NinjaCard QLabel {
            margin: 0px;
            padding: 0px;
            min-height: 16px;
            max-height: 16px;
        }

        /* 调整删除按钮的样式 */
        QPushButton#deleteButton {
            padding: 0px 2px;
            margin: 0px;
            height: 16px;
            font-size: 10px;
        }

        /* 调整卡片内部布局容器 */
        .NinjaCard > QWidget {
            margin: 0px;
            padding: 0px;
            min-height: 16px;
            max-height: 16px;
        }

        /* 调整水平布局 */
        .NinjaCard QHBoxLayout {
            margin: 0px;
            padding: 0px;
            spacing: 0px;
        }

        /* 调整垂直布局 */
        .NinjaCard QVBoxLayout {
            margin: 0px;
            padding: 0px;
            spacing: 0px;
        }

        QWidget[objectName^="rank_container_"] {
            background-color: white;
            border-radius: 2px;
            padding: 1px;
            margin: 1px;
        }
        """
        self.setStyleSheet(style)