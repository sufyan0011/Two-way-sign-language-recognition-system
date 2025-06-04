import React, { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import GIF from "gif.js/dist/gif";

const TextToSign = () => {
  const [inputText, setInputText] = useState("");
  const [images, setImages] = useState([]);
  const [gifUrl, setGifUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [gifCreated, setGifCreated] = useState(false);

  const fetchSignImages = async () => {
    setLoading(true);
    setError("");
    setImages([]);
    setGifUrl("");
    setGifCreated(false);

    try {
      const response = await fetch("http://10.91.53.106:5001/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: inputText }),
      });

      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      const filteredImages = data.translated_signs.filter(
        (img) => img && img.startsWith("data:image")
      );

      if (filteredImages.length === 0) throw new Error("No valid images found");

      setImages(filteredImages);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGif = () => {
    setLoading(true);
    setError("");

    try {
      const gif = new GIF({
        workers: 2,
        quality: 10,
        width: 500,
        height: 500,
        workerScript: "/gif.worker.js",
      });

      let loadedCount = 0;

      images.forEach((dataUrl) => {
        const img = new Image();
        img.src = dataUrl;
        img.crossOrigin = "Anonymous";

        img.onload = () => {
          gif.addFrame(img, { delay: 1000 });
          loadedCount++;

          if (loadedCount === images.length) {
            gif.render();
          }
        };

        img.onerror = () => {
          loadedCount++;
          if (loadedCount === images.length) {
            gif.render();
          }
        };
      });

      gif.on("finished", (blob) => {
        setGifUrl(URL.createObjectURL(blob));
        setGifCreated(true);
        setLoading(false);
      });
    } catch (e) {
      setError("GIF creation failed: " + e.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      if (gifUrl) URL.revokeObjectURL(gifUrl);
    };
  }, [gifUrl]);

  return (
    <div
      className="container-fluid py-5 flex-grow-1 d-flex flex-column justify-content-center"
      style={{
        backgroundColor: "#e6e6e6",
        backgroundImage:
          'url("https://www.transparenttextures.com/patterns/inspiration-geometry.png")',
        backgroundRepeat: "repeat",
        backgroundSize: "contain",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div className="container text-center">
        <h1 className="mb-4">Text to Sign Language Converter</h1>
        <div className="row justify-content-center">
          <div className="col-12 col-md-8">
            <div className="card shadow p-3">
              <div className="card-body">
                <div className="input-group mb-3">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Enter text to translate..."
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                  />
                  <button
                    className="btn btn-primary"
                    onClick={fetchSignImages}
                    disabled={loading || !inputText.trim()}
                  >
                    {loading ? "Loading..." : "Convert to Sign"}
                  </button>
                </div>
                {error && <div className="alert alert-danger">{error}</div>}
                {images.length > 0 ? (
                  <div className="mt-4">
                    <h4>Sign Language Translation</h4>
                    <div className="row row-cols-2 row-cols-md-4 g-2 mt-2">
                      {images.map((img, index) => (
                        <div className="col" key={index}>
                          <img
                            src={img}
                            alt={`Sign ${index}`}
                            className="img-fluid img-thumbnail"
                            style={{ width: "100%", height: "auto" }}
                          />
                        </div>
                      ))}
                    </div>
                    {!gifCreated && (
                      <button
                        className="btn btn-success mt-3"
                        onClick={handleCreateGif}
                        disabled={loading || images.length === 0}
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
                ) : (
                  <div className="text-center">
                    <img
                      src="72631756_9756520.jpg"
                      alt="Placeholder"
                      className="img-fluid"
                      style={{
                        width: "100%",
                        maxWidth: "400px",
                        height: "auto",
                      }}
                    />
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

export default TextToSign;
