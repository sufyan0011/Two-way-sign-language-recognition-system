import React from "react";

const Home = () => {
  const backgroundStyle = {
    backgroundImage: "url('/background.webp')",
    backgroundSize: "cover",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
    height: "100vh",
    width: "100%",
    position: "relative",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "white",
  };

  const overlayStyle = {
    position: "absolute",
    top: 0,
    left: 0,
    height: "100%",
    width: "100%",
    backgroundColor: "rgba(0, 0, 0, 0.5)", // Semi-transparent dark overlay
  };

  const contentStyle = {
    position: "relative",
    zIndex: 2,
    textAlign: "center",
    maxWidth: "1000px",
  };

  return (
    <div className="img-fluid" style={backgroundStyle}>
      <div style={overlayStyle}></div>
      <div style={contentStyle}>
        <h1 className="fw-bold" style={{ textShadow: "2px 2px 4px rgba(0,0,0,0.6)" }}>
          Welcome to the Sign Language Detection System
        </h1>
        <p className="lead text-center fw-normal">
          Detect and interpret sign language gestures with ease using our advanced system.
        </p>
        <div className="mt-4">
          <a
            href="/sign-to-text"
            className="btn btn-lg btn-dark px-4 py-2 rounded-pill shadow"
          >
            <i className="fas fa-hand-paper mr-2"></i> Start Sign To Text Detection
          </a>
        </div>
      </div>
    </div>
  );
};

export default Home;
