from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSlot

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
            layout.addWidget(QLabel("Plazo del Préstamo (en días):"))
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
        # Valida la dirección Ethereum en todas las acciones que la requieren.
        if self.accion in ["Alta de Prestamista", "Alta de Cliente", "Obtener préstamos por prestatario", "Aceptar Préstamo"]:
            if not self.direccionInput.text().startswith("0x") or len(self.direccionInput.text()) != 42:
                QMessageBox.warning(self, "Error", "La dirección Ethereum debe ser válida.")
                return

        # Valida el valor a depositar en la acción Depositar Garantía.
        if self.accion == "Depositar Garantía":
            try:
                valor = float(self.valorDepositoInput.text())
                if valor <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Error", "El valor a depositar debe ser un número positivo.")
                return

        # Valida monto y plazo para Solicitar Préstamo.
        if self.accion == "Solicitar Préstamo":
            try:
                monto = float(self.montoPrestamoInput.text())
                plazo = int(self.plazoPrestamoInput.text())
                if monto <= 0 or plazo <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Error", "El monto y el plazo deben ser valores positivos.")
                return

        # Valida ID del préstamo y valor de reembolso en Reembolsar Préstamo.
        if self.accion == "Reembolsar Préstamo":
            try:
                idPrestamo = int(self.idPrestamoInput.text())
                valorReembolso = float(self.valorReembolsoInput.text())
                if idPrestamo < 0 or valorReembolso <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Error", "El ID del préstamo y el valor del reembolso deben ser válidos.")
                return

        # Valida ID del préstamo para Liquidar Garantía.
        if self.accion == "Liquidar Garantía":
            try:
                idPrestamo = int(self.idPrestamoLiquidarInput.text())
                if idPrestamo < 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Error", "El ID del préstamo debe ser un valor positivo.")
                return

        # Valida ID del préstamo para Aceptar Préstamo.
        if self.accion == "Aceptar Préstamo":
            try:
                idPrestamo = int(self.idPrestamoAceptarInput.text())
                if idPrestamo < 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Error", "El ID del préstamo debe ser un valor positivo.")
                return

        # Valida la dirección Ethereum del prestatario para Obtener préstamos por prestatario.
        if self.accion == "Obtener préstamos por prestatario":
            if not self.direccionPrestatarioInput.text().startswith("0x") or len(self.direccionPrestatarioInput.text()) != 42:
                QMessageBox.warning(self, "Error", "La dirección Ethereum del prestatario debe ser válida.")
                return

        # Valida ID del préstamo para Obtener detalle de préstamo.
        if self.accion == "Obtener detalle de préstamo":
            try:
                idPrestamo = int(self.idPrestamoDetalleInput.text())
                if idPrestamo < 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Error", "El ID del préstamo debe ser un valor positivo.")
                return

        self.accept()
    
    def getDatos(self):
        datos = {}
        # Dependiendo de la acción, recoge los datos necesarios
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
    