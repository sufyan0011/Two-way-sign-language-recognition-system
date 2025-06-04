import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import SignToText from "./pages/SignToText";
import TextToSign from "./pages/TextToSign";
import SignToVoice from "./pages/SignToVoice";
import VoiceToSign from "./pages/VoiceToSign";
import Footer from "./components/Footer";

function App() {
  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar />
      
      {/* Main content area with flex-grow-1 to push footer down */}
      <div className="flex-grow-1 d-flex">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/sign-to-text" element={<SignToText />} />
          <Route path="/text-to-sign" element={<TextToSign />} />
          <Route path="/sign-to-voice" element={<SignToVoice />} />
          <Route path="/voice-to-sign" element={<VoiceToSign />} />
        </Routes>
      </div>
      
      <Footer />
    </div>
  );
}

export default App;
