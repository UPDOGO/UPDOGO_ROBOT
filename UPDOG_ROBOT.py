# -- coding: utf-8 --
"""
UPDOGO_ROBOT.py - v4.3.7 (Consolidated Full Rebuild - Revised Part 1)

Main application window for UPDOGO Robot.
This is a single, complete file, delivered in 4 text parts for manageability.
Concatenate Part 1/4, 2/4, 3/4, and 4/4 to get the full script.

This part (1/4) includes:
- All import statements.
- Logging setup.
- Global constants (application details, paths, UI constants, full THEMES_CSS,
  CHAT_STYLES, message templates, camera filters, TTS defaults).
- Global variables for tracking module import status.
- Helper function for conditional imports (_try_import).
- All Dummy Class definitions (internal fallbacks for external modules).
- Attempted imports of REAL external component modules and assignment to
  corresponding '_cls' variables (which will hold either the Real or Dummy class).
"""

# --- Core Python Imports ---
import sys
import os
import json
import time  # Generally useful, though not directly in this part
import datetime
import logging
import re  # Often useful for text processing
import threading  # For QThread context, though QThread itself is used
from typing import Dict, Any, Tuple, List, Optional, Callable, Type

# --- PyQt5 Imports ---
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QGroupBox,
    QStatusBar, QMessageBox, QFileDialog, QSizePolicy, QSpacerItem, QSlider,
    QAction, QMenuBar, QMenu, QDialog, QTextBrowser, QDialogButtonBox,
    QActionGroup, QToolButton, QStyle, QDesktopWidget
)
from PyQt5.QtCore import (
    Qt, QObject, QThread, pyqtSignal, pyqtSlot, QTimer, QSettings, QSize, QPoint,
    QMetaObject, Q_ARG, QEvent, QCoreApplication, QLocale, QUrl
)
from PyQt5.QtGui import (
    QImage, QPixmap, QTextCursor, QColor, QFont, QPalette, QIcon, QDesktopServices
)

# --- Attempt to import required external data science/media libraries ---
# These are primarily for CameraWorker and ImageSaveWorker (defined in Part 2/4)
# and for the external robot_appearance.py (AI version).
CV2_AVAILABLE = False
NUMPY_AVAILABLE = False
PIL_AVAILABLE = False

try:
    import cv2

    CV2_AVAILABLE = True
except ImportError:
    pass  # Logging for missing CV2 will occur later if a component specifically needs it.

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    pass  # Logging for missing NumPy will occur later.

try:
    from PIL import Image, ImageDraw  # ImageDraw needed for dummy creation in robot_appearance

    PIL_AVAILABLE = True
except ImportError:
    pass  # Logging for missing Pillow will occur later.

# --- Logging Setup ---
# This basicConfig is a fallback. The _setup_logging method in MainWindow
# will configure file logging and more detailed formatting from the JSON config.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - [%(threadName)s] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]  # Default to console output
)
logger = logging.getLogger(__name__)  # Main application logger

# --- Global Constants ---
APP_NAME_CONST: str = "UPDOGO Robot"
APP_VERSION_CONST: str = "4.3.7"  # Updated version for this rebuild
APP_TITLE_CONST: str = f"{APP_NAME_CONST} Control Suite v{APP_VERSION_CONST} (Consolidated)"
CONFIG_FILE: str = "updogo_config_v4.3.json"
LOG_FILE_NAME: str = "updogo_robot_main.log"
SETTINGS_ORG: str = "UPDOGORobotics"
SETTINGS_APP_BASE: str = "UPDOGOControlSuite"
SETTINGS_APP: str = f"{SETTINGS_APP_BASE}_v{APP_VERSION_CONST.split('.')[0]}.{APP_VERSION_CONST.split('.')[1]}"

VISUALS_BASE_PATH: str = "visuals"
ICONS_BASE_PATH: str = os.path.join(VISUALS_BASE_PATH, "icons")
DEFAULT_CHAT_HISTORY_FILE: str = "updogo_chat_log.html"
USER_GUIDE_CONTENT_FILE: str = os.path.join(VISUALS_BASE_PATH, "user_guide_content_v4.3.html")

DEFAULT_WINDOW_SIZE: Tuple[int, int] = (1600, 950)
LAYOUT_STRETCH_LEFT: int = 35
LAYOUT_STRETCH_CENTER: int = 30
LAYOUT_STRETCH_RIGHT: int = 35

DEFAULT_CAMERA_INDEX: int = 0
DEFAULT_CAMERA_RESOLUTION: Tuple[int, int] = (640, 480)
RAW_CAMERA_FILTERS: Dict[str, Optional[str]] = {
    "None": None, "Grayscale": "grayscale", "Blur": "blur",
    "Edges": "canny", "Sepia": "sepia", "Invert": "invert", "Cartoon": "cartoon"
}
RAW_DEFAULT_CAMERA_FILTER: str = "None"

TTS_DEFAULTS: Dict[str, int] = {
    "rate": 160, "min_rate": 50, "max_rate": 350,
    "volume": 85, "min_volume": 0, "max_volume": 100
}
DEFAULT_CHAT_FONT_SIZE: int = 10

