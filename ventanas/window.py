import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import QTimer
import os
import winsound
from window_system import System
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import mysql.connector
import globals
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class FaceRecognitionApp(QWidget):
    def __init__(self):
        super().__init__()

        self.dataPath = 'C:/Users/james/PycharmProjects/Reconocer/data'
        self.imagePaths = os.listdir(self.dataPath)
        print('imagePaths=', self.imagePaths)

        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.face_recognizer.read('modelos/modeloLBPHFace.xml')

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        self.label = QLabel(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        self.button_siguiente = QPushButton('SIGUIENTE', self)
        self.button_siguiente.setStyleSheet("background-color: blue; color: #fff;")
        self.button_siguiente.setVisible(False)
        layout.addWidget(self.button_siguiente)
        self.button_siguiente.clicked.connect(self.open_window)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

        self.setWindowTitle("Reconocimiento Facial")
        self.setFixedSize(640, 480)

        self.desconocido_count = 0
        self.desconocido_images = []

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret == False:
            return
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        auxFrame = gray.copy()

        faces = self.faceClassif.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            rostro = auxFrame[y:y + h, x:x + w]
            rostro = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
            result = self.face_recognizer.predict(rostro)

            cv2.putText(frame, '{}'.format(result), (x, y - 5), 1, 1.3, (255, 255, 0), 1, cv2.LINE_AA)

            if result[1] < 75:
                cv2.putText(frame, '{}'.format(self.imagePaths[result[0]]), (x, y - 25), 2, 1.1, (0, 255, 0), 1,
                            cv2.LINE_AA)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                self.button_siguiente.setVisible(True)
            else:
                cv2.putText(frame, 'Desconocido', (x, y - 20), 2, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                self.play_alarm()
                self.button_siguiente.setVisible(False)
                self.capture_unknown(frame[y:y + h, x:x + w])

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

    def capture_unknown(self, face):
        if self.desconocido_count < 5:
            image_path = f'unknown_{self.desconocido_count}.jpg'
            cv2.imwrite(image_path, face)
            self.desconocido_images.append(image_path)
            self.desconocido_count += 1
            if self.desconocido_count == 5:
                self.send_email()

    def send_email(self):
        try:
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="recface"
            )
            cursor = conexion.cursor()
            cursor.execute("SELECT correo FROM login WHERE id_usuario = %s", (globals.global_id_usuario,))
            resultado = cursor.fetchone()
            conexion.close()

            if resultado:
                email_admin = resultado[0]
                subject = "Alerta: Persona desconocida detectada"
                body = "Se han detectado 5 imágenes de una persona desconocida. Ver las imágenes adjuntas."
                sender_email = "jamesvc2002@gmail.com"
                sender_password = os.getenv("PASSWORD")
                receiver_email = email_admin

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                for img_path in self.desconocido_images:
                    with open(img_path, 'rb') as f:
                        img = MIMEImage(f.read())
                        img.add_header('Content-Disposition', f'attachment; filename="{img_path}"')
                        msg.attach(img)

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
                server.quit()

                # Borrar imágenes temporales
                for img_path in self.desconocido_images:
                    os.remove(img_path)

                self.desconocido_count = 0
                self.desconocido_images = []

        except Exception as e:
            print(f"Error al enviar el correo: {e}")

    def play_alarm(self):
        frequency = 2500
        duration = 1000
        winsound.Beep(frequency, duration)

    def registrar_ingreso(self, id_usuario):
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="recface"
        )
        cursor = conexion.cursor()

        # Insertar nuevo registro con la fecha actual
        cursor.execute("""
                       INSERT INTO historial_ingresos (id_usuario, fecha_ingreso)
                       VALUES (%s, CURRENT_TIMESTAMP)
                       """, (id_usuario,))

        # Actualizar el contador de ingresos en la tabla login
        cursor.execute("""
                       UPDATE login
                       SET numero_ingresos = (SELECT COUNT(*)
                                              FROM historial_ingresos
                                              WHERE id_usuario = %s)
                       WHERE id_usuario = %s
                       """, (id_usuario, id_usuario))

        conexion.commit()
        conexion.close()

    def open_window(self):
        self.cap.release()
        self.timer.stop()
        self.hide()
        self.window_system = System()
        self.window_system.show()
        self.registrar_ingreso(globals.global_id_usuario)
        # Actualizar la tabla después de registrar el ingreso
        datos_usuario = self.window_system.obtener_datos_usuario()
        self.window_system.llenar_tabla(datos_usuario)

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('recursos/iconoFace.jpg'))
    face_recognition_app = FaceRecognitionApp()
    face_recognition_app.show()
    sys.exit(app.exec_())
