import sys
import ctypes
from ctypes import wintypes
from PyQt6.QtWidgets import QMainWindow, QApplication, QStyle, QGraphicsDropShadowEffect
from PyQt6.uic import loadUi
from PyQt6.QtCore import QTimer, Qt, QPoint, QSize, QPropertyAnimation, QEasingCurve
from PyQt6 import QtGui, QtWidgets, QtCore
from time import strftime, localtime
import uuid

class ClockWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("clock.ui", self)

        self.setWindowTitle("E2E")
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        #self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Setup title bar buttons
        self.closeButton.clicked.connect(self.animateClose)
        self.minimizeButton.clicked.connect(self.showMinimized)
        self.maximizeButton.clicked.connect(self.maximize)
        max_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarNormalButton)
        #max_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        min_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMinButton)
        close_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
        close_icon = self.recolor_icon(close_icon, QtGui.QColor(20,20,20))
        max_icon = self.recolor_icon(max_icon, QtGui.QColor(20,20,20))
        min_icon = self.recolor_icon(min_icon, QtGui.QColor(20,20,20))
        self.maximizeButton.setIcon(max_icon)
        self.minimizeButton.setIcon(min_icon)
        self.closeButton.setIcon(close_icon)

        #add drop shadow to close button
        #self.closeButton.setStyleSheet("QPushButton {border-radius: 10px; background-color: rgba(255, 0, 0, 0);}")
        # Add drop shadow effect to close button
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QtGui.QColor(0, 0, 0, 80))  # Semi-transparent black
        shadow.setOffset(2, 2)  # Slight offset to bottom-right
        self.closeButton.setGraphicsEffect(shadow)
        self.closeButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.closeButton.setToolTip("Close")
        self.closeButton.setToolTipDuration(2000)

        #self.showMaximized
        '''
        QPushButton {
                background-color: transparent;
                border: none;
            }
            '''
        # Setup title bar dragging
        self.titleBar.mousePressEvent = self.mousePressEvent
        self.titleBar.mouseMoveEvent = self.mouseMoveEvent
        #title bar double click event
        self.titleBar.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        self.dragging = False
        self.dragPos = QPoint()
        
        # Setup clock updating
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_time)
        self.timer.start()
        self.update_time()  # initial update
        
        checkbox = QtWidgets.QCheckBox()
        checkbox.setText("Check me")

        model = QtGui.QStandardItemModel()
        items = ["Item 1", "Item 2", "Item 3", "Item 4"]
        for text in items:
            item = QtGui.QStandardItem(text)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            item.setData(QtCore.Qt.CheckState.Unchecked, QtCore.Qt.ItemDataRole.CheckStateRole)
            model.appendRow(item)

        

        dropdownBtn = QtWidgets.QComboBox()
        dropdownBtn.setPlaceholderText("Select an item")
        
        dropdownBtn.setModel(model)

        self.smallButton = QtWidgets.QPushButton()
        self.smallButton.setText("Small Button")
        self.smallButton.setFixedSize(40, 30)
        self.smallButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.smallButton.clicked.connect(self.smallButtonClicked)
        self.smallButton.setStyleSheet("""
            QPushButton {
                background-color: dodgerblue;
                color: white;
                border: none;
                border-radius: 25px;  /* Adjust based on your button size */
                padding: 20px 28px;
                font-size: 24px;
            }
            QPushButton:pressed {
                background-color: #1C86EE;  /* A slightly darker shade to simulate 75% brightness */
            }
        """)
        self.smallButton.setCheckable(True)


        self.horizontalLayout_2.addWidget(dropdownBtn)
        self.horizontalLayout_2.addWidget(self.smallButton)
        self.titleBar.setMinimumHeight(50)
        self.titleBar.setMaximumHeight(50)

    # def create_checkable_combobox(items):
    #     combo = QtWidgets.QComboBox()
    #     model = QtGui.QStandardItemModel()

    #     for text in items:
    #         item = QtGui.QStandardItem(text)
    #         item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
    #         item.setData(QtCore.Qt.CheckState.Unchecked, QtCore.Qt.ItemDataRole.CheckStateRole)
    #         model.appendRow(item)

    #     combo.setModel(model)
    #     return combo

    def smallButtonClicked(self):
        if self.smallButton.isChecked():
            #create an overlay that sticks to the right side of the window
            overlay = QtWidgets.QWidget()
            overlay.setFixedSize(200, 200)
            overlay.setStyleSheet("background-color: rgba(80, 80, 80, 230);")
            
            # Get the position of the button inside of main window
            pos = self.smallButton.mapTo(self, QPoint(0, 0))

            overlay.move(self.width() - overlay.width(), self.titleBar.height())
            print(f"pos: {pos.x()}, {pos.y()}\nOther Pos: {self.width() - overlay.width()}")
            # overlay.move(self.width() - overlay.width(), 100)
            # Store the overlay as an instance variable
            self.overlay = overlay
            # Make the overlay a child of the main window
            self.overlay.setParent(self)
            # Show the overlay
            self.overlay.show()
            # Bring the overlay to the front
            self.overlay.raise_()
        else:
            print("unchecked")
            # Hide the overlay
            self.overlay.hide()
            # Delete the overlay
            #self.overlay.deleteLater()
        
    def resizeEvent(self, event):
        #if window is resized, move the overlay to the right side of the window
        if hasattr(self, 'overlay'):
            pos = self.smallButton.mapTo(self, QPoint(0, 0))
            self.overlay.move(self.width() - self.overlay.width(), self.titleBar.height())
            # Bring the overlay to the front
            self.overlay.raise_()
        #super().resizeEvent(event)

    def animateClose(self):
        # Animate opacity from 1.0 to 0.0, then minimize.
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(150)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.anim.finished.connect(self.close)
        self.anim.start()

    def recolor_icon(self, icon, target_color, size=QSize(32,32)):
        # Get the original pixmap and convert it to an ARGB image.
        pixmap = icon.pixmap(size)
        image = pixmap.toImage().convertToFormat(QtGui.QImage.Format.Format_ARGB32)
        
        # Create a new transparent image of the same size.
        result = QtGui.QImage(image.size(), QtGui.QImage.Format.Format_ARGB32)
        result.fill(QtGui.QColor(Qt.GlobalColor.transparent))
        
        # Use QPainter to draw the original icon and recolor it.
        painter = QtGui.QPainter(result)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Source)
        painter.drawImage(0, 0, image)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(result.rect(), target_color)
        painter.end()
        
        return QtGui.QIcon(QtGui.QPixmap.fromImage(result))
     
    def maximize(self):
        # if self.isMaximized():
        #     self.showNormal()
        # else:
        #     self.showMaximized()
        icon = self.get_icon_from_exe(r"E:\PyMeow\projects\Dishonored_DO.exe")
        self.maximizeButton.setIcon(icon)

    def mousePressEvent(self, event):
        if self.childAt(event.position().toPoint()) == self.titleBar:
            if event.button() == Qt.MouseButton.LeftButton:
                self.dragging = True
                self.dragPos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.childAt(event.position().toPoint()) == self.titleBar:
            if event.buttons() & Qt.MouseButton.LeftButton and self.dragging:
                self.move(event.globalPosition().toPoint() - self.dragPos)
                event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.childAt(event.position().toPoint()) == self.titleBar:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        #self.maximize()
        print("double click title bar")
        pass

    def update_time(self):
        curr_time = strftime("%H:%M:%S", localtime())
        self.labelTime.setText(curr_time)
        #self.labelTime.setVisible(False)

    def get_icon_from_exe(self, path):
        model = QtGui.QFileSystemModel()
        icon = model.fileIcon(model.index(path))
        
        print(icon.availableSizes())
        pixmap = icon.pixmap(256, 256)
        pixmap.save("icon.png")
        return icon
    
    

import ctypes
from ctypes import wintypes

# DWMWA_CAPTION_COLOR is 35 on supported systems.
DWMWA_CAPTION_COLOR = 35

def set_caption_color(window, color_value):
    """
    Set the caption (title bar) color of a native window.
    
    color_value is converted from HEX to COLORREF: 0x00BBGGRR.
    For example, 0x000000FF for red or #FF0000 for red.
    """
    #convert color from HEX to BGR
    if "#" in color_value:
        color_value = color_value.lstrip('#')
    color_value = int(color_value, 16)
    color_value = ((color_value & 0x000000FF) << 16) | (color_value & 0x0000FF00) | ((color_value & 0x00FF0000) >> 16)
    
    hwnd = int(window.winId())
    color = wintypes.DWORD(color_value)
    hr = ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd,
        DWMWA_CAPTION_COLOR,
        ctypes.byref(color),
        ctypes.sizeof(color)
    )
    if hr != 0:
        print("Failed to set caption color. HRESULT:", hr)
    #return hr



app = QApplication(sys.argv)
window = ClockWindow()
window.show()
set_caption_color(window, "3c3c3c")  # Red title bar

sys.exit(app.exec())