# --- THEMES_CSS Dictionary ---
# This large dictionary defines the stylesheets for different application themes.
# It may generate line-length warnings from linters, which is often acceptable for such data.
THEMES_CSS: Dict[str, str] = {
    "Default": """QWidget{background-color:#f0f0f0;color:#000;font-family:Arial,sans-serif;font-size:9pt}QMainWindow,QGroupBox{background-color:#f0f0f0}QGroupBox{border:1px solid #c0c0c0;border-radius:4px;margin-top:12px;padding:10px 5px 5px 5px}QGroupBox::title{color:#333;background-color:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#e1e1e1;border:1px solid #b0b0b0;padding:6px 10px;min-height:20px;border-radius:3px}QPushButton:hover{background-color:#d8d8d8}QPushButton:pressed{background-color:#c8c8c8}QPushButton:disabled{background-color:#f5f5f5;color:#a0a0a0}QLineEdit,QTextEdit#UserInput{background-color:#fff;color:#000;border:1px solid #c0c0c0;border-radius:3px;padding:4px}QTextEdit#ChatDisplay{background-color:#fff;color:#000;border:1px solid #c0c0c0;border-radius:3px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #b0b0b0;background:#e8e8e8;width:15px;margin:1px 0 1px 0}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#c0c0c0;min-height:25px;border-radius:6px}QTextEdit#ChatDisplay QScrollBar::add-line:vertical,QTextEdit#ChatDisplay QScrollBar::sub-line:vertical{height:0px;width:0px;border:none;background:none}QToolButton{background-color:#e1e1e1;border:1px solid #b0b0b0;border-radius:3px;padding:3px}QToolButton:hover{background-color:#d8d8d8}QToolButton:pressed{background-color:#c8c8c8}QToolButton:checked{background-color:#c0c0c0;border-color:#a0a0a0}QComboBox{background-color:#e1e1e1;border:1px solid #b0b0b0;padding:4px 5px;border-radius:3px;min-height:22px}QComboBox::drop-down{border-left:1px solid #b0b0b0}QComboBox QAbstractItemView{background-color:#fff;color:#000;selection-background-color:#0078d7;border:1px solid #b0b0b0}QSlider::groove:horizontal{border:1px solid #bbb;background:#fff;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#0078d7;border:1px solid #005ea0;width:14px;margin:-4px 0;border-radius:7px}QStatusBar{background-color:#dcdcdc;color:#000}QLabel#CameraLabel{background-color:black;border:1px solid grey}QMenuBar{background-color:#e8e8e8;color:#000}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#d0d0d0}QMenuBar::item:disabled{color:#a0a0a0}QMenu{background-color:#f8f8f8;border:1px solid #b0b0b0;color:#000}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#0078d7;color:white}QMenu::item:disabled{color:#a0a0a0}""",
    "Cyberpunk Neon": """QWidget{color:#0ff;font-family:Consolas,monospace;font-size:10pt}QMainWindow,QGroupBox{background-color:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0a0a0a,stop:1 #2a002a)}QGroupBox{border:1px solid #f0f;border-radius:0px;margin-top:12px;padding:10px 5px 5px 5px;color:#0ff}QGroupBox::title{color:#f0f;background:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#222;border:1px solid #f0f;padding:7px 12px;color:#f0f;min-height:22px;border-radius:0px}QPushButton:hover{background-color:#333;color:#fff}QPushButton:pressed{background-color:#111}QPushButton:disabled{background-color:#1a1a1a;color:#505}QLineEdit,QTextEdit#UserInput{background-color:#050505;color:#0ff;border:1px solid #f0f;border-radius:0px;selection-background-color:#f0f;selection-color:#000;padding:4px}QTextEdit#ChatDisplay{background-color:#080808;color:#0ff;border:1px solid #f0f;border-radius:0px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #f0f;background:#050505;width:15px;margin:1px 0 1px 0}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#f0f;min-height:25px;border-radius:0px}QToolButton{background-color:#222;border:1px solid #f0f;border-radius:0px;padding:3px;color:#f0f}QToolButton:hover{background-color:#333;color:#fff}QToolButton:pressed{background-color:#111}QToolButton:checked{background-color:#f0f;color:#000;border-color:#a0a}QComboBox{background-color:#222;border:1px solid #f0f;color:#f0f;padding:4px 5px;border-radius:0px;min-height:22px}QComboBox::drop-down{border-left:1px solid #f0f}QComboBox QAbstractItemView{background-color:#050505;color:#0ff;selection-background-color:#f0f;selection-color:#000;border:1px solid #f0f}QSlider::groove:horizontal{border:1px solid #f0f;background:#050505;height:6px;border-radius:0px}QSlider::handle:horizontal{background:#f0f;border:1px solid #a0a;width:12px;margin:-4px 0;border-radius:0px}QStatusBar{background-color:#111;color:#0ff}QLabel#CameraLabel{background-color:#000;border:1px solid #f0f}QMenuBar{background-color:#111;color:#f0f;border-bottom:1px solid #f0f}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#333}QMenuBar::item:disabled{color:#505}QMenu{background-color:#0a0a0a;color:#0ff;border:1px solid #f0f}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#f0f;color:#000}QMenu::item:disabled{color:#505}""",
    "Sunset Glow": """QWidget{color:#fff;font-family:Arial,sans-serif;font-size:9pt}QMainWindow,QGroupBox{background-color:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ff7e5f,stop:1 #feb47b)}QGroupBox{border:1px solid #ff9a8b;border-radius:4px;margin-top:12px;padding:10px 5px 5px 5px}QGroupBox::title{color:#fff;background:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#ff9a8b;border:1px solid #ff7e5f;color:#fff;padding:6px 10px;min-height:20px;border-radius:3px}QPushButton:hover{background-color:#ffac9b}QPushButton:pressed{background-color:#ff7e5f}QLineEdit,QTextEdit#UserInput{background-color:#fff8f0;color:#333;border:1px solid #feb47b;border-radius:3px;padding:4px}QTextEdit#ChatDisplay{background-color:#fff8f0;color:#333;border:1px solid #feb47b;border-radius:3px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #feb47b;background:#fff8f0;width:15px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#ff9a8b;min-height:25px;border-radius:6px}QToolButton{background-color:#ff9a8b;border:1px solid #ff7e5f;color:#fff;border-radius:3px;padding:3px}QToolButton:hover{background-color:#ffac9b}QToolButton:checked{background-color:#ff7e5f}QComboBox{background-color:#ff9a8b;border:1px solid #ff7e5f;color:#fff;padding:4px 5px;border-radius:3px;min-height:22px}QComboBox QAbstractItemView{background-color:#fff8f0;color:#333;selection-background-color:#ff9a8b;border:1px solid #feb47b}QSlider::handle:horizontal{background:#ff6b6b;border:1px solid #e05050}QStatusBar{background-color:#ff7e5f;color:#fff}QLabel#CameraLabel{background-color:#331a00;border:1px solid #ff9a8b}QMenuBar{background-color:#ff7e5f;color:white}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#e05050}QMenu{background-color:#feb47b;border:1px solid #ff9a8b;color:#fff}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#ff7e5f;color:white}""",
    "Azure Dreams": """QWidget{font-family:Calibri,sans-serif;font-size:10pt;color:#FFFFFF}QMainWindow,QGroupBox{background-color:qlineargradient(spread:pad,x1:0,y1:0,x2:1,y2:1,stop:0 #3A6073,stop:1 #16222A)}QGroupBox{border:1px solid #5F97B1;border-radius:6px;margin-top:12px;padding:12px 6px 6px 6px;background-color:rgba(255,255,255,0.03)}QGroupBox::title{color:#B2DAE8;background:transparent;padding:0 4px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:qlineargradient(spread:pad,x1:0,y1:0,x2:1,y2:0,stop:0 #4A83A0,stop:1 #6CADD1);border:1px solid #8FCDED;color:#fff;padding:7px 14px;min-height:24px;border-radius:4px}QPushButton:hover{background-color:qlineargradient(spread:pad,x1:0,y1:0,x2:1,y2:0,stop:0 #5F97B1,stop:1 #8FCDED)}QPushButton:pressed{background-color:qlineargradient(spread:pad,x1:0,y1:0,x2:1,y2:0,stop:0 #3A6073,stop:1 #5F97B1)}QLineEdit,QTextEdit#UserInput{background-color:rgba(10,30,45,0.7);color:#E0F2F7;border:1px solid #5F97B1;border-radius:4px;padding:5px}QTextEdit#ChatDisplay{background-color:rgba(5,20,30,0.8);color:#E0F2F7;border:1px solid #5F97B1;border-radius:4px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #5F97B1;background:rgba(10,30,45,0.7);width:16px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#5F97B1;min-height:28px;border-radius:7px}QToolButton{background-color:transparent;border:1px solid #5F97B1;color:#B2DAE8;border-radius:4px;padding:3px}QToolButton:hover{background-color:rgba(74,131,160,0.5)}QToolButton:checked{background-color:#5F97B1;border-color:#8FCDED}QComboBox{background-color:#4A83A0;border:1px solid #8FCDED;color:#fff;padding:5px 7px;border-radius:4px;min-height:24px}QComboBox QAbstractItemView{background-color:#16222A;color:#E0F2F7;selection-background-color:#4A83A0;border:1px solid #5F97B1}QSlider::groove:horizontal{border:1px solid #5F97B1;background:rgba(10,30,45,0.7);height:10px;border-radius:5px}QSlider::handle:horizontal{background:#8FCDED;border:1px solid #E0F2F7;width:18px;margin:-5px 0;border-radius:9px}QStatusBar{background-color:#16222A;color:#8FCDED;border-top:1px solid #3A6073}QLabel#CameraLabel{background-color:#0A121A;border:1px solid #5F97B1}QMenuBar{background-color:#16222A;color:#8FCDED}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#3A6073}QMenu{background-color:#263A4A;color:#E0F2F7;border:1px solid #5F97B1}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#4A83A0;color:white}""",
    "Emerald Twilight": """QWidget{font-family:Verdana,sans-serif;font-size:9pt;color:#D4E9E1}QMainWindow,QGroupBox{background-color:qlineargradient(spread:pad,x1:0.5,y1:0,x2:0.5,y2:1,stop:0 #0F2027,stop:0.5 #203A43,stop:1 #2C5364)}QGroupBox{border:1px solid #3E8070;border-radius:5px;margin-top:12px;padding:10px 5px 5px 5px;background-color:rgba(0,0,0,0.1)}QGroupBox::title{color:#88C9B2;background:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#2C7A6A;border:1px solid #6AAF98;color:#fff;padding:6px 12px;min-height:22px;border-radius:4px}QPushButton:hover{background-color:#3E8070}QPushButton:pressed{background-color:#1F5A4F}QLineEdit,QTextEdit#UserInput{background-color:#1A2E36;color:#D4E9E1;border:1px solid #3E8070;border-radius:4px;padding:4px}QTextEdit#ChatDisplay{background-color:#101C20;color:#D4E9E1;border:1px solid #3E8070;border-radius:4px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #3E8070;background:#1A2E36;width:15px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#3E8070;min-height:25px;border-radius:7px}QToolButton{background-color:transparent;border:1px solid #3E8070;color:#88C9B2;border-radius:4px;padding:3px}QToolButton:hover{background-color:rgba(62,128,112,0.5)}QToolButton:checked{background-color:#3E8070;border-color:#6AAF98}QComboBox{background-color:#2C7A6A;border:1px solid #6AAF98;color:#fff;padding:4px 6px;border-radius:4px;min-height:22px}QComboBox QAbstractItemView{background-color:#1A2E36;color:#D4E9E1;selection-background-color:#3E8070;border:1px solid #3E8070}QSlider::groove:horizontal{border:1px solid #6AAF98;background:#1A2E36;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#6AAF98;border:1px solid #D4E9E1;width:16px;margin:-5px 0;border-radius:8px}QStatusBar{background-color:#0F2027;color:#88C9B2;border-top:1px solid #203A43}QLabel#CameraLabel{background-color:#0A1014;border:1px solid #3E8070}QMenuBar{background-color:#0F2027;color:#88C9B2}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#203A43}QMenu{background-color:#1A2E36;color:#D4E9E1;border:1px solid #3E8070}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#2C7A6A;color:white}""",
    "Crimson Nightfall": """QWidget{font-family:'Roboto',sans-serif;font-size:9pt;color:#FADBD8}QMainWindow,QGroupBox{background-color:qlineargradient(spread:pad,x1:1,y1:0,x2:0,y2:1,stop:0 #4A0000,stop:0.5 #800000,stop:1 #4A0000)}QGroupBox{border:1px solid #C0392B;border-radius:5px;margin-top:12px;padding:10px 5px 5px 5px;background-color:rgba(255,255,255,0.05)}QGroupBox::title{color:#F5B7B1;background:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#A93226;border:1px solid #E6B0AA;color:#fff;padding:7px 13px;min-height:23px;border-radius:4px}QPushButton:hover{background-color:#C0392B}QPushButton:pressed{background-color:#922B21}QLineEdit,QTextEdit#UserInput{background-color:#5B2C2C;color:#FADBD8;border:1px solid #C0392B;border-radius:4px;padding:4px}QTextEdit#ChatDisplay{background-color:#3E1F1F;color:#FADBD8;border:1px solid #C0392B;border-radius:4px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #C0392B;background:#5B2C2C;width:15px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#C0392B;min-height:25px;border-radius:7px}QToolButton{background-color:transparent;border:1px solid #C0392B;color:#F5B7B1;border-radius:4px;padding:3px}QToolButton:hover{background-color:rgba(192,57,43,0.5)}QToolButton:checked{background-color:#C0392B;border-color:#E6B0AA}QComboBox{background-color:#A93226;border:1px solid #E6B0AA;color:#fff;padding:4px 6px;border-radius:4px;min-height:23px}QComboBox QAbstractItemView{background-color:#5B2C2C;color:#FADBD8;selection-background-color:#C0392B;border:1px solid #C0392B}QSlider::groove:horizontal{border:1px solid #E6B0AA;background:#5B2C2C;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#E6B0AA;border:1px solid #FADBD8;width:16px;margin:-5px 0;border-radius:8px}QStatusBar{background-color:#4A0000;color:#F5B7B1;border-top:1px solid #800000}QLabel#CameraLabel{background-color:#2C0E0E;border:1px solid #C0392B}QMenuBar{background-color:#4A0000;color:#F5B7B1}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#800000}QMenu{background-color:#5B2C2C;color:#FADBD8;border:1px solid #C0392B}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#A93226;color:white}""",
    "Golden Amethyst": """QWidget{font-family:'Lato',sans-serif;font-size:10pt;color:#EAE0F7}QMainWindow,QGroupBox{background-color:qlineargradient(spread:pad,x1:0,y1:1,x2:1,y2:0,stop:0 #4A148C,stop:0.5 #FFB300,stop:1 #8E24AA)}QGroupBox{border:1px solid #CE93D8;border-radius:6px;margin-top:12px;padding:12px 6px 6px 6px;background-color:rgba(0,0,0,0.15)}QGroupBox::title{color:#F3E5F5;background:transparent;padding:0 4px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px;font-weight:bold}QPushButton{background-color:qlineargradient(spread:pad,x1:0,y1:0,x2:1,y2:0,stop:0 #AB47BC,stop:1 #FFC107);border:1px solid #F3E5F5;color:#311B92;padding:8px 15px;min-height:25px;border-radius:5px;font-weight:bold}QPushButton:hover{background-color:qlineargradient(spread:pad,x1:0,y1:0,x2:1,y2:0,stop:0 #BA68C8,stop:1 #FFCA28)}QPushButton:pressed{background-color:qlineargradient(spread:pad,x1:0,y1:0,x2:1,y2:0,stop:0 #8E24AA,stop:1 #FFA000)}QLineEdit,QTextEdit#UserInput{background-color:rgba(49,27,146,0.7);color:#EAE0F7;border:1px solid #CE93D8;border-radius:5px;padding:5px}QTextEdit#ChatDisplay{background-color:rgba(30,10,90,0.8);color:#EAE0F7;border:1px solid #CE93D8;border-radius:5px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #CE93D8;background:rgba(49,27,146,0.7);width:16px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#CE93D8;min-height:28px;border-radius:7px}QToolButton{background-color:transparent;border:1px solid #CE93D8;color:#F3E5F5;border-radius:5px;padding:3px}QToolButton:hover{background-color:rgba(171,71,188,0.5)}QToolButton:checked{background-color:#AB47BC;border-color:#F3E5F5}QComboBox{background-color:#AB47BC;border:1px solid #F3E5F5;color:#fff;padding:5px 7px;border-radius:5px;min-height:25px}QComboBox QAbstractItemView{background-color:#4A148C;color:#EAE0F7;selection-background-color:#AB47BC;border:1px solid #CE93D8}QSlider::groove:horizontal{border:1px solid #CE93D8;background:rgba(49,27,146,0.7);height:10px;border-radius:5px}QSlider::handle:horizontal{background:#FFC107;border:2px solid #4A148C;width:18px;margin:-5px 0;border-radius:9px}QStatusBar{background-color:#311B92;color:#FFB300;border-top:1px solid #6A1B9A}QLabel#CameraLabel{background-color:#2A0A4F;border:1px solid #CE93D8}QMenuBar{background-color:#311B92;color:#FFB300}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#6A1B9A}QMenu{background-color:#4A148C;color:#EAE0F7;border:1px solid #CE93D8}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#AB47BC;color:white}""",
    "Mystic Forest": """QWidget{font-family:'Georgia',serif;font-size:10pt;color:#E8F5E9}QMainWindow,QGroupBox{background-color:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #004D40,stop:1 #00796B)}QGroupBox{border:1px solid #4DB6AC;border-radius:6px;margin-top:12px;padding:12px 6px 6px 6px;background-color:rgba(0,0,0,0.2)}QGroupBox::title{color:#A7FFEB;background:transparent;padding:0 4px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px;font-style:italic}QPushButton{background-color:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #26A69A,stop:1 #00796B);border:1px solid #80CBC4;color:#E8F5E9;padding:7px 14px;min-height:24px;border-radius:4px}QPushButton:hover{background-color:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #4DB6AC,stop:1 #26A69A)}QPushButton:pressed{background-color:#00695C}QLineEdit,QTextEdit#UserInput{background-color:rgba(0,77,64,0.6);color:#E8F5E9;border:1px solid #4DB6AC;border-radius:4px;padding:5px}QTextEdit#ChatDisplay{background-color:rgba(0,50,40,0.7);color:#E8F5E9;border:1px solid #4DB6AC;border-radius:4px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #4DB6AC;background:rgba(0,77,64,0.6);width:16px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#4DB6AC;min-height:28px;border-radius:7px}QToolButton{background-color:transparent;border:1px solid #4DB6AC;color:#A7FFEB;border-radius:4px;padding:3px}QToolButton:hover{background-color:rgba(77,182,172,0.4)}QToolButton:checked{background-color:#26A69A;border-color:#80CBC4}QComboBox{background-color:#26A69A;border:1px solid #80CBC4;color:#E8F5E9;padding:5px 7px;border-radius:4px;min-height:24px}QComboBox QAbstractItemView{background-color:#004D40;color:#E8F5E9;selection-background-color:#26A69A;border:1px solid #4DB6AC}QSlider::groove:horizontal{border:1px solid #4DB6AC;background:rgba(0,77,64,0.6);height:10px;border-radius:5px}QSlider::handle:horizontal{background:#80CBC4;border:1px solid #E8F5E9;width:18px;margin:-5px 0;border-radius:9px}QStatusBar{background-color:#004D40;color:#A7FFEB;border-top:1px solid #00796B}QLabel#CameraLabel{background-color:#00251A;border:1px solid #4DB6AC}QMenuBar{background-color:#004D40;color:#A7FFEB}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#00695C}QMenu{background-color:#00695C;color:#E8F5E9;border:1px solid #4DB6AC}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#26A69A;color:white}""",
    "Classic Dark": """QWidget{background-color:#2e2e2e;color:#e0e0e0;font-family:Segoe UI,sans-serif;font-size:9pt}QMainWindow,QGroupBox{background-color:#2e2e2e}QGroupBox{border:1px solid #444;border-radius:4px;margin-top:12px;padding:10px 5px 5px 5px}QGroupBox::title{color:#00aaff;background-color:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#3c3c3c;border:1px solid #555;padding:6px 10px;min-height:20px;border-radius:3px}QPushButton:hover{background-color:#4a4a4a}QPushButton:pressed{background-color:#222}QPushButton:disabled{background-color:#333;color:#777}QLineEdit,QTextEdit#UserInput{background-color:#383838;color:#e0e0e0;border:1px solid #555;border-radius:3px;padding:4px}QTextEdit#ChatDisplay{background-color:#222222;color:#e0e0e0;border:1px solid #444;border-radius:3px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #444;background:#383838;width:15px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#555;min-height:25px;border-radius:6px}QToolButton{background-color:#3c3c3c;border:1px solid #555;border-radius:3px;padding:3px}QToolButton:hover{background-color:#4a4a4a}QToolButton:checked{background-color:#007acc;border-color:#005c99}QComboBox{background-color:#3c3c3c;border:1px solid #555;padding:4px 5px;border-radius:3px;min-height:22px}QComboBox::drop-down{border-left:1px solid #555}QComboBox QAbstractItemView{background-color:#383838;color:#e0e0e0;selection-background-color:#007acc;border:1px solid #555}QSlider::groove:horizontal{border:1px solid #444;background:#222;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#007acc;border:1px solid #005c99;width:14px;margin:-4px 0;border-radius:7px}QStatusBar{background-color:#222;color:#e0e0e0}QLabel#CameraLabel{background-color:black;border:1px solid #555}QMenuBar{background-color:#383838;color:#e0e0e0}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#555}QMenu{background-color:#3c3c3c;border:1px solid #555;color:#e0e0e0}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#007acc;color:white}""",
    "Minty Fresh": """QWidget{background-color:#E0F2F1;color:#004D40;font-family:Verdana,sans-serif;font-size:9pt}QMainWindow,QGroupBox{background-color:#E0F2F1}QGroupBox{border:1px solid #A7FFEB;border-radius:4px;margin-top:12px;padding:10px 5px 5px 5px}QGroupBox::title{color:#00796B;background:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#A7FFEB;border:1px solid #26A69A;color:#004D40;padding:6px 10px;min-height:20px;border-radius:3px}QPushButton:hover{background-color:#80CBC4}QPushButton:pressed{background-color:#26A69A}QLineEdit,QTextEdit#UserInput{background-color:#FFFFFF;color:#004D40;border:1px solid #B2DFDB;border-radius:3px;padding:4px}QTextEdit#ChatDisplay{background-color:#F0FAF9;color:#004D40;border:1px solid #B2DFDB;border-radius:3px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #B2DFDB;background:#E0F2F1;width:15px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#80CBC4;min-height:25px;border-radius:6px}QToolButton{background-color:#A7FFEB;border:1px solid #26A69A;color:#004D40;border-radius:3px;padding:3px}QToolButton:hover{background-color:#80CBC4}QToolButton:checked{background-color:#26A69A;border-color:#00796B}QComboBox{background-color:#A7FFEB;border:1px solid #26A69A;color:#004D40;padding:4px 5px;border-radius:3px;min-height:22px}QComboBox QAbstractItemView{background-color:#FFFFFF;color:#004D40;selection-background-color:#80CBC4;border:1px solid #B2DFDB}QSlider::groove:horizontal{border:1px solid #B2DFDB;background:#FFFFFF;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#00796B;border:1px solid #004D40;width:14px;margin:-4px 0;border-radius:7px}QStatusBar{background-color:#B2DFDB;color:#004D40}QLabel#CameraLabel{background-color:#004D40;border:1px solid #80CBC4}QMenuBar{background-color:#B2DFDB;color:#004D40}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#80CBC4}QMenu{background-color:#E0F2F1;border:1px solid #A7FFEB;color:#004D40}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#00796B;color:white}""",
    "Ocean Blue": """QWidget{background-color:#E1F5FE;color:#01579B;font-family:Calibri,sans-serif;font-size:10pt}QMainWindow,QGroupBox{background-color:#E1F5FE}QGroupBox{border:1px solid #81D4FA;border-radius:4px;margin-top:12px;padding:10px 5px 5px 5px}QGroupBox::title{color:#0277BD;background:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#81D4FA;border:1px solid #03A9F4;color:#01579B;padding:6px 10px;min-height:20px;border-radius:3px}QPushButton:hover{background-color:#4FC3F7}QPushButton:pressed{background-color:#039BE5}QLineEdit,QTextEdit#UserInput{background-color:#FFFFFF;color:#01579B;border:1px solid #B3E5FC;border-radius:3px;padding:4px}QTextEdit#ChatDisplay{background-color:#F0FAFD;color:#01579B;border:1px solid #B3E5FC;border-radius:3px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #B3E5FC;background:#E1F5FE;width:15px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#4FC3F7;min-height:25px;border-radius:6px}QToolButton{background-color:#81D4FA;border:1px solid #03A9F4;color:#01579B;border-radius:3px;padding:3px}QToolButton:hover{background-color:#4FC3F7}QToolButton:checked{background-color:#039BE5;border-color:#0277BD}QComboBox{background-color:#81D4FA;border:1px solid #03A9F4;color:#01579B;padding:4px 5px;border-radius:3px;min-height:22px}QComboBox QAbstractItemView{background-color:#FFFFFF;color:#01579B;selection-background-color:#4FC3F7;border:1px solid #B3E5FC}QSlider::groove:horizontal{border:1px solid #B3E5FC;background:#FFFFFF;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#0288D1;border:1px solid #01579B;width:14px;margin:-4px 0;border-radius:7px}QStatusBar{background-color:#B3E5FC;color:#01579B}QLabel#CameraLabel{background-color:#01579B;border:1px solid #4FC3F7}QMenuBar{background-color:#B3E5FC;color:#01579B}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#81D4FA}QMenu{background-color:#E1F5FE;border:1px solid #81D4FA;color:#01579B}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#0288D1;color:white}""",
    "Ubuntu Ambiance": """QWidget{background-color:#3D3836;color:#F2F1F0;font-family:Ubuntu,sans-serif;font-size:10pt}QMainWindow,QGroupBox{background-color:#3D3836}QGroupBox{border:1px solid #5A514E;border-radius:4px;margin-top:12px;padding:10px 5px 5px 5px}QGroupBox::title{color:#DD4814;background:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#5A514E;border:1px solid #776B67;color:#F2F1F0;padding:6px 10px;min-height:20px;border-radius:3px}QPushButton:hover{background-color:#6C605C}QPushButton:pressed{background-color:#4E4540}QLineEdit,QTextEdit#UserInput{background-color:#4E4540;color:#F2F1F0;border:1px solid #776B67;border-radius:3px;padding:4px}QTextEdit#ChatDisplay{background-color:#302B29;color:#F2F1F0;border:1px solid #5A514E;border-radius:3px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #5A514E;background:#4E4540;width:15px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#776B67;min-height:25px;border-radius:6px}QToolButton{background-color:#5A514E;border:1px solid #776B67;color:#F2F1F0;border-radius:3px;padding:3px}QToolButton:hover{background-color:#6C605C}QToolButton:checked{background-color:#DD4814;border-color:#C33E0F}QComboBox{background-color:#5A514E;border:1px solid #776B67;color:#F2F1F0;padding:4px 5px;border-radius:3px;min-height:22px}QComboBox QAbstractItemView{background-color:#4E4540;color:#F2F1F0;selection-background-color:#DD4814;border:1px solid #776B67}QSlider::groove:horizontal{border:1px solid #776B67;background:#302B29;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#DD4814;border:1px solid #C33E0F;width:14px;margin:-4px 0;border-radius:7px}QStatusBar{background-color:#302B29;color:#F2F1F0}QLabel#CameraLabel{background-color:#1E1A18;border:1px solid #776B67}QMenuBar{background-color:#302B29;color:#F2F1F0}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#5A514E}QMenu{background-color:#3D3836;border:1px solid #5A514E;color:#F2F1F0}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#DD4814;color:white}""",
    "Forest Green": """QWidget{background-color:#E8F5E9;color:#1B5E20;font-family:Arial,sans-serif}QMainWindow,QGroupBox{background-color:#E8F5E9}QGroupBox{border:1px solid #A5D6A7;border-radius:4px;margin-top:12px;padding:10px 5px 5px 5px}QGroupBox::title{color:#2E7D32;background:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#A5D6A7;border:1px solid #388E3C;color:#1B5E20;padding:6px 10px;min-height:20px;border-radius:3px}QPushButton:hover{background-color:#81C784}QPushButton:pressed{background-color:#66BB6A}QLineEdit,QTextEdit#UserInput{background-color:#FFFFFF;color:#1B5E20;border:1px solid #C8E6C9;border-radius:3px;padding:4px}QTextEdit#ChatDisplay{background-color:#F1F8E9;color:#1B5E20;border:1px solid #C8E6C9;border-radius:3px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #C8E6C9;background:#E8F5E9;width:15px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#81C784;min-height:25px;border-radius:6px}QToolButton{background-color:#A5D6A7;border:1px solid #388E3C;color:#1B5E20;border-radius:3px;padding:3px}QToolButton:hover{background-color:#81C784}QToolButton:checked{background-color:#66BB6A;border-color:#2E7D32}QComboBox{background-color:#A5D6A7;border:1px solid #388E3C;color:#1B5E20;padding:4px 5px;border-radius:3px;min-height:22px}QComboBox QAbstractItemView{background-color:#FFFFFF;color:#1B5E20;selection-background-color:#81C784;border:1px solid #C8E6C9}QSlider::groove:horizontal{border:1px solid #C8E6C9;background:#FFFFFF;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#4CAF50;border:1px solid #2E7D32;width:14px;margin:-4px 0;border-radius:7px}QStatusBar{background-color:#C8E6C9;color:#1B5E20}QLabel#CameraLabel{background-color:#1B5E20;border:1px solid #81C784}QMenuBar{background-color:#C8E6C9;color:#1B5E20}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#A5D6A7}QMenu{background-color:#E8F5E9;border:1px solid #A5D6A7;color:#1B5E20}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#4CAF50;color:white}""",
    "Royal Purple": """QWidget{background-color:#EDE7F6;color:#4527A0;font-family:Georgia,serif}QMainWindow,QGroupBox{background-color:#EDE7F6}QGroupBox{border:1px solid #B39DDB;border-radius:4px;margin-top:12px;padding:10px 5px 5px 5px}QGroupBox::title{color:#5E35B1;background:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#B39DDB;border:1px solid #673AB7;color:#EDE7F6;padding:6px 10px;min-height:20px;border-radius:3px}QPushButton:hover{background-color:#9575CD}QPushButton:pressed{background-color:#7E57C2}QLineEdit,QTextEdit#UserInput{background-color:#FFFFFF;color:#4527A0;border:1px solid #D1C4E9;border-radius:3px;padding:4px}QTextEdit#ChatDisplay{background-color:#F8F5FA;color:#4527A0;border:1px solid #D1C4E9;border-radius:3px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #D1C4E9;background:#EDE7F6;width:15px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#9575CD;min-height:25px;border-radius:6px}QToolButton{background-color:#B39DDB;border:1px solid #673AB7;color:#EDE7F6;border-radius:3px;padding:3px}QToolButton:hover{background-color:#9575CD}QToolButton:checked{background-color:#7E57C2;border-color:#5E35B1}QComboBox{background-color:#B39DDB;border:1px solid #673AB7;color:#EDE7F6;padding:4px 5px;border-radius:3px;min-height:22px}QComboBox QAbstractItemView{background-color:#FFFFFF;color:#4527A0;selection-background-color:#9575CD;border:1px solid #D1C4E9}QSlider::groove:horizontal{border:1px solid #D1C4E9;background:#FFFFFF;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#7E57C2;border:1px solid #5E35B1;width:14px;margin:-4px 0;border-radius:7px}QStatusBar{background-color:#D1C4E9;color:#4527A0}QLabel#CameraLabel{background-color:#311B92;border:1px solid #9575CD}QMenuBar{background-color:#D1C4E9;color:#4527A0}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#B39DDB}QMenu{background-color:#EDE7F6;border:1px solid #B39DDB;color:#4527A0}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#7E57C2;color:white}""",
    "Warm Orange": """QWidget{background-color:#FFF3E0;color:#E65100;font-family:Tahoma,sans-serif}QMainWindow,QGroupBox{background-color:#FFF3E0}QGroupBox{border:1px solid #FFB74D;border-radius:4px;margin-top:12px;padding:10px 5px 5px 5px}QGroupBox::title{color:#F57C00;background:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#FFB74D;border:1px solid #FF9800;color:#E65100;padding:6px 10px;min-height:20px;border-radius:3px}QPushButton:hover{background-color:#FFA726}QPushButton:pressed{background-color:#FB8C00}QLineEdit,QTextEdit#UserInput{background-color:#FFFFFF;color:#E65100;border:1px solid #FFE0B2;border-radius:3px;padding:4px}QTextEdit#ChatDisplay{background-color:#FFF8F0;color:#E65100;border:1px solid #FFE0B2;border-radius:3px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #FFE0B2;background:#FFF3E0;width:15px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#FFA726;min-height:25px;border-radius:6px}QToolButton{background-color:#FFB74D;border:1px solid #FF9800;color:#E65100;border-radius:3px;padding:3px}QToolButton:hover{background-color:#FFA726}QToolButton:checked{background-color:#FB8C00;border-color:#F57C00}QComboBox{background-color:#FFB74D;border:1px solid #FF9800;color:#E65100;padding:4px 5px;border-radius:3px;min-height:22px}QComboBox QAbstractItemView{background-color:#FFFFFF;color:#E65100;selection-background-color:#FFA726;border:1px solid #FFE0B2}QSlider::groove:horizontal{border:1px solid #FFE0B2;background:#FFFFFF;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#FB8C00;border:1px solid #F57C00;width:14px;margin:-4px 0;border-radius:7px}QStatusBar{background-color:#FFE0B2;color:#E65100}QLabel#CameraLabel{background-color:#BF360C;border:1px solid #FFA726}QMenuBar{background-color:#FFE0B2;color:#E65100}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#FFB74D}QMenu{background-color:#FFF3E0;border:1px solid #FFB74D;color:#E65100}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#FB8C00;color:white}""",
    "Charcoal Gray": """QWidget{background-color:#37474F;color:#ECEFF1;font-family:Helvetica,sans-serif}QMainWindow,QGroupBox{background-color:#37474F}QGroupBox{border:1px solid #546E7A;border-radius:4px;margin-top:12px;padding:10px 5px 5px 5px}QGroupBox::title{color:#90A4AE;background:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#546E7A;border:1px solid #78909C;color:#ECEFF1;padding:6px 10px;min-height:20px;border-radius:3px}QPushButton:hover{background-color:#607D8B}QPushButton:pressed{background-color:#455A64}QLineEdit,QTextEdit#UserInput{background-color:#455A64;color:#ECEFF1;border:1px solid #78909C;border-radius:3px;padding:4px}QTextEdit#ChatDisplay{background-color:#263238;color:#ECEFF1;border:1px solid #546E7A;border-radius:3px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #546E7A;background:#455A64;width:15px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#78909C;min-height:25px;border-radius:6px}QToolButton{background-color:#546E7A;border:1px solid #78909C;color:#ECEFF1;border-radius:3px;padding:3px}QToolButton:hover{background-color:#607D8B}QToolButton:checked{background-color:#78909C;border-color:#90A4AE}QComboBox{background-color:#546E7A;border:1px solid #78909C;color:#ECEFF1;padding:4px 5px;border-radius:3px;min-height:22px}QComboBox QAbstractItemView{background-color:#455A64;color:#ECEFF1;selection-background-color:#78909C;border:1px solid #78909C}QSlider::groove:horizontal{border:1px solid #78909C;background:#263238;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#78909C;border:1px solid #90A4AE;width:14px;margin:-4px 0;border-radius:7px}QStatusBar{background-color:#263238;color:#ECEFF1}QLabel#CameraLabel{background-color:#102027;border:1px solid #78909C}QMenuBar{background-color:#263238;color:#ECEFF1}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#455A64}QMenu{background-color:#37474F;border:1px solid #546E7A;color:#ECEFF1}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#546E7A;color:white}""",
    "Ruby Red": """QWidget{background-color:#FFEBEE;color:#B71C1C;font-family:Times New Roman,serif}QMainWindow,QGroupBox{background-color:#FFEBEE}QGroupBox{border:1px solid #FFCDD2;border-radius:4px;margin-top:12px;padding:10px 5px 5px 5px}QGroupBox::title{color:#D32F2F;background:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#FFCDD2;border:1px solid #E57373;color:#B71C1C;padding:6px 10px;min-height:20px;border-radius:3px}QPushButton:hover{background-color:#EF9A9A}QPushButton:pressed{background-color:#E57373}QLineEdit,QTextEdit#UserInput{background-color:#FFFFFF;color:#B71C1C;border:1px solid #FFCDD2;border-radius:3px;padding:4px}QTextEdit#ChatDisplay{background-color:#FFF5F5;color:#B71C1C;border:1px solid #FFCDD2;border-radius:3px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #FFCDD2;background:#FFEBEE;width:15px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#EF9A9A;min-height:25px;border-radius:6px}QToolButton{background-color:#FFCDD2;border:1px solid #E57373;color:#B71C1C;border-radius:3px;padding:3px}QToolButton:hover{background-color:#EF9A9A}QToolButton:checked{background-color:#E57373;border-color:#D32F2F}QComboBox{background-color:#FFCDD2;border:1px solid #E57373;color:#B71C1C;padding:4px 5px;border-radius:3px;min-height:22px}QComboBox QAbstractItemView{background-color:#FFFFFF;color:#B71C1C;selection-background-color:#EF9A9A;border:1px solid #FFCDD2}QSlider::groove:horizontal{border:1px solid #FFCDD2;background:#FFFFFF;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#F44336;border:1px solid #C62828;width:14px;margin:-4px 0;border-radius:7px}QStatusBar{background-color:#FFCDD2;color:#B71C1C}QLabel#CameraLabel{background-color:#7f0000;border:1px solid #EF9A9A}QMenuBar{background-color:#FFCDD2;color:#B71C1C}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#EF9A9A}QMenu{background-color:#FFEBEE;border:1px solid #FFCDD2;color:#B71C1C}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#F44336;color:white}""",
    "Sapphire Blue": """QWidget{background-color:#E3F2FD;color:#0D47A1;font-family:Arial,sans-serif}QMainWindow,QGroupBox{background-color:#E3F2FD}QGroupBox{border:1px solid #90CAF9;border-radius:4px;margin-top:12px;padding:10px 5px 5px 5px}QGroupBox::title{color:#1976D2;background:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#90CAF9;border:1px solid #42A5F5;color:#0D47A1;padding:6px 10px;min-height:20px;border-radius:3px}QPushButton:hover{background-color:#64B5F6}QPushButton:pressed{background-color:#42A5F5}QLineEdit,QTextEdit#UserInput{background-color:#FFFFFF;color:#0D47A1;border:1px solid #BBDEFB;border-radius:3px;padding:4px}QTextEdit#ChatDisplay{background-color:#F0F7FF;color:#0D47A1;border:1px solid #BBDEFB;border-radius:3px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #BBDEFB;background:#E3F2FD;width:15px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#64B5F6;min-height:25px;border-radius:6px}QToolButton{background-color:#90CAF9;border:1px solid #42A5F5;color:#0D47A1;border-radius:3px;padding:3px}QToolButton:hover{background-color:#64B5F6}QToolButton:checked{background-color:#42A5F5;border-color:#1976D2}QComboBox{background-color:#90CAF9;border:1px solid #42A5F5;color:#0D47A1;padding:4px 5px;border-radius:3px;min-height:22px}QComboBox QAbstractItemView{background-color:#FFFFFF;color:#0D47A1;selection-background-color:#64B5F6;border:1px solid #BBDEFB}QSlider::groove:horizontal{border:1px solid #BBDEFB;background:#FFFFFF;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#2196F3;border:1px solid #1565C0;width:14px;margin:-4px 0;border-radius:7px}QStatusBar{background-color:#BBDEFB;color:#0D47A1}QLabel#CameraLabel{background-color:#0D47A1;border:1px solid #64B5F6}QMenuBar{background-color:#BBDEFB;color:#0D47A1}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#90CAF9}QMenu{background-color:#E3F2FD;border:1px solid #90CAF9;color:#0D47A1}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#2196F3;color:white}""",
    "Volcanic Ash": """QWidget{background-color:#424242;color:#FAFAFA;font-family:Consolas,monospace}QMainWindow,QGroupBox{background-color:#424242}QGroupBox{border:1px solid #616161;border-radius:3px;margin-top:12px;padding:10px 5px 5px 5px}QGroupBox::title{color:#BDBDBD;background:transparent;padding:0 3px;subcontrol-origin:margin;subcontrol-position:top left;left:10px;bottom:13px}QPushButton{background-color:#616161;border:1px solid #757575;color:#FAFAFA;padding:6px 10px;min-height:20px;border-radius:3px}QPushButton:hover{background-color:#757575}QPushButton:pressed{background-color:#424242}QLineEdit,QTextEdit#UserInput{background-color:#303030;color:#FAFAFA;border:1px solid #616161;border-radius:3px;padding:4px;selection-background-color:#757575}QTextEdit#ChatDisplay{background-color:#212121;color:#FAFAFA;border:1px solid #424242;border-radius:3px}QTextEdit#ChatDisplay QScrollBar:vertical{border:1px solid #424242;background:#303030;width:15px;margin:1px 0px 1px 0px}QTextEdit#ChatDisplay QScrollBar::handle:vertical{background:#616161;min-height:25px;border-radius:6px}QToolButton{background-color:#616161;border:1px solid #757575;color:#FAFAFA;border-radius:3px;padding:3px}QToolButton:hover{background-color:#757575}QToolButton:checked{background-color:#757575;border-color:#BDBDBD}QComboBox{background-color:#616161;border:1px solid #757575;color:#FAFAFA;padding:4px 5px;border-radius:3px;min-height:22px}QComboBox QAbstractItemView{background-color:#303030;color:#FAFAFA;selection-background-color:#757575;border:1px solid #616161}QSlider::groove:horizontal{border:1px solid #616161;background:#212121;height:8px;border-radius:4px}QSlider::handle:horizontal{background:#9E9E9E;border:1px solid #BDBDBD;width:14px;margin:-4px 0;border-radius:7px}QStatusBar{background-color:#212121;color:#FAFAFA}QLabel#CameraLabel{background-color:#000000;border:1px solid #616161}QMenuBar{background-color:#212121;color:#FAFAFA}QMenuBar::item{padding:4px 8px}QMenuBar::item:selected{background-color:#424242}QMenu{background-color:#424242;border:1px solid #616161;color:#FAFAFA}QMenu::item{padding:4px 20px}QMenu::item:selected{background-color:#616161;color:white}"""
}

# --- CHAT_STYLES and Message Templates ---
CHAT_STYLES: Dict[str, str] = {
    "user_name_color": "#82adda",  # Light blue for user name (if used)
    "robot_name_color": "#8AE234",  # Bright green for robot name
    "timestamp_color_light": "#777777",  # Timestamp color for light themes
    "timestamp_color_dark": "#9e9e9e",  # Timestamp color for dark themes
    "error_color": "#FF6B6B",  # Bright red for error text
    "correction_color": "#FFD166",  # Yellow/Orange for corrections
    "info_color": "#82EEFD",  # Cyan for info messages
    "suggestion_color": "#CDB4DB",  # Lavender for suggestions
    "context_color": "#b0b0b0",  # Grey for context/original text
    "warning_color": "#FFA500",  # Orange for warning text

    # Theme-dependent colors (will be updated by _update_chat_colors)
    "default_text_color_light": "#1e1e1e",  # Default text on light backgrounds
    "default_text_color_dark": "#e0e0e0",  # Default text on dark backgrounds
    "user_bg_color_light": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e9f5f7, stop:1 #d7efe2)",
    "robot_bg_color_light": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f5f5f5, stop:1 #eef1f5)",
    "user_bg_color_dark": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2c3e50, stop:1 #34495e)",
    "robot_bg_color_dark": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #212f3c, stop:1 #283747)",
    "error_bg_color_light": "#ffebee",  # Light red background for error bubbles
    "error_bg_color_dark": "#5e3232",  # Dark red background for error bubbles
    "user_border_light": "#b2dfdb",  # Border for user bubble on light themes
    "robot_border_light": "#dcedc8",  # Border for robot bubble on light themes
    "user_border_dark": "#475a70",  # Border for user bubble on dark themes
    "robot_border_dark": "#3a4c5f",  # Border for robot bubble on dark themes
    "error_border_color_light": "#ef9a9a",
    "error_border_color_dark": "#a15151",

    # 'current_' values are dynamically set based on active theme in _update_chat_colors
    "current_text_color": "#1e1e1e",
    "current_user_bg": "#e9f5f7",
    "current_robot_bg": "#f5f5f5",
    "current_error_bg": "#ffebee",
    "current_user_border": "#b2dfdb",
    "current_robot_border": "#dcedc8",
    "current_error_border_color": "#ef9a9a",
    "current_timestamp_color": "#777777"
}
COMMON_BUBBLE_STYLE: str = ("max-width:78%;padding:10px 14px;border-radius:18px;"
                            "margin-bottom:10px;line-height:1.45;"
                            "box-shadow:1px 1px 3px rgba(0,0,0,0.1);")
USER_MSG_TEMPLATE: str = (
    '<div style="display:flex;justify-content:flex-end;margin-right:8px;">'
    '<div style="background-color:{bg_color};border:1px solid {border_color};'
    '{common_style} border-bottom-right-radius:5px;">'
    '<div style="color:{text_color};word-wrap:break-word;font-size:{font_size}pt;">'
    '{message_html}</div>'
    '<div style="text-align:right;font-size:{timestamp_font_size}pt;'
    'color:{timestamp_color};padding-top:5px;">{timestamp}</div></div></div>')
ROBOT_MSG_TEMPLATE: str = (
    '<div style="display:flex;justify-content:flex-start;margin-left:8px;">'
    '<div style="background-color:{bg_color};border:1px solid {border_color};'
    '{common_style} border-bottom-left-radius:5px;">'
    '<strong style="color:{name_color};font-size:{font_size_plus_one}pt;'
    'display:block;margin-bottom:3px;">{robot_name}:</strong>'
    '<div style="color:{text_color};word-wrap:break-word;font-size:{font_size}pt;">'
    '{message_html}</div>'
    '<div style="text-align:right;font-size:{timestamp_font_size}pt;'
    'color:{timestamp_color};padding-top:5px;">{timestamp}</div></div></div>')
