// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract PrestamoDeFi {
    address public socioPrincipal;
    mapping(address => Cliente) public clientes;
    mapping(address => bool) public empleadosPrestamista;

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

    // Eventos
    event SolicitudPrestamo(address indexed prestatario, uint256 monto, uint256 plazo);
    event CambioEstadoPrestamo(address indexed prestatario, uint256 indexed id, EstadoPrestamo estado, uint256 monto);

    // Modificadores
    modifier soloSocioPrincipal() {
        require(msg.sender == socioPrincipal, "No estas autorizado para realizar esta operacion");
        _;
    }

    modifier soloEmpleadoPrestamista() {
        require(empleadosPrestamista[msg.sender], "No tienes el rol de prestamista");
        _;
    }

    modifier soloClienteRegistrado() {
        require(clientes[msg.sender].activado, "No estas registrado como cliente");
        _;
    }

    // Constructor
    constructor() {
        socioPrincipal = msg.sender;
        empleadosPrestamista[socioPrincipal] = true;
    }

    function altaPrestamista(address nuevoPrestamista) public soloSocioPrincipal {
        require(!empleadosPrestamista[nuevoPrestamista], "El prestamista ya esta dado de alta");
        empleadosPrestamista[nuevoPrestamista] = true;
    }

    function altaCliente(address nuevoCliente) public soloEmpleadoPrestamista {
        require(!clientes[nuevoCliente].activado, "El cliente ya esta registrado");

        Cliente storage structNuevoCliente = clientes[nuevoCliente];
        structNuevoCliente.saldoGarantia = 0;
        structNuevoCliente.activado = true;
    }

    function depositarGarantia() public payable soloClienteRegistrado {
        clientes[msg.sender].saldoGarantia += msg.value;
    }

    function solicitarPrestamo(uint256 monto_, uint256 plazo_) public soloClienteRegistrado returns (uint256) {
        require(clientes[msg.sender].saldoGarantia >= monto_, "Saldo de garantia insuficiente");

        uint256 nuevoId = clientes[msg.sender].prestamoIds.length + 1;

        Prestamo storage nuevoPrestamo = clientes[msg.sender].prestamos[nuevoId];
        nuevoPrestamo.id = nuevoId;
        nuevoPrestamo.prestatario = msg.sender;
        nuevoPrestamo.monto = monto_;
        nuevoPrestamo.plazo = plazo_;
        nuevoPrestamo.tiempoSolicitud = block.timestamp;
        nuevoPrestamo.estado = EstadoPrestamo.Pendiente;

        clientes[msg.sender].prestamoIds.push(nuevoId);

        emit SolicitudPrestamo(msg.sender, monto_, plazo_);

        return nuevoId;
    }

    function aprobarPrestamo(address prestatario_, uint256 id_) public soloEmpleadoPrestamista {
        Cliente storage prestatario = clientes[prestatario_];
        require(id_ > 0 && id_ <= prestatario.prestamoIds.length, "ID de prestamo no valido");
        Prestamo storage prestamo = prestatario.prestamos[id_];
        require(prestamo.estado == EstadoPrestamo.Pendiente, "El prestamo no esta pendiente de aprobacion");
        
        
        require(prestatario.saldoGarantia >= prestamo.monto, "Garantia insuficiente para cubrir el prestamo");

        prestatario.saldoGarantia -= prestamo.monto;
        prestamo.estado = EstadoPrestamo.Aprobado;
        prestamo.tiempoLimite = block.timestamp + prestamo.plazo;

        emit CambioEstadoPrestamo(prestatario_, id_, EstadoPrestamo.Aprobado, prestamo.monto);
    }

    function reembolsarPrestamo(uint256 id) public soloClienteRegistrado {
        Prestamo storage prestamo = clientes[msg.sender].prestamos[id];
        require(prestamo.estado == EstadoPrestamo.Aprobado, "El prestamo no esta aprobado.");
        require(block.timestamp <= prestamo.tiempoLimite, "Tiempo de pago expirado.");

        // Ajusta el balance de la garantía del cliente sin realizar una transferencia de Ether.
        clientes[msg.sender].saldoGarantia += prestamo.monto;

        prestamo.estado = EstadoPrestamo.Reembolsado;
        emit CambioEstadoPrestamo(msg.sender, id, EstadoPrestamo.Reembolsado, prestamo.monto);
    }

    function liquidarGarantia(address prestatario_, uint256 id_) public soloEmpleadoPrestamista {
        Cliente storage prestatario = clientes[prestatario_];
        require(id_ > 0 && id_ <= prestatario.prestamoIds.length, "ID de prestamo no valido");
        Prestamo storage prestamo = prestatario.prestamos[id_];
        require(prestamo.estado == EstadoPrestamo.Aprobado, "El prestamo no esta aprobado");
        require(block.timestamp > prestamo.tiempoLimite, "Tiempo de pago no ha expirado");
                
        // Transferir el monto del préstamo desde la garantía del cliente al socio principal
        payable(socioPrincipal).transfer(prestamo.monto);

        prestamo.estado = EstadoPrestamo.Liquidado;

        emit CambioEstadoPrestamo(prestatario_, id_, EstadoPrestamo.Liquidado, prestamo.monto);
    }

    function obtenerPrestamosPorPrestatario(address prestatario_) public view returns (uint256[] memory) {
        return clientes[prestatario_].prestamoIds;
    }

    function obtenerDetalleDePrestamo(address prestatario_, uint256 id_) public view returns (Prestamo memory) {
        return clientes[prestatario_].prestamos[id_];
    }
    
}
