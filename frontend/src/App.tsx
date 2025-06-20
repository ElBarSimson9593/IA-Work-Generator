import { useEffect, useState } from "react";
import ChatInterface from "./components/ChatInterface";
import Settings from "./components/Settings";
import { request } from "./request";

export default function App() {
  const [view, setView] = useState<"chat" | "settings">("chat");

  useEffect(() => {
    const lang = localStorage.getItem("idioma");
    if (lang) {
      request("/config/idioma", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idioma: lang }),
      }).catch(() => {});
    }
  }, []);

  return (
    <div className="h-screen flex flex-col">
      <header className="p-2 bg-gray-800 text-white flex gap-4">
        <button onClick={() => setView("chat")}>Chat</button>
        <button onClick={() => setView("settings")}>Settings</button>
      </header>
      <div className="flex-1">
        {view === "chat" ? <ChatInterface /> : <Settings />}
      </div>
    </div>
  );
}
