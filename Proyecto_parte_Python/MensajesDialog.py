from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class MensajesDialog(QDialog):
    def __init__(self, titulo, mensaje, parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.initUI(mensaje)

    def initUI(self, mensaje):
        layout = QVBoxLayout()

        # Mensaje
        self.labelMensaje = QLabel(mensaje)
        layout.addWidget(self.labelMensaje)

        # Botón de Aceptar
        self.botonAceptar = QPushButton('Aceptar')
        self.botonAceptar.clicked.connect(self.accept)
        layout.addWidget(self.botonAceptar)

        self.setLayout(layout)
        