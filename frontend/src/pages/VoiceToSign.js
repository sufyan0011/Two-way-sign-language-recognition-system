import React, { useState, useEffect } from 'react';
import "bootstrap/dist/css/bootstrap.min.css";
import GIF from "gif.js/dist/gif";

const VoiceToSign = () => {
  const [isListening, setIsListening] = useState(false);
  const [images, setImages] = useState([]);
  const [gifUrl, setGifUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [gifCreated, setGifCreated] = useState(false);
  const [transcribedText, setTranscribedText] = useState("");
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

  useEffect(() => {
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setTranscribedText(transcript);
      handleVoiceInput(transcript);
    };

    recognition.onerror = (event) => {
      setError("Error occurred in recognition: " + event.error);
      setIsListening(false);
    };
  }, []);

  const handleVoiceInput = async (text) => {
    setLoading(true);
    try {
      const response = await fetch("http://10.91.53.106:5002/process-speech", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) throw new Error("HTTP error! status: ${response.status}");
      
      const data = await response.json();
      const filteredImages = data.translated_signs.filter(img => 
        img && img.startsWith("data:image")
      );

      if (filteredImages.length === 0) throw new Error("No valid images found");
      
      setImages(filteredImages);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleListening = () => {
    if (isListening) {
      recognition.stop();
    } else {
      setImages([]);
      setGifUrl("");
      setTranscribedText("");
      recognition.start();
    }
    setIsListening(!isListening);
  };

  const handleCreateGif = () => {
    setLoading(true);
    const gif = new GIF({
      workers: 2,
      quality: 10,
      width: 500,
      height: 500,
      workerScript: "/gif.worker.js"
    });

    let loadedCount = 0;

    images.forEach((dataUrl) => {
      const img = new Image();
      img.src = dataUrl;
      img.onload = () => {
        gif.addFrame(img, { delay: 1000 });
        if (++loadedCount === images.length) gif.render();
      };
    });

    gif.on("finished", (blob) => {
      setGifUrl(URL.createObjectURL(blob));
      setGifCreated(true);
      setLoading(false);
    });
  };

  return (
    <div className="d-flex flex-column chat-background w-100" style={{ backgroundColor: "#e6e6e6", /* Light gray for WhatsApp-like feel */
      backgroundImage: 'url("https://www.transparenttextures.com/patterns/inspiration-geometry.png")', 
      backgroundRepeat: "repeat",
      backgroundSize: "contain",
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column" }}>
    <div className="container text-center mt-5" style={{ minHeight: "75vh" }}>
      <h1 className="mb-4">Voice to Sign Language Converter</h1>
      
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="card">
            <div className="card-body">
              <button 
                className={`btn btn-${isListening ? 'danger' : 'primary'} mb-3`}
                onClick={toggleListening}
              >
                {isListening ? 'Stop Recording' : 'Start Voice Input'}
              </button>

              {transcribedText && (
                <div className="alert alert-info">
                  Transcribed Text: {transcribedText}
                </div>
              )}

              {error && <div className="alert alert-danger">{error}</div>}

              {images.length > 0 && (
                <div className="mt-4">
                  <h4>Sign Language Translation</h4>
                  <div className="row row-cols-2 row-cols-md-4 g-2 mt-2">
                    {images.map((img, index) => (
                      <div className="col" key={index}>
                        <img
                          src={img}
                          alt={"Sign ${index}"}
                          className="img-thumbnail"
                          style={{ maxWidth: "170px" }}
                        />
                      </div>
                    ))}
                  </div>

                  {!gifCreated && (
                    <button
                      className="btn btn-success mt-3"
                      onClick={handleCreateGif}
                      disabled={loading}
                    >
                      {loading ? "Creating GIF..." : "Create GIF"}
                    </button>
                  )}

                  {gifUrl && (
                    <div className="mt-3">
                      <h5>Generated GIF</h5>
                      <img
                          src={gifUrl}
                          alt="Sign language GIF"
                          className="img-fluid mb-2"
                          style={{
                            width: "100%",
                            maxWidth: "400px",
                            height: "auto",
                          }}
                        />
                      <div>
                        <a
                          href={gifUrl}
                          download="sign-language.gif"
                          className="btn btn-primary"
                        >
                          Download GIF
                        </a>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  );
};

export default VoiceToSign;