// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PrestamoDeFiBM {
    address public socioPrincipal;
    mapping(address => Cliente) public clientes;
    mapping(address => bool) public empleadosPrestamista;

    struct Prestamo {
        uint256 id;
        address prestatario;
        uint256 monto;
        uint256 plazo;
        uint256 tiempoSolicitud;
        uint256 tiempoLimite;
        bool aprobado;
        bool reembolsado;
        bool liquidado;
    }

    struct Cliente {
        bool activado;
        uint256 saldoGarantia;
        mapping(uint256 => Prestamo) prestamos;
        uint256[] prestamoIds;
    }

    // Eventos
    event SolicitudPrestamo(address indexed prestatario, uint256 monto, uint256 plazo);
    event PrestamoAprobado(address indexed prestatario, uint256 monto);
    event PrestamoReembolsado(address indexed prestatario, uint256 monto);
    event GarantiaLiquidada(address indexed prestatario, uint256 monto);

    // Modificadores
    modifier soloSocioPrincipal() {
        require(msg.sender == socioPrincipal, "Solo el socio principal puede ejecutar esta accion.");
        _;
    }

    modifier soloEmpleadoPrestamista() {
        require(empleadosPrestamista[msg.sender], "Solo un empleado prestamista puede ejecutar esta accion.");
        _;
    }

    modifier soloClienteRegistrado() {
        require(clientes[msg.sender].activado, "Solo un cliente registrado puede ejecutar esta accion.");
        _;
    }

    // Constructor
    constructor() {
        socioPrincipal = msg.sender;
        empleadosPrestamista[msg.sender] = true;
    }

    function altaPrestamista(address nuevoPrestamista) public soloSocioPrincipal {
        require(!empleadosPrestamista[nuevoPrestamista], "El prestamista ya esta dado de alta.");
        empleadosPrestamista[nuevoPrestamista] = true;
    }

    function altaCliente(address nuevoCliente) public soloEmpleadoPrestamista {
        require(!clientes[nuevoCliente].activado, "El cliente ya esta dado de alta.");
        clientes[nuevoCliente].activado = true;
        clientes[nuevoCliente].saldoGarantia = 0;
    }

    function depositarGarantia() public payable soloClienteRegistrado {
        require(msg.value > 0, "El monto a depositar debe ser mayor a 0.");
        clientes[msg.sender].saldoGarantia += msg.value;
    }

    function solicitarPrestamo(uint256 monto_, uint256 plazo_) public soloClienteRegistrado returns (uint256) {
        require(clientes[msg.sender].saldoGarantia >= monto_, "Saldo de garantia insuficiente.");
        uint256 nuevoId = clientes[msg.sender].prestamoIds.length + 1;
        
        Prestamo storage nuevoPrestamo = clientes[msg.sender].prestamos[nuevoId];
        nuevoPrestamo.id = nuevoId;
        nuevoPrestamo.prestatario = msg.sender;
        nuevoPrestamo.monto = monto_;
        nuevoPrestamo.plazo = plazo_;
        nuevoPrestamo.tiempoSolicitud = block.timestamp;
        nuevoPrestamo.aprobado = false;
        nuevoPrestamo.reembolsado = false;
        nuevoPrestamo.liquidado = false;
        
        clientes[msg.sender].prestamoIds.push(nuevoId);
        
        emit SolicitudPrestamo(msg.sender, monto_, plazo_);
        
        return nuevoId;
    }

    function aprobarPrestamo(address prestatario_, uint256 id_) public soloEmpleadoPrestamista {
        Cliente storage prestatario = clientes[prestatario_];
        require(id_ > 0 && id_ <= prestatario.prestamoIds.length, "ID de prestamo no valido.");
        Prestamo storage prestamo = prestatario.prestamos[id_];
        require(!prestamo.aprobado, "El prestamo ya fue aprobado.");
        require(!prestamo.reembolsado, "El prestamo ya fue reembolsado.");
        require(!prestamo.liquidado, "El prestamo ya fue liquidado.");

        prestamo.aprobado = true;
        prestamo.tiempoLimite = block.timestamp + prestamo.plazo;

        emit PrestamoAprobado(prestatario_, prestamo.monto);
    }

    function reembolsarPrestamo(uint256 id_) public soloClienteRegistrado payable {
        Cliente storage prestatario = clientes[msg.sender];
        require(id_ > 0 && id_ <= prestatario.prestamoIds.length, "ID de prestamo no valido.");
        Prestamo storage prestamo = prestatario.prestamos[id_];
        require(prestamo.prestatario == msg.sender, "Solo el prestatario puede reembolsar el prestamo.");
        require(prestamo.aprobado, "El prestamo no ha sido aprobado.");
        require(!prestamo.reembolsado, "El prestamo ya ha sido reembolsado.");
        require(!prestamo.liquidado, "El prestamo ya ha sido liquidado.");
        require(prestamo.tiempoLimite >= block.timestamp, "El plazo del prestamo ha vencido.");
        require(prestatario.saldoGarantia >= prestamo.monto, "Saldo de garantia insuficiente para cubrir el prestamo.");

        prestatario.saldoGarantia -= prestamo.monto;
        payable(socioPrincipal).transfer(prestamo.monto);
        prestamo.reembolsado = true;

        emit PrestamoReembolsado(msg.sender, prestamo.monto);
    }

    function liquidarGarantia(address prestatario_, uint256 id_) public soloEmpleadoPrestamista {
        Cliente storage prestatario = clientes[prestatario_];
        require(id_ > 0 && id_ <= prestatario.prestamoIds.length, "ID de prestamo no valido.");
        Prestamo storage prestamo = prestatario.prestamos[id_];
        require(prestamo.aprobado, "El prestamo no ha sido aprobado.");
        require(!prestamo.reembolsado, "El prestamo ya ha sido reembolsado.");
        require(!prestamo.liquidado, "El prestamo ya ha sido liquidado.");
        require(prestamo.tiempoLimite < block.timestamp, "El plazo del prestamo no ha vencido.");
        require(prestatario.saldoGarantia >= prestamo.monto, "Saldo de garantia insuficiente para cubrir el prestamo.");

        prestatario.saldoGarantia -= prestamo.monto;
        payable(socioPrincipal).transfer(prestamo.monto);
        prestamo.liquidado = true;

        emit GarantiaLiquidada(prestatario_, prestamo.monto);
    }

    function obtenerPrestamosPorPrestatario(address prestatario_) public view returns (uint256[] memory) {
        return clientes[prestatario_].prestamoIds;
    }

    function obtenerDetalleDePrestamo(address prestatario_, uint256 id_) public view returns (Prestamo memory) {
        require(id_ > 0 && id_ <= clientes[prestatario_].prestamoIds.length, "ID de prestamo no valido.");
        return clientes[prestatario_].prestamos[id_];
    }
}