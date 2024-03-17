
from PrestamoDeFi import (
    alta_prestamista, alta_cliente, depositar_garantia, solicitar_prestamo,
    aprobar_prestamo, reembolsar_prestamo, liquidar_garantia,
    obtener_prestamos_por_prestatario, obtener_detalle_de_prestamo, get_web3
)
from getpass import getpass

web3 = get_web3()

def solicitar_credenciales_usuario():
    direccion = input("Ingrese su dirección Ethereum: ")
    while not web3.is_address(direccion):
        print("La dirección ingresada no es válida. Por favor, intente de nuevo.")
        direccion = input("Ingrese su dirección Ethereum: ")
    clave_privada = getpass("Ingrese su clave privada (la entrada será oculta): ")
    print("Clave privada capturada con éxito.")
    return direccion, clave_privada

def validar_entrada(mensaje, tipo='string'):
    entrada = input(mensaje)
    if tipo == 'ether':
        try:
            entrada = web3.to_wei(float(entrada), 'ether')
        except ValueError:
            print("Entrada inválida. Por favor, ingrese un número.")
            return None
    elif tipo == 'int':
        try:
            entrada = int(entrada)
        except ValueError:
            print("Entrada inválida. Por favor, ingrese un número entero.")
            return None
    return entrada

def handle_alta_prestamista(direccion_usuario, clave_privada_usuario):
    nueva_direccion = input("Dirección del nuevo prestamista: ")
    if web3.is_address(nueva_direccion):
        try:
            resultado = alta_prestamista(direccion_usuario, clave_privada_usuario, nueva_direccion)
            print(resultado)
        except Exception as e:
            print(f"Se produjo un error al intentar dar de alta un prestamista: {e}")
    else:
        print("Dirección inválida.")

def handle_alta_cliente(direccion_usuario, clave_privada_usuario):
    nueva_direccion = input("Dirección del nuevo cliente: ")
    if web3.is_address(nueva_direccion):
        try:
            resultado = alta_cliente(direccion_usuario, clave_privada_usuario, nueva_direccion)
            print(resultado)
        except Exception as e:
            print(f"Se produjo un error al intentar dar de alta un cliente: {e}")
    else:
        print("Dirección inválida.")

def handle_depositar_garantia(direccion_usuario, clave_privada_usuario):
    valor = validar_entrada("Valor a depositar en Ether: ", 'ether')                
    if valor is not None:
        try:
            resultado = depositar_garantia(direccion_usuario, clave_privada_usuario, valor)
            print(resultado)
        except Exception as e:
            print(f"Se produjo un error al intentar depositar garantía: {e}")
    else:
        print("Debe ingresar un valor válido.")

def handle_solicitar_prestamo(direccion_usuario, clave_privada_usuario):
    monto = validar_entrada("Monto del préstamo en Ether: ", 'ether')
    plazo = validar_entrada("Plazo del préstamo en segundos: ", 'int')
    if monto is not None and plazo is not None:
        try:
            resultado = solicitar_prestamo(direccion_usuario, clave_privada_usuario, monto, plazo)
            print(resultado)
        except Exception as e:
            print(f"Se produjo un error al intentar solicitar un préstamo: {e}")
    else:
        print("Datos inválidos.")

def handle_aprobar_prestamo(direccion_usuario, clave_privada_usuario):
    prestatario = input("Dirección del prestatario: ")
    id_prestamo = validar_entrada("ID del préstamo: ", 'int')
    if web3.is_address(prestatario) and id_prestamo is not None:
        try:
            resultado = aprobar_prestamo(direccion_usuario, clave_privada_usuario, prestatario, id_prestamo)
            print(resultado)
        except Exception as e:
            print(f"Se produjo un error al intentar aprobar un préstamo: {e}")
    else:
        print("Datos inválidos.")

