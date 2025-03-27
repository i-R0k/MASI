from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QStyle,
    QInputDialog, QMessageBox
)
from PyQt5.QtGui import (
    QPainter, QPen, QFont, QColor, QPainterPath
)
from PyQt5.QtCore import Qt, QRectF, QPointF, QSize

# Stałe operatorów
OPERATOR_SEQUENCING = ";"
OPERATOR_PARALLEL = ","

class UnitermWidget(QWidget):
    def __init__(self, parent=None):
        super(UnitermWidget, self).__init__(parent)
        self.sA = ""
        self.sOp = ""
        self.sB = ""
        self.sA2 = ""
        self.sB2 = ""
        self.shouldDrawLine = False      # dla trybu równoległego
        self.mode = "sequence"           # "sequence" lub "parallel"
        self.showSequenceArcLine = False # czy w trybie sekwencyjnym rysować łuk nad tekstem

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.mode == "horizontal_left_arc":
            # Łuk po lewej: (X, Y) ; B
            self.drawHorizontalParallelSequence(painter, arcSide="left")
        elif self.mode == "horizontal_right_arc":
            # Łuk po prawej: A ; (X, Y)
            self.drawHorizontalParallelSequence(painter, arcSide="right")
        elif self.mode == "sequence":
            self.drawSequence(painter)
        else:
            self.drawParallel(painter)

    def drawSequence(self, painter):
        # Wypełniamy tło
        painter.fillRect(self.rect(), QColor("#FAFAFA"))

        # Sprawdzamy, czy wprowadzono choć jeden element unitermu
        if not (self.sA.strip() or self.sOp.strip() or self.sB.strip()):
            return

        # Ustawienia wstępne
        margin = 5       # odstęp między liniami tekstu
        padding = 20     # odstęp "góra-dół" wewnątrz obszaru
        arcX = 50        # pozycja X, w której rysujemy krzywą
        topY = 50        # pozycja Y startu krzywej

        # Oblicz łączną wysokość tekstu (sA, sOp, sB)
        measureY = 0
        hA = self.getTextHeight(painter, self.sA)
        if hA:
            measureY += hA + margin
        hOp = self.getTextHeight(painter, self.sOp)
        if hOp:
            measureY += hOp + margin
        hB = self.getTextHeight(painter, self.sB)
        if hB:
            measureY += hB + margin

        if measureY > 0:
            measureY -= margin

        totalTextHeight = measureY
        lineHeight = totalTextHeight + 2 * padding
        bottomY = topY + lineHeight

        # Rysowanie krzywej (kształt nawiasu) po lewej stronie
        path = QPainterPath()
        start = QPointF(arcX, topY)
        end = QPointF(arcX, bottomY)

        # Punkty kontrolne przesunięte w lewo, by uzyskać łuk w lewo
        ctrl1 = QPointF(arcX - 25, topY + lineHeight * 0.25)
        ctrl2 = QPointF(arcX - 25, topY + lineHeight * 0.75)

        path.moveTo(start)
        path.cubicTo(ctrl1, ctrl2, end)

        # Ustawiamy pióro dla krzywej – SteelBlue
        penCurve = QPen(QColor("#4682B4"), 3)
        painter.setPen(penCurve)
        painter.drawPath(path)

        # Ustawiamy pióro na kolor tekstu
        painter.setPen(QColor("#212121"))

        # Rysowanie tekstu pionowo, z prawej strony krzywej
        textX = arcX + 20
        currentY = topY + padding

        if self.sA:
            painter.drawText(textX, int(currentY + hA), self.sA)
            currentY += hA + margin

        if self.sOp:
            painter.drawText(textX, int(currentY + hOp), self.sOp)
            currentY += hOp + margin

        if self.sB:
            painter.drawText(textX, int(currentY + hB), self.sB)
            currentY += hB + margin

    def drawParallel(self, painter):
        # Wypełniamy tło
        painter.fillRect(self.rect(), QColor("#FAFAFA"))
        margin = 5
        padding = 20
        lineX = 100
        topY = 30

        measureY = 0
        hA = self.getTextHeight(painter, self.sA)
        if hA:
            measureY += hA + margin
        hOp = self.getTextHeight(painter, self.sOp)
        if hOp:
            measureY += hOp + margin
        hB = self.getTextHeight(painter, self.sB)
        if hB:
            measureY += hB + margin

        if measureY > 0:
            measureY -= margin
        totalTextHeight = measureY
        lineHeight = totalTextHeight + 2 * padding
        bottomY = topY + lineHeight

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
        painter.setPen(QColor("#212121"))
        currentY = textStartY

        if self.sA:
            painter.drawText(textX, int(currentY + hA), self.sA)
            currentY += hA + margin
        if self.sOp:
            painter.drawText(textX, int(currentY + hOp), self.sOp)
            currentY += hOp + margin
        if self.sB:
            painter.drawText(textX, int(currentY + hB), self.sB)
            currentY += hB + margin
    
    def drawHorizontalParallelSequence(self, painter, arcSide):
        """
        Rysuje poziomy układ z kreską u góry i łukiem nad fragmentem X, Y.

        arcSide = "left"  -> (X, Y) ; B
        arcSide = "right" -> A ; (X, Y)
        Gdzie X = sA2, Y = sB2, A = sA, B = sB
        """

        painter.fillRect(self.rect(), QColor("#FAFAFA"))

        # 1. Kreska z "ptaszkami" u góry
        penLine = QPen(QColor("#00BCD4"), 3)
        painter.setPen(penLine)
        topLineY = 50
        leftX = 50
        rightX = 350
        painter.drawLine(QPointF(leftX, topLineY), QPointF(rightX, topLineY))
        tickLen = 10
        painter.drawLine(QPointF(leftX, topLineY - tickLen/2),
                         QPointF(leftX, topLineY + tickLen/2))
        painter.drawLine(QPointF(rightX, topLineY - tickLen/2),
                         QPointF(rightX, topLineY + tickLen/2))

        # 2. Przygotowanie tekstu
        # X, Y -> self.sA2, self.sB2
        # A -> self.sA
        # B -> self.sB
        # Wynik:
        #  - jeśli arcSide="left":   (X, Y) ; B
        #  - jeśli arcSide="right":  A ; (X, Y)

        XcommaY = f"{self.sA2}, {self.sB2}"  # np. "X, Y"
        baseTextY = 120
        spacing = 10
        painter.setFont(QFont("Segoe UI", 14))
        painter.setPen(QColor("#212121"))

        xPos = leftX

        if arcSide == "left":
            # Rysujemy "(X, Y)" po lewej z łukiem, potem "; B"
            rectXY = painter.boundingRect(0, 0, 9999, 9999, 0, XcommaY)
            # Rysujemy X, Y
            painter.drawText(xPos, baseTextY, XcommaY)

            # Rysujemy łuk nad "X, Y"
            xyWidth = rectXY.width()
            xyHeight = rectXY.height()
            arcBaseY = baseTextY - xyHeight - 10
            arcLeft = xPos
            arcRight = xPos + xyWidth

            arcPath = QPainterPath()
            arcPath.moveTo(QPointF(arcLeft, arcBaseY))
            arcPath.cubicTo(QPointF(arcLeft + xyWidth*0.25, arcBaseY - 15),
                            QPointF(arcLeft + xyWidth*0.75, arcBaseY - 15),
                            QPointF(arcRight, arcBaseY))

            penArc = QPen(QColor("#4682B4"), 2)
            painter.setPen(penArc)
            painter.drawPath(arcPath)

            # Przesuwamy xPos
            xPos += xyWidth + spacing

            # Teraz "; B"
            restExpr = f"; {self.sB}"  # np. "; B"
            painter.setPen(QColor("#212121"))
            painter.drawText(xPos, baseTextY, restExpr)

        else:
            # arcSide == "right": rysujemy "A ;" po lewej, a (X, Y) z łukiem po prawej
            # 1) Rysujemy "A ;"
            leftExpr = f"{self.sA} ;"
            rectLeft = painter.boundingRect(0, 0, 9999, 9999, 0, leftExpr)
            painter.drawText(xPos, baseTextY, leftExpr)
            xPos += rectLeft.width() + spacing

            # 2) Rysujemy "(X, Y)" z łukiem
            rectXY = painter.boundingRect(0, 0, 9999, 9999, 0, XcommaY)
            painter.drawText(xPos, baseTextY, XcommaY)

            # Łuk nad X, Y
            xyWidth = rectXY.width()
            xyHeight = rectXY.height()
            arcBaseY = baseTextY - xyHeight - 10
            arcLeft = xPos
            arcRight = xPos + xyWidth

            arcPath = QPainterPath()
            arcPath.moveTo(QPointF(arcLeft, arcBaseY))
            arcPath.cubicTo(QPointF(arcLeft + xyWidth*0.25, arcBaseY - 15),
                            QPointF(arcLeft + xyWidth*0.75, arcBaseY - 15),
                            QPointF(arcRight, arcBaseY))

            penArc = QPen(QColor("#4682B4"), 2)
            painter.setPen(penArc)
            painter.drawPath(arcPath)

    def drawBezierArc(self, painter, leftX, baselineY, width):
        path = QPainterPath()
        start = QPointF(leftX, baselineY)
        end = QPointF(leftX + width, baselineY)
        ctrl1 = QPointF(leftX + width * 0.25, baselineY - 20)
        ctrl2 = QPointF(leftX + width * 0.75, baselineY - 20)
        path.moveTo(start)
        path.cubicTo(ctrl1, ctrl2, end)
        pen = QPen(QColor("#4682B4"), 3)  # SteelBlue
        painter.setPen(pen)
        painter.drawPath(path)

    def getTextHeight(self, painter, text):
        if not text:
            return 0
        rect = painter.boundingRect(QRectF(0, 0, 400, 100),
                                    Qt.TextWordWrap, text)
        return rect.height()

