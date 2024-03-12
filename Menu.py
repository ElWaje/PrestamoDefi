import tkinter as tk
from tkinter import simpledialog, messagebox
from PrestamoDeFi import (
    alta_prestamista, alta_cliente, depositar_garantia, solicitar_prestamo,
    aprobar_prestamo, reembolsar_prestamo, liquidar_garantia,
    obtener_prestamos_por_prestatario, obtener_detalle_de_prestamo
)

def is_valid_eth_address(address):
    return Web3.isAddress(address)

def gui_alta_prestamista():
    address = simpledialog.askstring("Alta Prestamista", "Dirección del nuevo prestamista:")
    if address and is_valid_eth_address(address):
        resultado = alta_prestamista(address)
        messagebox.showinfo("Resultado", resultado)
    else:
        messagebox.showerror("Error", "Dirección Ethereum inválida.")

def gui_alta_cliente():
    address = simpledialog.askstring("Alta Cliente", "Dirección del nuevo cliente:")
    if address and is_valid_eth_address(address):
        resultado = alta_cliente(address)
        messagebox.showinfo("Resultado", resultado)
    else:
        messagebox.showerror("Error", "Dirección Ethereum inválida.")

def gui_depositar_garantia():
    valor = simpledialog.askstring("Depositar Garantía", "Valor a depositar en Ether:")
    if valor:
        try:
            valor_wei = Web3.toWei(float(valor), 'ether')
            resultado = depositar_garantia(valor_wei)
            messagebox.showinfo("Resultado", resultado)
        except ValueError:
            messagebox.showerror("Error", "Valor inválido.")

def gui_solicitar_prestamo():
    monto = simpledialog.askstring("Solicitar Préstamo", "Monto del préstamo en Ether:")
    plazo = simpledialog.askstring("Solicitar Préstamo", "Plazo del préstamo en segundos:")
    if monto and plazo:
        try:
            monto_wei = Web3.toWei(float(monto), 'ether')
            resultado = solicitar_prestamo(monto_wei, int(plazo))
            messagebox.showinfo("Resultado", resultado)
        except ValueError:
            messagebox.showerror("Error", "Monto o plazo inválido.")

def gui_aprobar_prestamo():
    prestatario = simpledialog.askstring("Aprobar Préstamo", "Dirección del prestatario:")
    prestamo_id = simpledialog.askstring("Aprobar Préstamo", "ID del préstamo:")
    if prestatario and prestamo_id and is_valid_eth_address(prestatario):
        resultado = aprobar_prestamo(prestatario, prestamo_id)
        messagebox.showinfo("Resultado", resultado)
    else:
        messagebox.showerror("Error", "Dirección Ethereum del prestatario inválida o ID del préstamo inválido.")

def gui_reembolsar_prestamo():
    prestamo_id = simpledialog.askstring("Reembolsar Préstamo", "ID del préstamo:")
    valor = simpledialog.askstring("Reembolsar Préstamo", "Valor del reembolso en Ether:")
    if prestamo_id and valor:
        try:
            valor_wei = Web3.toWei(float(valor), 'ether')
            resultado = reembolsar_prestamo(prestamo_id, valor_wei)
            messagebox.showinfo("Resultado", resultado)
        except ValueError:
            messagebox.showerror("Error", "Valor inválido.")

def gui_liquidar_garantia():
    prestatario = simpledialog.askstring("Liquidar Garantía", "Dirección del prestatario:")
    prestamo_id = simpledialog.askstring("Liquidar Garantía", "ID del préstamo:")
    if prestatario and prestamo_id and is_valid_eth_address(prestatario):
        resultado = liquidar_garantia(prestatario, prestamo_id)
        messagebox.showinfo("Resultado", resultado)
    else:
        messagebox.showerror("Error", "Dirección Ethereum del prestatario inválida o ID del préstamo inválido.")

def gui_obtener_prestamos_por_prestatario():
    prestatario = simpledialog.askstring("Obtener Préstamos", "Dirección del prestatario:")
    if prestatario and is_valid_eth_address(prestatario):
        resultado = obtener_prestamos_por_prestatario(prestatario)
        messagebox.showinfo("Préstamos", str(resultado))
    else:
        messagebox.showerror("Error", "Dirección Ethereum inválida.")

def gui_obtener_detalle_de_prestamo():
    prestatario = simpledialog.askstring("Detalle del Préstamo", "Dirección del prestatario:")
    prestamo_id = simpledialog.askstring("Detalle del Préstamo", "ID del préstamo:")
    if prestatario and prestamo_id and is_valid_eth_address(prestatario):
        resultado = obtener_detalle_de_prestamo(prestatario, prestamo_id)
        messagebox.showinfo("Detalle", str(resultado))
    else:
        messagebox.showerror("Error", "Dirección Ethereum del prestatario inválida o ID del préstamo inválido.")

def setup_gui():
    root = tk.Tk()
    root.title("Interfaz PrestamoDeFi")
    
     # Creación de botones para cada función
    tk.Button(root, text="Alta de Prestamista", command=gui_alta_prestamista).pack(pady=5)
    tk.Button(root, text="Alta de Cliente", command=gui_alta_cliente).pack(pady=5)
    tk.Button(root, text="Depositar Garantía", command=gui_depositar_garantia).pack(pady=5)
    tk.Button(root, text="Solicitar Préstamo", command=gui_solicitar_prestamo).pack(pady=5)
    tk.Button(root, text="Aprobar Préstamo", command=gui_aprobar_prestamo).pack(pady=5)
    tk.Button(root, text="Reembolsar Préstamo", command=gui_reembolsar_prestamo).pack(pady=5)
    tk.Button(root, text="Liquidar Garantía", command=gui_liquidar_garantia).pack(pady=5)
    tk.Button(root, text="Obtener Préstamos por Prestatario", command=gui_obtener_prestamos_por_prestatario).pack(pady=5)
    tk.Button(root, text="Obtener Detalle de Préstamo", command=gui_obtener_detalle_de_prestamo).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    setup_gui()
 
