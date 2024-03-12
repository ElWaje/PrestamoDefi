from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
import json
from web3.exceptions import (
    TransactionNotFound,
    ContractLogicError,
    InvalidAddress
)

# Configuración inicial
web3 = Web3(HTTPProvider('http://127.0.0.1:7545'))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

contract_address = web3.toChecksumAddress('tu_direccion_del_contrato')
private_key = 'tu_clave_privada'

with open('path_to_your_contract_abi.json', 'r') as abi_definition:
    contract_abi = json.load(abi_definition)

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

from_address = web3.eth.account.privateKeyToAccount(private_key).address

def sign_and_send_transaction(function_call, private_key, value=0):
    nonce = web3.eth.getTransactionCount(from_address)
    transaction = function_call.buildTransaction({
        'chainId': web3.eth.chain_id,
        'gas': 2000000,
        'gasPrice': web3.toWei('50', 'gwei'),
        'nonce': nonce,
        'value': value,
    })
    signed_txn = web3.eth.account.signTransaction(transaction, private_key=private_key)
    try:
        txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        receipt = web3.eth.waitForTransactionReceipt(txn_hash)
        return "Éxito", receipt
    except TransactionNotFound:
        return "Error", "La transacción no se encontró después de ser enviada."
    except ContractLogicError as e:
        return "Error de contrato", str(e)
    except Exception as e:
        return "Error", str(e)
    
def alta_prestamista(nuevo_prestamista):
    if not web3.isAddress(nuevo_prestamista):
        return "Dirección del prestamista no válida."
    function_call = contract.functions.altaPrestamista(nuevo_prestamista)
    estado, mensaje = sign_and_send_transaction(function_call, private_key)
    if estado == "Éxito":
        return f"Prestamista añadido con éxito, tx hash: {mensaje.transactionHash.hex()}"
    else:
        return f"No se pudo completar altaPrestamista: {mensaje}"

def alta_cliente(nuevo_cliente):
    if not web3.isAddress(nuevo_cliente):
        return "Dirección del cliente no válida."
    function_call = contract.functions.altaCliente(nuevo_cliente)
    estado, mensaje = sign_and_send_transaction(function_call, private_key)
    if estado == "Éxito":
        return f"Cliente añadido con éxito, tx hash: {mensaje.transactionHash.hex()}"
    else:
        return f"No se pudo completar altaCliente: {mensaje}"

def depositar_garantia(valor):
    try:
        valor = int(valor)  # Asumiendo que 'valor' es introducido en Wei por la GUI
    except ValueError:
        return "El valor debe ser un número entero."
    function_call = contract.functions.depositarGarantia()
    estado, mensaje = sign_and_send_transaction(function_call, private_key, value=valor)
    if estado == "Éxito":
        return "Garantía depositada con éxito."
    else:
        return f"No se pudo depositar la garantía: {mensaje}"

def solicitar_prestamo(monto, plazo):
    try:
        monto = int(monto)
        plazo = int(plazo)
    except ValueError:
        return "Monto y plazo deben ser números enteros."
    function_call = contract.functions.solicitarPrestamo(monto, plazo)
    estado, mensaje = sign_and_send_transaction(function_call, private_key)
    if estado == "Éxito":
        return "Préstamo solicitado con éxito."
    else:
        return f"No se pudo solicitar el préstamo: {mensaje}"

def aprobar_prestamo(prestatario, prestamo_id):
    if not web3.isAddress(prestatario):
        return "Dirección del prestatario no válida."
    try:
        prestamo_id = int(prestamo_id)
    except ValueError:
        return "ID de préstamo debe ser un número entero."
    function_call = contract.functions.aprobarPrestamo(prestatario, prestamo_id)
    estado, mensaje = sign_and_send_transaction(function_call, private_key)
    if estado == "Éxito":
        return "Préstamo aprobado con éxito."
    else:
        return f"No se pudo aprobar el préstamo: {mensaje}"

def reembolsar_prestamo(prestamo_id, valor):
    try:
        prestamo_id = int(prestamo_id)
        valor = int(valor)  # Asumiendo que 'valor' es introducido en Wei por la GUI
    except ValueError:
        return "ID de préstamo y valor deben ser números enteros."
    function_call = contract.functions.reembolsarPrestamo(prestamo_id)
    estado, mensaje = sign_and_send_transaction(function_call, private_key, value=valor)
    if estado == "Éxito":
        return "Préstamo reembolsado con éxito."
    else:
        return f"No se pudo reembolsar el préstamo: {mensaje}"

def liquidar_garantia(prestatario, prestamo_id):
    if not web3.isAddress(prestatario):
        return "Dirección del prestatario no válida."
    try:
        prestamo_id = int(prestamo_id)
    except ValueError:
        return "ID de préstamo debe ser un número entero."
    function_call = contract.functions.liquidarGarantia(prestatario, prestamo_id)
    estado, mensaje = sign_and_send_transaction(function_call, private_key)
    if estado == "Éxito":
        return "Garantía liquidada con éxito."
    else:
        return f"No se pudo liquidar la garantía: {mensaje}"

def obtener_prestamos_por_prestatario(prestatario):
    if not web3.isAddress(prestatario):
        return "Dirección del prestatario no válida."
    try:
        prestamos = contract.functions.obtenerPrestamosPorPrestatario(prestatario).call()
        return f"Préstamos del prestatario {prestatario}: {prestamos}"
    except Exception as e:
        return f"Error al obtener préstamos por prestatario: {str(e)}"

def obtener_detalle_de_prestamo(prestatario, prestamo_id):
    if not web3.isAddress(prestatario):
        return "Dirección del prestatario no válida."
    try:
        prestamo_id = int(prestamo_id)
        prestamo = contract.functions.obtenerDetalleDePrestamo(prestatario, prestamo_id).call()
        return f"Detalle del préstamo {prestamo_id} para el prestatario {prestatario}: {prestamo}"
    except Exception as e:
        return f"Error al obtener detalle de préstamo: {str(e)}"