class RecordItemWidget(QWidget):
    def __init__(self, record_id, name, parent=None):
        super().__init__(parent)
        self.record_id = record_id
        self.name = name

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.nameLabel = QLabel(self.name)
        self.nameLabel.setStyleSheet("margin: 0; padding: 0;")
        layout.addWidget(self.nameLabel)

        self.renameButton = QPushButton()
        self.renameButton.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.renameButton.setToolTip("Zmień nazwę")
        self.renameButton.setIconSize(QSize(16, 16))
        self.renameButton.setFlat(True)
        self.renameButton.setFixedSize(20, 20)
        self.renameButton.setStyleSheet("background: none; border: none;")
        layout.addWidget(self.renameButton)

        self.openButton = QPushButton()
        self.openButton.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.openButton.setToolTip("Otwórz")
        self.openButton.setIconSize(QSize(16, 16))
        self.openButton.setFlat(True)
        self.openButton.setFixedSize(20, 20)
        self.openButton.setStyleSheet("background: none; border: none;")
        layout.addWidget(self.openButton)

        self.deleteButton = QPushButton()
        self.deleteButton.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        self.deleteButton.setToolTip("Usuń")
        self.deleteButton.setIconSize(QSize(16, 16))
        self.deleteButton.setFlat(True)
        self.deleteButton.setFixedSize(20, 20)
        self.deleteButton.setStyleSheet("background: none; border: none;")
        layout.addWidget(self.deleteButton)

        self.setLayout(layout)

