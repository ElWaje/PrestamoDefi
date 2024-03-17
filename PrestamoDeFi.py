from web3 import Web3, HTTPProvider
from web3.exceptions import (
    TransactionNotFound,
    ContractLogicError,
    ValidationError,
    InvalidAddress
)
import json
from web3.middleware import geth_poa_middleware
from getpass import getpass

# Conexión a Ganache
web3 = Web3(HTTPProvider('http://127.0.0.1:7545'))  # Ganache endpoint
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Dirección y ABI del contrato
contract_address = web3.to_checksum_address('0x25238d7855c60436DA77483CDEDB037291958023')
with open('PrestamoDeFi.json') as f:
    contract_abi = json.load(f)

# Cargar el contrato
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def sign_and_send_transaction(function_call, from_address, private_key, value=0):
    try:
        nonce = web3.eth.get_transaction_count(web3.to_checksum_address(from_address))
        gas_estimate = function_call.estimate_gas({'from': web3.to_checksum_address(from_address)})
        
        # Aumentar el límite de gas en 100,000 unidades
        transaction = function_call.build_transaction({
            'chainId': web3.eth.chain_id,
            'gas': gas_estimate + 100000,
            'gasPrice': web3.to_wei('50', 'gwei'),
            'nonce': nonce,
            'value': value,
            'from': web3.to_checksum_address(from_address)
        })

        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
        return "Éxito", receipt.transactionHash.hex()
    except ValueError as e:
        print("Error al enviar la transacción:", e)
    except TransactionNotFound:
        print("Transacción no encontrada después de enviar.")
    except ContractLogicError as e:
        print("Error de lógica del contrato:", e)
    except ValidationError as e:
        print(f"Error de validación: {e}")
    except Exception as e:
        print("Error desconocido:", e)
        
def alta_prestamista(direccion_prestamista, clave_privada, nueva_direccion):
    
    try:
        es_socio_principal = direccion_prestamista.lower() == contract.functions.socioPrincipal().call().lower()
        es_prestamista_autorizado = contract.functions.empleadosPrestamista(web3.to_checksum_address(direccion_prestamista)).call()
        
        if not es_socio_principal and not es_prestamista_autorizado:
            return "Error", "No tiene permisos para realizar esta acción."

        if not web3.is_address(nueva_direccion):
            return "Error", "La dirección del nuevo prestamista no es válida."

        estado, tx_hash = sign_and_send_transaction(
            contract.functions.altaPrestamista(web3.to_checksum_address(nueva_direccion)),
            web3.to_checksum_address(direccion_prestamista),
            clave_privada
        )
        return estado, f"Prestamista agregado con éxito. Hash de la transacción: {tx_hash}"
    
    except (InvalidAddress, ValidationError) as e:
        return "Error", f"Error al procesar la transacción: {e}"
    except ContractLogicError as e:
        return "Error", f"Error de lógica de contrato: {e}"
    except Exception as e:
        return "Error", f"Error inesperado: {e}"
    
def alta_cliente(direccion_prestamista, clave_privada, nueva_direccion):
    try:
        if not contract.functions.empleadosPrestamista(web3.to_checksum_address(direccion_prestamista)).call():
            return "Error", "No tiene permisos para realizar esta acción."
        if not web3.is_address(nueva_direccion):
            return "Error", "La dirección del nuevo cliente no es válida."
        estado, tx_hash = sign_and_send_transaction(
            contract.functions.altaCliente(web3.to_checksum_address(nueva_direccion)),
            web3.to_checksum_address(direccion_prestamista),
            clave_privada
        )
        return estado, f"Cliente agregado con éxito. Hash de la transacción: {tx_hash}"
    except ContractLogicError as e:
        return "Error de lógica del contrato", str(e)
    except Exception as e:
        return "Error", str(e)

def depositar_garantia(direccion_cliente, clave_privada, valor_ether):
    try:
        # Convertir el valor a Wei desde Ether y asegurar que es positivo
        valor_wei = web3.to_wei(valor_ether, 'ether')
        if valor_wei <= 0:
            print("El valor a depositar debe ser mayor a 0.")
            return

        # Obtener el saldo de la cuenta
        account_balance = web3.eth.get_balance(web3.to_checksum_address(direccion_cliente))
        print(f"Saldo de la cuenta: {web3.from_wei(account_balance, 'ether')} ETH")

        # Verificar si el saldo es suficiente para cubrir el valor de la transacción
        if valor_wei > account_balance:
            print("Error: Fondos insuficientes para cubrir el valor de la transacción.")
            return

        # Obtener el estimado del gas
        gas_estimate = contract.functions.depositarGarantia().estimateGas({'from': web3.to_checksum_address(direccion_cliente)})

        # Calcular el valor de la transacción
        transaction_value = gas_estimate * web3.eth.gasPrice + valor_wei
        print(f"Valor estimado del gas: {gas_estimate}")
        print(f"Valor de la transacción: {web3.from_wei(transaction_value, 'ether')} ETH")

        # Realizar la transacción
        cliente_activado, saldo_garantia = contract.functions.clientes(web3.to_checksum_address(direccion_cliente)).call()
        if not cliente_activado:
            print("Error: No es un cliente activado o no tiene permisos para realizar esta acción.")
            return

        estado, tx_hash = sign_and_send_transaction(
            contract.functions.depositarGarantia(),
            web3.to_checksum_address(direccion_cliente),
            clave_privada,
            valor_wei
        )
        
        if estado == "Éxito":
            # Obtener el saldo de garantía actualizado después del depósito
            _, saldo_garantia_actualizado = contract.functions.clientes(web3.to_checksum_address(direccion_cliente)).call()
            print(f"Garantía depositada con éxito. Hash de la transacción: {tx_hash}. Valor depositado: {valor_ether} ETH.")
            print(f"Saldo de garantía actual: {saldo_garantia_actualizado} Wei")
        else:
            print(estado)
    except ContractLogicError as e:
        print(f"Error de lógica del contrato: {e}")
    except Exception as e:
        print(f"Error al intentar depositar garantía: {e}")

