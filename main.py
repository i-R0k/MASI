import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow
from database import DatabaseManager

def main():
    app = QApplication(sys.argv)
    db = DatabaseManager()        
    window = MainWindow(db)        
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()