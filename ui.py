from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QLabel, QPushButton, QRadioButton, QButtonGroup, QListWidget, QListWidgetItem, QStyle
)
from PyQt5.QtGui import (
    QPainter, QPen, QFont, QColor, QPainterPath
)
from PyQt5.QtCore import Qt, QRectF, QPointF, QSize

class UnitermWidget(QWidget):
    def __init__(self, parent=None):
        super(UnitermWidget, self).__init__(parent)
        self.sA = ""
        self.sOp = ""
        self.sB = ""
        self.shouldDrawLine = False      # dla trybu równoległego
        self.mode = "sequence"           # "sequence" lub "parallel"
        self.showSequenceArcLine = False # czy w trybie sekwencyjnym rysować łuk i pionową linię

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.mode == "sequence":
            self.drawSequence(painter)
        else:
            self.drawParallel(painter)

    # ============== SEKWENCJA ==============

    def drawSequence(self, painter):
        """
        Tryb sekwencyjny:
          - Zawsze rysujemy tekst (sA, sOp, sB) w jednej linii.
          - Jeżeli showSequenceArcLine = True, rysujemy też łuk i pionową linię.
        """
        painter.fillRect(self.rect(), QColor("#FAFAFA"))

        lineX = 50
        textTop = 100

        # Tekst z odstępami (np. "a   ;   b")
        combined = f"{self.sA}   {self.sOp}   {self.sB}"

        painter.setFont(QFont("Segoe UI", 14))
        rectText = painter.boundingRect(QRectF(0, 0, 9999, 9999), 0, combined)
        textWidth = rectText.width()
        textHeight = rectText.height()

        # Rysujemy tekst
        painter.setPen(QColor("#212121"))
        painter.drawText(int(lineX), int(textTop + textHeight), combined)

        # Jeśli showSequenceArcLine = True, rysujemy łuk i pionową linię
        if self.showSequenceArcLine:
            self.drawBezierArc(painter, lineX, textTop, textWidth)

            # Krótsza pionowa linia zależna od rozmiaru tekstu
            topLine = int(textTop - -120)
            bottomLine = int(textTop + textHeight + 20)

            pen = QPen(QColor("#00BCD4"), 2)
            painter.setPen(pen)
            painter.drawLine(QPointF(lineX, topLine), QPointF(lineX, bottomLine))

            self.drawOpOnVerticalLine(painter, lineX, topLine, bottomLine)

    def drawBezierArc(self, painter, leftX, baselineY, width):
        """
        Rysuje łagodny łuk (krzywą Beziera) nad tekstem (start w leftX, end w leftX+width).
        """
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

    def drawOpOnVerticalLine(self, painter, lineX, topLine, bottomLine):
        """
        Rysuje operator sOp pionowo na pionowej linii.
        """
        segmentCount = 2
        totalHeight = bottomLine - topLine
        segmentHeight = totalHeight / segmentCount

        painter.setPen(QColor("#212121"))
        painter.setFont(QFont("Segoe UI", 12))

        for i in range(segmentCount):
            segTop = topLine + i * segmentHeight
            textY = segTop + segmentHeight / 2
            painter.drawText(int(lineX + 5), int(textY), self.sOp)

    # ============== RÓWNOLEGŁOŚĆ ==============

    def drawParallel(self, painter):
        """
        Tryb równoległy – pionowa kreska łącząca sA, sOp, sB w pionie.
        """
        painter.fillRect(self.rect(), QColor("#FAFAFA"))
        margin = 5
        padding = 20
        lineX = 100
        topY = 30

        measureY = 0
        hA = self.getTextHeight(painter, self.sA)
        if hA: measureY += hA + margin
        hOp = self.getTextHeight(painter, self.sOp)
        if hOp: measureY += hOp + margin
        hB = self.getTextHeight(painter, self.sB)
        if hB: measureY += hB + margin

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
        pen = QPen(QColor("#212121"), 3)
        painter.setPen(pen)
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

        # Ustawienie layoutu z odstępem 5px i brakiem marginesów
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)  # odstęp między widgetami ustawiony na 5 pikseli

        # Etykieta z nazwą
        self.nameLabel = QLabel(self.name)
        self.nameLabel.setStyleSheet("margin: 0; padding: 0;")
        layout.addWidget(self.nameLabel)

        # Przycisk "Zmień nazwę"
        self.renameButton = QPushButton()
        self.renameButton.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.renameButton.setToolTip("Zmień nazwę")
        self.renameButton.setIconSize(QSize(16, 16))
        self.renameButton.setFlat(True)
        self.renameButton.setFixedSize(20, 20)  # wymusza stały rozmiar
        self.renameButton.setStyleSheet("background: none; border: none;")
        layout.addWidget(self.renameButton)

        # Przycisk "Otwórz"
        self.openButton = QPushButton()
        self.openButton.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.openButton.setToolTip("Otwórz")
        self.openButton.setIconSize(QSize(16, 16))
        self.openButton.setFlat(True)
        self.openButton.setFixedSize(20, 20)
        self.openButton.setStyleSheet("background: none; border: none;")
        layout.addWidget(self.openButton)

        # Przycisk "Usuń"
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

        # GŁÓWNY layout poziomy – podział na lewą i prawą kolumnę
        mainLayout = QHBoxLayout(self)
        mainLayout.setSpacing(15)
        mainLayout.setContentsMargins(20, 20, 20, 20)

        # ----- Lewa kolumna: lista rekordów i przyciski "Odśwież"/"Usuń" -----
        leftLayout = QVBoxLayout()
        self.listWidget = QListWidget()
        leftLayout.addWidget(QLabel("Lista zapisanych wyrażeń:"))
        leftLayout.addWidget(self.listWidget)

        leftContainer = QWidget()
        leftContainer.setLayout(leftLayout)
        # Lewa kolumna ma stałą (mniejszą) szerokość
        mainLayout.addWidget(leftContainer, stretch=0)

        # ----- Prawa kolumna: reszta interfejsu -----
        rightLayout = QVBoxLayout()

        # Panel wejściowy: sA, operator i sB
        inputLayout = QHBoxLayout()
        self.sAEdit = QLineEdit()
        self.sAEdit.setPlaceholderText("Wprowadź sA")
        self.semicolonRadio = QRadioButton(";")
        self.commaRadio = QRadioButton(",")
        self.operatorGroup = QButtonGroup(self)
        self.operatorGroup.addButton(self.semicolonRadio)
        self.operatorGroup.addButton(self.commaRadio)
        self.semicolonRadio.setChecked(True)
        self.sBEdit = QLineEdit()
        self.sBEdit.setPlaceholderText("Wprowadź sB")

        inputLayout.addWidget(QLabel("sA:"))
        inputLayout.addWidget(self.sAEdit)
        inputLayout.addWidget(QLabel("Operator:"))
        inputLayout.addWidget(self.semicolonRadio)
        inputLayout.addWidget(self.commaRadio)
        inputLayout.addWidget(QLabel("sB:"))
        inputLayout.addWidget(self.sBEdit)
        rightLayout.addLayout(inputLayout)

        # Panel przycisków trybu rysowania
        btnLayout = QHBoxLayout()
        self.seqButton = QPushButton("Sekwencjonuj")
        self.parButton = QPushButton("Zrównolegnij")
        btnLayout.addWidget(self.seqButton)
        btnLayout.addWidget(self.parButton)
        rightLayout.addLayout(btnLayout)

        # Widget rysujący
        self.unitermWidget = UnitermWidget(self)
        self.unitermWidget.setMinimumHeight(400)
        rightLayout.addWidget(self.unitermWidget)

        # Dolny pasek: pola "Nazwa" i "Opis" oraz przycisk "Zapisz"
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
        # Prawa kolumna zajmuje całą pozostałą przestrzeń
        mainLayout.addWidget(rightContainer, stretch=1)
        
        # Zdarzenia
        self.seqButton.clicked.connect(self.drawSequenceWithArcLine)
        self.parButton.clicked.connect(self.drawParallel)
        self.saveButton.clicked.connect(self.onSave)


        # Styl
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
        # Ustawienie głównego layoutu
        self.setLayout(mainLayout)
        self.refreshList()

    def updateUnitermData(self):
        self.unitermWidget.sA = self.sAEdit.text()
        if self.semicolonRadio.isChecked():
            self.unitermWidget.sOp = ";"
        elif self.commaRadio.isChecked():
            self.unitermWidget.sOp = ","
        else:
            self.unitermWidget.sOp = ""
        self.unitermWidget.sB = self.sBEdit.text()

    def drawSequenceWithArcLine(self):
        """
        Po naciśnięciu przycisku „Sekwencjonuj”:
         - tryb sekwencyjny
         - rysujemy łuk i pionową linię
        """
        self.unitermWidget.mode = "sequence"
        self.unitermWidget.showSequenceArcLine = True
        self.unitermWidget.shouldDrawLine = False  # nie dotyczy trybu sekwencyjnego
        self.updateUnitermData()
        self.unitermWidget.update()

    def drawParallel(self):
        """
        Po naciśnięciu „Zrównolegnij”:
         - tryb równoległy
         - rysujemy pionową kreskę z sA, sOp, sB w pionie
        """
        self.unitermWidget.mode = "parallel"
        self.unitermWidget.showSequenceArcLine = False
        self.unitermWidget.shouldDrawLine = True
        self.updateUnitermData()
        self.unitermWidget.update()

    def onSave(self):
        """Zapisuje rekord do bazy i odświeża listę."""
        name = self.nameEdit.text().strip()
        description = self.descEdit.text().strip()
        sA = self.sAEdit.text().strip()
        sB = self.sBEdit.text().strip()
        sOp = ";" if self.semicolonRadio.isChecked() else ","

        if not name:
            name = "Brak nazwy"

        from database import DatabaseManager
        db = DatabaseManager()
        db.insert_uniterm(name, description, sA, sOp, sB)

        # Wyczyść pola formularza
        self.nameEdit.clear()
        self.descEdit.clear()
        # Odśwież listę – dzięki temu zmiany są widoczne automatycznie
        self.refreshList()

    def refreshList(self):
        self.listWidget.clear()
        rows = self.db.fetch_all_uniterms()  # [(id, name, sOp), ...]

        for (record_id, name, sOp) in rows:
            # 1. Tworzymy pusty QListWidgetItem
            listItem = QListWidgetItem()
            self.listWidget.addItem(listItem)

            # 2. Tworzymy własny widget
            itemWidget = RecordItemWidget(record_id, name)

            # 3. Podpinamy sygnały przycisków do metod MainWindow
            itemWidget.renameButton.clicked.connect(lambda _, rid=record_id: self.onRename(rid))
            itemWidget.openButton.clicked.connect(lambda _, rid=record_id: self.onOpen(rid))
            itemWidget.deleteButton.clicked.connect(lambda _, rid=record_id: self.onDelete(rid))

            # 4. Osadzamy widget w wierszu listy
            self.listWidget.setItemWidget(listItem, itemWidget)

            # 5. (Opcjonalnie) dopasowujemy wysokość wiersza do widgetu
            listItem.setSizeHint(itemWidget.sizeHint())

    def onRename(self, record_id):
        # np. zapytaj o nową nazwę w QInputDialog
        # zaktualizuj w bazie (UPDATE)
        self.refreshList()
    
    def onOpen(self, record_id):
        # wczytanie do pól sA, sB, ewentualnie rysowanie, itp.
        self.refreshList()
    
    def onDelete(self, record_id):
        self.db.delete_uniterm(record_id)
        self.refreshList()
