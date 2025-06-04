import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";

const Footer = () => {
  return (
    <footer className="footer py-3 text-center bg-dark text-white">
      <p className="mb-2">© 2025 Created by Splash 10</p>
      <div className="d-flex justify-content-center gap-3">
      Linkedin of Contributors :
        <a href="https://www.linkedin.com/in/sufyan-waqar-khan-9905691b3/" target="_blank" rel="noopener noreferrer">
          <i className="fab fa-linkedin fa-lg text-white"></i>
        </a>
        <a href="https://www.linkedin.com/in/dharmik-patel-9a99a1206/" target="_blank" rel="noopener noreferrer">
          <i className="fab fa-linkedin fa-lg text-white"></i>
        </a>
        <a href="https://linkedin.com/in/krunal2206" target="_blank" rel="noopener noreferrer">
          <i className="fab fa-linkedin fa-lg text-white"></i>
        </a>
      </div>
    </footer>
  );
};

export default Footer;
