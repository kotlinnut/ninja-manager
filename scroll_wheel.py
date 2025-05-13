from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import math
import random


class ScrollWheel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
        self.current_rotation = 0
        self.target_rotation = 0
        self.is_spinning = False
        self.animation = QPropertyAnimation(self, b"rotation", self)
        self.animation.setDuration(3000)  # 3秒转动
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.finished.connect(self.on_spin_finished)

        # 设置最小尺寸
        self.setMinimumSize(300, 300)

    @Property(float)
    def rotation(self):
        return self.current_rotation

    @rotation.setter
    def rotation(self, value):
        self.current_rotation = value
        self.update()

    def set_items(self, items):
        self.items = items
        self.update()

    def spin(self):
        if self.is_spinning or not self.items:
            return

        self.is_spinning = True

        # 随机选择一个目标角度（确保至少转动720度）
        target_item = random.choice(range(len(self.items)))
        base_rotation = 720 + random.randint(0, 360)  # 至少转两圈
        self.target_rotation = base_rotation + (360 / len(self.items)) * target_item

        self.animation.setStartValue(self.current_rotation)
        self.animation.setEndValue(self.target_rotation)
        self.animation.start()

    def on_spin_finished(self):
        self.is_spinning = False
        self.current_rotation = self.target_rotation % 360

    def paintEvent(self, event):
        if not self.items:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 计算中心点和半径
        center = self.rect().center()
        radius = min(self.width(), self.height()) * 0.4

        # 绘制外圈
        painter.setPen(QPen(QColor("#2196F3"), 2))
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawEllipse(center, radius, radius)

        # 绘制分隔线
        painter.save()
        painter.translate(center)
        painter.rotate(-self.current_rotation)

        slice_angle = 360.0 / len(self.items)
        for i in range(len(self.items)):
            # 绘制分隔线
            painter.drawLine(0, 0, radius * math.cos(math.radians(i * slice_angle)),
                             radius * math.sin(math.radians(i * slice_angle)))
        painter.restore()

        # 单独绘制文字，保持水平
        for i, item in enumerate(self.items):
            painter.save()

            # 设置文字样式
            font = painter.font()
            font.setBold(True)
            font.setPointSize(16)
            painter.setFont(font)
            painter.setPen(QColor("#000000"))

            # 计算文字位置
            angle = math.radians(i * slice_angle - self.current_rotation)
            next_angle = math.radians((i + 1) * slice_angle - self.current_rotation)
            mid_angle = (angle + next_angle) / 2

            # 将文字放在扇形区域的中心位置
            text_radius = radius * 0.65
            text_x = center.x() + text_radius * math.cos(mid_angle)
            text_y = center.y() + text_radius * math.sin(mid_angle)

            # 计算文字边界框
            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(item)
            text_height = metrics.height()

            # 创建文字边界框
            text_rect = QRectF(
                text_x - text_width / 2,
                text_y - text_height / 2,
                text_width,
                text_height
            )

            # 绘制文字
            painter.drawText(text_rect, Qt.AlignCenter, item)
            painter.restore()

        # 绘制中心圆和指针
        center_radius = 20

        # 绘制三角形指针
        pointer_path = QPainterPath()
        pointer_path.moveTo(center.x(), center.y() - center_radius - 15)
        pointer_path.lineTo(center.x() - 8, center.y() - center_radius)
        pointer_path.lineTo(center.x() + 8, center.y() - center_radius)
        pointer_path.closeSubpath()

        # 绘制指针阴影
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 30))
        painter.translate(2, 2)
        painter.drawPath(pointer_path)

        # 绘制指针本体
        painter.translate(-2, -2)
        painter.setBrush(QColor("#F44336"))
        painter.drawPath(pointer_path)

        # 绘制中心圆
        painter.setBrush(QColor("#F44336"))
        painter.drawEllipse(center, center_radius, center_radius)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 保持正方形形状
        size = min(self.width(), self.height())
        self.setFixedSize(size, size)