SYSTEM_MSG_TEMPLATE: str = (
    '<div style="text-align:center;margin:8px 5px;padding:5px;">'
    '<em style="font-size:{timestamp_font_size}pt;color:{timestamp_color};">'
    '{message_html} ({timestamp})</em></div>')
ERROR_MSG_TEMPLATE: str = (
    '<div style="display:flex;justify-content:center;margin:8px;">'
    '<div style="background-color:{bg_color};border:1px solid {error_border_color};'
    '{common_style} border-radius:12px;padding:12px;max-width:88%;">'
    '<strong style="display:block;margin-bottom:4px;font-size:{font_size_plus_one}pt;'
    'color:{error_title_color};">System Error:</strong>'
    '<div style="color:{error_text_color};word-wrap:break-word;font-size:{font_size}pt;">'
    '{message_html}</div>'
    '<div style="text-align:right;font-size:{timestamp_font_size}pt;'
    'color:{timestamp_color};padding-top:5px;">{timestamp}</div></div></div>')

# --- Global Variables for Conditional Import Status ---
# These track if real external modules loaded successfully.
MODULE_IMPORTS_OK: bool = True
MISSING_MODULES: List[str] = []


# --- Helper Function for Conditional Imports ---
def _try_import(module_name: str,
                items_to_import: List[str],
                file_hint: str) -> Tuple[Optional[Dict[str, Type]], bool]:
    """
    Attempts to import specified items from a Python module.

    This function tries to import a list of classes or functions (`items_to_import`)
    from a given `module_name`. It updates global flags (`MODULE_IMPORTS_OK`, `MISSING_MODULES`)
    based on the success or failure of these imports. It's used to gracefully handle
    missing optional external dependencies by allowing the application to fall back
    to dummy implementations.

    Args:
        module_name: The name of the module to import (e.g., "emotion_engine").
        items_to_import: A list of strings, where each string is the name of an
                         item (class, function) to import from the module.
        file_hint: A string (usually the filename like "emotion_engine.py") used
                   for logging messages to help the user identify missing files.

    Returns:
        A tuple containing:
        - A dictionary where keys are item names and values are the imported
          class/function types if ALL items were successfully imported. Returns None otherwise.
        - A boolean indicating True if ALL items were successfully imported, False otherwise.
    """
    global MODULE_IMPORTS_OK, MISSING_MODULES
    imported_items: Dict[str, Type] = {}
    all_items_found_in_module = True
    module_successfully_imported = False

    try:
        module = __import__(module_name, fromlist=items_to_import)
        module_successfully_imported = True
        for item_name in items_to_import:
            if hasattr(module, item_name):
                imported_items[item_name] = getattr(module, item_name)
                logger.info(f"Successfully imported REAL '{item_name}' from '{file_hint}'.")
            else:
                logger.error(f"Failed to find REAL item '{item_name}' within imported module "
                             f"'{module_name}' (expected in '{file_hint}').")
                all_items_found_in_module = False

        if not all_items_found_in_module:
            if file_hint not in MISSING_MODULES:
                MISSING_MODULES.append(f"{file_hint} (item missing within module)")
            MODULE_IMPORTS_OK = False  # Mark as not okay if even one item is missing

        # Return successfully imported items only if all requested items were found
        return imported_items if all_items_found_in_module and imported_items else None, \
            all_items_found_in_module and bool(imported_items)

    except ImportError as e:
        logger.error(f"Failed to import REAL module '{module_name}' (expected in '{file_hint}'): {e}")
        MODULE_IMPORTS_OK = False
        if file_hint not in MISSING_MODULES:
            MISSING_MODULES.append(file_hint)
        return None, False
    except Exception as e_other:  # Catch any other unexpected errors during import
        logger.error(f"Unexpected error importing REAL module '{module_name}' ('{file_hint}'): {e_other}",
                     exc_info=True)
        MODULE_IMPORTS_OK = False
        if file_hint not in MISSING_MODULES:
            MISSING_MODULES.append(f"{file_hint} (unexpected import error)")
        return None, False


# --- All Dummy Class Definitions (Internal Fallbacks) ---
# These classes are used if their corresponding real external modules cannot be imported.

class BaseWorkerDummy(QObject):
    """Base dummy class for QObject-based workers, providing common signals and logging."""
    error = pyqtSignal(str, str)  # Emits worker_name, error_message
    finished = pyqtSignal()  # Emitted when worker's main task is done (for thread quitting)
    status_update = pyqtSignal(str, int)  # Emits message, timeout_ms for status bar updates

    def __init__(self, name: str = "UnknownWorkerDummy", parent: Optional[QObject] = None):
        """Initializes the base dummy worker."""
        super().__init__(parent)
        self.worker_name: str = name
        logger.warning(f"USING DUMMY: {self.worker_name}. Real module likely missing or failed to load.")

    def log_dummy_call(self, method_name: str, *args: Any) -> None:
        """Logs a call to a dummy method for debugging."""
        args_str = ", ".join(map(repr, args)) if args else ""
        logger.warning(f"DUMMY CALL: {self.worker_name}.{method_name}({args_str}) (No real action taken).")

    def shutdown(self) -> None:
        """Simulates worker shutdown for thread management."""
        self.log_dummy_call("shutdown")
        self.finished.emit()  # Essential for QThread.quit()

    def stop(self) -> None:
        """Simulates stopping the worker's operations (often called by shutdown)."""
        self.log_dummy_call("stop")


class RobotInfoModule_Dummy:
    """Dummy fallback for the Robot Information Module."""

    def __init__(self, dependencies: Optional[Dict[str, Any]] = None):
        """Initializes the dummy RobotInfoModule."""
        logger.warning("USING DUMMY: RobotInfoModule (provides static information).")
        # Args 'dependencies' is kept for interface compatibility with real module.
        _ = dependencies  # Mark as used to satisfy linters
        self.dev_info: Dict[str, str] = {"full_name": "Umar Ibrahim (Dummy)", "id": "062", "title": "Boss"}
        self.robot_info: Dict[str, str] = {"name": f"{APP_NAME_CONST} (Dummy)", "version": f"DUMMY {APP_VERSION_CONST}"}
        self.faq_info: Dict[str, str] = {
            "creator": f"Created by {self.dev_info['full_name']}",
            "name": f"My name is {self.robot_info['name']}"
        }

    def get_information(self, query: str) -> Optional[str]:
        """Provides dummy answers based on the query."""
        self.log_dummy_call("get_information", query)
        q_lower = query.lower()
        if self.dev_info["full_name"].lower() in q_lower and self.dev_info["id"] in q_lower or "boss" in q_lower:
            return f"Greetings, {self.dev_info['title']}! (Dummy Info Response)"
        if "creator" in q_lower: return self.faq_info["creator"]
        if "who are you" in q_lower or "name" in q_lower: return self.faq_info["name"]
        return f"Dummy RobotInfo: I don't have specific information on '{query[:30].strip()}...'."

    def get_robot_info(self) -> Dict[str, str]:
        """Returns basic dummy robot information."""
        self.log_dummy_call("get_robot_info")
        return self.robot_info

    def get_developer_info(self) -> Dict[str, str]:
        """Returns basic dummy developer information."""
        self.log_dummy_call("get_developer_info")
        return self.dev_info

    def log_dummy_call(self, method_name: str, *args: Any) -> None:  # Helper for this dummy
        """Logs a call to a dummy method."""
        args_str = ", ".join(map(repr, args)) if args else ""
        logger.warning(f"DUMMY CALL: RobotInfoModule_Dummy.{method_name}({args_str}).")


class GrammarSystem_Dummy:
    """Dummy fallback for the Grammar System module."""

    def __init__(self, language_code: str = "en-US"):
        """Initializes the dummy GrammarSystem."""
        logger.warning(f"USING DUMMY: GrammarSystem (Language: {language_code}). No grammar checks will be performed.")
        self.lang_code: str = language_code

    def analyze_and_correct(self, text: str) -> Dict[str, Any]:
        """Simulates grammar analysis, returning text انرژی unchanged."""
        self.log_dummy_call("analyze_and_correct", text)
        return {
            "original_text": text, "corrected_text": text, "has_errors": False,
            "suggestions_detail": [], "error_message": "Dummy Grammar System - No checks performed."
        }

    def log_dummy_call(self, method_name: str, *args: Any) -> None:  # Helper for this dummy
        """Logs a call to a dummy method."""
        args_str = ", ".join(map(repr, args)) if args else ""
        logger.warning(f"DUMMY CALL: GrammarSystem_Dummy.{method_name}({args_str}).")


class MultiLangCorrectionModule_Dummy:
    """Dummy fallback for the Multilingual Correction module."""
    SUPPORTED_LANGUAGES: set = {"ha", "zh"}  # Example dummy supported languages

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initializes the dummy MultiLangCorrectionModule."""
        logger.warning("USING DUMMY: EnhancedMultilingualCorrector. Language detection will be basic.")
        self.config: Dict[str, Any] = config if config else {}

    def detect_language_robust(self, text: str) -> str:
        """Simulates language detection, defaulting to English."""
        self.log_dummy_call("detect_language_robust", text)
        if any(char >= '\u0600' and char <= '\u06FF' for char in text):  # Basic Arabic script check for Hausa
            return "ha"
        return "en"  # Default for dummy

    def correct_text(self, text: str, specific_language: Optional[str] = None) -> Dict[str, Any]:
        """Simulates text correction, returning text unchanged."""
        self.log_dummy_call("correct_text", text, specific_language)
        lang_to_use = specific_language or self.detect_language_robust(text)
        unsupported = lang_to_use not in self.SUPPORTED_LANGUAGES and lang_to_use != "en"
        return {
            "original_text": text, "corrected_text": text, "detected_language": lang_to_use,
            "corrections_made": [], "unsupported_language_flag": unsupported,
            "error_message": "Dummy Multilingual Corrector - No corrections performed."
        }

    def log_dummy_call(self, method_name: str, *args: Any) -> None:  # Helper for this dummy
        """Logs a call to a dummy method."""
        args_str = ", ".join(map(repr, args)) if args else ""
        logger.warning(f"DUMMY CALL: MultiLangCorrectionModule_Dummy.{method_name}({args_str}).")


class EmotionWorker_Dummy(BaseWorkerDummy):
    """Dummy fallback for the Emotion Worker."""
    emotion_detected = pyqtSignal(str, float)  # Emits emotion_name, confidence_score

    def __init__(self, parent: Optional[QObject] = None,
                 use_vader_if_available: bool = False,
                 emotion_config: Optional[Dict[str, Any]] = None):
        """Initializes the dummy EmotionWorker."""
        super().__init__("EmotionWorkerDummy", parent)
        # Args are for interface compatibility with real worker
        _ = use_vader_if_available, emotion_config

    @pyqtSlot(str)
    def analyze_text_emotion(self, text: str) -> None:
        """Simulates emotion analysis, emitting a neutral emotion."""
        self.log_dummy_call("analyze_text_emotion", text)
        # Simple heuristic for dummy
        if "happy" in text.lower() or "great" in text.lower():
            self.emotion_detected.emit("happy", 0.75)
        elif "sad" in text.lower() or "bad" in text.lower():
            self.emotion_detected.emit("sad", 0.70)
        else:
            self.emotion_detected.emit("neutral", 0.5)


class RobotAppearanceWidget_Dummy(QWidget):
    """
    Minimal dummy QWidget for Robot Appearance.
    This is the *internal* fallback if the external `robot_appearance.py`
    (which contains the advanced AI version) fails to load.
    """
    request_speak = pyqtSignal(str)  # For interface compatibility

    def __init__(self, parent: Optional[QWidget] = None, **kwargs: Any):
        """Initializes the dummy RobotAppearanceWidget."""
        super().__init__(parent)
        logger.warning(
            "USING INTERNAL DUMMY: RobotAppearanceWidget. Real external 'robot_appearance.py' "
            "(AI version) likely missing, failed to load, or an error occurred during its import."
        )
        _ = kwargs  # Accept arbitrary kwargs for constructor compatibility
        layout = QVBoxLayout(self)
        self.label = QLabel("Robot Appearance (Internal Dummy)\nReal module not loaded.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "background-color:#383838; color:#999999; border:2px dashed #555555; padding:10px;"
            "font-size: 10pt; font-family: Monospace;"
        )
        layout.addWidget(self.label)
        self.setMinimumSize(QSize(200, 150))

    @pyqtSlot(str, float)
    def set_emotion_display(self, emotion_name: str, intensity: float) -> None:
        """Simulates setting the robot's emotion display."""
        self.label.setText(f"Dummy Appearance:\nEmotion: {emotion_name.capitalize()} ({intensity:.1f})")
        logger.debug(f"DUMMY RobotAppearance (Internal): Emotion set to '{emotion_name}', Intensity {intensity:.2f}")

    @pyqtSlot(bool)
    def set_speaking_state(self, is_speaking: bool) -> None:
        """Simulates setting the robot's speaking state."""
        current_text_parts = self.label.text().split('\n')
        emotion_line = current_text_parts[0] if "Emotion:" in current_text_parts[0] else "Dummy Appearance:"
        self.label.setText(f"{emotion_line}\nSpeaking: {'Yes' if is_speaking else 'No'}")
        logger.debug(f"DUMMY RobotAppearance (Internal): Speaking state set to: {is_speaking}")

    def start_appearance_updates(self) -> None:
        """Simulates starting appearance updates."""
        logger.debug("DUMMY RobotAppearance (Internal): start_appearance_updates() called.")

    def stop_appearance_updates(self) -> None:
        """Simulates stopping appearance updates."""
        logger.debug("DUMMY RobotAppearance (Internal): stop_appearance_updates() called.")


class TTSWorker_Dummy(BaseWorkerDummy):
    """Dummy fallback for the Text-to-Speech (TTS) Worker."""
    speech_started = pyqtSignal(str)  # Emits text_being_spoken
    speech_word_boundary = pyqtSignal(str, int, int)  # Emits word, location, length
    speech_finished = pyqtSignal(str)  # Emits spoken_text
    available_voices_signal = pyqtSignal(list)  # Emits list of voice dicts

    def __init__(self, parent: Optional[QObject] = None):
        """Initializes the dummy TTSWorker."""
        super().__init__("TTSWorkerDummy", parent)

    @pyqtSlot()
    def initialize_engine(self) -> None:
        """Simulates TTS engine initialization and emits dummy voice list."""
        self.log_dummy_call("initialize_engine")
        dummy_voices = [
            {'id': 'dummy_voice_en', 'name': 'Dummy English Voice (Fallback)', 'lang': 'en_US', 'gender': 'Neutral'}]
        self.available_voices_signal.emit(dummy_voices)

    @pyqtSlot(str)
    def speak(self, text: str) -> None:
        """Simulates speaking the given text with timed signals."""
        self.log_dummy_call("speak", text)
        self.speech_started.emit(text)
        words = text.split()
        char_pos = 0
        delay_ms_per_word = 200  # Milliseconds per word for simulation
        for i, word_val in enumerate(words):
            word_len = len(word_val)
            # Use lambda with default arguments to capture current values for QTimer
            # This avoids issues with loop variable scope in delayed calls.
            QTimer.singleShot(
                i * delay_ms_per_word + (delay_ms_per_word // 2),
                lambda w=word_val, p=char_pos, l=word_len: self.speech_word_boundary.emit(w, p, l)
            )
            char_pos += word_len + 1  # Account for space
        QTimer.singleShot(
            len(words) * delay_ms_per_word + delay_ms_per_word,  # After last word boundary
            lambda t=text: self.speech_finished.emit(t)
        )

    @pyqtSlot()
    def stop_speaking(self) -> None:
        """Simulates stopping speech."""
        self.log_dummy_call("stop_speaking")
        self.speech_finished.emit("(Dummy TTS Speech Interrupted)")

    @pyqtSlot(str)
    def set_voice(self, voice_id: str) -> None:
        """Simulates setting the TTS voice."""
        self.log_dummy_call("set_voice", voice_id)

    @pyqtSlot(int)
    def set_rate(self, rate: int) -> None:
        """Simulates setting the TTS speech rate."""
        self.log_dummy_call("set_rate", rate)

    @pyqtSlot(float)  # TTS Engines often use volume from 0.0 to 1.0
    def set_volume(self, volume: float) -> None:
        """Simulates setting the TTS volume."""
        self.log_dummy_call("set_volume", volume)


class VoiceListenerWorker_Dummy(BaseWorkerDummy):
    """Dummy fallback for the Voice Listener (Speech-to-Text) Worker."""
    text_recognized = pyqtSignal(str, float)  # Emits recognized_text, confidence_score
    listening_started_signal = pyqtSignal()
    listening_stopped_signal = pyqtSignal()
    vad_status_changed = pyqtSignal(bool)  # Emits is_user_speaking
    listening_error = pyqtSignal(str, str)  # Emits error_type, error_message

    def __init__(self, parent: Optional[QObject] = None, language: str = "en-US",
                 mic_idx: Optional[int] = None, energy: int = 300, pause: float = 0.8,
                 phrase_limit: Optional[float] = 5.0):
        """Initializes the dummy VoiceListenerWorker."""
        super().__init__("VoiceListenerWorkerDummy", parent)
        self._is_listening: bool = False
        self.language: str = language
        # Other args are for interface compatibility
        _ = mic_idx, energy, pause, phrase_limit

    @pyqtSlot()
    def initialize_microphone(self) -> None:
        """Simulates microphone initialization."""
        self.log_dummy_call("initialize_microphone")

    @pyqtSlot()
    def start_listening(self) -> None:
        """Simulates starting voice listening."""
        self.log_dummy_call("start_listening")
        if not self._is_listening:
            self._is_listening = True
            self.listening_started_signal.emit()
            self.vad_status_changed.emit(True)  # Simulate VAD detecting speech start
            # Simulate a recognition after a short delay
            QTimer.singleShot(2500, self._simulate_recognition_if_active)

    def _simulate_recognition_if_active(self) -> None:
        """Helper to emit recognition only if still listening."""
        if self._is_listening:  # Check if stop_listening wasn't called in the meantime
            self.text_recognized.emit("Dummy voice input: This is a test.", 0.85)
            self.vad_status_changed.emit(False)  # Simulate VAD detecting speech end
            # Optionally, auto-stop after one simulated phrase for dummy behavior:
            # QTimer.singleShot(500, self.stop_listening)

    @pyqtSlot()
    def stop_listening(self) -> None:
        """Simulates stopping voice listening."""
        if self._is_listening:
            self.log_dummy_call("stop_listening")
            self._is_listening = False
            self.vad_status_changed.emit(False)  # Ensure VAD shows not speaking
            self.listening_stopped_signal.emit()

    @pyqtSlot(str)
    def set_language(self, lang: str) -> None:
        """Simulates setting the listening language."""
        self.log_dummy_call("set_language", lang)
        self.language = lang


class NLPWorker_Dummy(BaseWorkerDummy):
    """Dummy fallback for the Natural Language Processing (NLP) Worker."""
    processing_complete = pyqtSignal(dict)  # Emits response_dictionary

    def __init__(self, dependencies: Optional[Dict[str, Any]] = None,
                 parent: Optional[QObject] = None):
        """Initializes the dummy NLPWorker."""
        super().__init__("NLPWorkerDummy", parent)
        # Use provided dummy RobotInfoModule if available in dependencies, else create new one
        self.robot_info: RobotInfoModule_Dummy = (dependencies.get('robot_info_module')
                                                  if dependencies and isinstance(dependencies.get('robot_info_module'),
                                                                                 RobotInfoModule_Dummy)
                                                  else RobotInfoModule_Dummy())

    @pyqtSlot(str)
    def process_user_input(self, text: str) -> None:
        """Simulates NLP processing of user input."""
        self.log_dummy_call("process_user_input", text)
        response_text = self.robot_info.get_information(text)  # Use internal dummy robot_info
        response_type = "info_response"

        if not response_text or "don't have specific information on" in response_text:
            response_text = f"NLP Dummy: I received '{text[:50].strip()}' and will provide a generic dummy reply."
            response_type = "fallback_info"  # Or some other generic type

        self.processing_complete.emit({
            "type": response_type,
            "text_to_speak": response_text,
            "display_details": [("normal", response_text)],  # Simple display for dummy
            "original_input": text,
            "timestamp": datetime.datetime.now().isoformat(),
            "detected_emotion_in_input": None,  # Dummy doesn't detect emotion
            "action_data": None  # Dummy doesn't propose actions
        })


# --- Attempt to import REAL external component modules & Assign _cls Variables ---
# These '_cls' variables will hold the actual class (Real or Dummy) to be instantiated.
# They are defined globally here and used later by MainWindow.
# Linter Warning Note: These variables WILL appear "unused" if this Part 1/4 is analyzed
# in isolation, as their usage is in subsequent parts of the complete file.

logger.info("--- Attempting to load REAL external modules ---")

# Emotion Engine (expects emotion_engine.py)
imported_ee_items, _ = _try_import("emotion_engine", ["EmotionWorker"], "emotion_engine.py")
EmotionWorker_cls: Type = imported_ee_items["EmotionWorker"] if imported_ee_items else EmotionWorker_Dummy

# Robot Appearance (expects robot_appearance.py with your AI version)
imported_ra_items, _ = _try_import("robot_appearance", ["RobotAppearanceWidget"], "robot_appearance.py")
RobotAppearanceWidget_cls: Type = imported_ra_items[
    "RobotAppearanceWidget"] if imported_ra_items else RobotAppearanceWidget_Dummy  # Fallback to INTERNAL simple dummy

# Voice Output (TTS) (expects voice_output_v2.py)
imported_vo_items, _ = _try_import("voice_output_v2", ["TTSWorker"], "voice_output_v2.py")
TTSWorker_cls: Type = imported_vo_items["TTSWorker"] if imported_vo_items else TTSWorker_Dummy

# Robot Audio Listener (STT) (expects robot_audio_listener_v2.py)
imported_ral_items, _ = _try_import("robot_audio_listener_v2", ["VoiceListenerWorker"], "robot_audio_listener_v2.py")
VoiceListenerWorker_cls: Type = imported_ral_items[
    "VoiceListenerWorker"] if imported_ral_items else VoiceListenerWorker_Dummy

# NLP Worker (expects nlp_worker_v2.py)
imported_nlp_items, _ = _try_import("nlp_worker_v2", ["NLPWorker"], "nlp_worker_v2.py")
NLPWorker_cls: Type = imported_nlp_items["NLPWorker"] if imported_nlp_items else NLPWorker_Dummy

# Dependencies for NLPWorker & MainWindow (e.g., About Dialog uses RobotInfoModule)
# These are typically not workers themselves but provide services.
imported_ri_items, _ = _try_import("robot_info_module_v2", ["RobotInfoModule"], "robot_info_module_v2.py")
RobotInfoModule_for_deps: Type = imported_ri_items["RobotInfoModule"] if imported_ri_items else RobotInfoModule_Dummy

imported_gs_items, _ = _try_import("grammar_system_v2", ["GrammarSystem"], "grammar_system_v2.py")
GrammarSystem_for_deps: Type = imported_gs_items["GrammarSystem"] if imported_gs_items else GrammarSystem_Dummy

imported_mlc_items, _ = _try_import("multi_language_correction_v2", ["EnhancedMultilingualCorrector"],
                                    "multi_language_correction_v2.py")
MultiLangCorrector_for_deps: Type = imported_mlc_items[
    "EnhancedMultilingualCorrector"] if imported_mlc_items else MultiLangCorrectionModule_Dummy

logger.info("--- External module loading summary ---")
logger.info(f"EmotionWorker will use: {EmotionWorker_cls.__name__}")
logger.info(f"RobotAppearanceWidget will use: {RobotAppearanceWidget_cls.__name__}")
logger.info(f"TTSWorker will use: {TTSWorker_cls.__name__}")
logger.info(f"VoiceListenerWorker will use: {VoiceListenerWorker_cls.__name__}")
logger.info(f"NLPWorker will use: {NLPWorker_cls.__name__}")
logger.info(f"RobotInfoModule (for dependencies) will use: {RobotInfoModule_for_deps.__name__}")
logger.info(f"GrammarSystem (for dependencies) will use: {GrammarSystem_for_deps.__name__}")
logger.info(f"MultiLangCorrector (for dependencies) will use: {MultiLangCorrector_for_deps.__name__}")
if not MODULE_IMPORTS_OK:
    logger.warning(
        f"One or more REAL modules failed to load. Missing modules: {MISSING_MODULES}. Application will use dummies.")
else:
    logger.info("All located REAL external modules loaded successfully (or fallbacks explicitly chosen).")

# END OF UPDOGO_ROBOT.py - DELIVERABLE PART 1/4
# --- Internal Worker Class Definitions (Not from external files) ---
# These workers are defined directly within this main application file.

class Worker(QObject):
    """
    A basic QObject worker template that can be moved to a QThread.
    Provides common signals like finished, error, and status_update.
    """
    finished = pyqtSignal()  # Emitted when the worker's main task is done
    error = pyqtSignal(str, str)  # Emits worker_name, error_message
    status_update = pyqtSignal(str, int)  # Emits message, timeout_ms for status bar

    def __init__(self, worker_name: str = "UnnamedInternalWorker", parent: Optional[QObject] = None):
        """
        Initializes the base Worker.
        Args:
            worker_name: A descriptive name for this worker instance.
            parent: The parent QObject, if any.
        """
        super().__init__(parent)
        self.worker_name: str = worker_name
        self._is_running: bool = True  # Flag to control the worker's main loop
        logger.info(f"Internal Worker '{self.worker_name}' initialized.")

    def stop(self) -> None:
        """
        Signals the worker to stop its operations.
        Subclasses should check self._is_running in their loops.
        """
        logger.info(f"Stopping internal worker '{self.worker_name}'...")
        self._is_running = False
        # Note: finished.emit() is usually called by the run loop itself when it exits.

    def shutdown(self) -> None:
        """
        Requests a more explicit shutdown, often calling stop() and then emitting finished.
        This ensures the thread management in MainWindow can properly join the thread.
        """
        self.log_internal_worker_call("shutdown")
        self.stop()
        self.finished.emit()  # Ensure finished is emitted for thread cleanup

    def log_internal_worker_call(self, method_name: str, *args: Any) -> None:
        """Logs a call to an internal worker method for debugging."""
        args_str = ", ".join(map(repr, args)) if args else ""
        logger.debug(f"INTERNAL WORKER CALL: {self.worker_name}.{method_name}({args_str}).")


class CameraWorker(Worker):
    """
    Internal worker to handle camera frame capture in a separate thread.
    Uses OpenCV for camera operations.
    """
    frame_ready = pyqtSignal(object)  # Emits the captured frame (expected to be np.ndarray)

    def __init__(self, config: Dict[str, Any], parent: Optional[QObject] = None):
        """
        Initializes the CameraWorker.
        Args:
            config: A dictionary containing camera configuration
                    (e.g., 'camera_index', 'camera_resolution').
            parent: The parent QObject, if any.
        """
        super().__init__("CameraWorker", parent)
        self.config: Dict[str, Any] = config
        self.camera_index: int = self.config.get('camera_index', DEFAULT_CAMERA_INDEX)
        self.resolution: Tuple[int, int] = tuple(self.config.get('camera_resolution', DEFAULT_CAMERA_RESOLUTION))
        self.cap: Optional[cv2.VideoCapture] = None
        self.current_filter_key: Optional[str] = RAW_DEFAULT_CAMERA_FILTER
        # _is_running is inherited from Worker and controls the main loop in run()

    @pyqtSlot(str)
    def set_filter(self, filter_key: str) -> None:
        """Sets the image filter to be applied to camera frames."""
        self.log_internal_worker_call("set_filter", filter_key)
        if filter_key in RAW_CAMERA_FILTERS:
            self.current_filter_key = filter_key
            logger.info(f"CameraWorker: Filter set to '{filter_key}'.")
        else:
            logger.warning(f"CameraWorker: Unknown filter key '{filter_key}'. Filter not changed.")

    def _apply_filter_to_frame(self, frame: 'np.ndarray') -> 'np.ndarray':
        """Applies the current filter to the given frame."""
        # Ensure NumPy and OpenCV are available for filtering operations
        if not NUMPY_AVAILABLE or not CV2_AVAILABLE:
            if not hasattr(self, '_filter_warning_logged'):  # Log warning only once
                logger.warning("CameraWorker: NumPy or OpenCV not available. Cannot apply filters.")
                self._filter_warning_logged = True
            return frame

        filter_name = RAW_CAMERA_FILTERS.get(self.current_filter_key)
        if filter_name is None: return frame  # "None" filter or invalid key

        try:
            if filter_name == "grayscale": return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if filter_name == "blur": return cv2.GaussianBlur(frame, (15, 15), 0)
            if filter_name == "canny": return cv2.Canny(frame, 100, 200)
            if filter_name == "sepia":
                kernel = np.array([[0.272, 0.534, 0.131],
                                   [0.349, 0.686, 0.168],
                                   [0.393, 0.769, 0.189]])
                return cv2.filter2D(frame, -1, kernel)
            if filter_name == "invert": return cv2.bitwise_not(frame)
            if filter_name == "cartoon":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray_blur = cv2.medianBlur(gray, 5)
                edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                              cv2.THRESH_BINARY, 9, 9)
                color_frame = cv2.bilateralFilter(frame, 9, 250, 250)
                return cv2.bitwise_and(color_frame, color_frame, mask=edges)
        except cv2.error as e_cv:
            logger.error(f"OpenCV error applying filter '{filter_name}': {e_cv}")
        except Exception as e_filter:  # Catch other potential errors
            logger.error(f"Error applying filter '{filter_name}': {e_filter}", exc_info=True)
        return frame  # Return original frame if filter application fails

    @pyqtSlot()
    def run(self) -> None:
        """Main loop for camera frame capture and processing. Called when thread starts."""
        self.log_internal_worker_call("run (thread started)")
        if not CV2_AVAILABLE:
            self.error.emit(self.worker_name, "OpenCV (cv2) is not available. Camera cannot operate.")
            self.finished.emit()
            return

        logger.info(f"CameraWorker attempting to open camera {self.camera_index} at {self.resolution} resolution.")
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            err_msg = f"Cannot open camera at index {self.camera_index}."
            logger.error(err_msg)
            self.error.emit(self.worker_name, err_msg)
            self.finished.emit()
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self._is_running = True  # Ensure running flag is true at start of loop
        logger.info(f"CameraWorker started successfully on thread {QThread.currentThreadId()}.")
        self.status_update.emit("Camera stream started.", 2000)

        while self._is_running:  # Check flag from Worker base class
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("CameraWorker: Failed to grab frame or stream ended.")
                self._is_running = False  # Stop loop if no frame
                break

            if self.current_filter_key and self.current_filter_key != "None":
                frame = self._apply_filter_to_frame(frame)

            self.frame_ready.emit(frame.copy())  # Emit a copy to avoid issues with shared data

            # Control frame rate. QThread.msleep is thread-safe.
            # This provides a basic delay; more sophisticated timing could be added.
            QThread.msleep(30)  # Approx 33 FPS target, adjust as needed for performance.

        if self.cap:
            self.cap.release()
            self.cap = None
        logger.info("CameraWorker run loop finished and camera released.")
        self.status_update.emit("Camera stream stopped.", 2000)
        self.finished.emit()  # Signal that the worker's task is done


