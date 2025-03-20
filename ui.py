from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
    QPushButton, QRadioButton, QButtonGroup
)
from PyQt5.QtGui import QPainter, QPen, QFont, QLinearGradient, QColor, QBrush
from PyQt5.QtCore import Qt, QRectF, QPointF

class UnitermWidget(QWidget):
    def __init__(self, parent=None):
        super(UnitermWidget, self).__init__(parent)
        self.sA = ""
        self.sOp = "" 
        self.sB = ""
        self.shouldDrawLine = False  
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        font = QFont("Segoe UI", 14)
        painter.setFont(font)
        
        margin = 5
        padding = 20
        lineX = 100
        topY = 30
        
        measureY = 0
        heightA = 0
        if self.sA:
            rectA = painter.boundingRect(QRectF(0, 0, 400, 100),
                                         Qt.TextWordWrap, self.sA)
            heightA = rectA.height()
            measureY += heightA + margin
        
        heightOp = 0
        if self.sOp:
            rectOp = painter.boundingRect(QRectF(0, 0, 400, 100),
                                          Qt.TextWordWrap, self.sOp)
            heightOp = rectOp.height()
            measureY += heightOp + margin
        
        heightB = 0
        if self.sB:
            rectB = painter.boundingRect(QRectF(0, 0, 400, 100),
                                         Qt.TextWordWrap, self.sB)
            heightB = rectB.height()
            measureY += heightB + margin
        
        if measureY > 0:
            measureY -= margin
        totalTextHeight = measureY
        
        lineHeight = totalTextHeight + 2 * padding
        bottomY = topY + lineHeight
        
        painter.fillRect(self.rect(), QColor("#FAFAFA"))
        
        if self.shouldDrawLine:
            pen = QPen(QColor("#00BCD4"), 3)
            painter.setPen(pen)
            painter.drawLine(QPointF(lineX, topY), QPointF(lineX, bottomY))
            
            tickLength = 10
            painter.drawLine(QPointF(lineX - tickLength/2, topY),
                             QPointF(lineX + tickLength/2, topY))
            painter.drawLine(QPointF(lineX - tickLength/2, bottomY),
                             QPointF(lineX + tickLength/2, bottomY))
        
        textStartY = topY + (lineHeight - totalTextHeight) / 2
        textX = lineX + 20
        
        pen = QPen(QColor("#212121"), 3)
        painter.setPen(pen)
        currentY = textStartY
        
        if self.sA:
            painter.drawText(textX, int(currentY + heightA), self.sA)
            currentY += heightA + margin
        
        if self.sOp:
            painter.drawText(textX, int(currentY + heightOp), self.sOp)
            currentY += heightOp + margin
        
        if self.sB:
            painter.drawText(textX, int(currentY + heightB), self.sB)
            currentY += heightB + margin

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Uniterm")
        self.resize(900, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        inputLayout = QHBoxLayout()
        self.sAEdit = QLineEdit(self)
        self.sAEdit.setPlaceholderText("Wprowadź sA")
        
        self.semicolonRadio = QRadioButton(";")
        self.commaRadio = QRadioButton(",")
        self.operatorGroup = QButtonGroup(self)
        self.operatorGroup.addButton(self.semicolonRadio)
        self.operatorGroup.addButton(self.commaRadio)
        self.semicolonRadio.setChecked(True)
        
        self.sBEdit = QLineEdit(self)
        self.sBEdit.setPlaceholderText("Wprowadź sB")
        
        inputLayout.addWidget(QLabel("sA:"))
        inputLayout.addWidget(self.sAEdit)
        
        inputLayout.addWidget(QLabel("Operator:"))
        inputLayout.addWidget(self.semicolonRadio)
        inputLayout.addWidget(self.commaRadio)
        
        inputLayout.addWidget(QLabel("sB:"))
        inputLayout.addWidget(self.sBEdit)
        
        layout.addLayout(inputLayout)
        
        self.drawButton = QPushButton("Rysuj", self)
        layout.addWidget(self.drawButton)
        
        self.unitermWidget = UnitermWidget(self)
        self.unitermWidget.setMinimumHeight(400)
        layout.addWidget(self.unitermWidget)
        
        self.drawButton.clicked.connect(self.updateDrawing)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #FAFAFA;
                color: #212121;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }

            QLineEdit {
                background-color: #E3F2FD;
                color: #212121;
                border: 1px solid #90CAF9;
                border-radius: 6px;
                padding: 4px;
            }

            QLabel {
                font-size: 14px;
                color: #212121;
            }

            QPushButton {
                background-color: #81D4FA;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 14px;
                color: #212121;
            }

            QPushButton:hover {
                background-color: #4FC3F7;
            }

            QRadioButton {
                font-size: 14px;
                color: #212121;
            }
        """)
        
        self.setLayout(layout)
    
    def updateDrawing(self):
        self.unitermWidget.sA = self.sAEdit.text()
        
        if self.semicolonRadio.isChecked():
            self.unitermWidget.sOp = ";"
        elif self.commaRadio.isChecked():
            self.unitermWidget.sOp = ","
        else:
            self.unitermWidget.sOp = ""
        
        self.unitermWidget.sB = self.sBEdit.text()
        
        self.unitermWidget.shouldDrawLine = True
        self.unitermWidget.update()
