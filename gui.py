import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QCoreApplication
import os
import threading
from time import sleep


def create_tray_icon():
    icon_path = os.path.join(os.environ["LOCALAPPDATA"], "Summer AI", "icon.png")

    app_icon = QIcon(icon_path)
    menu = QMenu()

    # Add one or more actions to the menu
    exit_action = menu.addAction("Exit")
    exit_action.triggered.connect(on_exit_trigger)

    enable_action = menu.addAction("Enable")
    enable_action.triggered.connect(on_exit_trigger)

    tray_icon = QSystemTrayIcon()
    tray_icon.setIcon(app_icon)
    tray_icon.setContextMenu(menu)
    tray_icon.setToolTip("Your Application Name")
    tray_icon.show()
    return tray_icon

def on_exit_trigger():
    QApplication.quit()
    sys.exit()