def handle_reembolsar_prestamo(direccion_usuario, clave_privada_usuario):
    id_prestamo = validar_entrada("ID del préstamo a reembolsar: ", 'int')
    valor = validar_entrada("Valor del reembolso en Ether: ", 'ether')
    if id_prestamo is not None and valor is not None:
        try:
            resultado = reembolsar_prestamo(direccion_usuario, clave_privada_usuario, id_prestamo, valor)
            print(resultado)
        except Exception as e:
            print(f"Se produjo un error al intentar reembolsar un préstamo: {e}")
    else:
        print("Datos inválidos.")

def handle_liquidar_garantia(direccion_usuario, clave_privada_usuario):
    prestatario = input("Dirección del prestatario cuya garantía se va a liquidar: ")
    id_prestamo = validar_entrada("ID del préstamo cuya garantía se va a liquidar: ", 'int')
    if web3.is_address(prestatario) and id_prestamo is not None:
        try:
            resultado = liquidar_garantia(direccion_usuario, clave_privada_usuario, prestatario, id_prestamo)
            print(resultado)
        except Exception as e:
            print(f"Se produjo un error al intentar liquidar una garantía: {e}")
    else:
        print("Datos inválidos.")

def handle_obtener_prestamos_por_prestatario(direccion_usuario):
    prestatario = input("Dirección del prestatario: ")
    if web3.is_address(prestatario):
        try:
            resultado = obtener_prestamos_por_prestatario(prestatario)
            print(resultado)
        except Exception as e:
            print(f"Se produjo un error al intentar obtener los préstamos por prestatario: {e}")
    else:
        print("Dirección inválida.")

def handle_obtener_detalle_de_prestamo(direccion_usuario):
    prestatario = input("Dirección del prestatario: ")
    id_prestamo = validar_entrada("ID del préstamo: ", 'int')
    if web3.is_address(prestatario) and id_prestamo is not None:
        try:
            resultado = obtener_detalle_de_prestamo(prestatario, id_prestamo)
            print(resultado)
        except Exception as e:
            print(f"Se produjo un error al intentar obtener el detalle de un préstamo: {e}")
    else:
        print("Datos inválidos.")

def main_menu():
    while True:
        print("\nMenú Principal:")
        print("1. Alta de Prestamista")
        print("2. Alta de Cliente")
        print("3. Depositar Garantía")
        print("4. Solicitar Préstamo")
        print("5. Aprobar Préstamo")
        print("6. Reembolsar Préstamo")
        print("7. Liquidar Garantía")
        print("8. Obtener Préstamos por Prestatario")
        print("9. Obtener Detalle de Préstamo")
        print("0. Salir")

        opcion = input("Seleccione una opción: ")
        if opcion == '0':
            
            print("¡Hasta la próxima aventura financiera! ") 
            print(" Enrique Solís ")
            break

        direccion_usuario, clave_privada_usuario = solicitar_credenciales_usuario()

        try:
            if opcion == '1':
                handle_alta_prestamista(direccion_usuario, clave_privada_usuario)
            elif opcion == '2':
                handle_alta_cliente(direccion_usuario, clave_privada_usuario)
            elif opcion == '3':
                handle_depositar_garantia(direccion_usuario, clave_privada_usuario)
            elif opcion == '4':
                handle_solicitar_prestamo(direccion_usuario, clave_privada_usuario)
            elif opcion == '5':
                handle_aprobar_prestamo(direccion_usuario, clave_privada_usuario)
            elif opcion == '6':
                handle_reembolsar_prestamo(direccion_usuario, clave_privada_usuario)
            elif opcion == '7':
                handle_liquidar_garantia(direccion_usuario, clave_privada_usuario)
            elif opcion == '8':
                handle_obtener_prestamos_por_prestatario(direccion_usuario)
            elif opcion == '9':
                handle_obtener_detalle_de_prestamo(direccion_usuario)
            else:
                print("Opción inválida. Por favor, intente de nuevo.")
        except Exception as e:
            print(f"Error al procesar la solicitud: {e}")

if __name__ == "__main__":
    main_menu()
    
