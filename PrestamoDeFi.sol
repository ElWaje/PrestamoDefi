
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PrestamoDeFi {
    address public socioPrincipal;

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
        require(msg.sender == socioPrincipal, "Operación exclusiva del socio principal.");
        _;
    }

    modifier soloEmpleadoPrestamista() {
        require(empleadosPrestamista[msg.sender], "Operación exclusiva de empleados prestamistas.");
        _;
    }

    modifier soloClienteRegistrado() {
        require(clientes[msg.sender].activado, "El cliente no está registrado.");
        _;
    }

    constructor() {
        socioPrincipal = msg.sender;
        empleadosPrestamista[msg.sender] = true;
    }

    function altaPrestamista(address nuevoPrestamista) public soloSocioPrincipal {
        require(!empleadosPrestamista[nuevoPrestamista], "El prestamista ya está registrado.");
        empleadosPrestamista[nuevoPrestamista] = true;
    }

    function altaCliente(address nuevoCliente) public soloEmpleadoPrestamista {
        require(!clientes[nuevoCliente].activado, "El cliente ya está registrado.");
        clientes[nuevoCliente].activado = true;
        clientes[nuevoCliente].saldoGarantia = 0;
    }

    function depositarGarantia() public payable soloClienteRegistrado {
        clientes[msg.sender].saldoGarantia += msg.value;
    }

    function solicitarPrestamo(uint256 monto, uint256 plazo) public soloClienteRegistrado returns (uint256) {
        require(clientes[msg.sender].saldoGarantia >= monto, "Saldo de garantía insuficiente para el monto solicitado.");
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
        require(id > 0 && id <= clientes[prestatario].prestamoIds.length, "ID de préstamo inválido.");
        Prestamo storage prestamo = clientes[prestatario].prestamos[id];
        require(prestamo.estado == EstadoPrestamo.Pendiente, "El préstamo no está pendiente de aprobación.");

        prestamo.estado = EstadoPrestamo.Aprobado;
        prestamo.tiempoLimite = block.timestamp + prestamo.plazo;

        emit PrestamoAprobado(prestatario, prestamo.monto);
    }

    function reembolsarPrestamo(uint256 id) public soloClienteRegistrado {
        require(id > 0 && id <= clientes[msg.sender].prestamoIds.length, "ID de préstamo inválido.");
        Prestamo storage prestamo = clientes[msg.sender].prestamos[id];
        require(prestamo.estado == EstadoPrestamo.Aprobado, "El préstamo no está aprobado o ya fue manejado.");
        require(prestamo.tiempoLimite >= block.timestamp, "El tiempo para reembolsar ha expirado.");

        prestamo.estado = EstadoPrestamo.Reembolsado;
        clientes[msg.sender].saldoGarantia -= prestamo.monto;

        emit PrestamoReembolsado(msg.sender, prestamo.monto);
    }

    function liquidarGarantia(address prestatario, uint256 id) public soloEmpleadoPrestamista {
        require(id > 0 && id <= clientes[prestatario].prestamoIds.length, "ID de préstamo inválido.");
        Prestamo storage prestamo = clientes[prestatario].prestamos[id];
        require(prestamo.estado == EstadoPrestamo.Aprobado, "El préstamo no está aprobado o ya fue manejado.");
        require(prestamo.tiempoLimite < block.timestamp, "El tiempo límite para el préstamo aún no ha expirado.");

        prestamo.estado = EstadoPrestamo.Liquidado;
        clientes[prestatario].saldoGarantia -= prestamo.monto;

        emit GarantiaLiquidada(prestatario, prestamo.monto);
    }

    function obtenerPrestamosPorPrestatario(address prestatario) public view returns (uint256[] memory) {
        return clientes[prestatario].prestamoIds;
    }

    function obtenerDetalleDePrestamo(address prestatario, uint256 id) public view returns (Prestamo memory) {
        require(id > 0 && id <= clientes[prestatario].prestamoIds.length, "ID de préstamo inválido.");
        return clientes[prestatario].prestamos[id];
    }
}
