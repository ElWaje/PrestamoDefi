from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow
from BlockchainManager import BlockchainManager

def main():
    app = QApplication([])
    blockchainManager = BlockchainManager(ganache_url="http://127.0.0.1:7545", contract_address="0x25238d7855c60436DA77483CDEDB037291958023")
    window = MainWindow(blockchainManager)
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()