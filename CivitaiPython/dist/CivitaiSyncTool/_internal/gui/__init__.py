import sys
from PyQt5.QtWidgets import QApplication
from gui.app import MainWindow

if __name__ == "__main__":
    # 创建Qt应用程序实例
    # sys.argv包含命令行参数列表
    app = QApplication(sys.argv)
    
    # 创建主窗口实例
    win = MainWindow()
    
    # 显示主窗口
    win.show()
    
    # 启动应用程序的事件循环
    # 等待用户操作并处理事件
    # sys.exit确保程序退出时返回正确的退出码
    sys.exit(app.exec_())
