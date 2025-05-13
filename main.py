import sys
import os
from PySide6.QtWidgets import QApplication
from ninja_manager import NinjaManager

if __name__ == '__main__':
    # 确保必要的目录存在
    for dir_name in ['data', 'images']:
        os.makedirs(dir_name, exist_ok=True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = NinjaManager()
    window.show()

    sys.exit(app.exec())