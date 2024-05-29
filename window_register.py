import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from register import Register

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('iconoFace.jpg'))
    register = Register()
    register.show()
    sys.exit(app.exec_())
