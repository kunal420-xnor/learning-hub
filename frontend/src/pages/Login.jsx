import { useState } from "react";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    if (!username || !password) return;
    setLoading(true);
    setError("");

    const res = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    setLoading(false);

    if (res.ok) {
      localStorage.setItem("token", data.token);
      localStorage.setItem("username", data.username);
      onLogin(data.username, data.token);
    } else {
      setError("Invalid username or password");
    }
  }

  return (
    <div className="min-h-screen bg-[#080808] flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <h1 className="text-4xl font-bold text-white mb-2 tracking-tight">Sign in</h1>
        <p className="text-[#444] text-sm mb-8">Enter your credentials to access the platform</p>

        <div className="flex flex-col gap-4">
          <div>
            <label className="text-xs text-[#444] uppercase tracking-widest mb-2 block">Username</label>
            <input
              className="w-full bg-[#111] border border-[#1E1E1E] text-white px-4 py-3 rounded text-sm outline-none focus:border-[#333] placeholder-[#333]"
              placeholder="kunal"
              value={username}
              onChange={e => setUsername(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleLogin()}
            />
          </div>
          <div>
            <label className="text-xs text-[#444] uppercase tracking-widest mb-2 block">Password</label>
            <input
              type="password"
              className="w-full bg-[#111] border border-[#1E1E1E] text-white px-4 py-3 rounded text-sm outline-none focus:border-[#333] placeholder-[#333]"
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleLogin()}
            />
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <button
            onClick={handleLogin}
            disabled={loading}
            className="w-full bg-white text-black py-3 rounded text-sm font-semibold tracking-wide hover:bg-[#E5E5E5] disabled:opacity-50 transition mt-2"
          >
            {loading ? "Signing in..." : "Sign in →"}
          </button>
        </div>

        <div className="mt-8 p-4 bg-[#0D0D0D] border border-[#1A1A1A] rounded">
          <p className="text-xs text-[#444] mb-2 uppercase tracking-widest">Test accounts</p>
          <p className="text-xs text-[#555]">kunal / password123</p>
          <p className="text-xs text-[#555]">demo / demo123</p>
          <p className="text-xs text-[#555]">admin / admin123</p>
        </div>
      </div>
    </div>
  );
}
