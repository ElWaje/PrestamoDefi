from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QLabel, QPushButton

class CredencialesDialog(QDialog):
    def __init__(self, parent=None):
        super(CredencialesDialog, self).__init__(parent)
        self.setWindowTitle("Ingresar Credenciales\nPara Operar")
        self.setupUI()

    def setupUI(self):
        layout = QFormLayout()
        self.direccionEthereum = QLineEdit(self)
        layout.addRow(QLabel("Dirección Ethereum:"), self.direccionEthereum)

        self.clavePrivada = QLineEdit(self)
        self.clavePrivada.setEchoMode(QLineEdit.Password)
        layout.addRow(QLabel("Clave Privada:"), self.clavePrivada)

        botonAceptar = QPushButton('Aceptar', self)
        botonAceptar.clicked.connect(self.accept)
        layout.addRow(botonAceptar)

        self.setLayout(layout)

    def getDireccionEthereum(self):
        return self.direccionEthereum.text()

    def getClavePrivada(self):
        return self.clavePrivada.text()
    