class ImageSaveWorker(Worker):
    """
    Internal worker to handle saving images to disk in a separate thread.
    Uses Pillow or OpenCV for saving.
    """
    image_saved = pyqtSignal(str)  # Emits the filename of the saved image

    def __init__(self, parent: Optional[QObject] = None):
        """Initializes the ImageSaveWorker."""
        super().__init__("ImageSaveWorker", parent)

    @pyqtSlot(object, str)  # Accepts frame_object (QPixmap, QImage, or np.ndarray) and filename
    def save_image(self, frame_object: Any, filename: str) -> None:
        """Saves the given frame object to the specified filename."""
        self.log_internal_worker_call("save_image", type(frame_object), filename)

        if not PIL_AVAILABLE and not CV2_AVAILABLE:
            err_msg = "Neither Pillow (PIL) nor OpenCV is available for saving images."
            logger.error(err_msg)
            self.error.emit(self.worker_name, err_msg)
            return

        try:
            if isinstance(frame_object, QPixmap):
                frame_object.save(filename)
                logger.info(f"Image saved from QPixmap to '{filename}'.")
            elif isinstance(frame_object, QImage):
                frame_object.save(filename)
                logger.info(f"Image saved from QImage to '{filename}'.")
            elif NUMPY_AVAILABLE and isinstance(frame_object, np.ndarray):
                if CV2_AVAILABLE:
                    # OpenCV imwrite expects BGR format by default.
                    # If frame_object is RGB from elsewhere, it might need conversion.
                    # Assuming frame_object is already in a suitable format (e.g., BGR or Grayscale).
                    cv2.imwrite(filename, frame_object)
                    logger.info(f"Image saved from NumPy array (using OpenCV) to '{filename}'.")
                elif PIL_AVAILABLE:  # Fallback to Pillow if OpenCV not used or failed for some reason
                    # Pillow Image.fromarray expects RGB for color, or single channel for grayscale.
                    # If frame_object is BGR (common from OpenCV capture), convert to RGB.
                    img_to_save_pil: Optional[Image.Image] = None
                    if frame_object.ndim == 3 and frame_object.shape[2] == 3:  # Color
                        try:  # Attempt BGR to RGB conversion if CV2 is available for it
                            if CV2_AVAILABLE:
                                frame_rgb = cv2.cvtColor(frame_object, cv2.COLOR_BGR2RGB)
                                img_to_save_pil = Image.fromarray(frame_rgb)
                            else:  # No CV2, assume it might be RGB already or try direct
                                img_to_save_pil = Image.fromarray(frame_object)
                        except Exception as e_conv:
                            logger.warning(f"Could not ensure RGB for Pillow, trying direct fromarray. Error: {e_conv}")
                            img_to_save_pil = Image.fromarray(frame_object)  # Try direct
                    elif frame_object.ndim == 2:  # Grayscale
                        img_to_save_pil = Image.fromarray(frame_object)
                    else:
                        err_msg = f"Unsupported NumPy array format for Pillow: dimensions {frame_object.ndim}, shape {frame_object.shape}"
                        logger.error(err_msg)
                        self.error.emit(self.worker_name, err_msg)
                        return

                    if img_to_save_pil:
                        img_to_save_pil.save(filename)
                        logger.info(f"Image saved from NumPy array (using Pillow) to '{filename}'.")
                    else:
                        raise ValueError("Failed to convert NumPy array to Pillow Image.")
                else:  # Should not be reached due to initial check, but defensive.
                    err_msg = "No library available to save NumPy array."
                    logger.error(err_msg)
                    self.error.emit(self.worker_name, err_msg)
                    return
            else:
                err_msg = f"Unsupported frame type for saving: {type(frame_object)}."
                logger.error(err_msg)
                self.error.emit(self.worker_name, err_msg)
                return

            self.image_saved.emit(filename)
            self.status_update.emit(f"Saved: {os.path.basename(filename)}", 3000)

        except Exception as e:
            err_msg = f"Error saving image to '{filename}': {e}"
            logger.error(err_msg, exc_info=True)
            self.error.emit(self.worker_name, err_msg)


# --- Dialog Class Definitions ---
# These define custom dialogs used by the application.

class AboutDialog(QDialog):
    """Custom 'About' dialog for the application."""

    def __init__(self, parent: Optional[QWidget] = None,
                 robot_info_module: Optional[Any] = None):  # Accepts RobotInfoModule or its Dummy
        """Initializes the About dialog."""
        super().__init__(parent)
        self.setWindowTitle(QCoreApplication.translate("AboutDialog", f"About {APP_NAME_CONST}"))
        self.setModal(True)
        self.setMinimumWidth(450)

        # Use robot_info_module if provided, otherwise use a dummy for safety
        info_src = robot_info_module if robot_info_module else RobotInfoModule_Dummy()

        try:
            robot_info = info_src.get_robot_info()
            dev_info = info_src.get_developer_info()
        except Exception as e:  # Catch errors if methods are missing from a bad module
            logger.error(f"Error getting info from robot_info_module in AboutDialog: {e}")
            robot_info = RobotInfoModule_Dummy().get_robot_info()  # Fallback
            dev_info = RobotInfoModule_Dummy().get_developer_info()

        layout = QVBoxLayout(self)
        title_label = QLabel(f"<b>{robot_info.get('name', APP_NAME_CONST)}</b>")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        version_label = QLabel(f"Version: {robot_info.get('version', APP_VERSION_CONST)}")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        info_text = (
            f"This is the control suite for {robot_info.get('name', APP_NAME_CONST)}, "
            f"an interactive assistant.\n\n"
            f"Developed by: {dev_info.get('full_name', 'The UPDOGO Team')}\n"
            f"Developer ID: {dev_info.get('id', 'N/A')}\n"
            f"Title: {dev_info.get('title', 'Lead Developer')}\n\n"
            f"© {datetime.date.today().year} {SETTINGS_ORG}. All rights reserved.\n\n"
            "For more information, please consult the User Guide or visit our (hypothetical) website."
        )
        details_label = QTextBrowser()  # Use QTextBrowser for rich text and links
        details_label.setPlainText(info_text)  # For simple text display
        details_label.setOpenExternalLinks(True)  # Allow opening http links if any were added
        details_label.setStyleSheet("QTextBrowser { border: none; background-color: transparent; }")
        details_label.setFixedHeight(180)  # Adjust as needed
        layout.addWidget(details_label)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)
        logger.debug("AboutDialog initialized.")


class SettingsDialog(QDialog):
    """Custom 'Settings' dialog for application preferences."""
    settings_changed_signal = pyqtSignal()  # Emitted when settings are applied

    def __init__(self, parent: Optional[QWidget] = None,
                 settings: Optional[QSettings] = None,
                 current_config: Optional[Dict[str, Any]] = None):
        """Initializes the Settings dialog."""
        super().__init__(parent)
        self.setWindowTitle(QCoreApplication.translate("SettingsDialog", f"{APP_NAME_CONST} Settings"))
        self.setModal(True)
        self.setMinimumWidth(400)

        self.settings: Optional[QSettings] = settings
        self.config: Dict[str, Any] = current_config if current_config else {}  # Live config dict

        self.ui_elements: Dict[str, QWidget] = {}  # To store created UI elements for later access

        layout = QVBoxLayout(self)
        form_layout = QGridLayout()

        # --- Log Level Setting ---
        row = 0
        form_layout.addWidget(QLabel(QCoreApplication.translate("SettingsDialog", "Logging Level:")), row, 0)
        self.ui_elements["log_level_combo"] = QComboBox()
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.ui_elements["log_level_combo"].addItems(log_levels)
        if self.settings:
            current_log_level = self.settings.value("log_level", "INFO").upper()
            if current_log_level in log_levels:
                self.ui_elements["log_level_combo"].setCurrentText(current_log_level)
        form_layout.addWidget(self.ui_elements["log_level_combo"], row, 1)
        row += 1

        # --- Chat Font Size Setting ---
        form_layout.addWidget(QLabel(QCoreApplication.translate("SettingsDialog", "Chat Font Size:")), row, 0)
        self.ui_elements["chat_font_size_slider"] = QSlider(Qt.Horizontal)
        self.ui_elements["chat_font_size_slider"].setRange(7, 24)  # Min 7pt, Max 24pt
        self.ui_elements["chat_font_size_label"] = QLabel()
        if self.settings:
            font_size_val = self.settings.value("chat_font_size", DEFAULT_CHAT_FONT_SIZE, type=int)
            self.ui_elements["chat_font_size_slider"].setValue(font_size_val)
            self.ui_elements["chat_font_size_label"].setText(f"{font_size_val} pt")
        self.ui_elements["chat_font_size_slider"].valueChanged.connect(
            lambda val: self.ui_elements["chat_font_size_label"].setText(f"{val} pt")
        )
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.ui_elements["chat_font_size_slider"])
        slider_layout.addWidget(self.ui_elements["chat_font_size_label"])
        form_layout.addLayout(slider_layout, row, 1)
        row += 1

        # --- Add more settings here as needed ---
        # Example: API Key (if used by an external module)
        # form_layout.addWidget(QLabel(QCoreApplication.translate("SettingsDialog", "Some API Key:")), row, 0)
        # self.ui_elements["api_key_input"] = QLineEdit()
        # if self.config: # API keys are usually in config, not QSettings for security/portability
        #     self.ui_elements["api_key_input"].setText(self.config.get("some_module_api_key", ""))
        # form_layout.addWidget(self.ui_elements["api_key_input"], row, 1)
        # row +=1

        layout.addLayout(form_layout)
        layout.addStretch(1)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        button_box.accepted.connect(self.accept_settings)  # Ok = Apply + Close
        button_box.rejected.connect(self.reject)  # Cancel
        layout.addWidget(button_box)

        self.setLayout(layout)
        logger.debug("SettingsDialog initialized.")

    def apply_settings(self) -> None:
        """Applies the current settings from the dialog UI without closing."""
        logger.info("Applying settings from dialog...")
        changed = False
        if self.settings:
            # Log Level
            new_log_level = self.ui_elements["log_level_combo"].currentText()
            if self.settings.value("log_level", "INFO") != new_log_level:
                self.settings.setValue("log_level", new_log_level)
                changed = True
                logger.info(f"Setting 'log_level' changed to: {new_log_level}")

            # Chat Font Size
            new_font_size = self.ui_elements["chat_font_size_slider"].value()
            if self.settings.value("chat_font_size", DEFAULT_CHAT_FONT_SIZE, type=int) != new_font_size:
                self.settings.setValue("chat_font_size", new_font_size)
                changed = True
                logger.info(f"Setting 'chat_font_size' changed to: {new_font_size}pt")

            # API Key Example (saving to live config, not QSettings)
            # if "api_key_input" in self.ui_elements and self.config is not None:
            #     new_api_key = self.ui_elements["api_key_input"].text()
            #     if self.config.get("some_module_api_key", "") != new_api_key:
            #         self.config["some_module_api_key"] = new_api_key # Update live config
            #         # To persist this config change, MainWindow would need to save its self.config to JSON
            #         logger.info("Live config 'some_module_api_key' updated. (Requires app to save config file to persist).")
            #         # Note: Persisting config changes from dialog is complex; often requires app restart or module re-init.

            if changed:
                self.settings.sync()  # Persist QSettings changes
                self.settings_changed_signal.emit()  # Notify MainWindow
                QMessageBox.information(self, QCoreApplication.translate("SettingsDialog", "Settings Applied"),
                                        QCoreApplication.translate("SettingsDialog", "Settings have been applied."))
            else:
                QMessageBox.information(self, QCoreApplication.translate("SettingsDialog", "No Changes"),
                                        QCoreApplication.translate("SettingsDialog", "No settings were changed."))

        else:
            logger.warning("SettingsDialog: QSettings object not available. Cannot apply settings.")
            QMessageBox.warning(self, QCoreApplication.translate("SettingsDialog", "Error"),
                                QCoreApplication.translate("SettingsDialog",
                                                           "Settings could not be applied (internal error)."))

    def accept_settings(self) -> None:
        """Applies settings and then closes the dialog."""
        self.apply_settings()
        self.accept()  # QDialog.accept()


class UserGuideDialog(QDialog):
    """Displays the user guide, loaded from an HTML file."""

    def __init__(self, parent: Optional[QWidget] = None):
        """Initializes the UserGuide dialog."""
        super().__init__(parent)
        self.setWindowTitle(QCoreApplication.translate("UserGuideDialog", f"{APP_NAME_CONST} - User Guide"))
        self.setModal(False)  # User guide can be non-modal
        self.resize(QSize(700, 550))

        layout = QVBoxLayout(self)
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)  # Allow opening http links

        try:
            if os.path.exists(USER_GUIDE_CONTENT_FILE):
                with open(USER_GUIDE_CONTENT_FILE, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                self.text_browser.setHtml(html_content)
            else:
                err_msg = QCoreApplication.translate("UserGuideDialog",
                                                     f"User guide content file not found at: {USER_GUIDE_CONTENT_FILE}\n\n"
                                                     "Please ensure the user guide HTML file is correctly placed. Displaying basic help.")
                logger.warning(err_msg)
                self.text_browser.setPlainText(err_msg + self._get_basic_help_text())
        except Exception as e:
            err_msg = QCoreApplication.translate("UserGuideDialog",
                                                 f"Error loading user guide: {e}\n\nDisplaying basic help.")
            logger.error(err_msg, exc_info=True)
            self.text_browser.setPlainText(err_msg + self._get_basic_help_text())

        layout.addWidget(self.text_browser)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)  # Close button acts as reject
        layout.addWidget(button_box)
        self.setLayout(layout)
        logger.debug("UserGuideDialog initialized.")

    def _get_basic_help_text(self) -> str:
        """Provides very basic help text if the HTML guide fails to load."""
        return (
            "\n\n--- Basic Usage ---\n"
            "1. Type messages in the input field at the bottom of the chat interface and press Enter or click Send.\n"
            "2. Use the control panel to adjust TTS (Text-to-Speech) settings like voice, rate, and volume.\n"
            "3. Toggle voice input (microphone) and voice output (speaker) using the buttons in the control panel.\n"
            "4. Manage themes via the 'View > Application Themes' menu or the theme dropdown in the control panel.\n"
            "5. Access additional features and settings through the File, View, and Tools menus.\n"
            "6. Camera controls allow starting/stopping the camera feed and applying visual filters.\n\n"
            "Slash Commands (type in chat input):\n"
            "  /help          - Show available slash commands.\n"
            "  /clear         - Clear the chat history.\n"
            "  /theme [Name]  - Change theme (e.g., /theme Cyberpunk Neon).\n"
            "  (More commands might be available depending on loaded modules)."
        )


