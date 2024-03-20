import React from "react";
import { Link } from "react-router-dom";

// Asumiendo que tienes un logo en tu proyecto
import logo from "../assets/logo.svg";

const Header = ({ onConnectWallet }) => {
  return (
    <header className="header">
      <div className="container">
        <Link to="/">
          <img src={logo} alt="Logo" className="logo" />
        </Link>
        <nav className="navbar">
          <ul>
            <li>
              <Link to="/">Inicio</Link>
            </li>
            <li>
              <Link to="/prestamos">Préstamos</Link>
            </li>
            <li>
              <Link to="/sobre-nosotros">Sobre Nosotros</Link>
            </li>
          </ul>
        </nav>
        <button onClick={onConnectWallet} className="connect-wallet-btn">
          Conectar Wallet
        </button>
      </div>
    </header>
  );
};

export default Header;
