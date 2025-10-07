import { useState } from "react";
import "./App.css";

export default function App() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage("⚠️ Please select a file first!");
      return;
    }
  
    console.log("📤 Uploading file:", file);
  
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      const res = await fetch("http://127.0.0.1:5002/upload", {
        method: "POST",
        body: formData,
      });
  
      const data = await res.json();
      if (res.ok) {
        setMessage("✅ " + data.message);
      } else {
        setMessage("❌ " + data.error);
      }
    } catch (error) {
      setMessage("❌ Upload failed: " + error.message);
    }
  };
  
  return (
    <div className="app-container">
      <div className="upload-box">
        <h1 className="heading">Institute Personal Doc Upload</h1>
        <div className="form-area">
          <input type="file" onChange={handleFileChange} className="file-input" />
          <button onClick={handleUpload} className="upload-btn">Upload</button>
        </div>
        {message && <p className="message">{message}</p>}
      </div>
    </div>
  );
}