# --- Main Application Window Class ---
class MainWindow(QMainWindow):
    """
    The main window of the UPDOGO Robot application.
    It orchestrates the UI, worker threads, and interactions between modules.
    """
    # --- Custom Signals ---
    # Signals to request actions from workers (defined here, connected in _setup_workers_and_threads)
    start_nlp_processing = pyqtSignal(str)  # Emits user_text for NLPWorker
    request_emotion_analysis = pyqtSignal(str)  # Emits text for EmotionWorker
    stop_tts_signal = pyqtSignal()  # Signals TTSWorker to stop speaking
    request_camera_filter_change = pyqtSignal(str)  # Emits filter_key for CameraWorker

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initializes the MainWindow.
        Sets up essential attributes, loads initial settings, and schedules
        the main initialization sequence.
        """
        super().__init__(parent)
        logger.info(f"Initializing {APP_TITLE_CONST}...")

        # --- Core Attributes ---
        self.config: Dict[str, Any] = {}  # Loaded from JSON file
        self.settings: Optional[QSettings] = None  # For persistent app state (window size, theme, etc.)
        self.icons: Dict[str, QIcon] = {}  # Loaded application icons
        self.workers: Dict[str, Dict[str, Any]] = {}  # Stores worker instances and their threads
        self.robot_info_direct_instance: Optional[Any] = None  # Direct instance for AboutDialog, NLP deps

        # --- UI State Attributes ---
        self.current_theme_name: str = "Default"  # Default theme key
        self.current_chat_font_size: int = DEFAULT_CHAT_FONT_SIZE
        self.camera_on: bool = False
        self._last_camera_frame: Optional['np.ndarray'] = None  # Stores the last raw camera frame (NumPy)
        self.current_camera_filter_key: str = RAW_DEFAULT_CAMERA_FILTER
        self.voice_output_enabled: bool = True
        self.voice_input_on: bool = False
        self.available_tts_voices: List[Dict[str, Any]] = []  # Populated by TTSWorker

        # --- UI Element Placeholders (will be assigned in _init_ui and its helpers) ---
        # These are declared here for type hinting and to indicate they will exist.
        # If a linter flags them as "unused" in __init__, it's because their primary
        # assignment and use is in methods called later by _perform_full_initialization.
        self.menu_bar: Optional[QMenuBar] = None
        self.theme_menu: Optional[QMenu] = None
        self.theme_action_group: Optional[QActionGroup] = None
        self.status_bar: Optional[QStatusBar] = None
        self.module_status_icon_label: Optional[QLabel] = None
        self.chat_display: Optional[QTextEdit] = None
        self.user_input: Optional[QLineEdit] = None
        self.send_button: Optional[QToolButton] = None
        self.clear_chat_button: Optional[QToolButton] = None
        self.status_labels: Dict[str, QLabel] = {}
        self.robot_appearance_widget_instance: Optional[QWidget] = None  # Will hold RobotAppearanceWidget or its Dummy
        self.cam_btn: Optional[QPushButton] = None
        self.filter_combo: Optional[QComboBox] = None
        self.raw_keys_for_filters: List[str] = []  # Populated in _create_camera_interface
        self.capture_btn: Optional[QPushButton] = None
        self.camera_label: Optional[QLabel] = None
        self.theme_combo: Optional[QComboBox] = None
        self.theme_combo_keys: List[str] = []  # Populated in _create_control_panel
        self.voice_input_btn: Optional[QToolButton] = None
        self.voice_output_btn: Optional[QToolButton] = None
        self.tts_stop_button: Optional[QToolButton] = None
        self.voice_select_combo: Optional[QComboBox] = None
        self.rate_slider: Optional[QSlider] = None
        self.rate_label: Optional[QLabel] = None
        self.volume_slider: Optional[QSlider] = None
        self.volume_label: Optional[QLabel] = None

        # --- Schedule Full Initialization ---
        # This ensures that the main event loop is running before we do heavy setup
        # like UI construction and worker thread creation.
        logger.debug("Scheduling _perform_full_initialization via QTimer.singleShot(0).")
        QTimer.singleShot(0, self._perform_full_initialization)

        logger.info("MainWindow __init__ completed.")

    def _perform_full_initialization(self) -> None:
        """
        Orchestrates the main setup sequence after __init__ and event loop start.
        This includes loading configuration, setting up logging, UI, and workers.
        """
        logger.info("Starting _perform_full_initialization...")
        try:
            # 1. Load Configuration (JSON)
            self._load_config()  # Loads into self.config

            # 2. Setup Logging (based on config)
            self._setup_logging()  # Reconfigures logger based on self.config and self.settings

            # 3. Initialize QSettings (for persistent user preferences)
            self.settings = QSettings(SETTINGS_ORG, SETTINGS_APP, self)  # QSettings must be after config for log level
            logger.info(f"QSettings initialized for {SETTINGS_ORG} - {SETTINGS_APP}.")

            # 4. Load Application Icons
            self._load_app_icons()  # Loads into self.icons

            # 5. Apply Initial Settings from QSettings
            # Theme (must be applied before UI creation for some elements)
            self.current_theme_name = self.settings.value("theme", "Default", type=str)
            if self.current_theme_name not in THEMES_CSS:  # Validate saved theme
                logger.warning(f"Saved theme '{self.current_theme_name}' not found. Defaulting to 'Default'.")
                self.current_theme_name = "Default"
            self._apply_theme(self.current_theme_name)  # Applies stylesheet

            # Chat font size
            self.current_chat_font_size = self.settings.value("chat_font_size", DEFAULT_CHAT_FONT_SIZE, type=int)
            # Voice output enabled state
            self.voice_output_enabled = self.settings.value("voice_output_enabled", True, type=bool)
            # Camera filter
            self.current_camera_filter_key = self.settings.value("camera_filter", RAW_DEFAULT_CAMERA_FILTER, type=str)
            if self.current_camera_filter_key not in RAW_CAMERA_FILTERS:  # Validate
                self.current_camera_filter_key = RAW_DEFAULT_CAMERA_FILTER

            # 6. Create Direct Instance of RobotInfoModule for About Dialog & NLP deps
            # RobotInfoModule_for_deps was determined in Part 1 (Real or Dummy)
            try:
                self.robot_info_direct_instance = RobotInfoModule_for_deps()
                logger.info(f"Direct instance of {RobotInfoModule_for_deps.__name__} created for About Dialog/NLP.")
            except Exception as e_ri:
                logger.error(
                    f"Failed to create direct instance of RobotInfoModule: {e_ri}. Using fallback for About Dialog.",
                    exc_info=True)
                self.robot_info_direct_instance = RobotInfoModule_Dummy()

            # 7. Initialize User Interface
            logger.info("Calling _init_ui() to construct the main interface...")
            self._init_ui()  # Builds all UI panels and sets central widget
            logger.info("Main UI construction completed.")

            # 8. Setup Worker Threads and Modules
            logger.info("Calling _setup_workers_and_threads()...")
            self._setup_workers_and_threads()  # Instantiates workers, moves to threads, connects signals
            logger.info("Worker setup completed.")

            # 9. Perform initial calls to workers and status notifications
            # This is delayed slightly to ensure GUI is fully responsive and workers are settled.
            QTimer.singleShot(200, self._initial_worker_calls_and_notifications)

            self.update_status(QCoreApplication.translate("MainWindow", "Application initialized successfully."), 5000)
            logger.info("Full application initialization sequence completed.")

        except Exception as e_init:
            logger.critical(f"CRITICAL ERROR during _perform_full_initialization: {e_init}", exc_info=True)
            QMessageBox.critical(
                self,
                QCoreApplication.translate("MainWindow", "Initialization Error"),
                QCoreApplication.translate("MainWindow",
                                           "A critical error occurred during application startup:\n\n{0}\n\n"
                                           "The application might be unstable or some features may not work. "
                                           "Please check the logs ({1}) for details."
                                           ).format(str(e_init), LOG_FILE_NAME)
            )
            # Depending on severity, could call self.close() here.

    def _load_config(self) -> None:
        """Loads application configuration from the JSON file."""
        logger.info(f"Loading configuration from '{CONFIG_FILE}'...")
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)

                # Basic validation or merging with defaults can be done here
                # For now, directly assign. Ensure config keys are handled with .get() later.
                self.config = loaded_config
                logger.info(f"Configuration loaded successfully. {len(self.config)} top-level keys found.")
            else:
                logger.warning(f"Configuration file '{CONFIG_FILE}' not found. Using default values where possible.")
                self.config = {}  # Ensure self.config is an empty dict, not None
                # Populate with some essential defaults if file is missing
                self.config.setdefault("log_level", "INFO")
                self.config.setdefault("log_to_file", True)
                self.config.setdefault("application_language", QLocale.system().name()[:2])  # e.g., "en"
                # Add other critical defaults your app needs if config is absent
        except json.JSONDecodeError as e_json:
            logger.error(f"Error decoding JSON from '{CONFIG_FILE}': {e_json}. Using empty config.", exc_info=True)
            self.config = {}
        except Exception as e_load:
            logger.error(f"Failed to load configuration from '{CONFIG_FILE}': {e_load}. Using empty config.",
                         exc_info=True)
            self.config = {}

    def _setup_logging(self) -> None:
        """
        Configures the application's logging system based on loaded configuration
        and persistent QSettings.
        """
        # Determine log level: QSettings (user override) > JSON config > Code Default (INFO)
        log_level_str = "INFO"  # Code default
        if self.config and "log_level" in self.config:
            log_level_str = self.config.get("log_level", "INFO").upper()
        if self.settings:  # QSettings might not be initialized on first call if _load_config fails early
            log_level_str = self.settings.value("log_level", log_level_str).upper()

        numeric_log_level = getattr(logging, log_level_str, logging.INFO)

        # Get root logger and set its level
        root_logger = logging.getLogger()  # Get the root logger
        root_logger.setLevel(numeric_log_level)

        # Clear any existing handlers to avoid duplication if this is called multiple times
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

        # Console Handler (always add for visibility)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)-8s - %(name)-15s - [%(threadName)-10s] - %(message)s')
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(numeric_log_level)  # Set its level too
        root_logger.addHandler(console_handler)

        # File Handler (if enabled in config)
        log_to_file = self.config.get("log_to_file", True)  # Default to True if not in config
        if log_to_file:
            try:
                # Ensure visuals directory exists for logs (if config places it there, else use CWD)
                log_dir = self.config.get("log_directory", VISUALS_BASE_PATH)  # Default to visuals dir
                os.makedirs(log_dir, exist_ok=True)
                log_file_path = os.path.join(log_dir, LOG_FILE_NAME)

                file_formatter = logging.Formatter(
                    '%(asctime)s - %(levelname)-8s - %(name)-20s - [%(threadName)-12s] - %(funcName)-20s - Lin:%(lineno)-4d - %(message)s')
                file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')  # Append mode
                file_handler.setFormatter(file_formatter)
                file_handler.setLevel(numeric_log_level)  # Set its level
                root_logger.addHandler(file_handler)
                logger.info(
                    f"Logging reconfigured. Level: {log_level_str}. Output to console and file: '{log_file_path}'.")
            except Exception as e_fh:
                logger.error(f"Failed to set up file logger at '{log_file_path}': {e_fh}. Logging to console only.",
                             exc_info=True)
        else:
            logger.info(
                f"Logging reconfigured. Level: {log_level_str}. Output to console only (file logging disabled).")

    def _load_app_icons(self) -> None:
        """Loads all necessary application icons from the ICONS_BASE_PATH."""
        logger.info(f"Loading application icons from '{ICONS_BASE_PATH}'...")
        os.makedirs(ICONS_BASE_PATH, exist_ok=True)  # Ensure icons directory exists

        icon_keys = [
            "app_icon", "send", "clear", "camera_on", "camera_off", "capture_image",
            "speak_on", "speak_off", "mic_on", "mic_off", "tts_stop",
            "save", "open", "settings", "exit", "zoom_in", "zoom_out",
            "module_status", "user_guide", "about", "status_ok", "status_warning"
        ]
        # Standard icon extensions to try
        extensions = ['.png', '.svg', '.ico', '.jpg']

        for key in icon_keys:
            found_icon = False
            for ext in extensions:
                icon_path = os.path.join(ICONS_BASE_PATH, key + ext)
                if os.path.exists(icon_path):
                    self.icons[key] = QIcon(icon_path)
                    logger.debug(f"Icon loaded: '{key}' from '{icon_path}'.")
                    found_icon = True
                    break
            if not found_icon:
                logger.warning(
                    f"Icon for '{key}' not found in '{ICONS_BASE_PATH}' with extensions {extensions}. Using default/empty icon.")
                self.icons[key] = QIcon()  # Empty QIcon as fallback

        # Set main window icon
        if "app_icon" in self.icons and not self.icons["app_icon"].isNull():
            self.setWindowIcon(self.icons["app_icon"])
            logger.info("Application window icon set.")
        else:
            logger.warning("Main application icon ('app_icon') not loaded. Window icon will be default.")
        logger.info("Icon loading process completed.")


    # --- UI Construction Methods ---
    def _init_ui(self) -> None:
        """
        Initializes the main User Interface, including window properties,
        menu bar, main panels (chat, robot, camera), and the control panel.
        This method constructs the entire visible structure of the application.
        """
        logger.info("Constructing Main UI in _init_ui...")
        self.setWindowTitle(QCoreApplication.translate("MainWindow", APP_TITLE_CONST))

        # Restore window geometry (size and position)
        default_size = QSize(*DEFAULT_WINDOW_SIZE)
        self.resize(self.settings.value("geometry", default_size, type=QSize))  # type=QSize for proper conversion
        saved_pos = self.settings.value("pos", None, type=QPoint)  # type=QPoint
        if saved_pos:
            self.move(saved_pos)
        else:  # Center window if no saved position
            try:
                screen_geometry = QApplication.desktop().screenGeometry()
                self.move(
                    (screen_geometry.width() - self.width()) // 2,
                    (screen_geometry.height() - self.height()) // 2
                )
            except Exception as e_screen:  # Fallback if desktop info fails
                logger.warning(f"Could not center window using screenGeometry: {e_screen}. Using default pos.")
                self.move(QPoint(100, 100))  # Arbitrary default

        # Create Menu Bar
        self._create_menu_bar()  # Assigns to self.menu_bar

        # Central Widget and Main Layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_vertical_layout = QVBoxLayout(central_widget)

        # Main Panels Layout (Chat, Robot, Camera side-by-side)
        main_panels_horizontal_layout = QHBoxLayout()

        # Create individual interface panels
        # These helper methods should return QGroupBox or QWidget instances
        chat_group = self._create_chat_interface()  # Assigns to self.chat_display, self.user_input etc.
        robot_group = self._create_robot_interface()  # Assigns to self.robot_appearance_widget_instance, self.status_labels
        camera_group = self._create_camera_interface()  # Assigns to self.cam_btn, self.filter_combo, self.camera_label etc.

        if chat_group: main_panels_horizontal_layout.addWidget(chat_group, stretch=LAYOUT_STRETCH_LEFT)
        if robot_group: main_panels_horizontal_layout.addWidget(robot_group, stretch=LAYOUT_STRETCH_CENTER)
        if camera_group: main_panels_horizontal_layout.addWidget(camera_group, stretch=LAYOUT_STRETCH_RIGHT)

        main_vertical_layout.addLayout(main_panels_horizontal_layout, stretch=1)  # Panels take most vertical space

        # Control Panel at the bottom
        control_panel_widget = self._create_control_panel()  # Assigns to self.theme_combo, self.voice_select_combo etc.
        if control_panel_widget:
            main_vertical_layout.addWidget(control_panel_widget)

        # Status Bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("padding-left: 5px;")

        # Module Status Icon in Status Bar
        self.module_status_icon_label = QLabel("")
        self.module_status_icon_label.setMinimumWidth(20)  # Ensure visibility
        self.module_status_icon_label.setToolTip(
            QCoreApplication.translate("MainWindow", "Module status (Tools > Module Status for details)")
        )
        self.status_bar.addPermanentWidget(self.module_status_icon_label)
        self._update_module_status_icon()  # Set initial icon

        # Apply current chat font size after UI elements are created
        if hasattr(self, 'chat_display') and self.chat_display:
            self._apply_chat_font_size()

        logger.info("Main UI panels and structure constructed.")

    def _create_menu_bar(self) -> None:
        """Creates and populates the main menu bar."""
        logger.debug("Creating menu bar...")
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # File Menu
        file_menu = self.menu_bar.addMenu(QCoreApplication.translate("MainWindow", "&File"))
        save_action = QAction(self.icons.get("save", QIcon()),
                              QCoreApplication.translate("MainWindow", "&Save Chat As..."), self)
        save_action.triggered.connect(self.save_chat_history_as_slot)
        file_menu.addAction(save_action)
        load_action = QAction(self.icons.get("open", QIcon()),
                              QCoreApplication.translate("MainWindow", "&Load Chat From..."), self)
        load_action.triggered.connect(self.load_chat_history_slot)
        file_menu.addAction(load_action)
        file_menu.addSeparator()
        settings_action = QAction(self.icons.get("settings", QIcon()),
                                  QCoreApplication.translate("MainWindow", "Se&ttings..."), self)
        settings_action.triggered.connect(self.open_settings_dialog_slot)
        file_menu.addAction(settings_action)
        file_menu.addSeparator()
        exit_action = QAction(self.icons.get("exit", QIcon()), QCoreApplication.translate("MainWindow", "E&xit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)  # self.close() will trigger closeEvent
        file_menu.addAction(exit_action)

        # View Menu
        view_menu = self.menu_bar.addMenu(QCoreApplication.translate("MainWindow", "&View"))
        self.theme_menu = QMenu(QCoreApplication.translate("MainWindow", "Application &Themes"), self)
        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.setExclusive(True)
        for theme_key in THEMES_CSS:  # THEMES_CSS is global from Part 1
            action = QAction(QCoreApplication.translate("MainWindow", theme_key), self, checkable=True)
            action.setData(theme_key)  # Store original key
            action.triggered.connect(self._handle_theme_action_triggered)
            self.theme_menu.addAction(action)
            self.theme_action_group.addAction(action)
        view_menu.addMenu(self.theme_menu)
        view_menu.addSeparator()
        zoom_in_action = QAction(self.icons.get("zoom_in", QIcon()),
                                 QCoreApplication.translate("MainWindow", "Zoom In Chat"), self)
        zoom_in_action.setShortcut(Qt.CTRL | Qt.Key_Plus)
        zoom_in_action.triggered.connect(self.zoom_in_chat)
        view_menu.addAction(zoom_in_action)
        zoom_out_action = QAction(self.icons.get("zoom_out", QIcon()),
                                  QCoreApplication.translate("MainWindow", "Zoom Out Chat"), self)
        zoom_out_action.setShortcut(Qt.CTRL | Qt.Key_Minus)
        zoom_out_action.triggered.connect(self.zoom_out_chat)
        view_menu.addAction(zoom_out_action)
        reset_zoom_action = QAction(QCoreApplication.translate("MainWindow", "Reset Chat Zoom"), self)
        reset_zoom_action.setShortcut(Qt.CTRL | Qt.Key_0)
        reset_zoom_action.triggered.connect(self.reset_chat_zoom)
        view_menu.addAction(reset_zoom_action)

        # Tools Menu
        tools_menu = self.menu_bar.addMenu(QCoreApplication.translate("MainWindow", "&Tools"))
        module_status_action = QAction(self.icons.get("module_status", QIcon()),
                                       QCoreApplication.translate("MainWindow", "&Module Status..."), self)
        module_status_action.triggered.connect(self.show_module_status_slot)
        tools_menu.addAction(module_status_action)
        interrupt_tts_action = QAction(self.icons.get("tts_stop", QIcon()),
                                       QCoreApplication.translate("MainWindow", "&Interrupt Speech"), self)
        interrupt_tts_action.setShortcut(Qt.CTRL | Qt.SHIFT | Qt.Key_S)
        interrupt_tts_action.triggered.connect(self.interrupt_tts_slot)
        tools_menu.addAction(interrupt_tts_action)

        # Help Menu
        help_menu = self.menu_bar.addMenu(QCoreApplication.translate("MainWindow", "&Help"))
        user_guide_action = QAction(self.icons.get("user_guide", QIcon()),
                                    QCoreApplication.translate("MainWindow", "&User Guide..."), self)
        user_guide_action.triggered.connect(self.show_user_guide_dialog_slot)
        help_menu.addAction(user_guide_action)
        about_action = QAction(self.icons.get("about", QIcon()),
                               QCoreApplication.translate("MainWindow", "&About {}...").format(APP_NAME_CONST), self)
        about_action.triggered.connect(self.show_about_dialog_slot)
        help_menu.addAction(about_action)
        logger.debug("Menu bar created.")

    def _create_chat_interface(self) -> QGroupBox:
        """Creates the chat interface QGroupBox."""
        logger.debug("Creating chat interface...")
        group_box = QGroupBox(QCoreApplication.translate("MainWindow", "Chat Interface"))
        layout = QVBoxLayout(group_box)

        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("ChatDisplay")  # For specific styling via QSS
        self.chat_display.setReadOnly(True)
        self.chat_display.setAcceptRichText(True)  # Important for HTML formatted messages
        self.chat_display.setToolTip(QCoreApplication.translate("MainWindow", "Conversation history"))
        layout.addWidget(self.chat_display, stretch=1)

        input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setObjectName("UserInput")  # For specific styling
        self.user_input.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "Type message or /help for commands...")
        )
        self.user_input.returnPressed.connect(self.send_input_slot)
        input_layout.addWidget(self.user_input, stretch=1)

        self.send_button = QToolButton()
        self.send_button.setIcon(self.icons.get("send", QIcon()))
        self.send_button.setIconSize(QSize(24, 24))
        self.send_button.setToolTip(QCoreApplication.translate("MainWindow", "Send Message"))
        self.send_button.setStyleSheet(
            "QToolButton { border: none; padding: 3px; } QToolButton:hover { background-color: rgba(0,0,0,0.1); }"
        )
        self.send_button.clicked.connect(self.send_input_slot)
        input_layout.addWidget(self.send_button)

        self.clear_chat_button = QToolButton()
        self.clear_chat_button.setIcon(self.icons.get("clear", QIcon()))
        self.clear_chat_button.setIconSize(QSize(24, 24))
        self.clear_chat_button.setToolTip(QCoreApplication.translate("MainWindow", "Clear Chat History"))
        self.clear_chat_button.setStyleSheet(
            "QToolButton { border: none; padding: 3px; } QToolButton:hover { background-color: rgba(0,0,0,0.1); }"
        )
        self.clear_chat_button.clicked.connect(self.clear_chat_slot)
        input_layout.addWidget(self.clear_chat_button)

        layout.addLayout(input_layout)
        logger.debug("Chat interface created.")
        return group_box

    def _create_robot_interface(self) -> QGroupBox:
        """Creates the robot interface QGroupBox, including the appearance widget."""
        logger.debug("Creating robot interface...")
        group_box = QGroupBox(QCoreApplication.translate("MainWindow", "Robot Interface"))
        layout = QVBoxLayout(group_box)

        status_layout = QHBoxLayout()
        self.status_labels = {  # Storing labels in a dictionary for easy access
            "power": QLabel(QCoreApplication.translate("MainWindow", "⚡ Pwr: ON")),
            "connection": QLabel(QCoreApplication.translate("MainWindow", "📶 Stat: Idle")),
            "emotion": QLabel(QCoreApplication.translate("MainWindow", "😊 Emo: Neutral"))
        }
        for key, lbl_widget in self.status_labels.items():
            lbl_widget.setToolTip(QCoreApplication.translate("MainWindow", f"Robot {key.capitalize()} Status"))
            status_layout.addWidget(lbl_widget)
        status_layout.addStretch(1)  # Push labels to the left
        layout.addLayout(status_layout)

        # Instantiate Robot Appearance Widget (Real or Dummy based on RobotAppearanceWidget_cls from Part 1)
        try:
            # RobotAppearanceWidget_cls was determined in Part 1.
            # If it's the AI version from external robot_appearance.py, it might take arguments.
            # For simplicity, assuming a default constructor or one that accepts parent.
            # The Dummy version from Part 1 takes (parent, **kwargs).
            self.robot_appearance_widget_instance = RobotAppearanceWidget_cls(self)  # Pass parent
            self.robot_appearance_widget_instance.setToolTip(
                QCoreApplication.translate("MainWindow", "Visual representation of UPDOGO Robot")
            )
            layout.addWidget(self.robot_appearance_widget_instance, stretch=1)
            logger.info(f"Robot appearance widget instantiated using: {RobotAppearanceWidget_cls.__name__}")
        except Exception as e_ra_inst:
            logger.error(
                f"Failed to instantiate RobotAppearanceWidget_cls ({RobotAppearanceWidget_cls.__name__}): {e_ra_inst}",
                exc_info=True)
            # Fallback display if instantiation fails catastrophically (though _cls should provide a Dummy)
            error_label = QLabel("Error: Robot Appearance module failed to load.\nPlease check logs.")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; border: 1px solid red; padding: 10px;")
            layout.addWidget(error_label, stretch=1)
            self.robot_appearance_widget_instance = None  # Ensure it's None

        logger.debug("Robot interface created.")
        return group_box

    def _create_camera_interface(self) -> QGroupBox:
        """Creates the camera/vision system interface QGroupBox."""
        logger.debug("Creating camera interface...")
        group_box = QGroupBox(QCoreApplication.translate("MainWindow", "Vision System"))
        layout = QVBoxLayout(group_box)

        controls_layout = QHBoxLayout()
        self.cam_btn = QPushButton()  # Text/Icon set by _update_camera_button_text
        self.cam_btn.setCheckable(True)
        self.cam_btn.clicked.connect(self.toggle_camera_slot)  # Pass checked state
        controls_layout.addWidget(self.cam_btn)

        self.filter_combo = QComboBox(self)
        self.raw_keys_for_filters = list(RAW_CAMERA_FILTERS.keys())  # Global from Part 1
        for raw_key in self.raw_keys_for_filters:
            self.filter_combo.addItem(QCoreApplication.translate("MainWindow", raw_key), raw_key)

        # Set initial selection for filter_combo based on self.current_camera_filter_key (from QSettings)
        try:
            initial_filter_idx = self.raw_keys_for_filters.index(self.current_camera_filter_key)
        except ValueError:  # Should not happen if current_camera_filter_key is valid from settings
            initial_filter_idx = 0
            logger.warning(
                f"Camera filter key '{self.current_camera_filter_key}' (from settings) not in RAW_CAMERA_FILTERS. Defaulting."
            )
        self.filter_combo.setCurrentIndex(initial_filter_idx)
        self.filter_combo.setToolTip(QCoreApplication.translate("MainWindow", "Select camera filter."))
        # Connect to the slot that handles both UI update and worker call
        self.filter_combo.currentIndexChanged.connect(self._handle_filter_combo_change_slot)
        controls_layout.addWidget(self.filter_combo)
        controls_layout.addStretch(1)

        self.capture_btn = QPushButton(self.icons.get("capture_image", QIcon()),
                                       QCoreApplication.translate("MainWindow", "Capture"))
        self.capture_btn.setToolTip(QCoreApplication.translate("MainWindow", "Save current camera frame"))
        self.capture_btn.clicked.connect(self.capture_image_slot)
        self.capture_btn.setEnabled(False)  # Initially disabled until camera is on
        controls_layout.addWidget(self.capture_btn)
        layout.addLayout(controls_layout)

        self.camera_label = QLabel(QCoreApplication.translate("MainWindow", "(Camera is Off)"))
        self.camera_label.setObjectName("CameraLabel")  # For specific styling (e.g., black background)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.camera_label.setMinimumSize(QSize(320, 240))  # Ensure a decent minimum size
        layout.addWidget(self.camera_label, stretch=1)

        self._update_camera_button_text()  # Set initial button text/icon for cam_btn
        logger.debug("Camera interface created.")
        return group_box

    def _create_control_panel(self) -> QWidget:
        """Creates the main control panel widget with various settings controls."""
        logger.debug("Creating control panel...")
        panel_widget = QWidget()
        layout = QGridLayout(panel_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(8)
        current_row = 0

        # Theme Selection (ComboBox)
        layout.addWidget(QLabel(QCoreApplication.translate("MainWindow", "Theme:")), current_row, 0, Qt.AlignRight)
        self.theme_combo = QComboBox()
        self.theme_combo_keys = list(THEMES_CSS.keys())  # Global from Part 1
        for theme_key_iter in self.theme_combo_keys:
            self.theme_combo.addItem(QCoreApplication.translate("MainWindow", theme_key_iter), theme_key_iter)

        # Set initial selection for theme_combo based on self.current_theme_name (from QSettings)
        try:
            initial_theme_idx = self.theme_combo_keys.index(self.current_theme_name)
        except ValueError:  # Should not happen if current_theme_name is valid from settings
            initial_theme_idx = 0
            logger.warning(f"Theme key '{self.current_theme_name}' (from settings) not in THEMES_CSS. Defaulting.")
        self.theme_combo.setCurrentIndex(initial_theme_idx)
        self.theme_combo.setToolTip(
            QCoreApplication.translate("MainWindow", "Select visual theme for the application."))
        self.theme_combo.currentIndexChanged.connect(self._handle_theme_combo_change_slot)
        layout.addWidget(self.theme_combo, current_row, 1, 1, 2)  # Span 2 columns

        # Voice Input/Output and TTS Stop Buttons (using QToolButton for compact icon buttons)
        self.voice_input_btn = QToolButton()
        self.voice_input_btn.setCheckable(True)
        self.voice_input_btn.setIconSize(QSize(22, 22))
        self.voice_input_btn.setStyleSheet(
            "QToolButton{border:none;padding:2px} QToolButton:hover{background-color:rgba(0,0,0,0.1)} "
            "QToolButton:checked{background-color:rgba(0,100,0,0.2)}"
        )
        self.voice_input_btn.clicked.connect(self.toggle_voice_input_slot)  # Pass checked state
        layout.addWidget(self.voice_input_btn, current_row, 3, Qt.AlignCenter)

        self.voice_output_btn = QToolButton()
        self.voice_output_btn.setCheckable(True)
        self.voice_output_btn.setChecked(self.voice_output_enabled)  # Set from QSettings
        self.voice_output_btn.setIconSize(QSize(22, 22))
        self.voice_output_btn.setStyleSheet(
            "QToolButton{border:none;padding:2px} QToolButton:hover{background-color:rgba(0,0,0,0.1)} "
            "QToolButton:checked{background-color:rgba(0,100,0,0.2)}"
        )
        self.voice_output_btn.clicked.connect(self.toggle_voice_output_slot)  # Pass checked state
        layout.addWidget(self.voice_output_btn, current_row, 4, Qt.AlignCenter)

        self.tts_stop_button = QToolButton()
        self.tts_stop_button.setIcon(self.icons.get("tts_stop", QIcon()))
        self.tts_stop_button.setIconSize(QSize(20, 20))
        self.tts_stop_button.setStyleSheet(
            "QToolButton{border:none;padding:2px} QToolButton:hover{background-color:rgba(200,0,0,0.2)}"
        )
        self.tts_stop_button.setToolTip(QCoreApplication.translate("MainWindow", "Stop current speech output"))
        self.tts_stop_button.clicked.connect(self.interrupt_tts_slot)
        layout.addWidget(self.tts_stop_button, current_row, 5, Qt.AlignCenter)
        current_row += 1

        # TTS Voice Selection ComboBox
        layout.addWidget(QLabel(QCoreApplication.translate("MainWindow", "TTS Voice:")), current_row, 0, Qt.AlignRight)
        self.voice_select_combo = QComboBox()
        self.voice_select_combo.setMinimumWidth(200)
        self.voice_select_combo.setToolTip(QCoreApplication.translate("MainWindow", "Select speech synthesis voice."))
        self.voice_select_combo.view().setMinimumWidth(250)  # Ensure dropdown list is wide enough
        self.voice_select_combo.currentIndexChanged.connect(self.change_tts_voice_selection_slot)  # Pass index
        layout.addWidget(self.voice_select_combo, current_row, 1, 1, 5)  # Span 5 columns
        current_row += 1

        # TTS Rate Slider
        layout.addWidget(QLabel(QCoreApplication.translate("MainWindow", "TTS Rate:")), current_row, 0, Qt.AlignRight)
        self.rate_slider = QSlider(Qt.Horizontal)
        self.rate_slider.setRange(TTS_DEFAULTS["min_rate"], TTS_DEFAULTS["max_rate"])  # Global from Part 1
        self.rate_slider.setValue(self.settings.value("tts_rate", TTS_DEFAULTS["rate"], type=int))
        self.rate_slider.setToolTip(
            QCoreApplication.translate("MainWindow", "Adjust speech rate ({}-{}).").format(
                TTS_DEFAULTS['min_rate'], TTS_DEFAULTS['max_rate']
            )
        )
        self.rate_slider.valueChanged.connect(self.change_tts_rate_slot)  # Pass value
        layout.addWidget(self.rate_slider, current_row, 1, 1, 4)  # Span 4 columns
        self.rate_label = QLabel(str(self.rate_slider.value()))
        self.rate_label.setMinimumWidth(35)
        layout.addWidget(self.rate_label, current_row, 5, Qt.AlignLeft)
        current_row += 1

        # TTS Volume Slider
        layout.addWidget(QLabel(QCoreApplication.translate("MainWindow", "TTS Volume:")), current_row, 0, Qt.AlignRight)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(TTS_DEFAULTS["min_volume"], TTS_DEFAULTS["max_volume"])
        self.volume_slider.setValue(self.settings.value("tts_volume", TTS_DEFAULTS["volume"], type=int))
        self.volume_slider.setToolTip(
            QCoreApplication.translate("MainWindow", "Adjust speech volume ({}-{}%).").format(
                TTS_DEFAULTS['min_volume'], TTS_DEFAULTS['max_volume']
            )
        )
        self.volume_slider.valueChanged.connect(self.change_tts_volume_slot)  # Pass value
        layout.addWidget(self.volume_slider, current_row, 1, 1, 4)  # Span 4 columns
        self.volume_label = QLabel(str(self.volume_slider.value()))
        self.volume_label.setMinimumWidth(35)
        layout.addWidget(self.volume_label, current_row, 5, Qt.AlignLeft)
        # current_row += 1 # If more rows needed

        # Set column stretches for the grid to allow sliders to expand
        layout.setColumnStretch(1, 1)  # Column for sliders and combos (expandable)
        layout.setColumnStretch(2, 1)  # (If spanned elements like combos use this)

        # Update button texts/icons now that they are created
        self._update_voice_output_button_text()
        self._update_voice_input_button_text()

        logger.debug("Control panel created.")
        return panel_widget

    # --- Theme and Chat Appearance Logic ---
    def _handle_theme_action_triggered(self) -> None:
        """Handles theme selection from the menu bar."""
        action = self.sender()
        if isinstance(action, QAction) and action.isChecked():
            theme_key = action.data()  # Original theme key
            if theme_key and theme_key in THEMES_CSS:
                self._apply_theme(theme_key)
            else:
                logger.warning(f"Theme key '{theme_key}' from menu action not found or invalid.")

    def _handle_theme_combo_change_slot(self, index: int) -> None:
        """Handles theme selection from the ComboBox in the control panel."""
        if hasattr(self, 'theme_combo') and self.theme_combo and index >= 0:
            theme_key = self.theme_combo.itemData(index)  # Original theme key from item data
            if theme_key and theme_key in THEMES_CSS:
                self._apply_theme(theme_key)
            else:
                logger.warning(f"Theme key '{theme_key}' from combobox not found or invalid.")

    def _apply_theme(self, theme_name_key: str) -> None:
        """Applies the selected theme stylesheet and updates related UI elements."""
        logger.info(f"Applying theme: '{theme_name_key}'")
        if theme_name_key in THEMES_CSS:
            try:
                self.setStyleSheet(THEMES_CSS[theme_name_key])
                self.current_theme_name = theme_name_key
                if self.settings: self.settings.setValue("theme", self.current_theme_name)

                self._update_chat_colors(self.current_theme_name)
                self._update_chat_display_style()  # Applies font size and re-evaluates chat display colors

                # Provide user feedback
                self.update_status(
                    QCoreApplication.translate("MainWindow", "Theme applied: {}").format(
                        QCoreApplication.translate("MainWindow", self.current_theme_name)  # Translate display name
                    ), 3000
                )
                logger.info(f"Theme successfully applied: {self.current_theme_name}")
            except Exception as e_theme:
                logger.error(f"Error applying theme '{self.current_theme_name}': {e_theme}", exc_info=True)
                self.update_status(QCoreApplication.translate("MainWindow", "Error applying theme."), 3000)
        else:
            logger.warning(f"Attempted to apply unknown theme key: '{theme_name_key}'")

        self._update_theme_menu_and_combo_selection()  # Sync menu and combo with current_theme_name
        self._update_all_button_states()  # Ensure button icons/styles reflect new theme if needed

    def _update_theme_menu_and_combo_selection(self) -> None:
        """Synchronizes the theme menu check state and combobox selection with the current theme."""
        # Sync Theme Menu (QActionGroup)
        if hasattr(self, 'theme_action_group') and self.theme_action_group:
            for action in self.theme_action_group.actions():
                if action.data() == self.current_theme_name:
                    action.setChecked(True)
                    break
        # Sync Theme ComboBox
        if hasattr(self, 'theme_combo') and self.theme_combo:
            self.theme_combo.blockSignals(True)  # Prevent signal emission during programmatic change
            for i in range(self.theme_combo.count()):
                if self.theme_combo.itemData(i) == self.current_theme_name:
                    self.theme_combo.setCurrentIndex(i)
                    break
            self.theme_combo.blockSignals(False)
        logger.debug(f"Theme menu and combobox synced to: {self.current_theme_name}")

    def _update_chat_colors(self, theme_name_key: str) -> None:
        """Updates CHAT_STYLES dictionary based on whether the current theme is considered 'dark'."""
        # Simple heuristic for dark themes - can be expanded
        is_dark = any(s in theme_name_key.lower() for s in [
            'dark', 'night', 'ash', 'cyberpunk', 'purple', 'ruby', 'emerald', 'sapphire',
            'volcanic', 'azure dreams', 'emerald twilight', 'crimson nightfall',
            'golden amethyst', 'mystic forest', 'ubuntu ambiance', 'charcoal gray'  # Added more darks
        ])
        logger.debug(f"Theme '{theme_name_key}' identified as {'dark' if is_dark else 'light'} for chat colors.")

        CHAT_STYLES['current_text_color'] = CHAT_STYLES['default_text_color_dark'] if is_dark else CHAT_STYLES[
            'default_text_color_light']
        CHAT_STYLES['current_user_bg'] = CHAT_STYLES['user_bg_color_dark'] if is_dark else CHAT_STYLES[
            'user_bg_color_light']
        CHAT_STYLES['current_robot_bg'] = CHAT_STYLES['robot_bg_color_dark'] if is_dark else CHAT_STYLES[
            'robot_bg_color_light']
        CHAT_STYLES['current_error_bg'] = CHAT_STYLES['error_bg_color_dark'] if is_dark else CHAT_STYLES[
            'error_bg_color_light']
        CHAT_STYLES['current_user_border'] = CHAT_STYLES['user_border_dark'] if is_dark else CHAT_STYLES[
            'user_border_light']
        CHAT_STYLES['current_robot_border'] = CHAT_STYLES['robot_border_dark'] if is_dark else CHAT_STYLES[
            'robot_border_light']
        CHAT_STYLES['current_error_border_color'] = CHAT_STYLES['error_border_color_dark'] if is_dark else CHAT_STYLES[
            'error_border_color_light']
        CHAT_STYLES['current_timestamp_color'] = CHAT_STYLES['timestamp_color_dark'] if is_dark else CHAT_STYLES[
            'timestamp_color_light']
        logger.debug("CHAT_STYLES dictionary updated based on theme.")

    def _update_chat_display_style(self) -> None:
        """
        Re-applies styles to the chat display.
        Mainly ensures font size is current. Background/border are typically
        handled by the main theme's QSS targeting QTextEdit#ChatDisplay.
        """
        if hasattr(self, 'chat_display') and self.chat_display:
            self._apply_chat_font_size()  # Ensure font size is correct
            # If chat display's specific background needs to be set outside QSS:
            # palette = self.chat_display.palette()
            # palette.setColor(QPalette.Base, QColor(CHAT_STYLES['current_chat_bg_color'])) # Example
            # self.chat_display.setPalette(palette)
            logger.debug("Chat display style updated (font size applied).")

    @pyqtSlot()
    def zoom_in_chat(self) -> None:
        """Increases chat display font size."""
        self.current_chat_font_size = min(24, self.current_chat_font_size + 1)
        self._apply_chat_font_size()
        if self.settings: self.settings.setValue("chat_font_size", self.current_chat_font_size)
        logger.debug(f"Chat zoomed in. New font size: {self.current_chat_font_size}pt")

    @pyqtSlot()
    def zoom_out_chat(self) -> None:
        """Decreases chat display font size."""
        self.current_chat_font_size = max(7, self.current_chat_font_size - 1)
        self._apply_chat_font_size()
        if self.settings: self.settings.setValue("chat_font_size", self.current_chat_font_size)
        logger.debug(f"Chat zoomed out. New font size: {self.current_chat_font_size}pt")

    @pyqtSlot()
    def reset_chat_zoom(self) -> None:
        """Resets chat display font size to the default."""
        self.current_chat_font_size = self.config.get("display_settings", {}).get("chat_font_size",
                                                                                  DEFAULT_CHAT_FONT_SIZE)
        self._apply_chat_font_size()
        if self.settings: self.settings.setValue("chat_font_size", self.current_chat_font_size)
        logger.debug(f"Chat zoom reset. New font size: {self.current_chat_font_size}pt")

    def _apply_chat_font_size(self) -> None:
        """Applies the current_chat_font_size to the chat_display widget."""
        if hasattr(self, 'chat_display') and self.chat_display:
            font = self.chat_display.font()
            font.setPointSize(self.current_chat_font_size)
            self.chat_display.setFont(font)
            # For QTextBrowser, sometimes need to update document's default font too
            # self.chat_display.document().setDefaultFont(font)
            self.update_status(
                QCoreApplication.translate("MainWindow", "Chat font size: {}pt").format(self.current_chat_font_size),
                1500
            )
            logger.debug(f"Chat base font size set to {self.current_chat_font_size}pt in chat_display.")

    def add_chat_message(self, sender: str, message_details: List[Tuple[str, str]], is_error: bool = False) -> None:
        """
        Adds a formatted message to the chat display.
        Uses HTML templates defined globally and styles from CHAT_STYLES.
        """
        if not hasattr(self, 'chat_display') or not self.chat_display:
            logger.error("add_chat_message called, but chat_display is not available.")
            return

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        msg_html_parts: List[str] = []
        base_font_size = self.current_chat_font_size
        timestamp_font_size = max(7, base_font_size - 2)
        sender_name_font_size = base_font_size  # Can be adjusted, e.g., base_font_size + 1 for bold

        # Define styles for different message parts using CHAT_STYLES (global, Part 1)
        tag_styles: Dict[str, str] = {
            "normal": f"color:{CHAT_STYLES['current_text_color']};",
            "info": f"color:{CHAT_STYLES['info_color']}; font-style:italic; display:block;",
            "original": f"color:{CHAT_STYLES['context_color']}; font-style:italic; font-size:{max(7, base_font_size - 1)}pt; display:block; margin-top:3px;",
            "corrected": f"color:{CHAT_STYLES['correction_color']}; font-weight:bold;",
            "suggestion_msg": f"color:{CHAT_STYLES['suggestion_color']};",
            "error": f"color:{CHAT_STYLES['error_color']}; font-weight:bold;",  # For text within an error bubble
            "fallback_info": f"color:{CHAT_STYLES['context_color']}; font-style:italic;",
            "system": f"color:{CHAT_STYLES['current_timestamp_color']}; font-style:italic;",
            # For system messages like "/clear"
            "warning": f"color:{CHAT_STYLES.get('warning_color', 'orange')}; font-weight:bold;"
        }

        for tag, text_content in message_details:
            # Escape HTML special characters in text_content to prevent XSS or display issues
            escaped_text = str(text_content).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace(
                '\n', '<br>')
            style = tag_styles.get(tag, tag_styles["normal"])  # Fallback to normal style
            msg_html_parts.append(f'<span style="{style}">{escaped_text}</span>')

        message_html_content = "<br>".join(filter(None, msg_html_parts))  # Filter out empty parts

        final_html_output = ""
        robot_display_name_tr = QCoreApplication.translate("MainWindow", APP_NAME_CONST)

        common_args = {
            "message_html": message_html_content, "timestamp": timestamp,
            "common_style": COMMON_BUBBLE_STYLE,  # Global from Part 1
            "text_color": CHAT_STYLES['current_text_color'],
            "timestamp_color": CHAT_STYLES['current_timestamp_color'],
            "font_size": base_font_size, "timestamp_font_size": timestamp_font_size,
            "font_size_plus_one": sender_name_font_size,
            "robot_name": robot_display_name_tr
        }

        if is_error:
            final_html_output = ERROR_MSG_TEMPLATE.format(  # Global from Part 1
                bg_color=CHAT_STYLES['current_error_bg'],
                error_border_color=CHAT_STYLES['current_error_border_color'],
                error_text_color=CHAT_STYLES['error_color'],  # Main text color for error
                error_title_color=CHAT_STYLES['error_color'],  # Title color for "System Error:"
                **common_args
            )
        elif sender == "User":
            final_html_output = USER_MSG_TEMPLATE.format(  # Global from Part 1
                bg_color=CHAT_STYLES['current_user_bg'],
                border_color=CHAT_STYLES['current_user_border'],
                **common_args
            )
        elif sender == robot_display_name_tr or sender == APP_NAME_CONST:  # Handle raw and translated name
            final_html_output = ROBOT_MSG_TEMPLATE.format(  # Global from Part 1
                bg_color=CHAT_STYLES['current_robot_bg'],
                border_color=CHAT_STYLES['current_robot_border'],
                name_color=CHAT_STYLES['robot_name_color'],
                **common_args
            )
        elif sender == "System":  # For non-error system messages (e.g., command feedback)
            final_html_output = SYSTEM_MSG_TEMPLATE.format(  # Global from Part 1
                message_html=message_html_content,  # System messages might not use bubble styles
                timestamp_color=CHAT_STYLES['current_timestamp_color'],
                timestamp_font_size=timestamp_font_size,
                timestamp=timestamp
            )
        else:  # Fallback for unknown sender (should ideally not happen)
            logger.warning(f"add_chat_message called with unknown sender: '{sender}'. Formatting as generic message.")
            # Basic formatting for unknown sender
            final_html_output = (
                f'<div style="margin:5px; padding:8px; background:#eee; border-radius:8px; color:#333;">'
                f'<strong>{sender}:</strong> {message_html_content} '
                f'<span style="font-size:{timestamp_font_size - 1}pt; color:#888;">({timestamp})</span></div>')

        if final_html_output:
            self.chat_display.append(final_html_output)
            # Scroll to bottom. Using QTimer.singleShot(0, ...) ensures it happens after layout updates.
            QTimer.singleShot(0, lambda: self.chat_display.verticalScrollBar().setValue(
                self.chat_display.verticalScrollBar().maximum()))
        logger.debug(f"Added chat message from '{sender}'.")

    # --- Button State Update Methods ---
    def _update_all_button_states(self) -> None:
        """Updates the text, icon, and tooltip of all stateful buttons."""
        logger.debug("Updating all button states...")
        if hasattr(self, 'cam_btn') and self.cam_btn: self._update_camera_button_text()
        if hasattr(self, 'voice_output_btn') and self.voice_output_btn: self._update_voice_output_button_text()
        if hasattr(self, 'voice_input_btn') and self.voice_input_btn: self._update_voice_input_button_text()
        if hasattr(self, 'capture_btn') and self.capture_btn: self.capture_btn.setEnabled(self.camera_on)

    def _update_camera_button_text(self) -> None:
        """Updates the camera toggle button's text, icon, and tooltip based on camera_on state."""
        if hasattr(self, 'cam_btn') and self.cam_btn:
            text = QCoreApplication.translate("MainWindow", "Stop Cam") if self.camera_on else \
                QCoreApplication.translate("MainWindow", "Start Cam")
            icon_name = "camera_off" if self.camera_on else "camera_on"
            icon = self.icons.get(icon_name, QIcon())
            tooltip = QCoreApplication.translate("MainWindow", "Stop camera stream") if self.camera_on else \
                QCoreApplication.translate("MainWindow", "Start camera stream")

            self.cam_btn.setText(text)
            self.cam_btn.setIcon(icon)
            self.cam_btn.setToolTip(tooltip)
            self.cam_btn.setChecked(self.camera_on)  # Synchronize checked state with internal flag
        if hasattr(self, 'capture_btn') and self.capture_btn:
            self.capture_btn.setEnabled(self.camera_on)  # Enable/disable capture button

    def _update_voice_output_button_text(self) -> None:
        """Updates the voice output toggle button's icon and tooltip."""
        if hasattr(self, 'voice_output_btn') and self.voice_output_btn:
            icon_name = "speak_on" if self.voice_output_enabled else "speak_off"
            icon = self.icons.get(icon_name, QIcon())
            tooltip = (QCoreApplication.translate("MainWindow", "Voice Output is ON - Click to Mute")
                       if self.voice_output_enabled else
                       QCoreApplication.translate("MainWindow", "Voice Output is OFF - Click to Unmute"))
            self.voice_output_btn.setIcon(icon)
            self.voice_output_btn.setToolTip(tooltip)
            self.voice_output_btn.setChecked(self.voice_output_enabled)

    def _update_voice_input_button_text(self) -> None:
        """Updates the voice input toggle button's icon and tooltip."""
        if hasattr(self, 'voice_input_btn') and self.voice_input_btn:
            icon_name = "mic_on" if self.voice_input_on else "mic_off"
            icon = self.icons.get(icon_name, QIcon())
            tooltip = (QCoreApplication.translate("MainWindow", "Voice Input is ON - Click to Stop Listening")
                       if self.voice_input_on else
                       QCoreApplication.translate("MainWindow", "Voice Input is OFF - Click to Start Listening"))
            self.voice_input_btn.setIcon(icon)
            self.voice_input_btn.setToolTip(tooltip)
            self.voice_input_btn.setChecked(self.voice_input_on)

    # --- Dialog Invocation Slots & Related Logic ---
    @pyqtSlot()
    def show_about_dialog_slot(self) -> None:
        """Displays the 'About' dialog."""
        logger.debug("Showing AboutDialog...")
        # self.robot_info_direct_instance was created in _perform_full_initialization
        if self.robot_info_direct_instance:
            dialog = AboutDialog(self, self.robot_info_direct_instance)
            dialog.exec_()
        else:
            logger.error("Cannot show AboutDialog: robot_info_direct_instance is None.")
            QMessageBox.warning(self, QCoreApplication.translate("MainWindow", "Error"),
                                QCoreApplication.translate("MainWindow", "About information is currently unavailable."))

    @pyqtSlot()
    def open_settings_dialog_slot(self) -> None:
        """Opens the settings dialog."""
        logger.debug("Opening SettingsDialog...")
        if self.settings and self.config is not None:  # self.config can be empty dict but not None
            dialog = SettingsDialog(self, self.settings, self.config)
            dialog.settings_changed_signal.connect(self.handle_settings_changed)
            if dialog.exec_():  # True if Ok/Apply accepted
                logger.info("Settings dialog accepted by user.")
                # Changes are applied via handle_settings_changed through Apply button or Ok.
            else:
                logger.info("Settings dialog cancelled by user.")
        else:
            logger.error("Cannot open SettingsDialog: QSettings or config not initialized.")
            QMessageBox.warning(self, QCoreApplication.translate("MainWindow", "Error"),
                                QCoreApplication.translate("MainWindow", "Settings are currently unavailable."))

    @pyqtSlot()
    def handle_settings_changed(self) -> None:
        """Handles the settings_changed_signal from SettingsDialog."""
        logger.info("Handling settings_changed signal from SettingsDialog...")
        if not self.settings:
            logger.error("Cannot handle settings changed: QSettings not available.")
            return

        # Re-apply log level from settings
        # Note: _setup_logging is now more robust and handles this.
        # We might just need to call it again, or a more specific part of it.
        logger.info("Re-applying log level from changed settings...")
        self._setup_logging()  # This reconfigures handlers with new level from self.settings

        # Re-apply chat font size
        new_font_size = self.settings.value("chat_font_size", DEFAULT_CHAT_FONT_SIZE, type=int)
        if self.current_chat_font_size != new_font_size:
            self.current_chat_font_size = new_font_size
            self._apply_chat_font_size()
            logger.info(f"Chat font size re-applied from settings: {self.current_chat_font_size}pt")

        self.update_status(QCoreApplication.translate("MainWindow", "Settings updated and applied."), 3000)

    @pyqtSlot()
    def show_user_guide_dialog_slot(self) -> None:
        """Displays the User Guide dialog."""
        logger.debug("Showing UserGuideDialog...")
        dialog = UserGuideDialog(self)
        dialog.exec_()

    @pyqtSlot()
    def show_module_status_slot(self) -> None:
        """Displays a dialog showing the status of loaded modules."""
        logger.debug("Showing Module Status dialog...")
        active_modules, fallback_modules = self._get_module_statuses()

        message = f"<b>{QCoreApplication.translate('MainWindow', 'Active Components (Real Modules Loaded):')}</b><br>"
        message += (', '.join(active_modules) if active_modules else
                    QCoreApplication.translate('MainWindow', 'None currently active or fully initialized.'))
        message += "<br><br>"

        message += f"<b>{QCoreApplication.translate('MainWindow', 'Components Using Fallbacks (Dummy Modules):')}</b><br>"
        message += (', '.join(fallback_modules) if fallback_modules else
                    QCoreApplication.translate('MainWindow', 'All components appear to be loaded without fallbacks.'))

        if MISSING_MODULES:  # Global list from Part 1 import attempts
            message += f"<br><br><b>{QCoreApplication.translate('MainWindow', 'Specifically Failed Imports (Check log for details):')}</b><br>"
            message += ', '.join(MISSING_MODULES)

        QMessageBox.information(self, QCoreApplication.translate("MainWindow", "Module Status"), message)
        self._update_module_status_icon()  # Refresh icon just in case something changed programmatically

    def _get_module_statuses(self) -> Tuple[List[str], List[str]]:
        """
        Determines which components are using real modules vs. fallbacks.
        Checks instantiated workers and global _cls variables.
        """
        active_display_names: List[str] = []
        fallback_display_names: List[str] = []

        # Map of display names to their corresponding _cls variables (from Part 1)
        # and an optional check if they are managed as a worker in self.workers
        module_map: Dict[str, Tuple[Type, bool]] = {
            "Emotion Engine": (EmotionWorker_cls, True),
            "Robot Appearance Renderer": (RobotAppearanceWidget_cls, False),
            # Instantiated directly, not in self.workers
            "TTS Engine": (TTSWorker_cls, True),
            "Voice Listener (STT)": (VoiceListenerWorker_cls, True),
            "NLP System Core": (NLPWorker_cls, True),
            "Robot Information Service": (RobotInfoModule_for_deps, False),  # Used as dependency, and direct for About
            "Grammar System (for NLP)": (GrammarSystem_for_deps, False),  # Dependency
            "Multi-Lang Corrector (for NLP)": (MultiLangCorrector_for_deps, False)  # Dependency
        }

        for display_name, (cls_variable, is_managed_worker) in module_map.items():
            is_dummy = "Dummy" in cls_variable.__name__

            # For managed workers, double-check if their instance in self.workers matches the _cls type
            if is_managed_worker:
                worker_name_key = display_name.lower().replace(" (stt)", "").replace(" (for nlp)", "").replace(" ",
                                                                                                               "_").replace(
                    "_engine", "").replace("_core", "").replace("_renderer", "").replace("_service", "").replace(
                    "_system", "")  # Approximate key for self.workers
                worker_data = self.workers.get(worker_name_key)
                if worker_data and worker_data.get('worker'):
                    # If worker instance exists, its type is more definitive than the _cls variable
                    # (though they should ideally align)
                    is_dummy = "Dummy" in worker_data['worker'].__class__.__name__
                # If worker_data is missing, the _cls based is_dummy remains our best guess.

            if is_dummy:
                fallback_display_names.append(display_name)
            else:
                active_display_names.append(display_name)

        # Add any from MISSING_MODULES that aren't already captured by a dummy class name
        for missing_file_hint in MISSING_MODULES:
            # Try to make a nice display name from the file hint
            display_hint = missing_file_hint.replace(".py", "").replace("_", " ").title()
            if not any(display_hint in name for name in fallback_display_names) and \
                    not any(display_hint in name for name in active_display_names):
                fallback_display_names.append(f"{display_hint} (Import Failed)")

        return sorted(list(set(active_display_names))), sorted(list(set(fallback_display_names)))

    def _update_module_status_icon(self) -> None:
        """Updates the module status icon in the status bar based on loaded modules."""
        if hasattr(self, 'module_status_icon_label') and self.module_status_icon_label:
            _, fallback_modules = self._get_module_statuses()
            # Consider an issue if MISSING_MODULES has entries OR if any critical module is in fallback_modules.
            # For simplicity now, any fallback or missing import is a "warning".
            is_issue = bool(MISSING_MODULES or fallback_modules)

            icon_name = "status_warning" if is_issue else "status_ok"
            tooltip_text = (QCoreApplication.translate("MainWindow",
                                                       "One or more modules have issues, are using fallbacks, or failed to import.")
                            if is_issue else
                            QCoreApplication.translate("MainWindow",
                                                       "All modules appear to be operating nominally or as configured."))

            # Use icons loaded in _load_app_icons, with QIcon.fromTheme as a further fallback
            icon_to_use = self.icons.get(icon_name, QIcon.fromTheme(
                "dialog-warning-symbolic" if is_issue else "emblem-ok-symbolic",
                # Symbolic for better theme integration
                QIcon.fromTheme("dialog-warning" if is_issue else "emblem-ok")  # Fallback non-symbolic
            ))

            if not icon_to_use.isNull():
                self.module_status_icon_label.setPixmap(icon_to_use.pixmap(QSize(16, 16)))
            else:  # Absolute fallback if no icons load
                self.module_status_icon_label.setText("⚠️" if is_issue else "✔️")
            self.module_status_icon_label.setToolTip(tooltip_text)
            logger.debug(f"Module status icon updated. Issue: {is_issue}")

    # --- Chat History Slots ---
    @pyqtSlot()
    def save_chat_history_as_slot(self) -> None:
        """Saves the current chat history to a file (HTML or TXT)."""
        logger.debug("Save chat history slot triggered.")
        if not hasattr(self, 'chat_display') or not self.chat_display: return

        default_dir = self.settings.value("last_chat_save_path", os.getcwd(), type=str)
        default_filename = os.path.join(default_dir, DEFAULT_CHAT_HISTORY_FILE)

        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog # Uncomment if native dialog causes issues
        file_name, selected_filter = QFileDialog.getSaveFileName(
            self, QCoreApplication.translate("MainWindow", "Save Chat As..."), default_filename,
            QCoreApplication.translate("MainWindow", "HTML files (*.html *.htm);;Text files (*.txt);;All files (*)"),
            "", options
        )
        if file_name:
            self.settings.setValue("last_chat_save_path", os.path.dirname(file_name))

            final_file_name = file_name  # Ensure correct extension based on filter
            if selected_filter.startswith(QCoreApplication.translate("MainWindow", "HTML files")) and \
                    not (final_file_name.lower().endswith(".html") or final_file_name.lower().endswith(".htm")):
                final_file_name += ".html"
            elif selected_filter.startswith(QCoreApplication.translate("MainWindow", "Text files")) and \
                    not final_file_name.lower().endswith(".txt"):
                final_file_name += ".txt"
            try:
                content_to_save = (self.chat_display.toHtml()
                                   if final_file_name.lower().endswith((".html", ".htm"))
                                   else self.chat_display.toPlainText())
                with open(final_file_name, 'w', encoding='utf-8') as f:
                    f.write(content_to_save)
                self.update_status(
                    QCoreApplication.translate("MainWindow", "Chat history saved to: {}").format(
                        os.path.basename(final_file_name)), 3000
                )
                logger.info(f"Chat history successfully saved to '{final_file_name}'.")
            except Exception as e_save:
                QMessageBox.warning(self, QCoreApplication.translate("MainWindow", "Save Error"),
                                    QCoreApplication.translate("MainWindow", "Could not save chat history: {}").format(
                                        str(e_save)))
                logger.error(f"Error saving chat history to '{final_file_name}': {e_save}", exc_info=True)

    @pyqtSlot()
    def load_chat_history_slot(self) -> None:
        """Loads chat history from a file (HTML or TXT) into the chat display."""
        logger.debug("Load chat history slot triggered.")
        if not hasattr(self, 'chat_display') or not self.chat_display: return

        default_path = self.settings.value("last_chat_load_path", os.getcwd(), type=str)
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, QCoreApplication.translate("MainWindow", "Load Chat History"), default_path,
            QCoreApplication.translate("MainWindow", "HTML files (*.html *.htm);;Text files (*.txt);;All files (*)"),
            "", options
        )
        if file_name:
            self.settings.setValue("last_chat_load_path", os.path.dirname(file_name))
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    content_loaded = f.read()

                reply = QMessageBox.question(
                    self, QCoreApplication.translate("MainWindow", "Load Chat"),
                    QCoreApplication.translate("MainWindow", "Append to current chat or replace it?"),
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,  # Yes=Append, No=Replace
                    QMessageBox.Yes  # Default to Append
                )
                if reply == QMessageBox.Cancel: return
                if reply == QMessageBox.No: self.chat_display.clear()  # Replace

                # Append content
                if file_name.lower().endswith((".html", ".htm")):
                    self.chat_display.append(content_loaded)  # Append HTML directly
                else:  # Plain text, add line by line formatted as system info messages
                    for i, line_text in enumerate(content_loaded.splitlines()):
                        if line_text.strip():
                            self.add_chat_message("System", [("info", QCoreApplication.translate(
                                "MainWindow", "Loaded line {}: {}").format(i + 1, line_text.strip()))])

                self.update_status(
                    QCoreApplication.translate("MainWindow", "Chat history loaded from: {}").format(
                        os.path.basename(file_name)), 3000
                )
                logger.info(f"Chat history successfully loaded from '{file_name}'.")
            except Exception as e_load:
                QMessageBox.warning(self, QCoreApplication.translate("MainWindow", "Load Error"),
                                    QCoreApplication.translate("MainWindow", "Could not load chat history: {}").format(
                                        str(e_load)))
                logger.error(f"Error loading chat history from '{file_name}': {e_load}", exc_info=True)

    # --- Initial Worker Calls & Notifications (Called by _perform_full_initialization via QTimer) ---
    def _initial_worker_calls_and_notifications(self) -> None:
        """
        Performs initial calls to workers (e.g., request TTS voices) and checks
        module statuses after the main GUI is up and the event loop is running.
        """
        logger.info("Performing initial worker calls and notifications...")

        # 1. Request TTS voices if TTS worker is available
        self._request_tts_voices()  # Calls initialize_engine on TTS worker

        # 2. Initialize Voice Listener microphone (if worker available)
        listener_info = self.workers.get('voice_listener')
        if listener_info and listener_info.get('worker') and hasattr(listener_info['worker'], 'initialize_microphone'):
            logger.info("Requesting Voice Listener to initialize microphone...")
            QMetaObject.invokeMethod(listener_info['worker'], "initialize_microphone", Qt.QueuedConnection)
        elif not listener_info or not listener_info.get('worker'):  # Check if worker itself is None
            logger.warning("Voice Listener worker not available for microphone initialization.")

        # 3. Start RobotAppearanceWidget updates if it's the real one and has the method
        if (hasattr(self, 'robot_appearance_widget_instance') and
                self.robot_appearance_widget_instance and
                hasattr(self.robot_appearance_widget_instance, 'start_appearance_updates') and
                not isinstance(self.robot_appearance_widget_instance, RobotAppearanceWidget_Dummy)):  # Check not dummy
            try:
                logger.info("Starting Robot Appearance updates (for real widget)...")
                self.robot_appearance_widget_instance.start_appearance_updates()
            except Exception as e_ra_start:
                logger.error(f"Error starting robot appearance updates on real widget: {e_ra_start}", exc_info=True)

        # 4. Check module import status and notify user / update status icon
        self.check_module_import_status_and_notify()  # Updates status bar and logs
        self._update_module_status_icon()  # Ensure icon reflects current status accurately

        logger.info("Initial worker calls and notifications completed.")

    def _request_tts_voices(self) -> None:
        """Requests the TTS worker to initialize its engine and provide available voices."""
        logger.debug("MainWindow requesting TTS voices from worker...")
        tts_info = self.workers.get('tts')  # self.workers populated in _setup_workers_and_threads

        if tts_info and tts_info.get('worker'):
            worker_instance = tts_info['worker']
            if hasattr(worker_instance, 'initialize_engine'):
                logger.info("Calling initialize_engine on TTS worker to get voices...")
                # The initialize_engine method in TTSWorker should emit available_voices_signal
                QMetaObject.invokeMethod(worker_instance, "initialize_engine", Qt.QueuedConnection)
            else:
                logger.warning("TTS worker does not have an 'initialize_engine' method.")
        elif not hasattr(self, 'workers') or not self.workers.get('tts', {}).get('worker'):
            logger.warning("TTS Worker not available or not fully set up when trying to request voices.")
            # Disable TTS related UI elements if worker is truly missing
            if hasattr(self, 'voice_select_combo'):
                self.voice_select_combo.setEnabled(False)
                self.voice_select_combo.clear()  # Clear any placeholder items
                self.voice_select_combo.addItem(QCoreApplication.translate("MainWindow", "(TTS N/A)"))
            if hasattr(self, 'rate_slider'): self.rate_slider.setEnabled(False)
            if hasattr(self, 'volume_slider'): self.volume_slider.setEnabled(False)
            if hasattr(self, 'tts_stop_button'): self.tts_stop_button.setEnabled(False)

    def check_module_import_status_and_notify(self) -> None:
        """Checks global import status flags and notifies user via status bar."""
        # MISSING_MODULES and MODULE_IMPORTS_OK are global vars from Part 1
        if MISSING_MODULES:  # True if any specific file import failed
            missing_modules_str = ", ".join(MISSING_MODULES)
            status_message = QCoreApplication.translate("MainWindow",
                                                        "Warning: Core modules failed to import ({}). Functionality reduced. Check logs.").format(
                missing_modules_str)
            self.update_status(status_message, 15000)  # Long duration for important warning
            logger.critical(f"CRITICAL STARTUP CHECK: Modules failed to import: {missing_modules_str}.")
        elif not MODULE_IMPORTS_OK:  # True if _try_import ever returned False, even if no specific file is in MISSING_MODULES
            self.update_status(
                QCoreApplication.translate("MainWindow",
                                           "Note: Some optional modules might not have loaded. Check logs if issues arise."),
                10000)
            logger.warning(
                "STARTUP CHECK: MODULE_IMPORTS_OK is False, indicating some import issue occurred for an item within a module.")
        else:  # All explicitly checked imports were okay
            self.update_status(QCoreApplication.translate("MainWindow", "All essential modules appear loaded."), 5000)
            logger.info("STARTUP CHECK: All essential modules reported as loaded (or fallbacks chosen).")
        self._update_module_status_icon()  # Refresh icon

    # --- Worker Setup ---
        # (Other methods of MainWindow like _initial_worker_calls_and_notifications, etc.)
        # ...

        def _initial_worker_calls_and_notifications(self) -> None:
            # ... (content of this method) ...
            logger.info("Initial worker calls and notifications completed.")

        # --- Worker Setup --- # <--- THIS IS THE METHOD YOU NEED TO ENSURE IS CORRECTLY PLACED
        def _setup_workers_and_threads(self) -> None:
            """
            Initializes all worker objects, moves them to their respective QThreads,
            and connects their signals to MainWindow's slots.
            Uses the '_cls' variables defined in Part 1 to decide Real or Dummy instantiation.
            This version is corrected based on user-provided TypeErrors.
            """
            logger.info("Setting up worker threads and modules (Corrected Argument Passing Attempt 2)...") # Updated log message
            self.workers = {} # Clear any previous worker setup
            parent_qobject = self # MainWindow instance, to be used as parent for QObject workers

            worker_setups = [
                {"name": "emotion", "class": EmotionWorker_cls},
                {"name": "tts", "class": TTSWorker_cls},
                {"name": "voice_listener", "class": VoiceListenerWorker_cls},
                {"name": "nlp", "class": NLPWorker_cls},
                {"name": "camera", "class": CameraWorker}, # Internal
                {"name": "image_save", "class": ImageSaveWorker} # Internal
            ]

            for setup in worker_setups:
                worker_name = setup["name"]
                WorkerClass = setup["class"]

                logger.info(f"Setting up worker: '{worker_name}' using class '{WorkerClass.__name__}'...")
                try:
                    worker_instance: Optional[QObject] = None

                    if worker_name == "emotion":
                        if "Dummy" in WorkerClass.__name__:
                            worker_instance = WorkerClass(parent=parent_qobject)
                        else:
                            try:
                                worker_instance = WorkerClass(parent=parent_qobject)
                            except TypeError:
                                logger.debug(f"Real EmotionWorker does not take parent, trying default init.")
                                worker_instance = WorkerClass()

                    elif worker_name == "tts":
                        worker_instance = WorkerClass()

                    elif worker_name == "voice_listener":
                        if "Dummy" in WorkerClass.__name__:
                            worker_instance = WorkerClass(parent=parent_qobject,
                                                          language=self.config.get("speech_to_text_settings",{}).get("language", "en-US"),
                                                          mic_idx=self.config.get("speech_to_text_settings",{}).get("microphone_index"),
                                                          energy=self.config.get("speech_to_text_settings",{}).get("energy_threshold", 300),
                                                          pause=self.config.get("speech_to_text_settings",{}).get("pause_threshold", 0.8),
                                                          phrase_limit=self.config.get("speech_to_text_settings",{}).get("phrase_time_limit", 5.0)
                                                          )
                        else:
                            vls_args_possible = [
                                self.config.get("speech_to_text_settings",{}).get("language", "en-US"),
                                self.config.get("speech_to_text_settings",{}).get("microphone_index"),
                                self.config.get("speech_to_text_settings",{}).get("energy_threshold", 300),
                                self.config.get("speech_to_text_settings",{}).get("pause_threshold", 0.8),
                                self.config.get("speech_to_text_settings",{}).get("phrase_time_limit", 5.0),
                                self.config.get("speech_to_text_settings",{}).get("stt_engine", "google")
                            ]
                            instantiated_successfully = False
                            for i in range(len(vls_args_possible), 0, -1):
                                try:
                                    worker_instance = WorkerClass(*vls_args_possible[:i])
                                    logger.info(f"Instantiated real VoiceListenerWorker with {i} arguments.")
                                    instantiated_successfully = True
                                    break
                                except TypeError:
                                    logger.debug(f"Real VoiceListenerWorker instantiation failed with {i} args.")
                                    continue
                            if not instantiated_successfully:
                                logger.warning(f"Could not determine correct args for real VoiceListenerWorker. Attempting default init.")
                                try:
                                    worker_instance = WorkerClass()
                                except Exception as e_def_init:
                                    logger.error(f"Default init for VoiceListenerWorker also failed: {e_def_init}")
                                    raise # Re-raise if default init also fails

                    elif worker_name == "nlp":
                        if "Dummy" in WorkerClass.__name__:
                            dependencies_dict_dummy = {"robot_info_module": self.robot_info_direct_instance}
                            worker_instance = WorkerClass(dependencies=dependencies_dict_dummy, parent=parent_qobject)
                        else:
                            grammar_system_instance = None
                            try:
                                grammar_system_instance = GrammarSystem_for_deps(language_code="en-US")
                            except Exception as e_gs_init:
                                logger.error(f"Failed to initialize GrammarSystem_for_deps for NLP: {e_gs_init}. Passing None or Dummy.", exc_info=True)
                                if not isinstance(GrammarSystem_for_deps, GrammarSystem_Dummy):
                                    grammar_system_instance = GrammarSystem_Dummy(language_code="en-US")
                                else:
                                    try:
                                        grammar_system_instance = GrammarSystem_for_deps() if GrammarSystem_for_deps else None
                                    except Exception: grammar_system_instance = None


                            dependencies_dict_real = {
                                "robot_info_module": self.robot_info_direct_instance,
                                "grammar_system": grammar_system_instance,
                                "multi_lang_corrector": MultiLangCorrector_for_deps(config=self.config.get("multilang_settings"))
                            }
                            try:
                                worker_instance = WorkerClass(dependencies_dict_real)
                            except TypeError:
                                logger.debug("NLPWorker failed with 1 arg (dependencies), trying with parent as 2nd arg.")
                                worker_instance = WorkerClass(dependencies_dict_real, parent=parent_qobject)

                    elif worker_name == "camera":
                        camera_config = self.config.get("camera_settings", {})
                        worker_instance = WorkerClass(camera_config, parent=parent_qobject)

                    elif worker_name == "image_save":
                        worker_instance = WorkerClass(parent=parent_qobject)

                    else:
                        logger.warning(f"Worker '{worker_name}' has no specific instantiation logic, trying default with parent.")
                        worker_instance = WorkerClass(parent=parent_qobject)

                    if worker_instance is None:
                        raise ValueError(f"Worker instance for '{worker_name}' was not created after attempts.")

                    thread = QThread(self)
                    thread.setObjectName(f"{worker_name}Thread")
                    worker_instance.moveToThread(thread)

                    if hasattr(worker_instance, 'finished'): worker_instance.finished.connect(thread.quit)

                    original_setups_data = [
                        {"name": "emotion", "signals": [("emotion_detected", self.handle_emotion_update), ("error", self.handle_worker_error)]},
                        {"name": "tts", "signals": [("speech_started", self.handle_speech_started), ("speech_word_boundary", self.handle_speech_word_boundary), ("speech_finished", self.handle_speech_finished), ("available_voices_signal", self.handle_available_voices), ("error", self.handle_worker_error)]},
                        {"name": "voice_listener", "signals": [("text_recognized", self.handle_recognized_voice), ("listening_started_signal", self.handle_voice_listener_started_ui), ("listening_stopped_signal", self.handle_voice_listener_stopped_ui), ("vad_status_changed", self.handle_vad_status_changed), ("listening_error", self.handle_listening_error), ("error", self.handle_worker_error)]},
                        {"name": "nlp", "signals": [("processing_complete", self.handle_nlp_result), ("error", self.handle_worker_error)]},
                        {"name": "camera", "signals": [("frame_ready", self.update_camera_feed), ("error", self.handle_worker_error)]},
                        {"name": "image_save", "signals": [("image_saved", self.handle_image_saved), ("error", self.handle_worker_error)]}
                    ]
                    current_setup_data = next((s for s in original_setups_data if s["name"] == worker_name), None)
                    if current_setup_data:
                        for signal_name, slot_method in current_setup_data.get("signals", []):
                            if hasattr(worker_instance, signal_name) and hasattr(self, slot_method.__name__):
                                getattr(worker_instance, signal_name).connect(slot_method)
                                logger.debug(f"Connected {worker_name}.{signal_name} to MainWindow.{slot_method.__name__}")
                            else:
                                logger.error(f"Signal/Slot connection FAILED for {worker_name}: Signal '{signal_name}' in {WorkerClass.__name__} or Slot '{slot_method.__name__}' in MainWindow not found.")

                    if worker_name == "camera" and hasattr(worker_instance, "run"):
                        thread.started.connect(worker_instance.run)

                    self.workers[worker_name] = {"worker": worker_instance, "thread": thread}
                    if worker_name not in ["camera"]:
                        thread.start()
                        logger.info(f"Thread '{thread.objectName()}' started for worker '{worker_name}'.")
                    logger.info(f"Worker '{worker_name}' setup complete.")

                except Exception as e_worker_setup:
                    logger.error(f"Failed to setup worker '{worker_name}' with class {WorkerClass.__name__}: {e_worker_setup}", exc_info=True)
                    self.workers[worker_name] = {"worker": None, "thread": None}
                    if worker_name not in MISSING_MODULES:
                        MISSING_MODULES.append(f"{worker_name} (setup_failed)")
                    self._update_module_status_icon()

            # Connect signals from MainWindow to worker slots
            if "nlp" in self.workers and self.workers["nlp"]["worker"] and hasattr(self.workers["nlp"]["worker"], 'process_user_input'):
                self.start_nlp_processing.connect(self.workers["nlp"]["worker"].process_user_input)
            if "emotion" in self.workers and self.workers["emotion"]["worker"] and hasattr(self.workers["emotion"]["worker"], 'analyze_text_emotion'):
                self.request_emotion_analysis.connect(self.workers["emotion"]["worker"].analyze_text_emotion)
            if "tts" in self.workers and self.workers["tts"]["worker"] and hasattr(self.workers["tts"]["worker"], 'stop_speaking'):
                self.stop_tts_signal.connect(self.workers["tts"]["worker"].stop_speaking)
            if "camera" in self.workers and self.workers["camera"]["worker"] and hasattr(self.workers["camera"]["worker"], 'set_filter'):
                self.request_camera_filter_change.connect(self.workers["camera"]["worker"].set_filter)

            logger.info("All worker threads and modules setup process finished (Corrected Argument Passing Attempt 2).")