class MainWindow(QWidget):
    def __init__(self, db, parent=None):
        super(MainWindow, self).__init__(parent)
        self.db = db
        self.setWindowTitle("Uniterm")
        self.resize(1080, 720)

        # GŁÓWNY layout – podział na lewą i prawą kolumnę
        mainLayout = QHBoxLayout(self)
        mainLayout.setSpacing(15)
        mainLayout.setContentsMargins(20, 20, 20, 20)

        # Lewa kolumna: lista rekordów
        leftLayout = QVBoxLayout()
        self.listWidget = QListWidget()
        leftLayout.addWidget(QLabel("Lista zapisanych wyrażeń:"))
        leftLayout.addWidget(self.listWidget)
        leftContainer = QWidget()
        leftContainer.setLayout(leftLayout)
        mainLayout.addWidget(leftContainer, stretch=0)

        # Prawa kolumna: interfejs główny
        rightLayout = QVBoxLayout()

        # Panel wejściowy: sA i sB dla pierwszego unitermu (operator stały)
        inputLayout = QHBoxLayout()
        self.sAEdit = QLineEdit()
        self.sAEdit.setPlaceholderText("Wprowadź sA")
        self.sBEdit = QLineEdit()
        self.sBEdit.setPlaceholderText("Wprowadź sB")
        inputLayout.addWidget(QLabel("sA:"))
        inputLayout.addWidget(self.sAEdit)
        inputLayout.addWidget(QLabel("sB:"))
        inputLayout.addWidget(self.sBEdit)
        rightLayout.addLayout(inputLayout)

        # Panel wejściowy: sA i sB dla drugiego unitermu
        inputLayout2 = QHBoxLayout()
        self.sA2Edit = QLineEdit()
        self.sA2Edit.setPlaceholderText("Wprowadź sA")
        self.sB2Edit = QLineEdit()
        self.sB2Edit.setPlaceholderText("Wprowadź sB")
        inputLayout2.addWidget(QLabel("sA:"))
        inputLayout2.addWidget(self.sA2Edit)
        inputLayout2.addWidget(QLabel("sB:"))
        inputLayout2.addWidget(self.sB2Edit)
        rightLayout.addLayout(inputLayout2)

        # Panel przycisków trybu rysowania
        btnLayout = QHBoxLayout()
        self.seqButton = QPushButton("Sekwencjonuj")
        self.parButton = QPushButton("Zrównolegnij")
        btnLayout.addWidget(self.seqButton)
        btnLayout.addWidget(self.parButton)
        rightLayout.addLayout(btnLayout)

        # Widget rysujący uniterm
        self.unitermWidget = UnitermWidget(self)
        self.unitermWidget.setMinimumHeight(400)
        rightLayout.addWidget(self.unitermWidget)

        # Dolny pasek: pola "Nazwa", "Opis" oraz przycisk "Zapisz"
        bottomLayout = QHBoxLayout()
        self.nameEdit = QLineEdit()
        self.nameEdit.setPlaceholderText("Nazwa")
        self.descEdit = QLineEdit()
        self.descEdit.setPlaceholderText("Opis")
        self.saveButton = QPushButton("Zapisz")
        bottomLayout.addWidget(QLabel("Nazwa:"))
        bottomLayout.addWidget(self.nameEdit)
        bottomLayout.addWidget(QLabel("Opis:"))
        bottomLayout.addWidget(self.descEdit)
        bottomLayout.addWidget(self.saveButton)
        rightLayout.addLayout(bottomLayout)

        rightContainer = QWidget()
        rightContainer.setLayout(rightLayout)
        mainLayout.addWidget(rightContainer, stretch=1)
        
        # Podpięcie zdarzeń
        self.seqButton.clicked.connect(self.drawSequenceWithArcLine)
        self.parButton.clicked.connect(self.onParallel)
        self.saveButton.clicked.connect(self.onSave)

        # Stylizacja
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
        """)
        self.setLayout(mainLayout)
        self.refreshList()

    def updateUnitermData(self):
        self.unitermWidget.sA = self.sAEdit.text()
        if self.unitermWidget.mode == "parallel":
            self.unitermWidget.sOp = OPERATOR_PARALLEL
        else:
            self.unitermWidget.sOp = OPERATOR_SEQUENCING
        self.unitermWidget.sB = self.sBEdit.text()

    def drawSequenceWithArcLine(self):
        choice, ok = QInputDialog.getItem(
            self,
            "Wybierz uniterm",
            "Który uniterm sekwencjonować?",
            ["Pierwszy", "Drugi"],
            0, False
        )
        if not ok:
            return

        self.unitermWidget.mode = "sequence"
        self.unitermWidget.showSequenceArcLine = True
        self.unitermWidget.shouldDrawLine = False

        if choice == "Pierwszy":
            self.unitermWidget.sA = self.sAEdit.text()
            self.unitermWidget.sOp = OPERATOR_SEQUENCING
            self.unitermWidget.sB = self.sBEdit.text()
        else:
            self.unitermWidget.sA = self.sA2Edit.text()
            self.unitermWidget.sOp = OPERATOR_SEQUENCING
            self.unitermWidget.sB = self.sB2Edit.text()

        self.unitermWidget.update()

    def drawParallel(self):
        """
        Ustawia tryb równoległy – pobiera dane i ustawia operator na OPERATOR_PARALLEL.
        """
        self.unitermWidget.mode = "parallel"
        self.unitermWidget.showSequenceArcLine = False
        self.unitermWidget.shouldDrawLine = True
        self.updateUnitermData()
        self.unitermWidget.update()

    def onSave(self):
        name = self.nameEdit.text().strip()
        description = self.descEdit.text().strip()
        sA = self.sAEdit.text().strip()
        sB = self.sBEdit.text().strip()
        sOp = OPERATOR_SEQUENCING  # domyślny operator dla sekwencjonowania
        sA2 = self.sA2Edit.text().strip()
        sB2 = self.sB2Edit.text().strip()
        sOp2 = OPERATOR_SEQUENCING  # domyślny operator dla drugiego unitermu

        if not name:
            name = "Brak nazwy"

        from database import DatabaseManager
        db = DatabaseManager()
        db.insert_uniterm(name, description, sA, sOp, sB, sA2)

        self.nameEdit.clear()
        self.descEdit.clear()
        self.refreshList()

    def refreshList(self):
        self.listWidget.clear()
        rows = self.db.fetch_all_uniterms()
        for (record_id, name, description, sOp) in rows:
            listItem = QListWidgetItem()
            listItem.setToolTip(description)
            self.listWidget.addItem(listItem)
    
            itemWidget = RecordItemWidget(record_id, name)
            itemWidget.renameButton.clicked.connect(lambda _, rid=record_id: self.onRename(rid))
            itemWidget.openButton.clicked.connect(lambda _, rid=record_id: self.onOpen(rid))
            itemWidget.deleteButton.clicked.connect(lambda _, rid=record_id: self.onDelete(rid))
    
            self.listWidget.setItemWidget(listItem, itemWidget)
            listItem.setSizeHint(itemWidget.sizeHint())

    def onRename(self, record_id):
        new_name, ok = QInputDialog.getText(self, "Zmień nazwę", "Podaj nową nazwę:")
        if ok and new_name:
            self.db.update_uniterm_name(record_id, new_name)
            self.refreshList()

    def onOpen(self, record_id):
        record = self.db.fetch_uniterm_by_id(record_id)
        if record:
            name, description, sA, sOp, sB, sA2, sOp2, sB2 = record
            self.nameEdit.setText(name)
            self.descEdit.setText(description)
            self.sAEdit.setText(sA)
            self.sBEdit.setText(sB)
            self.sA2Edit.setText(sA2)
            self.sB2Edit.setText(sB2)

    def onDelete(self, record_id):
        self.db.delete_uniterm(record_id)
        self.refreshList()

    def onEqualize(self):
        sA2 = self.sA2Edit.text().strip()
        sOp2 = OPERATOR_SEQUENCING
        sB2 = self.sB2Edit.text().strip()

        if not (sA2 or sOp2 or sB2):
            QMessageBox.information(self, "Brak danych", "Wprowadź dane drugiego unitermu.")
            return

        choice, ok = QInputDialog.getItem(
            self, "Wybierz składową",
            "Podmień komponent pierwszego unitermu:",
            ["sA", "sOp", "sB"],
            0, False
        )
        if not ok:
            return

        if choice == "sA":
            self.unitermWidget.sA = sA2
        elif choice == "sOp":
            self.unitermWidget.sOp = sOp2
        elif choice == "sB":
            self.unitermWidget.sB = sB2

        self.unitermWidget.mode = "parallel"
        self.unitermWidget.shouldDrawLine = True
        self.updateUnitermData()
        self.unitermWidget.update()

    def onParallel(self):
        choice, ok = QInputDialog.getItem(
            self,
            "Wybierz wyrażenie do zrównolegnienia",
            "Wybierz wyrażenie do zrównolegnienia:",
            ["sA", "sB"],
            0,
            False
        )
        if not ok:
            return
    
        # Pobieramy teksty
        A = self.sAEdit.text().strip()   
        B = self.sBEdit.text().strip()   
        X = self.sA2Edit.text().strip()  
        Y = self.sB2Edit.text().strip()  
    
        if choice == "sA":
            # -> (X, Y) ; B  z łukiem nad X, Y
            self.unitermWidget.mode = "horizontal_left_arc"
            self.unitermWidget.sA2 = X  # "X"
            self.unitermWidget.sB2 = Y  # "Y"
            self.unitermWidget.sB = B   # "B"
            # sA nie jest używane w arcSide="left"
        else:
            # choice == "sB"
            # -> A ; (X, Y)  z łukiem nad X, Y
            self.unitermWidget.mode = "horizontal_right_arc"
            self.unitermWidget.sA = A   # "A"
            self.unitermWidget.sA2 = X  # "X"
            self.unitermWidget.sB2 = Y  # "Y"
            # sB nie jest używane w arcSide="right"
    
        self.unitermWidget.update()
    