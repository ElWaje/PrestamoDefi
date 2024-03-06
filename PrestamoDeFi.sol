// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PrestamoDeFi {
    address payable public socioPrincipal;

    enum EstadoPrestamo { Pendiente, Aprobado, Reembolsado, Liquidado }

    struct Prestamo {
        uint256 id;
        address prestatario;
        uint256 monto;
        uint256 plazo;
        uint256 tiempoSolicitud;
        uint256 tiempoLimite;
        EstadoPrestamo estado;
    }
    
    struct Cliente {
        bool activado;
        uint256 saldoGarantia;
        mapping(uint256 => Prestamo) prestamos;
        uint256[] prestamoIds;
    }
    
    mapping(address => Cliente) public clientes;
    mapping(address => bool) public empleadosPrestamista;

    event SolicitudPrestamo(address indexed prestatario, uint256 monto, uint256 plazo);
    event PrestamoAprobado(address indexed prestatario, uint256 monto);
    event PrestamoReembolsado(address indexed prestatario, uint256 monto);
    event GarantiaLiquidada(address indexed prestatario, uint256 monto);

    modifier soloSocioPrincipal() {
        require(msg.sender == socioPrincipal, "Operacion exclusiva del socio principal.");
        _;
    }

    modifier soloEmpleadoPrestamista() {
        require(empleadosPrestamista[msg.sender], "Operacion exclusiva de empleados prestamistas.");
        _;
    }

    modifier soloClienteRegistrado() {
        require(clientes[msg.sender].activado, "El cliente no esta registrado.");
        _;
    }

    constructor() {
        socioPrincipal = payable(msg.sender);
        empleadosPrestamista[msg.sender] = true;
    }

    function altaPrestamista(address nuevoPrestamista) public soloSocioPrincipal {
        require(!empleadosPrestamista[nuevoPrestamista], "El prestamista ya esta registrado.");
        empleadosPrestamista[nuevoPrestamista] = true;
    }

    function altaCliente(address nuevoCliente) public soloEmpleadoPrestamista {        
        require(!empleadosPrestamista[nuevoCliente], "Un empleado no puede ser cliente.");
        require(!clientes[nuevoCliente].activado, "El cliente ya esta registrado.");
        clientes[nuevoCliente].activado = true;
        clientes[nuevoCliente].saldoGarantia = 0;
    }

    function depositarGarantia() public payable soloClienteRegistrado {
        clientes[msg.sender].saldoGarantia += msg.value;
    }

        // Función para permitir al socio principal depositar fondos en el contrato
    function depositarFondos() public payable soloSocioPrincipal {
        require(msg.value > 0, "Debe depositar una cantidad de Ether positiva.");
        // El Ether enviado se añade automáticamente al balance del contrato.
    }

    function solicitarPrestamo(uint256 monto, uint256 plazo) public soloClienteRegistrado returns (uint256) {
        require(clientes[msg.sender].saldoGarantia >= monto, "Saldo de garantia insuficiente para el monto solicitado.");
        uint256 nuevoId = clientes[msg.sender].prestamoIds.length + 1;
            
        Prestamo storage nuevoPrestamo = clientes[msg.sender].prestamos[nuevoId];
        nuevoPrestamo.id = nuevoId;
        nuevoPrestamo.prestatario = msg.sender;
        nuevoPrestamo.monto = monto;
        nuevoPrestamo.plazo = plazo;
        nuevoPrestamo.tiempoSolicitud = block.timestamp;
        nuevoPrestamo.estado = EstadoPrestamo.Pendiente;

        clientes[msg.sender].prestamoIds.push(nuevoId);

        emit SolicitudPrestamo(msg.sender, monto, plazo);

        return nuevoId;
    }

    function aprobarPrestamo(address prestatario, uint256 id) public soloEmpleadoPrestamista {
        require(id > 0 && id <= clientes[prestatario].prestamoIds.length, "ID de prestamo invalido.");
        Prestamo storage prestamo = clientes[prestatario].prestamos[id];
        require(prestamo.estado == EstadoPrestamo.Pendiente, "El prestamo no esta pendiente de aprobacion.");

        prestamo.estado = EstadoPrestamo.Aprobado;
        prestamo.tiempoLimite = block.timestamp + prestamo.plazo;
            
        // Transferir el monto del préstamo del contrato al prestatario
        payable(prestatario).transfer(prestamo.monto);

        emit PrestamoAprobado(prestatario, prestamo.monto);
    }

    function reembolsarPrestamo(uint256 id) public payable soloClienteRegistrado {
        require(id > 0 && id <= clientes[msg.sender].prestamoIds.length, "ID de prestamo invalido.");            
        Prestamo storage prestamo = clientes[msg.sender].prestamos[id];
        require(msg.value == prestamo.monto, "El monto a reembolsar no coincide con el monto del prestamo.");        
        require(prestamo.estado == EstadoPrestamo.Aprobado, "El prestamo no esta aprobado o ya fue manejado.");
        require(prestamo.tiempoLimite >= block.timestamp, "El tiempo para reembolsar ha expirado.");

        prestamo.estado = EstadoPrestamo.Reembolsado;
        
        // Transferir el monto del préstamo al socio principal
        socioPrincipal.transfer(msg.value);

        emit PrestamoReembolsado(msg.sender, prestamo.monto);
    }

    function liquidarGarantia(address prestatario, uint256 id) public soloEmpleadoPrestamista {
        require(id > 0 && id <= clientes[prestatario].prestamoIds.length, "ID de prestamo invalido.");
        Prestamo storage prestamo = clientes[prestatario].prestamos[id];
        require(prestamo.estado == EstadoPrestamo.Aprobado, "El prestamo no esta aprobado o ya fue manejado.");
        require(prestamo.tiempoLimite < block.timestamp, "El tiempo limite para el prestamo aun no ha expirado.");
        // Asegurarse de que hay suficiente garantía para cubrir el monto del préstamo
        require(clientes[prestatario].saldoGarantia >= prestamo.monto, "Garantia insuficiente.");

        prestamo.estado = EstadoPrestamo.Liquidado;
            
        // Transferir el monto del préstamo al socio principal
        socioPrincipal.transfer(prestamo.monto);

        // Actualizar el saldo de garantía del cliente
        clientes[prestatario].saldoGarantia -= prestamo.monto;

        emit GarantiaLiquidada(prestatario, prestamo.monto);
    }

    function obtenerPrestamosPorPrestatario(address prestatario) public view returns (uint256[] memory) {
        return clientes[prestatario].prestamoIds;
    }

    function obtenerDetalleDePrestamo(address prestatario, uint256 id) public view returns (Prestamo memory) {
        require(id > 0 && id <= clientes[prestatario].prestamoIds.length, "ID de prestamo invalido.");
        return clientes[prestatario].prestamos[id];
    }
    
    // Función para solicitar la devolución de la garantía
    function solicitarDevolucionGarantia() public soloClienteRegistrado {
        Cliente storage cliente = clientes[msg.sender];
        require(cliente.saldoGarantia > 0, "No hay garantia para devolver.");

        // Verificar que el cliente no tenga préstamos aprobados sin reembolsar o liquidar
        for (uint i = 0; i < cliente.prestamoIds.length; i++) {
            Prestamo storage prestamo = cliente.prestamos[cliente.prestamoIds[i]];
            require(prestamo.estado != EstadoPrestamo.Aprobado, "Existen prestamos aprobados sin reembolsar o liquidar.");
        }

        // Devolver la garantía al cliente
        uint256 montoGarantia = cliente.saldoGarantia;
        cliente.saldoGarantia = 0;
        payable(msg.sender).transfer(montoGarantia);
    }
        
}
