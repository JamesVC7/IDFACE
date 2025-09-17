import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ventanas.system import System

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('../recursos/iconoFace.jpg'))
    system = System()
    system.show()
    sys.exit(app.exec_())
