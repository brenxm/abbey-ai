import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QCoreApplication
import os

def create_tray_icon(terminate_app, clear_chat_hx):
    icon_path = os.path.join(os.environ["LOCALAPPDATA"], "Summer AI", "icon.png")

    app_icon = QIcon(icon_path)
    menu = QMenu()

    # Clear chat history
    clear_chat_action = menu.addAction("Clear chat history")
    clear_chat_action.triggered.connect(clear_chat_hx)

    # Add one or more actions to the menu
    exit_action = menu.addAction("Exit")
    exit_action.triggered.connect(terminate_app)
 
    tray_icon = QSystemTrayIcon()
    tray_icon.setIcon(app_icon)
    tray_icon.setContextMenu(menu)
    tray_icon.setToolTip("Your Application Name")
    tray_icon.show()
    return tray_icon

