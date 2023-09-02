import sys
import openai
import qtmodern.styles
import qtmodern.windows
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLineEdit
import pytesseract
from PyQt5.QtCore import pyqtSlot
from PIL import Image
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import ImageGrab
import os

openai.api_key = 'your_api_key'

imfilepath = 'image_path'

pytesseract.pytesseract.tesseract_cmd = ('tesseract_path')

class SnippingWidget(QtWidgets.QMainWindow,QLineEdit): #first class for snipping fuctionality
    closed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(SnippingWidget, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background:transparent;")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)


        self.outsideSquareColor = "red"
        self.squareThickness = 2

        self.start_point = QtCore.QPoint()
        self.end_point = QtCore.QPoint()

    def mousePressEvent(self, event):
        self.start_point = event.pos()
        self.end_point = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end_point = event.pos()
        self.update()

    def mouseReleaseEvent(self, QMouseEvent):
        r = QtCore.QRect(self.start_point, self.end_point).normalized()
        self.hide()
        img = ImageGrab.grab(bbox=r.getCoords())
        img.save("your_image_name")
        QApplication.restoreOverrideCursor()
        self.closed.emit()

    def paintEvent(self, event):
        trans = QtGui.QColor(22, 100, 233)
        r = QtCore.QRectF(self.start_point, self.end_point).normalized()
        qp = QtGui.QPainter(self)
        trans.setAlphaF(0.2)
        qp.setBrush(trans)
        outer = QtGui.QPainterPath()
        outer.addRect(QtCore.QRectF(self.rect()))
        inner = QtGui.QPainterPath()
        inner.addRect(r)
        r_path = outer - inner
        qp.drawPath(r_path)
        qp.setPen(
            QtGui.QPen(QtGui.QColor(self.outsideSquareColor), self.squareThickness)
        )
        trans.setAlphaF(0)
        qp.setBrush(trans)
        qp.drawRect(r)

class ChatGPTApp(QMainWindow): # class for chatgpt work 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMGGPT ")
        self.setGeometry(100, 100, 800, 600)
        self.topMenu()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.text_input = QLineEdit(self)
        layout.addWidget(self.text_input)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.get_chatgpt_response)
        self.submit_button.move(30,150)
        layout.addWidget(self.submit_button)
        
        self.response_label = QLabel(self)
        layout.addWidget(self.response_label)
        
        container = QWidget()
        container.setLayout(layout)
        
        self.setCentralWidget(container)
    
        self.button = QPushButton('input text', self)
        self.button.move(30,150)
        self.button.clicked.connect(self.on_click)
        self.show()

    @pyqtSlot()
    def on_click(self):
        textboxValue = self.text_input.text()
        image_path = "same_image_path"
        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image)
        self.text_input.setText(extracted_text)

    def topMenu(self):
        menubar = self.menuBar()

        fileMenu = menubar.addMenu("File")
        saveAct = QtWidgets.QAction(QtGui.QIcon("icon_image_if available"), "Save", self)
        saveAsAct = QtWidgets.QAction(QtGui.QIcon("same_icon_image"), "Save As", self)

        modeMenu = menubar.addMenu("Mode")
        snipAct = QtWidgets.QAction(QtGui.QIcon("image_icon"), "Snip", self)
        snipAct.setShortcut(QtGui.QKeySequence("F1"))
        snipAct.triggered.connect(self.activateSnipping)
        autoAct = QtWidgets.QAction(QtGui.QIcon("image_icon"), "Automation", self)
        autoAct.setShortcut("F4")

        optionsMenu = menubar.addMenu("Options")

        fileMenu.addAction(saveAct)
        fileMenu.addAction(saveAsAct)
        modeMenu.addAction(snipAct)
        self.snipper = SnippingWidget()
        self.snipper.closed.connect(self.on_closed)

    def activateSnipping(self):
        self.snipper.showFullScreen()
        QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
        self.hide()

    
    def get_chatgpt_response(self):
        user_input = self.text_input.text()
        
        response = self.generate_chatgpt_response(user_input)
        
        self.display_response(response)
    
    def generate_chatgpt_response(self, input_text):
        prompt = f"User: {input_text}\nAI:"
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can experiment with different engines
            prompt=prompt,
            max_tokens=50  # You can adjust the response length
        )
        return response.choices[0].text.strip()
    
    def display_response(self, response):
        self.response_label.setText(response)

    def on_closed(self):
        self.show()

    def on_closed(self):
        self.show()

    try:
        if os.path.isfile(imfilepath)is True:
            os.remove('ocr.png')
        else:
            pass
    except FileNotFoundError as e:
        print(f"FileNotFoundError successfully handled\n"
          f"{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qtmodern.styles.dark(app)
    
    window = ChatGPTApp()
    mw = qtmodern.windows.ModernWindow(window)
    mw.show()
    sys.exit(app.exec_())
