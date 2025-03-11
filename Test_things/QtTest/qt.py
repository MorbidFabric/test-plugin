import sys
import ctypes
from ctypes import wintypes
from PyQt6.QtWidgets import QMainWindow, QApplication, QStyle
from PyQt6.uic import loadUi
from PyQt6.QtCore import QTimer, Qt, QPoint, QSize, QPropertyAnimation, QEasingCurve
from PyQt6 import QtGui
from time import strftime, localtime

class ClockWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("clock.ui", self)

        self.setWindowTitle("E2E")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        #self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinimizeButtonHint)
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
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

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
        self.maximize()

    def update_time(self):
        curr_time = strftime("%H:%M:%S", localtime())
        self.labelTime.setText(curr_time)
        #self.labelTime.setVisible(False)

app = QApplication(sys.argv)
window = ClockWindow()
window.show()
sys.exit(app.exec())