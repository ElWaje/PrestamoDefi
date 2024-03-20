from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QMessageBox, QLabel
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from DatosDialog import DatosDialog
from CredencialesDialog import CredencialesDialog
from MensajesDialog import MensajesDialog
from BlockchainManager import BlockchainManager
from web3 import Web3 

class HoverButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.defaultFont = self.font()
        self.setStyleSheet("background-color: #2E2E2E; color: white; border: 1px solid black; padding: 10px 20px;")
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.setStyleSheet("background-color: #555; color: white; border: 1px solid black; padding: 10px 20px; border-style: outset;")
        self.setFont(QFont(self.defaultFont.family(), self.defaultFont.pointSize() + 1))

    def leaveEvent(self, event):
        self.setStyleSheet("background-color: #2E2E2E; color: white; border: 1px solid black; padding: 10px 20px; border-style: outset;")
        self.setFont(self.defaultFont)

class HoverExitButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.defaultStyleSheet = self.styleSheet()
        self.defaultFont = self.font()
        self.setStyleSheet("background-color: #f0f0f0; color: black; border: 1px solid black; padding: 15px 25px; border-style: outset;")
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.setStyleSheet("background-color: #eee; color: black; border: 1px solid black; padding: 15px 25px; border-style: outset;")
        self.setFont(QFont(self.defaultFont.family(), self.defaultFont.pointSize() + 1))

    def leaveEvent(self, event):
        self.setStyleSheet(self.defaultStyleSheet)
        self.setFont(self.defaultFont)

class MainWindow(QMainWindow):
    def __init__(self, blockchainManager):
        super().__init__()
        self.blockchainManager = blockchainManager
        self.setWindowTitle('Aplicación DeFi - Gestión de Préstamos')
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        layout = QVBoxLayout()

        # Título
        titleLabel = QLabel("Bienvenid@, Sistema DeFi de Préstamos", self)
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setStyleSheet("font-size: 24px; color: #333;")
        layout.addWidget(titleLabel)

        actions = ["Alta de Prestamista", "Alta de Cliente", "Depositar Garantía", 
                   "Solicitar Préstamo", "Aceptar Préstamo","Reembolsar Préstamo", "Liquidar Garantía",
                    "Obtener préstamos por prestatario", 
                   "Obtener detalle de préstamo"]
                   
        for action in actions:
            btn = HoverButton(action, self)
            btn.clicked.connect(lambda checked, a=action: self.onActionClicked(a))
            layout.addWidget(btn)

        # Botón de Salida
        exitButton = HoverExitButton('Salir', self)
        exitButton.setStyleSheet("font-size: 16px; padding: 15px 25px; border-style: outset;")
        exitButton.clicked.connect(self.closeApplication)
        layout.addWidget(exitButton)

        # Pie de página con derechos de autor
        copyrightLabel = QLabel("", self)
        copyrightLabel.setAlignment(Qt.AlignCenter)
        current_year = QDate.currentDate().year()
        copyrightLabel.setText(f"Copyright © Enrique Solis {current_year}")
        copyrightLabel.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(copyrightLabel)

        self.centralWidget.setLayout(layout)

        # Cambiar el color de fondo de la ventana principal
        self.setStyleSheet("background-color: #f0f0f0;")
                
    def onActionClicked(self, action):
        credDialog = CredencialesDialog(self)
        if credDialog.exec_():
            direccion, clavePrivada = credDialog.getDireccionEthereum(), credDialog.getClavePrivada()
            
            datosDialog = DatosDialog(action, self)
            if datosDialog.exec_():
                datos = datosDialog.getDatos()
                
                try:
                    if action == "Alta de Prestamista" or action == "Alta de Cliente":
                        self.blockchainManager.alta_prestamista(direccion, clavePrivada, datos['direccion'])
                    elif action == "Depositar Garantía":
                        valorWei = Web3.to_wei(datos['valorDeposito'], 'ether')
                        self.blockchainManager.depositar_garantia(direccion, clavePrivada, valorWei)
                    elif action == "Solicitar Préstamo":
                        montoWei = Web3.to_wei(datos['montoPrestamo'], 'ether')
                        self.blockchainManager.solicitar_prestamo(direccion, clavePrivada, montoWei, int(datos['plazoPrestamo']))
                    elif action == "Reembolsar Préstamo":
                        valorWei = Web3.to_wei(datos['valorReembolso'], 'ether')
                        self.blockchainManager.reembolsar_prestamo(direccion, clavePrivada, int(datos['idPrestamo']), valorWei)
                    elif action == "Liquidar Garantía":
                        self.blockchainManager.liquidar_garantia(direccion, clavePrivada, int(datos['idPrestamoLiquidar']))
                    elif action == "Aceptar Préstamo":
                        self.blockchainManager.aprobar_prestamo(direccion, clavePrivada, int(datos['idPrestamoAceptar']))
                    elif action == "Obtener préstamos por prestatario":
                        prestamos = self.blockchainManager.obtener_prestamos_por_prestatario(datos['direccionPrestatario'])
                        MensajesDialog("Préstamos por Prestatario", str(prestamos), self).exec_()
                        return
                    elif action == "Obtener detalle de préstamo":
                        detalle = self.blockchainManager.obtener_detalle_de_prestamo(int(datos['idPrestamoDetalle']))
                        MensajesDialog("Detalle del Préstamo", str(detalle), self).exec_()
                        return
                    
                    # Muestra un mensaje de éxito al finalizar cualquier acción correctamente
                    MensajesDialog("Éxito", "La acción se completó con éxito.", self).exec_()

                except Exception as e:
                    MensajesDialog("Error", str(e), self).exec_()
                                            
    def closeApplication(self):
        reply = QMessageBox.question(self, 'Salir', '¿Estás seguro de que quieres salir?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Despedida", "Gracias por usar la aplicación. ¡Hasta la próxima!")
            QApplication.instance().quit() 
                    