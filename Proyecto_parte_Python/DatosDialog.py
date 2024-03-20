from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSlot
from web3 import Web3

def es_numero_decimal_positivo(valor):
    try:
        return float(valor) > 0
    except ValueError:
        return False

def is_valid_ethereum_address(address):
    return Web3.isAddress(address)

class DatosDialog(QDialog):
    def __init__(self, accion, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Datos para {accion}")
        self.accion = accion
        self.initUI(accion)
    
    def initUI(self, accion):
        layout = QVBoxLayout()
        
        if accion == "Alta de Prestamista" or accion == "Alta de Cliente":
            self.direccionInput = QLineEdit(self)
            layout.addWidget(QLabel("Dirección Ethereum:"))
            layout.addWidget(self.direccionInput)
        
        elif accion == "Depositar Garantía":
            self.valorDepositoInput = QLineEdit(self)
            layout.addWidget(QLabel("Valor a Depositar (en Ether):"))
            layout.addWidget(self.valorDepositoInput)
        
        elif accion == "Solicitar Préstamo":
            self.montoPrestamoInput = QLineEdit(self)
            self.plazoPrestamoInput = QLineEdit(self)
            layout.addWidget(QLabel("Monto del Préstamo (en Ether):"))
            layout.addWidget(self.montoPrestamoInput)
            layout.addWidget(QLabel("Plazo del Préstamo (en segundos):"))
            layout.addWidget(self.plazoPrestamoInput)
        
        elif accion == "Reembolsar Préstamo":
            self.idPrestamoInput = QLineEdit(self)
            self.valorReembolsoInput = QLineEdit(self)
            layout.addWidget(QLabel("ID del Préstamo:"))
            layout.addWidget(self.idPrestamoInput)
            layout.addWidget(QLabel("Valor del Reembolso (en Ether):"))
            layout.addWidget(self.valorReembolsoInput)
        
        elif accion == "Liquidar Garantía":
            self.idPrestamoLiquidarInput = QLineEdit(self)
            layout.addWidget(QLabel("ID del Préstamo para Liquidar:"))
            layout.addWidget(self.idPrestamoLiquidarInput)
        
        elif accion == "Aceptar Préstamo":
            self.idPrestamoAceptarInput = QLineEdit(self)
            layout.addWidget(QLabel("ID del Préstamo a Aceptar:"))
            layout.addWidget(self.idPrestamoAceptarInput)
        
        elif accion == "Obtener préstamos por prestatario":
            self.direccionPrestatarioInput = QLineEdit(self)
            layout.addWidget(QLabel("Dirección Ethereum del Prestatario:"))
            layout.addWidget(self.direccionPrestatarioInput)
        
        elif accion == "Obtener detalle de préstamo":
            self.idPrestamoDetalleInput = QLineEdit(self)
            layout.addWidget(QLabel("ID del Préstamo para Detalles:"))
            layout.addWidget(self.idPrestamoDetalleInput)
        
        self.botonAceptar = QPushButton('Aceptar', self)
        self.botonAceptar.clicked.connect(self.onAceptarClicked)
        layout.addWidget(self.botonAceptar)
        
        self.setLayout(layout)

    @pyqtSlot()
    def onAceptarClicked(self):
        try:
            if self.accion in ["Alta de Prestamista", "Alta de Cliente", "Obtener préstamos por prestatario", "Aceptar Préstamo"]:
                direccion = self.direccionInput.text()
                if not (direccion.startswith("0x") and is_valid_ethereum_address(direccion)):
                    QMessageBox.warning(self, "Error", "La dirección Ethereum debe ser válida.")
                    return

            if self.accion == "Depositar Garantía":
                valor = self.valorDepositoInput.text()
                if not es_numero_decimal_positivo(valor):
                    QMessageBox.warning(self, "Error", "El valor a depositar debe ser un número positivo.")
                    return

            if self.accion == "Solicitar Préstamo":
                monto = self.montoPrestamoInput.text()
                plazo_en_segundos = self.plazoPrestamoInput.text()  # Asume que plazo es dado en segundos
                if not (es_numero_decimal_positivo(monto) and plazo_en_segundos.isdigit() and int(plazo_en_segundos) > 0):
                    QMessageBox.warning(self, "Error", "El monto debe ser un valor positivo y el plazo debe ser un número positivo de segundos.")
                    return

            # Valida ID del préstamo y valor de reembolso en Reembolsar Préstamo.
            if self.accion == "Reembolsar Préstamo":
                idPrestamo = self.idPrestamoInput.text()
                valorReembolso = self.valorReembolsoInput.text()
                if not (idPrestamo.isdigit() and int(idPrestamo) > 0 and es_numero_decimal_positivo(valorReembolso)):
                    QMessageBox.warning(self, "Error", "El ID del préstamo debe ser un valor positivo y el valor del reembolso debe ser un número positivo.")
                    return

            # Valida ID del préstamo para Liquidar Garantía.
            if self.accion == "Liquidar Garantía":
                idPrestamoLiquidar = self.idPrestamoLiquidarInput.text()
                if not (idPrestamoLiquidar.isdigit() and int(idPrestamoLiquidar) > 0):
                    QMessageBox.warning(self, "Error", "El ID del préstamo para liquidar debe ser un valor positivo.")
                    return

            # Valida ID del préstamo para Aceptar Préstamo.
            if self.accion == "Aceptar Préstamo":
                idPrestamoAceptar = self.idPrestamoAceptarInput.text()
                if not (idPrestamoAceptar.isdigit() and int(idPrestamoAceptar) > 0):
                    QMessageBox.warning(self, "Error", "El ID del préstamo a aceptar debe ser un valor positivo.")
                    return

            # Valida la dirección Ethereum del prestatario para Obtener préstamos por prestatario.
            if self.accion == "Obtener préstamos por prestatario":
                direccionPrestatario = self.direccionPrestatarioInput.text()
                if not (direccionPrestatario.startswith("0x") and is_valid_ethereum_address(direccionPrestatario)):
                    QMessageBox.warning(self, "Error", "La dirección Ethereum del prestatario debe ser válida.")
                    return

            # Valida ID del préstamo para Obtener detalle de préstamo.
            if self.accion == "Obtener detalle de préstamo":
                idPrestamoDetalle = self.idPrestamoDetalleInput.text()
                if not (idPrestamoDetalle.isdigit() and int(idPrestamoDetalle) > 0):
                    QMessageBox.warning(self, "Error", "El ID del préstamo para obtener detalles debe ser un valor positivo.")
                    return
                
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Error de validación", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", f"Se ha producido un error inesperado: {e}")
            print(f"Error: {e}")
    
    def getDatos(self):
        datos = {}
        if self.accion == "Alta de Prestamista" or self.accion == "Alta de Cliente":
            datos['direccion'] = self.direccionInput.text()

        elif self.accion == "Depositar Garantía":
            datos['valorDeposito'] = self.valorDepositoInput.text()

        elif self.accion == "Solicitar Préstamo":
            datos['montoPrestamo'] = self.montoPrestamoInput.text()
            datos['plazoPrestamo'] = self.plazoPrestamoInput.text()

        elif self.accion == "Reembolsar Préstamo":
            datos['idPrestamo'] = self.idPrestamoInput.text()
            datos['valorReembolso'] = self.valorReembolsoInput.text()

        elif self.accion == "Liquidar Garantía":
            datos['idPrestamoLiquidar'] = self.idPrestamoLiquidarInput.text()

        elif self.accion == "Aceptar Préstamo":
            datos['idPrestamoAceptar'] = self.idPrestamoAceptarInput.text()

        elif self.accion == "Obtener préstamos por prestatario":
            datos['direccionPrestatario'] = self.direccionPrestatarioInput.text()

        elif self.accion == "Obtener detalle de préstamo":
            datos['idPrestamoDetalle'] = self.idPrestamoDetalleInput.text()

        return datos
    