import PyInstaller.__main__
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 定义图标文件路径（如果有的话）
# icon_path = os.path.join(current_dir, 'icon.ico')

# 定义需要包含的数据文件
datas = [
    ('data', 'data'),  # (源文件夹, 目标文件夹)
    ('checkmark.svg', '.'),  # 包含 checkmark.svg 文件
]

# 定义 PyInstaller 参数
params = [
    'main.py',  # 你的主程序入口文件
    '--name=火影忍者段位赛挑战管理器猪头肉定制版',  # 生成的可执行文件名
    '--windowed',  # 使用 GUI 模式，不显示控制台窗口
    '--noconfirm',  # 覆盖之前的构建文件
    '--clean',  # 清理临时文件
    # '--icon=' + icon_path,  # 如果有图标的话
    '--add-data=' + os.pathsep.join(datas[0]),  # 添加 data 文件夹
    '--add-data=' + os.pathsep.join(datas[1]),  # 添加 checkmark.svg
    '--hidden-import=PySide6.QtXml',  # 确保包含所需的 Qt 模块
]

# 运行打包命令
PyInstaller.__main__.run(params)