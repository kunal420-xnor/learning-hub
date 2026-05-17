import { useState, useEffect } from "react";
import Home from "./pages/Home";
import ELI3 from "./pages/ELI3";
import Spanish from "./pages/Spanish";
import Login from "./pages/Login";

export default function App() {
  const [page, setPage] = useState("home");
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [username, setUsername] = useState(localStorage.getItem("username"));

  function handleLogin(user, tok) {
    setToken(tok);
    setUsername(user);
  }

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    setToken(null);
    setUsername(null);
    setPage("home");
  }

  if (!token) return <Login onLogin={handleLogin} />;

  return (
    <div>
      {page === "home" && <Home onSelect={setPage} username={username} onLogout={handleLogout} />}
      {page === "eli3" && <ELI3 onBack={() => setPage("home")} token={token} />}
      {page === "spanish" && <Spanish onBack={() => setPage("home")} token={token} />}
    </div>
  );
}
