import logging
from web3 import Web3, HTTPProvider, exceptions
import json
import time
from datetime import datetime
from ContractUtils import ether_to_wei, wei_to_ether, is_valid_ethereum_address, format_transaction_receipt, log_transaction_receipt
from web3.exceptions import (
    TransactionNotFound,
    TimeExhausted,
    ContractLogicError,
    InvalidAddress
)

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
    """
        Gestiona la conexión y las interacciones con un contrato inteligente en la red Ethereum,
        facilitando las operaciones comunes como la inicialización de la conexión Web3, la carga de
        contratos inteligentes y la ejecución de funciones del contrato.

        Esta clase se utiliza como una capa de abstracción para simplificar las tareas de comunicación
        y operación con la blockchain de Ethereum, especialmente para desarrolladores que trabajan con
        contratos inteligentes y aplicaciones descentralizadas (dApps).

        Atributos:
        - web3 (Web3): Una instancia de Web3.py utilizada para interactuar con la blockchain de Ethereum.
        - contract (Contract): Una instancia del contrato inteligente con el que se interactuará.
        - contract_address (str): La dirección del contrato inteligente en la red Ethereum.
        - contract_abi (json): La Interfaz Binaria de Aplicación (ABI) del contrato inteligente, necesaria
        para interactuar con sus funciones.

        Métodos:
        - __init__(self, ganache_url, contract_address, abi_path): Constructor de la clase.
        - init_web3(self, ganache_url): Inicializa la conexión con la red Ethereum utilizando Web3.
        - load_contract(self, contract_address, abi_path): Carga el contrato inteligente especificado
        por su dirección y ABI para interactuar con él.
        
    """
    def __init__(self, ganache_url='http://127.0.0.1:7545', contract_address=None, abi_path='PrestamoDeFi.json'):
        """
            Constructor para la clase BlockchainManager, que inicializa la conexión con la red Ethereum local
            utilizando Ganache y carga un contrato inteligente especificado para su interacción.

            Este método se llama automáticamente al crear una nueva instancia de BlockchainManager, realizando
            dos tareas principales: establecer la conexión con Ganache y cargar el contrato inteligente deseado
            utilizando su dirección y la Interfaz Binaria de Aplicación (ABI).

            Parámetros:
            - ganache_url (str, opcional): La URL de la instancia de Ganache a la que se conectará la aplicación.
            Por defecto, se asume que Ganache se ejecuta en http://127.0.0.1:7545.
            - contract_address (str, opcional): La dirección del contrato inteligente en la red Ethereum que se
            desea cargar e interactuar. Si se omite, se deberá establecer manualmente más tarde antes de realizar
            operaciones con el contrato.
            - abi_path (str, opcional): La ruta al archivo JSON que contiene la ABI del contrato inteligente.
            Por defecto, se usa 'PrestamoDeFi.json'. La ABI es necesaria para que Web3.py sepa cómo interactuar
            con el contrato (por ejemplo, qué funciones se pueden llamar).

            Proceso:
            1. Inicializa la conexión con Ganache utilizando la URL proporcionada.
            2. Carga el contrato inteligente utilizando su dirección y la ruta al archivo ABI especificadas.
            Si no se proporciona una dirección de contrato, la carga del contrato debe ser manejada
            externamente antes de interactuar con él.
            
        """
        self.init_web3(ganache_url)
        self.load_contract(contract_address, abi_path)
        
    def init_web3(self, ganache_url):
        """
            Establece la conexión con una instancia de Ganache para interactuar con la red Ethereum localmente.

            Ganache es una cadena de bloques Ethereum personal que se ejecuta localmente en tu máquina. Se utiliza
            principalmente para desarrollo y pruebas, permitiendo desplegar contratos, desarrollar aplicaciones y
            ejecutar pruebas en un entorno controlado sin costos de gas.

            Parámetros:
            - ganache_url: La URL de la instancia de Ganache a la que se desea conectar. Generalmente,
            Ganache se ejecuta en http://localhost:7545, pero puede variar dependiendo de la configuración.

            Proceso:
            - Intenta establecer una conexión utilizando la URL proporcionada. Si la conexión es exitosa,
            la instancia de Web3 quedará inicializada y lista para su uso.
            - Si no se puede establecer una conexión, se lanza una excepción `ConnectionError`.

            Excepciones:
            - ConnectionError: Se lanza si la conexión con Ganache no puede ser establecida. Esto puede suceder si
            Ganache no está en ejecución o si hay problemas de red o configuración que impiden la conexión.
            
        """
        try:
            self.web3 = Web3(Web3.HTTPProvider(ganache_url))
            if not self.web3.is_connected():
                raise ConnectionError("No se pudo conectar a Ganache.")
        except ConnectionError as e:
            logging.error(f"Error al conectar con Ganache: {e}")
            raise

    def load_contract(self, contract_address, abi_path):
        """
            Inicializa y carga el contrato inteligente especificado para permitir su interacción a través de Web3.

            Utiliza la dirección del contrato y la ruta al archivo de Interfaz Binaria de Aplicación (ABI) para
            crear una instancia del contrato que se puede usar para realizar llamadas y transacciones.

            Parámetros:
            - contract_address: La dirección del contrato inteligente en la red Ethereum. Esta dirección es
            utilizada para identificar de manera única el contrato con el que se desea interactuar.
            - abi_path: La ruta al archivo JSON que contiene la ABI del contrato inteligente. La ABI es esencial
            para definir las interfaces a través de las cuales se interactúa con el contrato, incluyendo
            funciones, eventos y tipos de variables.

            Excepciones:
            - Exception: Captura y reporta cualquier error que pueda ocurrir durante el proceso de carga del
            contrato, incluyendo errores al leer el archivo ABI, problemas con la dirección del contrato,
            o errores generales de Web3.
            
        """
        try:
            self.contract_address = self.web3.to_checksum_address(contract_address)
            with open(abi_path, 'r') as abi_file:
                self.contract_abi = json.load(abi_file)
            self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.contract_abi)
        except Exception as e:
            logging.error(f"Error al cargar el contrato: {e}")
            raise

    def sign_and_send_transaction(self, function_call, account_address, private_key, ether_value=0, gas_limit=None):
        """Firma y envía una transacción al blockchain, invocando una función específica de un contrato inteligente
            y asegurando que el emisor tenga fondos suficientes para cubrir el costo de gas y el valor de la transacción.
            Esta función es genérica y se puede utilizar para cualquier llamada a función de contrato que requiera
            una transacción, asegurando la flexibilidad en su uso.

            Parámetros:
            - function_call (ContractFunction): Una instancia de la función del contrato a ser invocada. 
            Esto se obtiene llamando al método de función correspondiente del objeto de contrato de Web3.py.
            - account_address (str): La dirección Ethereum desde la cual se envía la transacción. Debe ser una
            dirección válida que el usuario controle y por la cual pueda firmar transacciones.
            - private_key (str): La clave privada del emisor asociada a `account_address`, utilizada para firmar 
            la transacción. Debe empezar con '0x' y ser una cadena hexadecimal válida.
            - ether_value (int): El valor de la transacción en wei. Aunque denominado `ether_value`, este parámetro
            debe estar ya convertido a wei. Es el valor enviado junto con la llamada a la función del contrato.
            - gas_limit (int, opcional): El límite de gas para la transacción. Si no se proporciona, se estima un valor
            por defecto o se utiliza uno proporcionado por el usuario para asegurar que la transacción no falle por
            falta de gas.

            Retorna:
            Una cadena de texto que representa un mensaje de éxito y un resumen del recibo de la transacción si esta
            es exitosa. El resumen del recibo incluye detalles relevantes para su revisión y seguimiento.

            Excepciones:
            - ValueError: Se lanza si la dirección Ethereum no es válida, la clave privada no está en el formato correcto,
            o si la transacción falla (indicado por un estado de recibo de '0').
            - InvalidAddress: Se lanza si se proporciona una dirección inválida para la transacción.
            - TransactionNotFound: Se lanza si la transacción no se encuentra después de ser enviada a la red.
            - TimeExhausted: Se lanza si el tiempo de espera para que la transacción sea minada se agota.
            - ContractLogicError: Se lanza si ocurre un error en la lógica del contrato al intentar ejecutar la función.
            - Exception: Captura y lanza cualquier otro error no especificado que pueda ocurrir durante el proceso
            de firma y envío de la transacción.
        """     
        try:
            account_address = self.web3.to_checksum_address(account_address.strip())
            if not is_valid_ethereum_address(account_address):
                raise ValueError(f"La dirección {account_address} no es válida.")
            
            nonce = self.web3.eth.get_transaction_count(account_address)
            value_in_wei = ether_value
            gas_limit = gas_limit if gas_limit is not None else 2000000
            gas_price = self.web3.eth.gas_price
            transaction = function_call.build_transaction({
                'from': account_address,
                'chainId': self.web3.eth.chain_id,
                'gas': gas_limit,
                'gasPrice': self.web3.to_wei('50', 'gwei'),
                'nonce': nonce,
                'value': value_in_wei,
            })
            
            if not isinstance(private_key, str) or not private_key.startswith('0x'):
                raise ValueError("La clave privada debe ser una cadena hexadecimal que comience con 0x.")
            
            signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key)
            txn_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(txn_hash)
            
            if receipt.status == 0:
                logging.error("La transacción falló. Recibo: {}".format(receipt))
                raise ValueError("La transacción falló.")
            else:
                logging.info("Transacción exitosa. Recibo: {}".format(receipt))                
                formatted_receipt = format_transaction_receipt(receipt)
                success_message = "Transacción exitosa. Recibo: {}".format(formatted_receipt)
                return success_message 
        except ValueError as e:
            logging.error(f"Error de valor: {e}")
            raise e

        except InvalidAddress as e:
            logging.error(f"Dirección inválida: {e}")
            raise e

        except TransactionNotFound as e:
            logging.error(f"Transacción no encontrada: {e}")
            raise e

        except TimeExhausted as e:
            logging.error(f"Tiempo agotado esperando la transacción: {e}")
            raise e

        except ContractLogicError as e:
            logging.error(f"Error de lógica del contrato: {e}")
            raise e

        except Exception as e:
            logging.error(f"Error al realizar la transacción: {e}")
            raise e    
                        
    def alta_prestamista(self, direccion_prestamista, clave_privada, nueva_direccion):
        """
        Registra un nuevo prestamista en el contrato inteligente del sistema. Este método
        invoca la función altaPrestamista del contrato inteligente, la cual debe estar
        diseñada para añadir una nueva dirección de prestamista a un registro mantenido
        por el contrato.

        Parámetros:
        - direccion_prestamista: La dirección Ethereum del prestamista que realiza la acción.
                                Debe ser una dirección válida y tener los permisos adecuados
                                en el contrato para registrar nuevos prestamistas.
        - clave_privada: La clave privada del prestamista que se usa para firmar la transacción.
                        Debe corresponder a la dirección_prestamista.
        - nueva_direccion: La dirección Ethereum del nuevo prestamista a registrar. Esta dirección
                        debe ser válida y no previamente registrada como prestamista en el contrato.

        Retorna:
        Una representación formateada del recibo de la transacción si esta es exitosa. La
        representación incluye detalles clave del recibo para facilitar su revisión y seguimiento,
        como el hash de la transacción, el estado de la transacción, y el gas utilizado.

        Excepciones:
        - ValueError: Se lanza si la nueva dirección no es una dirección Ethereum válida.
        - Exception: Captura y maneja cualquier otra excepción general que pueda ocurrir durante
                    el proceso de la transacción. Esto incluye errores de firma de transacciones,
                    problemas al interactuar con el contrato inteligente, y cualquier otro error
                    de ejecución.
                
        """
        if not is_valid_ethereum_address(nueva_direccion):
            raise ValueError("La nueva dirección no es válida.")
        try:
            function_call = self.contract.functions.altaPrestamista(self.web3.to_checksum_address(nueva_direccion))
            receipt = self.sign_and_send_transaction(function_call, direccion_prestamista, clave_privada, 0)
            return format_transaction_receipt(receipt)
        except Exception as e:
            logging.error("Error en alta_prestamista: %s", str(e))
            raise Exception(f"Error al dar de alta al prestamista: {e}")
        
    def alta_cliente(self, direccion_prestamista, clave_privada, nueva_direccion):
        """
        Registra un nuevo cliente en el sistema mediante la invocación de la función
        del contrato inteligente destinada a este fin. La transacción es firmada y enviada
        por el prestamista, quien asume el papel de autorizador en este contexto.

        Parámetros:
        - direccion_prestamista (str): La dirección Ethereum del prestamista que realiza
        la operación. Esta dirección es utilizada para firmar y enviar la transacción.
        - clave_privada (str): La clave privada del prestamista, necesaria para firmar
        la transacción. Debe comenzar con '0x'.
        - nueva_direccion (str): La dirección Ethereum del nuevo cliente que se está
        registrando en el sistema.

        Retorna:
        - str: Una representación formateada del recibo de la transacción, que incluye
        detalles relevantes como el hash de la transacción, el estado, y el gas utilizado.
        
        Excepciones:
        - ValueError: Se lanza si alguna de las direcciones proporcionadas no es válida
        o si se encuentran otros errores de valor.
        - Exception: Se lanza para capturar y manejar cualquier otro tipo de error que
        pueda ocurrir durante la preparación, firma, envío de la transacción, o la
        interacción con el contrato inteligente.        
        """
        try:
            direccion_cliente = self.web3.to_checksum_address(direccion_cliente)
            if not is_valid_ethereum_address(direccion_cliente):
                raise ValueError(f"La dirección {direccion_cliente} no es válida.")

            function_call = self.contract.functions.altaCliente(self.web3.to_checksum_address(nueva_direccion))
            receipt = self.sign_and_send_transaction(function_call, direccion_prestamista, clave_privada, 0)
            
            return format_transaction_receipt(receipt)
        except ValueError as e:
            logging.error(f"Error de valor: {e}")
            raise e
        except InvalidAddress as e:
            logging.error(f"Dirección inválida: {e}")
            raise e
        except ContractLogicError as e:
            logging.error(f"Error de lógica del contrato: {e}")
            raise e
        except Exception as e:
            logging.error("Error al registrar al cliente: %s", str(e))
            raise Exception(f"Error al registrar al cliente: {e}")
        
    def depositar_garantia(self, direccion_cliente, clave_privada, valor_ether):
        """ Permite a un cliente depositar garantía en el contrato, llamando a la función depositarGarantia del contrato inteligente.    
            Esta función envuelve la lógica necesaria para preparar, firmar y enviar la transacción que invoca la función de depositar garantía en el contrato. Asume que el valor de ether ya ha sido convertido a wei antes de ser pasado a esta función.
            
            Parámetros:
            - direccion_cliente: La dirección Ethereum del cliente que deposita la garantía.
            - clave_privada: La clave privada del cliente para firmar la transacción.
            - valor_ether: El valor de la garantía a depositar, expresado en wei. Aunque el nombre del parámetro sugiere 'ether', se espera que este valor ya esté convertido a wei.
            
            Retorna:
            Una representación formateada del recibo de la transacción si esta es exitosa. La representación incluye detalles clave del recibo para facilitar su revisión y seguimiento.
            
            Excepciones:
            - ValueError: Se lanza si la dirección del cliente no es válida o si se encuentran otros errores de valor (por ejemplo, conversión de valores).
            - InvalidAddress: Se lanza si la dirección Ethereum proporcionada es inválida.
            - ContractLogicError: Se lanza si hay un error en la lógica del contrato al intentar depositar la garantía.
            - Exception: Captura y lanza cualquier otra excepción general que pueda ocurrir durante el proceso de la transacción.
        """
        try:
            direccion_cliente = self.web3.to_checksum_address(direccion_cliente)
            if not is_valid_ethereum_address(direccion_cliente):
                raise ValueError(f"La dirección {direccion_cliente} no es válida.")
            
            valor_wei = valor_ether
            function_call = self.contract.functions.depositarGarantia()
            receipt = self.sign_and_send_transaction(function_call, direccion_cliente, clave_privada, valor_wei, gas_limit=2000000)
            
            return format_transaction_receipt(receipt)
        except ValueError as e:
            logging.error(f"Error de valor: {e}")
            raise e
        
        except InvalidAddress as e:
            logging.error(f"Dirección inválida: {e}")
            raise e
        
        except ContractLogicError as e:
            logging.error(f"Error de lógica del contrato: {e}")
            raise e
        
        except Exception as e:
            logging.error("Error al depositar garantia: %s", str(e))
            raise Exception(f"Error al depositar garantia: {e}")
        
    def solicitar_prestamo(self, direccion_cliente, clave_privada, monto, plazo):
        """
            Permite a un cliente solicitar un préstamo en el contrato.

            Parámetros:
            - direccion_cliente: La dirección Ethereum del cliente que solicita el préstamo.
            - clave_privada: La clave privada del cliente para firmar la transacción.
            - monto_wei: El monto del préstamo solicitado, expresado en wei.
            - plazo_segundos: El plazo del préstamo, expresado en segundos.

            Retorna:
            Una representación formateada del recibo de la transacción si esta es exitosa.
        """
        monto_wei = monto
        try:
            function_call = self.contract.functions.solicitarPrestamo(monto_wei, plazo)
            receipt = self.sign_and_send_transaction(function_call, direccion_cliente, clave_privada, 0)
            return format_transaction_receipt(receipt)
        except Exception as e:
            logging.error("Error al solicitar prestamo: %s", str(e))
            raise Exception(f"Error al solicitar prestamo: {e}")
        
    def aprobar_prestamo(self, direccion_prestamista, clave_privada, direccion_prestatario, prestamo_id):
        """
            Aprueba un préstamo específico para un prestatario, identificado por su dirección y el ID del préstamo.

            Parámetros:
            - direccion_prestamista: La dirección Ethereum del prestamista que aprueba el préstamo.
            - clave_privada: La clave privada del prestamista para firmar la transacción.
            - direccion_prestatario: La dirección Ethereum del prestatario cuyo préstamo se está aprobando.
            - prestamo_id: El identificador del préstamo a aprobar.

            Retorna:
            Un recibo de la transacción formateado que proporciona detalles del resultado de la transacción.

            Excepciones:
            - ValueError: Si la dirección del prestatario no es válida.
            - Exception: Para otros errores capturados durante el proceso de la transacción.
        """
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
        """
            Aprueba un préstamo específico para un prestatario, identificado por su dirección y el ID del préstamo.

            Parámetros:
            - direccion_prestamista: La dirección Ethereum del prestamista que aprueba el préstamo.
            - clave_privada: La clave privada del prestamista para firmar la transacción.
            - direccion_prestatario: La dirección Ethereum del prestatario cuyo préstamo se está aprobando.
            - prestamo_id: El identificador del préstamo a aprobar.

            Retorna:
            Un recibo de la transacción formateado que proporciona detalles del resultado de la transacción.

            Excepciones:
            - ValueError: Si la dirección del prestatario no es válida.
            - Exception: Para otros errores capturados durante el proceso de la transacción.
        """
        valor_wei = valor_ether
        try:
            function_call = self.contract.functions.reembolsarPrestamo(prestamo_id)
            receipt = self.sign_and_send_transaction(function_call, direccion_cliente, clave_privada, valor_wei)
            return format_transaction_receipt(receipt)
        except Exception as e:
            logging.error("Error al reembolsar prestamo: %s", str(e))
            raise Exception(f"Error al reembolsar prestamo: {e}")

    def liquidar_garantia(self, direccion_prestamista, clave_privada, direccion_prestatario, prestamo_id):
        """
            Ejecuta la liquidación de la garantía asociada a un préstamo específico en caso de incumplimiento
            por parte del prestatario.

            Parámetros:
            - direccion_prestamista: La dirección Ethereum del prestamista que está iniciando la liquidación.
            - clave_privada: La clave privada del prestamista para firmar la transacción.
            - direccion_prestatario: La dirección Ethereum del prestatario cuya garantía se va a liquidar.
            - prestamo_id: El identificador del préstamo asociado a la garantía a liquidar.

            Retorna:
            Un recibo de la transacción formateado que proporciona detalles sobre el resultado de la transacción,
            incluyendo el éxito o fracaso de la misma.

            Excepciones:
            - ValueError: Se lanza si la dirección del prestatario no es válida.
            - Exception: Captura y maneja cualquier otro error que pueda ocurrir durante el proceso de la transacción.
        """
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
        """
            Convierte un código numérico de estado de préstamo en una descripción textual legible.

            Esta función se utiliza para traducir los códigos de estado almacenados en la blockchain
            o en la base de datos del contrato inteligente, que suelen ser números, en términos comprensibles
            para los humanos. Esto facilita la interpretación del estado actual de un préstamo por parte
            de los usuarios o en la interfaz de usuario de una aplicación.

            Parámetros:
            - estado: El código numérico del estado del préstamo que se desea traducir.

            Retorna:
            Una cadena de texto que describe el estado del préstamo. Si el código de estado no
            se reconoce, retorna 'Desconocido'.
        """
        return ESTADOS_PRESTAMO.get(estado, 'Desconocido')
    
    def obtener_prestamos_por_prestatario(self, direccion_prestatario):
        """
            Recupera todos los préstamos asociados con un prestatario específico y los formatea para una fácil lectura.

            Parámetros:
            - direccion_prestatario: La dirección Ethereum del prestatario cuyos préstamos se quieren consultar.

            Retorna:
            Una lista de diccionarios que representan los detalles de cada préstamo asociado al prestatario.
            Cada diccionario contiene el id del préstamo, el monto en ether, el plazo del préstamo, la fecha de inicio,
            y el estado actual del préstamo.

            Excepciones:
            - ValueError: Se lanza si la dirección del prestatario no es válida.
            - Exception: Captura y maneja cualquier otro error que pueda ocurrir durante la recuperación de los préstamos.
        """
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
        """
            Obtiene los detalles completos de un préstamo específico asociado con un prestatario.

            Parámetros:
            - direccion_prestatario: La dirección Ethereum del prestatario asociado al préstamo.
            - prestamo_id: El identificador único del préstamo cuyos detalles se desean obtener.

            Retorna:
            Un diccionario que contiene los detalles del préstamo, incluyendo ID, prestatario, monto, plazo,
            fecha de solicitud, fecha límite y estado. Si el préstamo no se encuentra, puede retornar None o un diccionario vacío.

            Excepciones:
            - ValueError: Se lanza si la dirección del prestatario no es válida o si el ID del préstamo no es positivo.
            - Exception: Captura y reporta cualquier otro error que pueda ocurrir durante la consulta.
        """
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
      