def solicitar_prestamo(direccion_cliente, clave_privada, monto, plazo):
    try:
        if monto <= 0 or plazo <= 0:
            return "Error", "El monto y el plazo del préstamo deben ser mayores a 0."
        
        if not contract.functions.clientes(web3.to_checksum_address(direccion_cliente)).call()[0]:
            return "Error", "No es un cliente activado o no tiene permisos para realizar esta acción."
        
        estado, tx_hash = sign_and_send_transaction(
            contract.functions.solicitarPrestamo(monto, plazo),
            web3.to_checksum_address(direccion_cliente),
            clave_privada
        )
        return estado, f"Préstamo solicitado con éxito. Hash de la transacción: {tx_hash}. Monto solicitado: {web3.fromWei(monto, 'ether')} ETH, Plazo: {plazo} segundos."
    except ContractLogicError as e:
        return "Error de lógica del contrato", str(e)
    except Exception as e:
        return "Error", str(e)
           
def aprobar_prestamo(direccion_prestamista, clave_privada, direccion_prestatario, prestamo_id):
    try:
        es_prestamista_autorizado = contract.functions.empleadosPrestamista(web3.to_checksum_address(direccion_prestamista)).call()
        if not es_prestamista_autorizado:
            return "Error", "No tiene permisos para realizar esta acción."
        if not web3.is_address(direccion_prestatario):
            return "Error", "Dirección del prestatario no válida."
        estado, tx_hash = sign_and_send_transaction(
            contract.functions.aprobarPrestamo(web3.to_checksum_address(direccion_prestatario), prestamo_id),
            web3.to_checksum_address(direccion_prestamista),
            clave_privada
        )
        return estado, f"Préstamo aprobado con éxito. Hash de la transacción: {tx_hash}"
    except ContractLogicError as e:
        print(f"Error de lógica de contrato: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

def reembolsar_prestamo(direccion_cliente, clave_privada, prestamo_id, valor):
    try:
        es_cliente_activado = contract.functions.clientes(web3.to_checksum_address(direccion_cliente)).call()[0]
        if not es_cliente_activado:
            return "Error", "No es un cliente activado."
        estado, tx_hash = sign_and_send_transaction(
            contract.functions.reembolsarPrestamo(prestamo_id),
            web3.to_checksum_address(direccion_cliente),
            clave_privada,
            valor
        )
        return estado, f"Préstamo reembolsado con éxito. Hash de la transacción: {tx_hash}"
    except ContractLogicError as e:
        print(f"Error de lógica de contrato: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

def liquidar_garantia(direccion_prestamista, clave_privada, direccion_prestatario, prestamo_id):
    try:
        es_prestamista_autorizado = contract.functions.empleadosPrestamista(web3.to_checksum_address(direccion_prestamista)).call()
        if not es_prestamista_autorizado:
            return "Error", "No tiene permisos para realizar esta acción."
        if not web3.is_address(direccion_prestatario):
            return "Error", "Dirección del prestatario no válida."
        estado, tx_hash = sign_and_send_transaction(
            contract.functions.liquidarGarantia(web3.to_checksum_address(direccion_prestatario), prestamo_id),
            web3.to_checksum_address(direccion_prestamista),
            clave_privada
        )
        return estado, f"Garantía liquidada con éxito. Hash de la transacción: {tx_hash}"
    except ContractLogicError as e:
        print(f"Error de lógica de contrato: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

def obtener_prestamos_por_prestatario(direccion_prestatario):
    try:
        if not web3.is_address(direccion_prestatario):
            return "Error", "Dirección del prestatario no válida."
        prestamos = contract.functions.obtenerPrestamosPorPrestatario(web3.to_checksum_address(direccion_prestatario)).call()
        return "Éxito", prestamos
    except ContractLogicError as e:
        print(f"Error de lógica de contrato: {e}")
    except Exception as e:
        print(f"Error al obtener los préstamos: {e}")

def obtener_detalle_de_prestamo(direccion_prestatario, prestamo_id):
    try:
        if not web3.is_address(direccion_prestatario):
            return "Error", "Dirección del prestatario no válida."
        detalle = contract.functions.obtenerDetalleDePrestamo(web3.to_checksum_address(direccion_prestatario), prestamo_id).call()
        return "Éxito", detalle
    except ContractLogicError as e:
        print(f"Error de lógica de contrato: {e}")
    except  Exception as e:
        return "Error", str(e)

def get_web3():
    return web3
