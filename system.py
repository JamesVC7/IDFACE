from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
import mysql.connector
import globals
import os
import shutil
import cv2
import numpy as np

class System(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome")
        self.setFixedSize(550, 400)
        self.setStyleSheet("background-color: #0a0a6f; color: white;")

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Obtener el nombre del usuario desde la base de datos
        nombre_usuario = self.obtener_nombre_usuario(globals.global_id_usuario)

        label = QLabel(f"Bienvenido {nombre_usuario}")
        label.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(label)

        # Tabla
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)

        column_names = ["ID", "Usuario","Nombre", "Correo", "Accion"]
        self.table_widget.setHorizontalHeaderLabels(column_names)
        self.table_widget.setStyleSheet("QHeaderView::section {background-color: black; color: white; }")

        #Boton Registro
        self.button_register = QPushButton("Nuevo Registro")
        self.button_register.clicked.connect(self.open_window)
        self.button_register.setStyleSheet("background-color: green; color: #fff;")
        layout.addWidget(self.button_register)

        # Obtener datos del usuario desde la base de datos
        datos_usuario = self.obtener_datos_usuario()

        # Llenar la tabla con los datos del usuario
        if datos_usuario:
            self.llenar_tabla(datos_usuario)

        layout.addWidget(self.table_widget)

    def obtener_nombre_usuario(self, id_usuario):

            # Conectar a la base de datos MySQL
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="recface"
            )
            cursor = conexion.cursor()

            # Realizar una consulta para obtener el nombre del usuario
            cursor.execute("SELECT nombre FROM login WHERE id_usuario = %s", (id_usuario,))
            resultado = cursor.fetchone()

            # Cerrar la conexión a la base de datos
            conexion.close()

            if resultado:
                return resultado[0]  # Devolver el nombre del usuario
            else:
                return "Usuario"

    def obtener_datos_usuario(self):
        # Conectar a la base de datos MySQL
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="recface"
        )
        cursor = conexion.cursor()

        # Realizar una consulta para obtener los datos del usuario
        cursor.execute("SELECT id_usuario, usuario, nombre, correo FROM login ")
        datos_usuario = cursor.fetchall()

        conexion.close()
        return datos_usuario

    def llenar_tabla(self, datos_usuario):
        # Establecer el número de filas de la tabla
        self.table_widget.setRowCount(len(datos_usuario))

        # Llenar la tabla con los datos del usuario
        for row, (id_detalle, usuario, nombre, correo) in enumerate(datos_usuario):
            item_id_detalle = QTableWidgetItem(str(id_detalle))  # Convertir a cadena
            item_usuario = QTableWidgetItem(usuario)
            item_nombre = QTableWidgetItem(nombre)
            item_correo= QTableWidgetItem(correo)
            self.table_widget.setItem(row, 0, item_id_detalle)
            self.table_widget.setItem(row, 1, item_usuario)
            self.table_widget.setItem(row, 2, item_nombre)
            self.table_widget.setItem(row, 3, item_correo)
            # Agregar botón a la columna "ACCION"
            button_accion = QPushButton("Borrar")
            button_accion.setStyleSheet("background-color: red; color: #fff;")
            self.table_widget.setCellWidget(row, 4, button_accion)
            button_accion.clicked.connect(lambda _, r=row: self.eliminar_fila(r))

    def eliminar_fila(self, row):
        id_detalle = self.table_widget.item(row, 0).text()
        nombre_usuario = self.table_widget.item(row, 2).text()

        # Confirmar la eliminación
        reply = QMessageBox.question(self, 'Confirmación',
                                     f'¿Estás seguro de que deseas eliminar la fila con ID {id_detalle}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.eliminar_de_base_datos(id_detalle, nombre_usuario)
            self.table_widget.removeRow(row)
            self.actualizar()

    def eliminar_de_base_datos(self, id_detalle, nombre_usuario):
        # Conectar a la base de datos MySQL
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="recface"
        )
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM login WHERE id_usuario = %s", (id_detalle,))
        conexion.commit()
        conexion.close()

        print(f"Fila con ID {id_detalle} eliminada de la base de datos")

        # Eliminar la carpeta del usuario
        self.eliminar_carpeta_usuario(nombre_usuario)

    def eliminar_carpeta_usuario(self, nombre_usuario):
        dataPath = 'C:/Users/james/PycharmProjects/Reconocer/data'
        personPath = os.path.join(dataPath, nombre_usuario)

        if os.path.exists(personPath):
            try:
                shutil.rmtree(personPath)  # Usar shutil.rmtree para eliminar directorios no vacíos
                print(f"Carpeta {personPath} eliminada")
            except OSError as e:
                print(f"Error al eliminar la carpeta {personPath}: {e}")

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

        face_recognizer.write('modeloLBPHFace.xml')
        print("Modelo almacenado...")
        QMessageBox.information(self, "Éxito", "Usuario eliminado y actualizado con éxito")


    def open_window(self):
        self.hide()
        from window_register import Register
        self.window_register = Register()
        self.window_register.show()
