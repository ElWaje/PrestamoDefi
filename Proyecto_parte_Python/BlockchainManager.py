import logging
from web3 import Web3, HTTPProvider, exceptions
import json
import time
from datetime import datetime
from ContractUtils import ether_to_wei, wei_to_ether, is_valid_ethereum_address, format_transaction_receipt

# Configuración básica del registro de errores
logging.basicConfig(filename='blockchain_errors.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

ESTADOS_PRESTAMO = {
    0: 'Pendiente',
    1: 'Aprobado',
    2: 'Reembolsado',
    3: 'Liquidado',
}

class BlockchainManager:
    def __init__(self, ganache_url='http://127.0.0.1:7545', contract_address=None, abi_path='PrestamoDeFi.json'):
        self.init_web3(ganache_url)
        self.load_contract(contract_address, abi_path)
        
    def init_web3(self, ganache_url):
        """Inicializa la conexión con Ganache."""
        try:
            self.web3 = Web3(Web3.HTTPProvider(ganache_url))
            if not self.web3.is_connected():
                raise ConnectionError("No se pudo conectar a Ganache.")
        except ConnectionError as e:
            logging.error(f"Error al conectar con Ganache: {e}")
            raise

    def load_contract(self, contract_address, abi_path):
        """Carga el contrato inteligente."""
        try:
            self.contract_address = self.web3.to_checksum_address(contract_address)
            with open(abi_path, 'r') as abi_file:
                self.contract_abi = json.load(abi_file)
            self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.contract_abi)
        except Exception as e:
            logging.error(f"Error al cargar el contrato: {e}")
            raise

    def sign_and_send_transaction(self, function_call, account_address, private_key, ether_value=0, gas_limit=None, gas_price=None, retry=0):
        """Firma y envía una transacción al blockchain, con reintento opcional."""
        value_in_wei = ether_to_wei(ether_value)  # Convertir Ether a Wei
        try:
            account_address = self.web3.to_checksum_address(account_address)
            nonce = self.web3.eth.get_transaction_count(account_address)
            
            # Si no se proporciona un gas limit, calcularlo utilizando una estimación
            if gas_limit is None:
                gas_limit = self.contract.estimateGas({'from': account_address})
            
            # Si no se especifica gas price, usar el valor por defecto
            if gas_price is None:
                gas_price = self.web3.eth.gas_price
            
            transaction = function_call.build_transaction({
                'chainId': self.web3.eth.chain_id,
                'nonce': nonce,
                'value': value_in_wei,
                'from': account_address,
                'gas': gas_limit,      
                'gasPrice': gas_price  
            })
            
            signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key)
            txn_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(txn_hash)
            
            if receipt.status == 0:
                logging.error(f"Transacción fallida con hash: {txn_hash.hex()}")
                raise ValueError("La transacción falló.")
            
            formatted_receipt = format_transaction_receipt(receipt)
            return formatted_receipt
        except Exception as e:
            if retry < 3:
                logging.warning(f"Transacción fallida, reintentando... Error: {e}")
                time.sleep(10)
                return self.sign_and_send_transaction(function_call, account_address, private_key, ether_value, gas_limit, gas_price, retry + 1)
            else:
                logging.error(f"Error al enviar la transacción después de {retry} intentos: {e}")
                raise
                            
    def alta_prestamista(self, direccion_prestamista, clave_privada, nueva_direccion):
        if not is_valid_ethereum_address(nueva_direccion):
            raise ValueError("La nueva dirección no es válida.")
        try:
            function_call = self.contract.functions.altaPrestamista(self.web3.to_checksum_address(nueva_direccion))
            receipt = self.sign_and_send_transaction(function_call, direccion_prestamista, clave_privada)
            return format_transaction_receipt(receipt)
        except Exception as e:
            logging.error("Error en alta_prestamista: %s", str(e))
            raise Exception(f"Error al dar de alta al prestamista: {e}")

    def alta_cliente(self, direccion_prestamista, clave_privada, nueva_direccion):
        if not is_valid_ethereum_address(nueva_direccion):
            raise ValueError("La nueva dirección no es válida.")
        try:
            function_call = self.contract.functions.altaCliente(self.web3.to_checksum_address(nueva_direccion))
            receipt = self.sign_and_send_transaction(function_call, direccion_prestamista, clave_privada)
            return format_transaction_receipt(receipt)
        except Exception as e:
            logging.error("Error en alta_cliente: %s", str(e))
            raise Exception(f"Error al dar de alta al cliente: {e}")

    def depositar_garantia(self, direccion_cliente, clave_privada, valor_ether):
        try:    
            # Convertir el valor en ether a wei
            valor_wei = ether_to_wei(valor_ether)                   
            
            # Definir un gas limit predeterminado
            gas_limit = 1000000
            
            # Obtener el precio del gas actual
            gas_price = self.web3.eth.gas_price
            
            # Llamar a la función del contrato para depositar la garantía
            function_call = self.contract.functions.depositarGarantia()
            
            # Firmar y enviar la transacción al blockchain
            receipt = self.sign_and_send_transaction(function_call, direccion_cliente, clave_privada, valor_ether, gas_limit, gas_price)
            
            # Retornar el recibo de la transacción formateado
            return format_transaction_receipt(receipt)
        except Exception as e:
            # Manejar errores y registrarlos en el log
            logging.error("Error al depositar garantia: %s", str(e))
            raise Exception(f"Error al depositar garantia: {e}")
        
    def solicitar_prestamo(self, direccion_cliente, clave_privada, monto, plazo):
        monto_wei = ether_to_wei(monto)
        try:
            function_call = self.contract.functions.solicitarPrestamo(monto_wei, plazo)
            receipt = self.sign_and_send_transaction(function_call, direccion_cliente, clave_privada)
            return format_transaction_receipt(receipt)
        except Exception as e:
            logging.error("Error al solicitar prestamo: %s", str(e))
            raise Exception(f"Error al solicitar prestamo: {e}")
        
    def aprobar_prestamo(self, direccion_prestamista, clave_privada, direccion_prestatario, prestamo_id):
        if not is_valid_ethereum_address(direccion_prestatario):
            raise ValueError("La dirección del prestatario no es válida.")
        try:
            function_call = self.contract.functions.aprobarPrestamo(self.web3.to_checksum_address(direccion_prestatario), prestamo_id)
            receipt = self.sign_and_send_transaction(function_call, direccion_prestamista, clave_privada)
            return format_transaction_receipt(receipt)
        except Exception as e:
            logging.error("Error al aprobar prestamo: %s", str(e))
            raise Exception(f"Error al aprobar prestamo: {e}")

    def reembolsar_prestamo(self, direccion_cliente, clave_privada, prestamo_id, valor_ether):
        valor_wei = ether_to_wei(valor_ether)
        try:
            function_call = self.contract.functions.reembolsarPrestamo(prestamo_id)
            receipt = self.sign_and_send_transaction(function_call, direccion_cliente, clave_privada, valor_wei)
            return format_transaction_receipt(receipt)
        except Exception as e:
            logging.error("Error al reembolsar prestamo: %s", str(e))
            raise Exception(f"Error al reembolsar prestamo: {e}")

    def liquidar_garantia(self, direccion_prestamista, clave_privada, direccion_prestatario, prestamo_id):
        if not is_valid_ethereum_address(direccion_prestatario):
            raise ValueError("La dirección del prestatario no es válida.")
        try:
            function_call = self.contract.functions.liquidarGarantia(self.web3.to_checksum_address(direccion_prestatario), prestamo_id)
            receipt = self.sign_and_send_transaction(function_call, direccion_prestamista, clave_privada)
            return format_transaction_receipt(receipt)
        except Exception as e:
            logging.error("Error al liquidar garantia: %s", str(e))
            raise Exception(f"Error al liquidar garantia: {e}")

    def mapear_estado_prestamo(self, estado):
        """Mapea el código de estado a una descripción legible."""
        return ESTADOS_PRESTAMO.get(estado, 'Desconocido')
    
    def obtener_prestamos_por_prestatario(self, direccion_prestatario):
        """Obtiene y formatea los préstamos de un prestatario."""
        if not is_valid_ethereum_address(direccion_prestatario):
            raise ValueError("La dirección del prestatario no es válida.")
        try:
            prestamos_raw = self.contract.functions.obtenerPrestamosPorPrestatario(self.web3.toChecksumAddress(direccion_prestatario)).call()
            prestamos_format = [{
                "id_prestamo": prestamo[0],
                "monto": wei_to_ether(prestamo[1]),
                "plazo": prestamo[2],
                "fecha_inicio": datetime.utcfromtimestamp(prestamo[3]).strftime('%Y-%m-%d %H:%M:%S'),
                "estado": self.mapear_estado_prestamo(prestamo[4]),
            } for prestamo in prestamos_raw]
            return prestamos_format
        except Exception as e:
            logging.error(f"Error al obtener préstamos por prestatario: {e}")
            raise Exception(f"Error al obtener préstamos por prestatario: {e}")
        
    def obtener_detalle_de_prestamo(self, direccion_prestatario, prestamo_id):
        if not is_valid_ethereum_address(direccion_prestatario):
            raise ValueError("La dirección del prestatario no es válida.")

        try:
            # Obtener los detalles del préstamo desde el contrato
            prestamo = self.contract.functions.obtenerDetalleDePrestamo(
                self.web3.toChecksumAddress(direccion_prestatario), prestamo_id).call()

            # Formatear los detalles del préstamo
            detalle_prestamo = {
                "id": prestamo[0],
                "prestatario": prestamo[1],
                "monto": wei_to_ether(prestamo[2]),  # Convertir de Wei a Ether
                "plazo": prestamo[3],
                "fecha_solicitud": datetime.utcfromtimestamp(prestamo[4]).strftime('%Y-%m-%d %H:%M:%S'),
                "fecha_limite": datetime.utcfromtimestamp(prestamo[5]).strftime('%Y-%m-%d %H:%M:%S'),
                "estado": self.mapear_estado_prestamo(prestamo[6]) 
            }

            return detalle_prestamo
        except Exception as e:
            logging.error("Error al obtener detalle de préstamo: %s", str(e))
            raise Exception(f"Error al obtener detalle de préstamo: {e}")
        
if __name__ == "__main__":
    ganache_url = 'http://127.0.0.1:7545'
    contract_address = '0xC55B44fa88A5389039cECaebcC2D164433908F04'
    blockchain_manager = BlockchainManager(ganache_url, contract_address)
      