# --- Slots for UI Actions (Triggering Worker Actions or Internal Logic) ---
# def send_input_slot(self) -> None:
# ... (rest of the MainWindow class methods from Part 4)
    # --- Slots for UI Actions that trigger Worker actions will be in Part 4/4 ---
    # --- Slots for handling signals from Workers will be in Part 4/4 ---
    # --- update_status and closeEvent will be in Part 4/4 ---

# END OF UPDOGO_ROBOT.py - DELIVERABLE PART 3/4
# (Continuing MainWindow class from Part 3/4)


    @pyqtSlot()
    def send_input_slot(self) -> None:
        """Handles sending user input from the input field for processing."""
        if not (hasattr(self, 'user_input') and self.user_input and
                hasattr(self, 'chat_display') and self.chat_display):
            logger.error("send_input_slot: UI elements not ready.")
            return

        user_text = self.user_input.text().strip()
        if not user_text:
            return

        logger.info(f"User input received: '{user_text}'")
        self.add_chat_message("User", [("normal", user_text)])  # Display user's own message

        # Handle slash commands locally first
        if user_text.startswith("/"):
            self._handle_slash_command(user_text)
        else:
            # Emit signal to start NLP processing in its thread
            self.start_nlp_processing.emit(user_text)
            # Optionally, also send to emotion worker
            self.request_emotion_analysis.emit(user_text)

        self.user_input.clear()

    def _handle_slash_command(self, command_text: str) -> None:
        """Handles local slash commands entered by the user."""
        parts = command_text.lower().split(" ", 1)
        command = parts[0]
        args_str = parts[1] if len(parts) > 1 else ""
        logger.info(f"Processing slash command: '{command}' with args: '{args_str}'")

        if command == "/clear":
            self.clear_chat_slot()
        elif command == "/help":
            help_msg = QCoreApplication.translate("MainWindow",
                                                  "Available commands:\n"
                                                  "/clear - Clear chat display.\n"
                                                  "/theme [theme_name] - Change theme (e.g., /theme Cyberpunk Neon).\n"
                                                  "/help - Show this help message.")
            self.add_chat_message("System", [("info", help_msg)])
        elif command == "/theme":
            if args_str and args_str in self.theme_combo_keys:  # Check against original keys
                self._apply_theme(args_str)
                self.add_chat_message("System", [("info", QCoreApplication.translate(
                    "MainWindow", "Theme changed to: {}").format(QCoreApplication.translate("MainWindow", args_str)))])
            elif args_str:
                self.add_chat_message("System", [("error", QCoreApplication.translate(
                    "MainWindow", "Unknown theme: {}. Available: {}").format(args_str,
                                                                             ", ".join(self.theme_combo_keys)))])
            else:
                self.add_chat_message("System", [("info", QCoreApplication.translate(
                    "MainWindow", "Usage: /theme [theme_name]. Available: {}").format(
                    ", ".join(self.theme_combo_keys)))])
        else:
            self.add_chat_message("System", [("error", QCoreApplication.translate(
                "MainWindow", "Unknown command: {}").format(command))])

    @pyqtSlot()
    def clear_chat_slot(self) -> None:
        """Clears the chat display."""
        if hasattr(self, 'chat_display') and self.chat_display:
            self.chat_display.clear()
            self.add_chat_message("System", [("info", QCoreApplication.translate("MainWindow", "Chat cleared."))])
            logger.info("Chat display cleared by user.")

    @pyqtSlot(bool)  # Receives the 'checked' state of the button
    def toggle_camera_slot(self, checked: bool) -> None:
        """Toggles the camera stream on or off."""
        self.camera_on = checked  # Update internal state based on button's new state
        logger.info(f"Camera toggled. New state: {'ON' if self.camera_on else 'OFF'}")

        cam_worker_info = self.workers.get("camera")
        if cam_worker_info and cam_worker_info.get("worker") and cam_worker_info.get("thread"):
            cam_worker = cam_worker_info["worker"]
            cam_thread = cam_worker_info["thread"]

            if self.camera_on:
                if not cam_thread.isRunning():
                    logger.info("Starting CameraWorker thread...")
                    # Ensure filter is set before starting (it's set from QSettings initially)
                    cam_worker.set_filter(self.current_camera_filter_key)
                    cam_thread.start()
                else:
                    logger.info("CameraWorker thread already running. Ensuring worker is active.")
                    # If thread is running but worker might have stopped its loop (e.g., error)
                    # this might need a way to restart the worker's internal loop.
                    # For now, assume starting the thread handles it.
                    # We could also directly call a 'start_capture' method on worker if it existed.
            else:  # Turn camera off
                if cam_thread.isRunning():
                    logger.info("Requesting CameraWorker to stop...")
                    # CameraWorker's run loop checks self._is_running which is set by stop()
                    QMetaObject.invokeMethod(cam_worker, "stop", Qt.QueuedConnection)
                    # The thread will quit when the worker emits finished.
                if hasattr(self, 'camera_label') and self.camera_label:
                    self.camera_label.clear()
                    self.camera_label.setText(QCoreApplication.translate("MainWindow", "(Camera is Off)"))
        else:
            logger.error("CameraWorker or its thread not available to toggle camera.")
            self.camera_on = False  # Ensure state reflects failure

        self._update_camera_button_text()  # Update button text/icon
        self.capture_btn.setEnabled(self.camera_on)

    @pyqtSlot(int)  # Receives index of combobox
    def _handle_filter_combo_change_slot(self, index: int) -> None:
        """Handles changes in the camera filter selection ComboBox."""
        if hasattr(self, 'filter_combo') and self.filter_combo and index >= 0:
            new_filter_key = self.filter_combo.itemData(index)  # Get original key from item data
            if new_filter_key != self.current_camera_filter_key:
                self.current_camera_filter_key = new_filter_key
                if self.settings: self.settings.setValue("camera_filter", self.current_camera_filter_key)
                logger.info(f"Camera filter changed to: {self.current_camera_filter_key}")
                # Emit signal to CameraWorker if it's running
                if self.camera_on:
                    self.request_camera_filter_change.emit(self.current_camera_filter_key)
                self.update_status(
                    QCoreApplication.translate("MainWindow", "Camera filter set to: {}").format(
                        QCoreApplication.translate("MainWindow", self.current_camera_filter_key)), 2000
                )

    @pyqtSlot()
    def capture_image_slot(self) -> None:
        """Captures the current camera frame and saves it to a file."""
        logger.debug("Capture image slot triggered.")
        if not self.camera_on or self._last_camera_frame is None:
            QMessageBox.information(self, QCoreApplication.translate("MainWindow", "Capture Image"),
                                    QCoreApplication.translate("MainWindow", "Camera is off or no frame available."))
            return

        default_dir = self.settings.value("last_image_save_path", VISUALS_BASE_PATH, type=str)
        os.makedirs(default_dir, exist_ok=True)  # Ensure directory exists
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = os.path.join(default_dir, f"capture_{timestamp}.png")

        file_name, _ = QFileDialog.getSaveFileName(
            self, QCoreApplication.translate("MainWindow", "Save Image As..."), default_filename,
            QCoreApplication.translate("MainWindow", "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All files (*)"),
        )
        if file_name:
            self.settings.setValue("last_image_save_path", os.path.dirname(file_name))
            save_worker_info = self.workers.get("image_save")
            if save_worker_info and save_worker_info.get("worker"):
                # Pass the raw NumPy frame (_last_camera_frame) for saving
                QMetaObject.invokeMethod(save_worker_info["worker"], "save_image", Qt.QueuedConnection,
                                         Q_ARG(object, self._last_camera_frame),
                                         Q_ARG(str, file_name))
            else:
                logger.error("ImageSaveWorker not available to save image.")
                QMessageBox.warning(self, QCoreApplication.translate("MainWindow", "Error"),
                                    QCoreApplication.translate("MainWindow", "Image saving service not available."))

    @pyqtSlot(bool)  # Receives 'checked' state
    def toggle_voice_output_slot(self, checked: bool) -> None:
        """Toggles voice output (TTS) on or off."""
        self.voice_output_enabled = checked
        if self.settings: self.settings.setValue("voice_output_enabled", self.voice_output_enabled)
        logger.info(f"Voice output toggled. New state: {'ON' if self.voice_output_enabled else 'OFF'}")
        self._update_voice_output_button_text()
        if not self.voice_output_enabled:
            self.interrupt_tts_slot()  # Stop any current speech if muting

    @pyqtSlot(bool)  # Receives 'checked' state
    def toggle_voice_input_slot(self, checked: bool) -> None:
        """Toggles voice input (STT) on or off."""
        self.voice_input_on = checked
        logger.info(f"Voice input toggled. New state: {'ON' if self.voice_input_on else 'OFF'}")
        listener_info = self.workers.get("voice_listener")
        if listener_info and listener_info.get("worker"):
            worker_instance = listener_info["worker"]
            if self.voice_input_on:
                QMetaObject.invokeMethod(worker_instance, "start_listening", Qt.QueuedConnection)
            else:
                QMetaObject.invokeMethod(worker_instance, "stop_listening", Qt.QueuedConnection)
        else:
            logger.error("VoiceListenerWorker not available to toggle voice input.")
            self.voice_input_on = False  # Ensure state reflects failure
        self._update_voice_input_button_text()

    @pyqtSlot()
    def interrupt_tts_slot(self) -> None:
        """Sends a signal to the TTS worker to stop the current speech."""
        logger.info("Interrupt TTS speech requested.")
        self.stop_tts_signal.emit()
        # UI feedback for speech finished will be handled by handle_speech_finished

    @pyqtSlot(int)  # Receives ComboBox index
    def change_tts_voice_selection_slot(self, index: int) -> None:
        """Handles change in TTS voice selection from ComboBox."""
        if not (hasattr(self, 'voice_select_combo') and self.voice_select_combo and index >= 0):
            return

        voice_id = self.voice_select_combo.itemData(index)  # Get voice ID stored in itemData
        if voice_id:
            logger.info(f"TTS voice selection changed to ID: {voice_id}")
            tts_info = self.workers.get("tts")
            if tts_info and tts_info.get("worker") and hasattr(tts_info["worker"], "set_voice"):
                QMetaObject.invokeMethod(tts_info["worker"], "set_voice", Qt.QueuedConnection, Q_ARG(str, voice_id))
                if self.settings: self.settings.setValue("tts_voice_id", voice_id)
                self.update_status(
                    QCoreApplication.translate("MainWindow", "TTS voice changed to: {}").format(
                        self.voice_select_combo.currentText()), 2000
                )
            else:
                logger.warning("TTS Worker not available or 'set_voice' method missing.")
        else:
            logger.warning(f"Invalid voice ID for selected voice at index {index}.")

    @pyqtSlot(int)  # Receives slider value
    def change_tts_rate_slot(self, value: int) -> None:
        """Handles change in TTS speech rate from slider."""
        if hasattr(self, 'rate_label') and self.rate_label: self.rate_label.setText(str(value))
        logger.info(f"TTS rate changed to: {value}")
        tts_info = self.workers.get("tts")
        if tts_info and tts_info.get("worker") and hasattr(tts_info["worker"], "set_rate"):
            QMetaObject.invokeMethod(tts_info["worker"], "set_rate", Qt.QueuedConnection, Q_ARG(int, value))
            if self.settings: self.settings.setValue("tts_rate", value)
        else:
            logger.warning("TTS Worker not available or 'set_rate' method missing.")

    @pyqtSlot(int)  # Receives slider value
    def change_tts_volume_slot(self, value: int) -> None:
        """Handles change in TTS speech volume from slider."""
        if hasattr(self, 'volume_label') and self.volume_label: self.volume_label.setText(str(value))
        volume_float = value / 100.0  # Assuming TTS engine expects 0.0-1.0
        logger.info(f"TTS volume changed to: {value}% ({volume_float:.2f})")
        tts_info = self.workers.get("tts")
        if tts_info and tts_info.get("worker") and hasattr(tts_info["worker"], "set_volume"):
            QMetaObject.invokeMethod(tts_info["worker"], "set_volume", Qt.QueuedConnection, Q_ARG(float, volume_float))
            if self.settings: self.settings.setValue("tts_volume", value)  # Store as int 0-100
        else:
            logger.warning("TTS Worker not available or 'set_volume' method missing.")

    # --- Slots for Handling Signals from Workers ---
    @pyqtSlot(dict)  # Receives response_dict from NLPWorker
    def handle_nlp_result(self, response_dict: Dict[str, Any]) -> None:
        """Handles the processing result from the NLPWorker."""
        logger.info(f"NLP processing result received: {response_dict.get('type', 'UnknownType')}")

        text_to_speak = response_dict.get("text_to_speak", "I have no specific response.")
        display_details = response_dict.get("display_details", [("normal", text_to_speak)])
        robot_name_tr = QCoreApplication.translate("MainWindow", APP_NAME_CONST)
        self.add_chat_message(robot_name_tr, display_details)

        detected_emotion = response_dict.get(
            "determined_emotion_for_response")  # Emotion NLP decided for *robot's* response
        if detected_emotion and isinstance(detected_emotion, dict):  # e.g. {"name": "happy", "intensity": 0.8}
            emo_name = detected_emotion.get("name", "neutral")
            emo_intensity = detected_emotion.get("intensity", 0.7)
            if self.robot_appearance_widget_instance and hasattr(self.robot_appearance_widget_instance,
                                                                 "set_emotion_display"):
                self.robot_appearance_widget_instance.set_emotion_display(emo_name, emo_intensity)
            self.status_labels["emotion"].setText(f"😊 Emo: {emo_name.capitalize()}")
        elif isinstance(detected_emotion, str):  # Simple emotion name
            if self.robot_appearance_widget_instance and hasattr(self.robot_appearance_widget_instance,
                                                                 "set_emotion_display"):
                self.robot_appearance_widget_instance.set_emotion_display(detected_emotion, 0.7)  # Default intensity
            self.status_labels["emotion"].setText(f"😊 Emo: {detected_emotion.capitalize()}")

        if self.voice_output_enabled and text_to_speak:
            tts_info = self.workers.get("tts")
            if tts_info and tts_info.get("worker") and hasattr(tts_info["worker"], "speak"):
                QMetaObject.invokeMethod(tts_info["worker"], "speak", Qt.QueuedConnection, Q_ARG(str, text_to_speak))
            else:
                logger.warning("TTS worker not available or 'speak' method missing for NLP response.")

        # Further actions based on response_dict.get("action_data") can be implemented here

    @pyqtSlot(str, float)  # Receives emotion_name, confidence_score from EmotionWorker
    def handle_emotion_update(self, emotion_name: str, confidence: float) -> None:
        """
        Handles emotion updates from the EmotionWorker.
        This emotion is typically from user input analysis. The robot's own expression
        might be set by NLP based on its response, or by this if NLP doesn't override.
        """
        logger.info(f"Emotion detected in user input: '{emotion_name}' (Confidence: {confidence:.2f})")
        # This is an opportunity to influence the robot's *next* expression, or a subtle background reaction.
        # For now, let's assume NLP's response will dictate the primary emotion display.
        # We could update a status or log, or have a subtle reaction.
        # self.status_labels["emotion"].setText(f"😊 User Emo: {emotion_name.capitalize()}") # Example if we want to show it

    @pyqtSlot(str)  # Receives text_being_spoken from TTSWorker
    def handle_speech_started(self, text_spoken: str) -> None:
        """Handles the start of speech synthesis from TTSWorker."""
        logger.info(f"Speech started for text: '{text_spoken[:50]}...'")
        self.status_labels["connection"].setText("📶 Stat: Speaking...")
        if self.robot_appearance_widget_instance and hasattr(self.robot_appearance_widget_instance,
                                                             "set_speaking_state"):
            self.robot_appearance_widget_instance.set_speaking_state(True)
        if hasattr(self, 'tts_stop_button'): self.tts_stop_button.setEnabled(True)

    @pyqtSlot(str, int, int)  # word, location, length from TTSWorker
    def handle_speech_word_boundary(self, word: str, location: int, length: int) -> None:
        """Handles word boundary events during speech (e.g., for highlighting)."""
        # logger.debug(f"Word boundary: '{word}' at {location} (len {length})")
        # Placeholder for potential future text highlighting in chat
        pass

    @pyqtSlot(str)  # Receives spoken_text from TTSWorker
    def handle_speech_finished(self, spoken_text: str) -> None:
        """Handles the end of speech synthesis from TTSWorker."""
        logger.info(f"Speech finished for text: '{spoken_text[:50]}...'")
        self.status_labels["connection"].setText("📶 Stat: Idle")
        if self.robot_appearance_widget_instance and hasattr(self.robot_appearance_widget_instance,
                                                             "set_speaking_state"):
            self.robot_appearance_widget_instance.set_speaking_state(False)
        if hasattr(self, 'tts_stop_button'): self.tts_stop_button.setEnabled(False)

    @pyqtSlot(list)  # Receives list of voice dicts from TTSWorker
    def handle_available_voices(self, voices: List[Dict[str, Any]]) -> None:
        """Populates the TTS voice selection ComboBox with available voices."""
        logger.info(f"Received {len(voices)} available TTS voices.")
        if not (hasattr(self, 'voice_select_combo') and self.voice_select_combo):
            logger.error("Voice select combo not available to populate voices.")
            return

        self.voice_select_combo.blockSignals(True)  # Prevent emission during population
        self.voice_select_combo.clear()
        self.available_tts_voices = voices  # Store for reference

        current_voice_id_from_settings = self.settings.value("tts_voice_id", None, type=str)
        current_index_to_set = -1

        for i, voice_info in enumerate(voices):
            display_name = voice_info.get('name', f"Voice {i + 1}")
            lang = voice_info.get('lang', 'N/A')
            gender = voice_info.get('gender', '')
            voice_id = voice_info.get('id')

            if not voice_id:
                logger.warning(f"Voice at index {i} has no ID, skipping: {voice_info}")
                continue

            # Make display name more informative
            item_text = f"{display_name} ({lang}"
            if gender: item_text += f", {gender}"
            item_text += ")"

            self.voice_select_combo.addItem(item_text, voice_id)  # Store actual ID as itemData

            if voice_id == current_voice_id_from_settings:
                current_index_to_set = i

        if voices:  # Enable combo if voices are available
            self.voice_select_combo.setEnabled(True)
            if current_index_to_set != -1:
                self.voice_select_combo.setCurrentIndex(current_index_to_set)
            elif self.voice_select_combo.count() > 0:  # If saved voice not found, select first
                self.voice_select_combo.setCurrentIndex(0)
                # And trigger its selection to set the TTS engine to this first voice
                self.change_tts_voice_selection_slot(0)
        else:  # No voices
            self.voice_select_combo.addItem(QCoreApplication.translate("MainWindow", "(No voices available)"), None)
            self.voice_select_combo.setEnabled(False)

        self.voice_select_combo.blockSignals(False)
        logger.debug("TTS Voice selection ComboBox populated.")

    @pyqtSlot(str, float)  # recognized_text, confidence from VoiceListenerWorker
    def handle_recognized_voice(self, text: str, confidence: float) -> None:
        """Handles recognized text from the VoiceListenerWorker."""
        logger.info(f"Voice recognized: '{text}' (Confidence: {confidence:.2f})")
        if not text.strip():
            logger.info("Empty text recognized, ignoring.")
            return

        # Add to chat display with a prefix
        formatted_voice_input = QCoreApplication.translate("MainWindow", "(Voice Input) {}").format(text)
        self.add_chat_message("User", [("normal", formatted_voice_input)])

        # Send to NLP for processing
        self.start_nlp_processing.emit(text)
        self.request_emotion_analysis.emit(text)  # Also analyze emotion of spoken input

    @pyqtSlot()
    def handle_voice_listener_started_ui(self) -> None:
        """Updates UI when voice listener starts."""
        self.voice_input_on = True  # Ensure internal state matches
        self._update_voice_input_button_text()
        self.update_status(QCoreApplication.translate("MainWindow", "Listening for voice input..."), 3000)
        logger.info("UI updated: Voice listener started.")

    @pyqtSlot()
    def handle_voice_listener_stopped_ui(self) -> None:
        """Updates UI when voice listener stops."""
        self.voice_input_on = False  # Ensure internal state matches
        self._update_voice_input_button_text()
        self.update_status(QCoreApplication.translate("MainWindow", "Voice listening stopped."), 3000)
        logger.info("UI updated: Voice listener stopped.")

    @pyqtSlot(bool)  # is_speaking_detected from VoiceListenerWorker (VAD)
    def handle_vad_status_changed(self, is_speaking_detected: bool) -> None:
        """Handles Voice Activity Detection status changes."""
        status_msg = "VAD: Speaking detected" if is_speaking_detected else "VAD: Silence detected"
        logger.debug(status_msg)
        # Can update a visual cue in UI if desired, e.g., mic icon color
        if is_speaking_detected and hasattr(self, 'voice_input_btn') and self.voice_input_btn:
            # Example: Make icon slightly different if speaking
            pass  # Placeholder for visual feedback
        elif not is_speaking_detected and hasattr(self, 'voice_input_btn') and self.voice_input_btn:
            pass  # Revert visual feedback

    @pyqtSlot(str, str)  # error_type, message from worker
    def handle_listening_error(self, error_type: str, message: str) -> None:
        """Handles specific errors from the VoiceListenerWorker."""
        logger.error(f"Voice Listener Error ({error_type}): {message}")
        self.add_chat_message("System", [("error", f"Voice Input Error: {message}")])
        self.voice_input_on = False  # Typically stop listening on error
        self._update_voice_input_button_text()

    @pyqtSlot(object)  # frame (np.ndarray or QImage/Pixmap) from CameraWorker
    def update_camera_feed(self, frame_data: Any) -> None:
        """Updates the camera feed display label with a new frame."""
        if not (hasattr(self, 'camera_label') and self.camera_label and self.camera_on):
            # logger.debug("Camera feed update skipped: Label not ready or camera off.")
            return

        pixmap_to_display: Optional[QPixmap] = None

        if isinstance(frame_data, QImage):
            pixmap_to_display = QPixmap.fromImage(frame_data)
            self._last_camera_frame = None  # Cannot reliably convert QImage back to np.ndarray for saving without CV2/NumPy
            if CV2_AVAILABLE and NUMPY_AVAILABLE:  # Attempt to store as numpy if possible
                try:
                    # Conversion from QImage to numpy array for _last_camera_frame
                    qimage = frame_data.convertToFormat(QImage.Format_RGB888)
                    ptr = qimage.bits()
                    ptr.setsize(qimage.byteCount())
                    arr = np.array(ptr, dtype=np.uint8).reshape((qimage.height(), qimage.width(), 3))
                    self._last_camera_frame = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)  # Store as BGR if from RGB888
                except Exception as e_conv:
                    logger.warning(f"Could not convert QImage to NumPy for _last_camera_frame: {e_conv}")
                    self._last_camera_frame = None


        elif NUMPY_AVAILABLE and isinstance(frame_data, np.ndarray):
            self._last_camera_frame = frame_data.copy()  # Store the raw NumPy frame for capture
            try:
                if frame_data.ndim == 2:  # Grayscale
                    h, w = frame_data.shape
                    bytes_per_line = w
                    qt_image = QImage(frame_data.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
                elif frame_data.ndim == 3 and frame_data.shape[2] == 3:  # Color (assume BGR from OpenCV)
                    h, w, ch = frame_data.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(frame_data.data, w, h, bytes_per_line,
                                      QImage.Format_RGB888).rgbSwapped()  # BGR to RGB
                else:
                    logger.warning(f"Unsupported NumPy array format for camera feed: {frame_data.shape}")
                    return
                pixmap_to_display = QPixmap.fromImage(qt_image)
            except Exception as e_np_conv:
                logger.error(f"Error converting NumPy frame to QPixmap: {e_np_conv}", exc_info=True)
                return

        elif isinstance(frame_data, QPixmap):  # If worker directly sends pixmap
            pixmap_to_display = frame_data
            self._last_camera_frame = None  # Cannot get np.ndarray from QPixmap easily

        if pixmap_to_display and not pixmap_to_display.isNull():
            self.camera_label.setPixmap(pixmap_to_display.scaled(
                self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        elif not pixmap_to_display or pixmap_to_display.isNull():
            # logger.debug("Received null or invalid pixmap for camera feed.") # Can be noisy
            pass

    @pyqtSlot(str)  # filename from ImageSaveWorker
    def handle_image_saved(self, filename: str) -> None:
        """Handles confirmation that an image was saved."""
        # Status update is already done by ImageSaveWorker itself
        logger.info(f"Image successfully saved by worker: '{filename}'")
        # Could add to a gallery or notify user further if needed

    @pyqtSlot(str, str)  # worker_name, error_message from any worker
    def handle_worker_error(self, worker_name: str, error_message: str) -> None:
        """Handles generic errors reported by worker threads."""
        logger.error(f"Error from {worker_name}: {error_message}")
        self.add_chat_message("System", [("error", f"Error in {worker_name}: {error_message}")])
        # Potentially update module status or disable features related to the failed worker
        self.update_status(f"Error in {worker_name}: {error_message[:60]}...", 7000)
        # If a worker errors out, its thread might quit. Check and update UI for it.
        if worker_name.lower() == "camera":
            self.camera_on = False
            self._update_camera_button_text()
            self.camera_label.setText(QCoreApplication.translate("MainWindow", "(Camera Error - See Log)"))
        elif "listener" in worker_name.lower():
            self.voice_input_on = False
            self._update_voice_input_button_text()
        # More specific error handling per worker type could be added.
        self._update_module_status_icon()

    # --- Status Bar and Window Closing ---
    def update_status(self, message: str, duration: int = 3000) -> None:
        """Displays a message on the status bar for a specified duration."""
        if hasattr(self, 'status_bar') and self.status_bar:
            self.status_bar.showMessage(message, duration)
            logger.debug(f"Status bar updated: '{message}' (duration: {duration}ms)")

    def closeEvent(self, event: QEvent) -> None:
        """Handles the window closing event to ensure graceful shutdown."""
        logger.info(QCoreApplication.translate("MainWindow", "Close event triggered. Initiating shutdown sequence..."))

        # 1. Stop Robot Appearance Updates (if applicable)
        if (hasattr(self, 'robot_appearance_widget_instance') and
                self.robot_appearance_widget_instance and
                hasattr(self.robot_appearance_widget_instance, 'stop_appearance_updates')):
            try:
                logger.info(QCoreApplication.translate("MainWindow", "Stopping robot appearance updates..."))
                self.robot_appearance_widget_instance.stop_appearance_updates()
            except Exception as e_ra_stop:
                logger.error(f"Error stopping robot appearance updates: {e_ra_stop}")

        # 2. Stop all worker threads
        logger.info(QCoreApplication.translate("MainWindow", "Requesting all worker threads to stop..."))
        for worker_name, worker_data in self.workers.items():
            thread = worker_data.get('thread')
            worker_instance = worker_data.get('worker')

            if worker_instance:
                # Prefer explicit shutdown method if available, otherwise try stop()
                if hasattr(worker_instance, 'shutdown'):
                    logger.info(f"Calling shutdown() on '{worker_name}' worker.")
                    QMetaObject.invokeMethod(worker_instance, "shutdown", Qt.QueuedConnection)
                elif hasattr(worker_instance, 'stop'):
                    logger.info(f"Calling stop() on '{worker_name}' worker.")
                    QMetaObject.invokeMethod(worker_instance, "stop", Qt.QueuedConnection)
                else:
                    logger.warning(f"Worker '{worker_name}' has no shutdown() or stop() method.")
            else:
                logger.warning(f"No worker instance found for '{worker_name}' during shutdown.")

            if thread and thread.isRunning():
                logger.info(f"Requesting thread '{thread.objectName()}' for worker '{worker_name}' to quit...")
                thread.quit()  # Ask event loop to exit
                if not thread.wait(2500):  # Wait up to 2.5 seconds
                    logger.warning(f"Thread '{thread.objectName()}' did not quit gracefully. Terminating...")
                    thread.terminate()  # Force stop if necessary
                    if not thread.wait(1000):  # Wait for termination
                        logger.error(f"Thread '{thread.objectName()}' failed to terminate.")
                else:
                    logger.info(f"Thread '{thread.objectName()}' finished gracefully.")
            elif thread:
                logger.info(f"Thread '{thread.objectName()}' for '{worker_name}' was not running or already finished.")
            else:
                logger.warning(f"No thread object found for '{worker_name}' during shutdown.")

        logger.info(QCoreApplication.translate("MainWindow", "All worker threads processed for shutdown."))

        # 3. Save application settings (like window geometry, theme, etc.)
        if self.settings:
            logger.info(QCoreApplication.translate("MainWindow", "Saving window geometry and other settings..."))
            self.settings.setValue("geometry", self.size())
            self.settings.setValue("pos", self.pos())
            self.settings.setValue("theme", self.current_theme_name)
            self.settings.setValue("chat_font_size", self.current_chat_font_size)
            self.settings.setValue("voice_output_enabled", self.voice_output_enabled)
            if hasattr(self,
                       'voice_select_combo') and self.voice_select_combo and self.voice_select_combo.currentIndex() >= 0:
                self.settings.setValue("tts_voice_id",
                                       self.voice_select_combo.itemData(self.voice_select_combo.currentIndex()))
            if hasattr(self, 'rate_slider'): self.settings.setValue("tts_rate", self.rate_slider.value())
            if hasattr(self, 'volume_slider'): self.settings.setValue("tts_volume", self.volume_slider.value())
            if hasattr(self, 'current_camera_filter_key'): self.settings.setValue("camera_filter",
                                                                                  self.current_camera_filter_key)
            self.settings.sync()  # Ensure changes are written
            logger.info(QCoreApplication.translate("MainWindow", "Settings saved."))
        else:
            logger.warning("QSettings not available during closeEvent. Cannot save settings.")

        logger.info(QCoreApplication.translate("MainWindow", "Shutdown sequence complete. Accepting close event."))
        event.accept()  # Proceed with closing the window


# --- Main Execution Block ---
if __name__ == "__main__":
    # Apply any necessary Qt CoreApplication attributes before QApplication is created
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    # QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True) # If using complex OpenGL in appearance

    app = QApplication(sys.argv)

    # Set application details (useful for QSettings, About dialogs, etc.)
    app.setApplicationName(APP_NAME_CONST)
    app.setApplicationVersion(APP_VERSION_CONST)
    app.setOrganizationName(SETTINGS_ORG)
    # Use a more specific organization domain if applicable
    app.setOrganizationDomain(f"{SETTINGS_ORG.lower().replace(' ', '')}.com")

    # Ensure the base visuals directory and icons subdirectory exist
    os.makedirs(ICONS_BASE_PATH, exist_ok=True)

    # Initialize and show the main window
    main_window_instance: Optional[MainWindow] = None
    try:
        logger.info(f"Attempting to launch {APP_TITLE_CONST}...")
        main_window_instance = MainWindow()
        main_window_instance.show()  # Show the window
        logger.info(f"{APP_TITLE_CONST} started successfully and window shown.")
    except Exception as e_startup:
        logger.critical(f"CRITICAL ERROR during application startup in __main__: {e_startup}", exc_info=True)
        # Show a simple QMessageBox if MainWindow instantiation fails catastrophically
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle(QCoreApplication.translate("main", "Application Startup Error"))
        error_box.setText(
            QCoreApplication.translate("main",
                                       "A critical error occurred during application startup:\n\n{0}\n\n"
                                       "Please check the logs ({1}) for more details. The application will now exit."
                                       ).format(str(e_startup),
                                                os.path.join(VISUALS_BASE_PATH, LOG_FILE_NAME) if os.path.exists(
                                                    VISUALS_BASE_PATH) else LOG_FILE_NAME)
        )
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.exec_()
        sys.exit(1)  # Exit with an error code

    # Start the Qt event loop
    exit_code = app.exec_()
    logger.info(f"Application event loop finished with exit code: {exit_code}.")
    sys.exit(exit_code)

# END OF UPDOGO_ROBOT.py - DELIVERABLE PART 4/4 (AND END OF COMPLETE FILE)
