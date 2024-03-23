from web3 import Web3
import logging

def ether_to_wei(amount_in_ether):
    """Convierte un valor de Ether a Wei."""
    return Web3.to_wei(amount_in_ether, 'ether')

def wei_to_ether(amount_in_wei):
    """Convierte un valor de Wei a Ether."""
    return Web3.from_wei(amount_in_wei, 'ether')

def is_valid_ethereum_address(address):
    """Valida si la dirección proporcionada es una dirección de Ethereum válida."""
    return Web3.is_address(address)

def format_transaction_receipt(receipt):
    """Formatea y devuelve información relevante de un recibo de transacción."""
    return {
        'transactionHash': receipt['transactionHash'].hex() if not isinstance(receipt['transactionHash'], str) else receipt['transactionHash'],
        'blockHash': receipt['blockHash'].hex() if not isinstance(receipt['blockHash'], str) else receipt['blockHash'],
        'blockNumber': receipt['blockNumber'],
        'from': receipt['from'],
        'to': receipt.get('to'),
        'gasUsed': receipt['gasUsed'],
        'status': 'Succeeded' if receipt['status'] == 1 else 'Failed',
        'cumulativeGasUsed': receipt['cumulativeGasUsed'],
        'contractAddress': receipt.get('contractAddress'),
        'logs': receipt['logs'],
    }
def log_transaction_receipt(receipt):
    """Registra detalles de un recibo de transacción para depuración o información."""
    if receipt.status == 1:
        logging.info(f"Transacción exitosa: Hash {receipt.transactionHash.hex()}, Gas Usado {receipt.gasUsed}")
    else:
        logging.error(f"Transacción fallida: Hash {receipt.transactionHash.hex()}, Gas Usado {receipt.gasUsed}")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
