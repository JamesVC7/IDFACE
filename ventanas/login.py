import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt,QTimer
from window import FaceRecognitionApp
import mysql.connector
import globals

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iniciar Sesión")
        self.setFixedSize(500, 400)
        self.setStyleSheet("background-color: black; color: white;")

        layout = QVBoxLayout()

        # Widget que contiene la imagen
        widget_usuario = QWidget()
        layout_usuario = QHBoxLayout(widget_usuario)

        imagen_usuario = QLabel()
        pixmap_usuario = QPixmap('recursos/iconoFC.png').scaled(332, 332)
        imagen_usuario.setPixmap(pixmap_usuario)
        imagen_usuario.setAlignment(Qt.AlignCenter)

        layout_usuario.addWidget(imagen_usuario)
        layout_usuario.setContentsMargins(0, 0, 0, 0)
        layout_usuario.setSpacing(10)

        # Agrega la imagen
        layout.addWidget(widget_usuario)

        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuario")
        self.usuario_input.setStyleSheet("height: 30px; margin: 0 auto; padding: 2px 10px;"
                                         "border: 2px solid green; border-radius: 10px;")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("height: 30px; margin: 0 auto; padding: 2px 10px;"
                                          "border: 2px solid green; border-radius: 10px;")

        self.iniciar_sesion_button = QPushButton("Iniciar Sesión")
        self.iniciar_sesion_button.clicked.connect(self.verificar)
        self.iniciar_sesion_button.setStyleSheet(
            """
            QPushButton {
                height: 30px;
                border-radius: 10px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #0d5b07, stop: 1 #13c035
                );
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #13c035, stop: 1 #0d5b07
                );
            }
            """
        )

        layout.addWidget(self.usuario_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.iniciar_sesion_button)

        self.setLayout(layout)

        # Contador de intentos fallidos
        self.intentos_fallidos = 0

        # Temporizador para habilitar el botón
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.habilitar_boton)

    def habilitar_boton(self):
        self.iniciar_sesion_button.setEnabled(True)

    def verificar(self):
        usuario = self.usuario_input.text()
        password = self.password_input.text()

        # Conexión a la base de datos MySQL
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="recface"
        )
        cursor = conexion.cursor()

        # Consulta sql
        cursor.execute("SELECT id_usuario FROM login WHERE usuario=%s AND clave=%s", (usuario, password))
        resultado = cursor.fetchone()

        conexion.close()

        # Condicion de acceso
        if resultado:
            globals.global_id_usuario = resultado[0]
            self.hide()
            self.intentos_fallidos = 0
            self.face_app = FaceRecognitionApp()
            self.face_app.show()
        else:
            self.intentos_fallidos += 1
            if self.intentos_fallidos >= 3:
                self.iniciar_sesion_button.setEnabled(False)
                self.timer.start(15000)
                QMessageBox.critical(self, "Error", "Cantidad de intentos fallidos superado")
                self.intentos_fallidos = 0
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('recursos/iconoFace.jpg'))
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
