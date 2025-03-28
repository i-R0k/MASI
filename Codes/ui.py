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
            self.drawHorizontalParallelSequence(painter, arcSide="left")
        elif self.mode == "horizontal_right_arc":
            self.drawHorizontalParallelSequence(painter, arcSide="right")
        elif self.mode == "vertical_top_arc":
            self.drawVerticalParallelSequence(painter, arcSide="top")
        elif self.mode == "vertical_bottom_arc":
            self.drawVerticalParallelSequence(painter, arcSide="bottom")
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
    
    def drawVerticalXY(self, painter, startX, startY, X, Y):
       """
       Rysuje pionowo:
          X
          ;
          Y
       z łukiem z lewej strony (jak w drawSequence).
       Zwraca (usedWidth, usedHeight, xBaseline),
       gdzie xBaseline to Y-owa baza rysowania X (przyda się do wyrównania A lub B).
       """

       margin = 5
       padding = 20

       # Wysokości tekstów
       hX = self.getTextHeight(painter, X)
       hOp = self.getTextHeight(painter, ";")
       hY = self.getTextHeight(painter, Y)

       measureY = 0
       if hX:
           measureY += hX + margin
       if hOp:
           measureY += hOp + margin
       if hY:
           measureY += hY + margin

       if measureY > 0:
           measureY -= margin

       lineHeight = measureY + 2 * padding
       bottomY = startY + lineHeight

       # Rysujemy łuk (nawias) z lewej
       arcX = startX
       path = QPainterPath()
       path.moveTo(QPointF(arcX, startY))
       ctrl1 = QPointF(arcX - 25, startY + lineHeight * 0.25)
       ctrl2 = QPointF(arcX - 25, startY + lineHeight * 0.75)
       path.cubicTo(ctrl1, ctrl2, QPointF(arcX, bottomY))

       penCurve = QPen(QColor("#4682B4"), 3)
       painter.setPen(penCurve)
       painter.drawPath(path)

       # Rysowanie tekstu pionowo, z prawej strony łuku
       painter.setPen(QColor("#212121"))
       textX = arcX + 20
       currentY = startY + padding

       xBaseline = currentY + hX  # Y-owa linia bazowa, gdzie narysujemy X

       # X
       if X:
           painter.drawText(textX, int(xBaseline), X)
           currentY += hX + margin

       # operator ";"
       if hOp:
           painter.drawText(textX, int(currentY + hOp), ";")
           currentY += hOp + margin

       # Y
       if Y:
           painter.drawText(textX, int(currentY + hY), Y)
           currentY += hY + margin

       usedWidth = 20 + max(hX, hOp, hY)  # orientacyjna szerokość
       usedHeight = lineHeight

       # Zwracamy też xBaseline, by móc wyrównać A/B do poziomu X
       return (usedWidth, usedHeight, xBaseline)

    def drawHorizontalXY(self, painter, startX, startY, X, Y):
        """
        Rysuje w poziomie:
           X ; Y
        z łukiem NAD tym tekstem (wybrzuszonym do góry).
        Zwraca używaną wysokość (by móc przesunąć się dalej w pionie).
        """
        if not (X.strip() or Y.strip()):
            return 0

        # Zbuduj napis "X ; Y" (możesz rozbić na 3 elementy: X, ";", Y)
        blockText = f"{X} ; {Y}"

        # Zmierz boundingRect
        flags = Qt.AlignLeft | Qt.TextSingleLine
        rect = painter.boundingRect(QRectF(0, 0, 1000, 200), flags, blockText)
        textWidth = rect.width()
        textHeight = rect.height()

        # Rysujemy łuk (bezier) od startX do startX + textWidth
        arcHeight = 20  # jak bardzo łuk ma być wybrzuszony
        path = QPainterPath()
        path.moveTo(startX, startY)
        # Punkty kontrolne przesunięte w górę
        ctrl1 = QPointF(startX + textWidth * 0.25, startY - arcHeight)
        ctrl2 = QPointF(startX + textWidth * 0.75, startY - arcHeight)
        end = QPointF(startX + textWidth, startY)
        path.cubicTo(ctrl1, ctrl2, end)

        penArc = QPen(QColor("#4682B4"), 3)
        painter.setPen(penArc)
        painter.drawPath(path)

        # Rysujemy tekst POD łukiem (przesuwając w dół o textHeight)
        painter.setPen(QColor("#212121"))
        textY = startY + textHeight
        painter.drawText(QRectF(startX, textY - rect.height(), textWidth + 5, rect.height()),
                         flags, blockText)

        # Łączna wysokość, jaką to zajeło, to arcHeight + textHeight
        return arcHeight + textHeight
    
    def drawHorizontalParallelSequence(self, painter, arcSide):
        """
        Rysuje poziomą linię (o długości wyliczonej na podstawie tekstu +10% z każdej strony)
        oraz zawartość:
          - Jeśli arcSide == "left": rysujemy pionowy blok (X; Y) (gdzie X = sA2, Y = sB2) z łukiem nad nim,
            a obok, na poziomie X, rysujemy tekst: ", B" (B = sB).
          - Jeśli arcSide == "right": rysujemy tekst "A ," (A = sA),
            a obok (na poziomie X) pionowy blok (X; Y) z łukiem nad nim.
        """
        painter.fillRect(self.rect(), QColor("#FAFAFA"))
        painter.setFont(QFont("Segoe UI", 14))

        # Przygotowanie pionowego bloku: (X; Y) – wykorzystujemy znak nowej linii "\n"
        verticalBlock = f"{self.sA2}\n;\n{self.sB2}"

        # Budujemy pełny ciąg tekstowy zależnie od trybu
        if arcSide == "left":
            # Chcemy uzyskać: (X; Y) , B
            fullExpr = f"{verticalBlock} , {self.sB}"
        else:
            # arcSide == "right": uzyskujemy: {self.sA} , {verticalBlock}
            fullExpr = f"{self.sA} , {verticalBlock}"

        # Mierzymy pełny tekst
        flags = Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop
        rectFull = painter.boundingRect(QRectF(0, 0, 1000, 200), flags, fullExpr)
        fullWidth = rectFull.width()

        lineWidth = int(fullWidth * 3.5)

        # Ustalamy pozycję linii
        leftX = 40
        rightX = leftX + lineWidth
        topLineY = 50

        # Rysujemy poziomą linię
        penLine = QPen(QColor("#00BCD4"), 3)
        painter.setPen(penLine)
        painter.drawLine(QPointF(leftX, topLineY), QPointF(rightX, topLineY))
        tickLen = 10
        # "Wąsy" skierowane wyłącznie w dół
        painter.drawLine(QPointF(leftX, topLineY), QPointF(leftX, topLineY + tickLen))
        painter.drawLine(QPointF(rightX, topLineY), QPointF(rightX, topLineY + tickLen))

        # Ustalamy pozycję rysowania tekstu wewnątrz linii – 10% marginesu z lewej
        textStartX = leftX + int(0.1 * lineWidth)
        baseTextY = 60  # przykładowa pozycja w pionie
        painter.setPen(QColor("#212121"))

        # Teraz rozbijamy tekst na dwie części, by uzyskać efekt wyrównania pionowego bloku
        if arcSide == "left":
            # W trybie "left" chcemy: (X; Y) , B
            # Rysujemy pionowy blok (X; Y) i zapamiętujemy jego pozycję bazową (gdzie rysujemy X)
            usedW, usedH, xBaseline = self.drawVerticalXY(painter, textStartX, baseTextY, self.sA2, self.sB2)
            # Następnie, obok, rysujemy przecinek i B, wyrównane do xBaseline
            xPos = textStartX + usedW + 20
            painter.drawText(int(xPos), int(xBaseline), f",   {self.sB}")
        else:
            # Chcemy: A , (X; Y)

             # 1. Najpierw zmierz szerokość "A ,"
             Asemicolon = f"{self.sA}    ,   "
             flags = Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop
             rectA = painter.boundingRect(QRectF(0, 0, 1000, 200), flags, Asemicolon)

             # 2. Określ, gdzie zacznie się blok (X; Y) - np. z prawej strony "A ," + margines 20 px
             xBlock = textStartX + rectA.width() + 20

             # 3. Rysuj pionowy blok i pobierz xBaseline (linia bazowa, na której wypada "X")
             usedW, usedH, xBaseline = self.drawVerticalXY(
                 painter,
                 xBlock,
                 baseTextY,
                 self.sA2,
                 self.sB2
             )
             painter.drawText(int(textStartX), int(xBaseline), Asemicolon)

    def drawVerticalParallelSequence(self, painter, arcSide):
        """
        Rysuje pionowy nawias kwadratowy (linia + wąsy) obejmujący:
          - w środku pionowy łuk (arc) dla (X, ;, Y),
          - ewentualnie linie u góry lub u dołu.

        Zakładamy, że:
          - arcSide == "top" oznacza "zrównolegnij sA2" -> bez A u góry
          - arcSide == "bottom" oznacza "zrównolegnij sB2" -> ewentualnie bez A, a B poniżej itd.
        """

        painter.fillRect(self.rect(), QColor("#FAFAFA"))
        painter.setFont(QFont("Segoe UI", 14))

        # Marginesy
        margin_line = 5   # odstęp pionowy między wierszami tekstu
        padding_top = 20
        bracketX = 50     # X-owa pozycja nawiasu kwadratowego

        # --- arcLines: (X; Y) ---
        arcLines = []
        if self.sA2.strip():
            arcLines.append(self.sA2)
        arcLines.append(";")
        if self.sB2.strip():
            arcLines.append(self.sB2)

        # Przygotowujemy topLines i bottomLines w zależności od arcSide
        if arcSide == "top":
            # Zrównolegnij sA2: nic na górze (ani A, ani przecinek),
            # ewentualnie na dole ", B" (jeśli B jest niepuste).
            topLines = []
            bottomLines = []
            if self.sB.strip():
                bottomLines.append(",")    # przecinek w osobnej linii
                bottomLines.append(self.sB)  # B w kolejnej linii
        else:
            # arcSide == "bottom" -> ZRÓWNOLEGNIJ sB2
            #  - Na górze: A, ','
            #  - Na dole: łuk z X;Y
            topLines = []
            if self.sA.strip():
                topLines.append(self.sA)
            topLines.append(",")
            bottomLines = []

        # Pomocnicza funkcja do mierzenia wysokości tekstu
        def measure_height(txt):
            if not txt.strip():
                return 0
            rect = painter.boundingRect(QRectF(0, 0, 400, 2000),
                                        Qt.TextWordWrap, txt)
            return rect.height()

        # --- Mierzymy wysokości wierszy ---
        topHeights = [measure_height(t) for t in topLines]
        sumTop = sum(topHeights) + margin_line*(len(topLines)-1) if topLines else 0

        arcHeights = [measure_height(t) for t in arcLines]
        sumArc = sum(arcHeights) + margin_line*(len(arcLines)-1)

        bottomHeights = [measure_height(t) for t in bottomLines]
        sumBottom = sum(bottomHeights) + margin_line*(len(bottomLines)-1) if bottomLines else 0

        totalHeight = padding_top + sumTop + sumArc + sumBottom + padding_top

        topY = 50
        bottomY = topY + totalHeight

        # --- Rysujemy pionowy nawias kwadratowy (linia + wąsy) ---
        penBracket = QPen(QColor("#00BCD4"), 3)
        painter.setPen(penBracket)
        painter.drawLine(QPointF(bracketX, topY), QPointF(bracketX, bottomY))

        # Wąsy poziome (skierowane w prawo)
        tickLen = 15
        painter.drawLine(QPointF(bracketX, topY),
                         QPointF(bracketX + tickLen, topY))
        painter.drawLine(QPointF(bracketX, bottomY),
                         QPointF(bracketX + tickLen, bottomY))

        # --- Pozycje do rysowania łuku i tekstu ---
        painter.setPen(QColor("#212121"))
        arcX = bracketX + 30
        textX = arcX + 20
        currentY = topY + padding_top

        # 1. Rysujemy topLines
        for i, txt in enumerate(topLines):
            h = topHeights[i]
            if h > 0:
                painter.drawText(int(textX), int(currentY + h), txt)
                currentY += h + margin_line

        if arcSide == "bottom":
            currentY += 10 

        # 2. Łuk pionowy dla (X; Y)
        arcStartY = currentY
        arcEndY = arcStartY + sumArc - margin_line
        path = QPainterPath()
        path.moveTo(QPointF(arcX, arcStartY))
        ctrl1 = QPointF(arcX - 25, arcStartY + (arcEndY - arcStartY)*0.25)
        ctrl2 = QPointF(arcX - 25, arcStartY + (arcEndY - arcStartY)*0.75)
        path.cubicTo(ctrl1, ctrl2, QPointF(arcX, arcEndY))

        penArc = QPen(QColor("#4682B4"), 3)
        painter.setPen(penArc)
        painter.drawPath(path)

        # 3. Rysujemy linie (X, ";", Y) pionowo
        painter.setPen(QColor("#212121"))
        for i, txt in enumerate(arcLines):
            h = arcHeights[i]
            if h > 0:
                painter.drawText(int(textX), int(currentY + h), txt)
                currentY += h + margin_line

        # 4. Rysujemy bottomLines
        for i, txt in enumerate(bottomLines):
            h = bottomHeights[i]
            if h > 0:
                painter.drawText(int(textX), int(currentY + h), txt)
                currentY += h + margin_line

    def drawVerticalXY(self, painter, startX, startY, X, Y):
        """
        Rysuje pionowo:
             X
             ;
             Y
        z łukiem po lewej stronie, tak jak w trybie sekwencyjnym.
        Zwraca (usedWidth, usedHeight, xBaseline),
        gdzie xBaseline to pozycja, na której rysujemy X (bazowa linia dla wyrównania).
        """
        margin = 5
        padding = 20
    
        hX = self.getTextHeight(painter, X)
        hOp = self.getTextHeight(painter, ";")
        hY = self.getTextHeight(painter, Y)
    
        measureY = 0
        if hX:
            measureY += hX + margin
        if hOp:
            measureY += hOp + margin
        if hY:
            measureY += hY + margin
        if measureY > 0:
            measureY -= margin
    
        lineHeight = measureY + 2 * padding
    
        # Rysujemy łuk po lewej
        arcX = startX
        path = QPainterPath()
        path.moveTo(QPointF(arcX, startY))
        ctrl1 = QPointF(arcX - 25, startY + lineHeight * 0.25)
        ctrl2 = QPointF(arcX - 25, startY + lineHeight * 0.75)
        path.cubicTo(ctrl1, ctrl2, QPointF(arcX, startY + lineHeight))
        penCurve = QPen(QColor("#4682B4"), 3)
        painter.setPen(penCurve)
        painter.drawPath(path)
    
        # Rysujemy pionowy blok tekstu (X, ;, Y)
        painter.setPen(QColor("#212121"))
        textX = arcX + 20
        currentY = startY + padding
    
        # Pozycja, na której rysujemy X – to nasza linia bazowa
        xBaseline = currentY + hX
        if X:
            painter.drawText(int(textX), int(xBaseline), X)
            currentY += hX + margin
        if hOp:
            painter.drawText(int(textX), int(currentY + hOp), ";")
            currentY += hOp + margin
        if Y:
            painter.drawText(int(textX), int(currentY + hY), Y)
            currentY += hY + margin
    
        usedWidth = 20 + max(hX, hOp, hY)
        usedHeight = lineHeight
        return (usedWidth, usedHeight, xBaseline)

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
        inputLayout.addWidget(QLabel("  sA:"))
        inputLayout.addWidget(self.sAEdit)
        inputLayout.addWidget(QLabel("  sB:"))
        inputLayout.addWidget(self.sBEdit)
        rightLayout.addLayout(inputLayout)

        # Panel wejściowy: sA i sB dla drugiego unitermu
        inputLayout2 = QHBoxLayout()
        self.sA2Edit = QLineEdit()
        self.sA2Edit.setPlaceholderText("Wprowadź sA2")
        self.sB2Edit = QLineEdit()
        self.sB2Edit.setPlaceholderText("Wprowadź sB2")
        inputLayout2.addWidget(QLabel("sA2:"))
        inputLayout2.addWidget(self.sA2Edit)
        inputLayout2.addWidget(QLabel("sB2:"))
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
        db.insert_uniterm(name, description, sA, sB, sA2, sB2)

        self.nameEdit.clear()
        self.descEdit.clear()
        self.refreshList()

    def refreshList(self):
        self.listWidget.clear()
        rows = self.db.fetch_all_uniterms()
        for (record_id, name, description) in rows:
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
            name, description, sA, sB, sA2, sB2 = record
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
            ["sA - poziomo", "sB - poziomo", "sA - pionowo", "sB - pionowo"],
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

        if choice == "sA - poziomo":
            # -> (X, Y) ; B  z łukiem nad X, Y
            self.unitermWidget.mode = "horizontal_left_arc"
            self.unitermWidget.sA2 = X  # "X"
            self.unitermWidget.sB2 = Y  # "Y"
            self.unitermWidget.sB = B   # "B"
        elif choice == "sB - poziomo":
            self.unitermWidget.mode = "horizontal_right_arc"
            self.unitermWidget.sA = A   # "A"
            self.unitermWidget.sA2 = X  # "X"
            self.unitermWidget.sB2 = Y  # "Y"
        elif choice == "sA - pionowo":
            self.unitermWidget.mode = "vertical_top_arc"
            self.unitermWidget.sA2 = X  # "X"
            self.unitermWidget.sB2 = Y  # "Y"
            self.unitermWidget.sB = B   # "B"
        elif choice == "sB - pionowo":
            self.unitermWidget.mode = "vertical_bottom_arc"
            self.unitermWidget.sA = A   # "A"
            self.unitermWidget.sA2 = X  # "X"
            self.unitermWidget.sB2 = Y  # "Y"

        self.unitermWidget.update()