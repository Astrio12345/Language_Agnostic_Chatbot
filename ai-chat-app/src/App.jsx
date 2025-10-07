import { useState, useRef, useEffect } from "react";
import "./App.css";

export default function App() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hello 👋, how can I help you today?" }
  ]);
  const [input, setInput] = useState("");
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message
    setMessages((prev) => [...prev, { sender: "user", text: input }]);

    try {
      const res = await fetch("http://localhost:5000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),  // <-- changed from 'question' to 'query'
      });

      const data = await res.json();
      setMessages((prev) => [...prev, { sender: "bot", text: data.answer }]);
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "⚠️ Error contacting server." },
      ]);
    }

    setInput("");
  };

  return (
    <div className="dark-bg">
      <div className="chat-wrapper">
        <header className="chat-header"> Institute AI Assistant</header>

        <main className="chat-main">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`chat-message ${msg.sender === "user" ? "user" : "bot"}`}
            >
              {msg.text}
            </div>
          ))}
          <div ref={chatEndRef} />
        </main>

        <footer className="chat-footer">
          <input
            type="text"
            className="chat-input"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
          />
          <button className="chat-button" onClick={handleSend}>Send</button>
        </footer>
      </div>
    </div>
  );
}
