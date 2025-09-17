import cv2
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import mysql.connector
import numpy as np

class Register(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #090435,
                stop:0.5 #2160a0,
                stop:1 #090435
            );
            color: white;
        """)
        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel(f"Registro")
        label.setStyleSheet("font-size: 22px; font-weight: bold; background: transparent; ")

        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuario")
        self.usuario_input.setStyleSheet("height: 30px; margin: 0 auto; padding: 2px 10px;"
                                         "border: 2px solid green; border-radius: 10px;"
                                         "background: transparent; color: white;")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("height: 30px; margin: 0 auto; padding: 2px 10px;"
                                          "border: 2px solid green; border-radius: 10px;"
                                          "background: transparent; color: white;")

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre")
        self.nombre_input.setStyleSheet("height: 30px; margin: 0 auto; padding: 2px 10px;"
                                         "border: 2px solid green; border-radius: 10px;"
                                        " background: transparent; color: white;")

        self.correo_input = QLineEdit()
        self.correo_input.setPlaceholderText("Correo")
        self.correo_input.setStyleSheet("height: 30px; margin: 0 auto; padding: 2px 10px;"
                                        "border: 2px solid green; border-radius: 10px;"
                                        "background: transparent; color: white;")

        # Boton Registro Facial
        self.button_add_face = QPushButton("Registro Facial")
        self.button_add_face.setStyleSheet("background-color: #410967")
        self.button_add_face.clicked.connect(self.registro_facial)

        # Boton Registro
        self.button_add = QPushButton("Registrar")
        self.button_add.setStyleSheet("background: green")
        self.button_add.clicked.connect(self.registro)

        # Boton Actualizar
        self.button_update = QPushButton("Actualizar")
        self.button_update.setStyleSheet("background-color: #12a3be")
        self.button_update.clicked.connect(self.actualizar)

        # Boton Volver
        self.button_return = QPushButton("Volver")
        self.button_return.setStyleSheet("background: black")
        self.button_return.clicked.connect(self.volver)

        layout.addWidget(label)
        layout.addWidget(self.usuario_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.nombre_input)
        layout.addWidget(self.correo_input)
        layout.addWidget(self.button_add_face)
        layout.addWidget(self.button_add)
        layout.addWidget(self.button_update)
        layout.addWidget(self.button_return)

    def volver(self):
        self.hide()
        from system import System
        self.window_system = System()
        self.window_system.show()

    def registro_facial(self):
        personName = self.nombre_input.text()
        dataPath = 'C:/Users/james/PycharmProjects/Reconocer/data'
        personPath = os.path.join(dataPath, personName)

        if not os.path.exists(personPath):
            print('Carpeta creada:', personPath)
            os.makedirs(personPath)

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        count = 0

        while True:
            ret, frame = cap.read()
            if ret == False:
                break
            frame = cv2.resize(frame, (640, 480))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = faceClassif.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                rostro = frame[y:y + h, x:x + w]
                rostro = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
                cv2.imwrite(os.path.join(personPath, f'rostro_{count}.jpg'), rostro)
                count = count + 1

            cv2.imshow('frame', frame)

            k = cv2.waitKey(200)
            if k == 27 or count >= 20:
                break

        cap.release()
        cv2.destroyAllWindows()

    def registro (self):

        usuario = self.usuario_input.text()
        clave = self.password_input.text()
        nombre = self.nombre_input.text()
        correo = self.correo_input.text()

        # Conectar a la base de datos MySQL
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="recface"
        )
        cursor = conexion.cursor()

        # Realizar una consulta para obtener el nombre del usuario
        query="INSERT INTO login (usuario, clave, nombre, correo) VALUES (%s, %s, %s, %s) "
        values = (usuario, clave, nombre, correo)
        cursor.execute(query, values)
        conexion.commit()

        conexion.close()
        QMessageBox.information(self, "Éxito", "Usuario registrado con éxito")

    def actualizar(self):
        dataPath = 'C:/Users/james/PycharmProjects/Reconocer/data'
        peopleList = os.listdir(dataPath)
        print('Lista de personas:', peopleList)

        labels = []
        facesData = []
        label = 0

        for nameDir in peopleList:
            personPath = os.path.join(dataPath, nameDir)
            print('Leyendo las imágenes de:', nameDir)

            for fileName in os.listdir(personPath):
                print('Rostros:', nameDir + '/' + fileName)
                labels.append(label)
                facesData.append(cv2.imread(os.path.join(personPath, fileName), 0))
                image = cv2.imread(os.path.join(personPath, fileName), 0)

            label += 1

        face_recognizer = cv2.face.LBPHFaceRecognizer_create()

        print("Entrenando...")
        face_recognizer.train(facesData, np.array(labels))

        face_recognizer.write('modelos/modeloLBPHFace.xml')
        print("Modelo almacenado...")
        QMessageBox.information(self, "Éxito", "Modelo actualizado y almacenado con éxito")

