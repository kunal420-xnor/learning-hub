import { useState, useRef, useEffect } from "react";

export default function ELI3({ onBack, token })  {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState(0);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send() {
    if (!input.trim()) return;
    const text = input.trim();
    setMessages(m => [...m, { role: "user", text }]);
    setInput("");
    setCount(c => c + 1);
    setLoading(true);

    const res = await fetch("/explain", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ text, count: count + 1 })
    });
    const data = await res.json();
    setMessages(m => [...m, { role: "ai", text: data.reply, run_id: data.run_id, feedback: null }]);
    setLoading(false);
  }

  async function sendFeedback(run_id, score, index, user_text, reply) {
    setMessages(m => m.map((msg, i) => i === index ? { ...msg, feedback: score } : msg));
    await fetch("/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ run_id, score, comment: score === 1 ? "Good explanation" : "Needs improvement" })
    });
    await fetch("/create_dataset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ run_id, score, user_text, reply })
    });
  }

  return (
    <div className="min-h-screen bg-[#fffbf4] flex flex-col items-center px-4 py-8">
      <h1 className="text-4xl font-extrabold text-[#3C3489] mb-1">🧸 Explain like I'm 3!</h1>
      <p className="text-lg text-[#AFA9EC] mb-6">Ask anything — I'll make it super simple ✨</p>

      <div className="w-full max-w-xl bg-white rounded-3xl border-2 border-[#EEEDFE] p-5 flex flex-col gap-4 min-h-64 mb-4">
        {messages.length === 0 && (
          <p className="text-[#CECBF6] text-center my-auto text-lg">Ask me anything!<br/>Try "What is gravity?" 🌍</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className="flex flex-col gap-1">
            <div className={`flex items-end gap-2 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-lg flex-shrink-0 ${m.role === "user" ? "bg-[#FAC775]" : "bg-[#EEEDFE]"}`}>
                {m.role === "user" ? "😊" : "🌟"}
              </div>
              <div className={`px-4 py-2 rounded-2xl text-lg max-w-[80%] leading-relaxed ${m.role === "user" ? "bg-[#FAC775] text-[#633806] rounded-br-sm" : "bg-[#EEEDFE] text-[#3C3489] rounded-bl-sm"}`}>
                {m.text}
              </div>
            </div>
            {m.role === "ai" && m.run_id && (
              <div className="flex gap-2 ml-10 mt-1">
                {m.feedback === null ? (
                  <>
                    <button
                      onClick={() => sendFeedback(m.run_id, 1, i, messages[i-1]?.text, m.text)}
                      className="text-sm bg-[#EAF3DE] text-[#27500A] px-3 py-1 rounded-full hover:bg-green-200 transition"
                    >👍 Helpful</button>
                    <button
                      onClick={() => sendFeedback(m.run_id, 0, i, messages[i-1]?.text, m.text)}
                      className="text-sm bg-[#FCEBEB] text-[#791F1F] px-3 py-1 rounded-full hover:bg-red-200 transition"
                    >👎 Not helpful</button>
                  </>
                ) : (
                  <span className="text-sm text-gray-400">
                    {m.feedback === 1 ? "👍 Thanks for the feedback!" : "👎 Got it, we'll improve!"}
                  </span>
                )}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-end gap-2">
            <div className="w-8 h-8 rounded-full bg-[#EEEDFE] flex items-center justify-center">🌟</div>
            <div className="bg-[#EEEDFE] text-[#AFA9EC] px-4 py-2 rounded-2xl text-lg italic">thinking...</div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="w-full max-w-xl">
        <div className="flex gap-2 mb-3">
          <input
            className="flex-1 px-5 py-3 rounded-full border-2 border-[#EEEDFE] text-lg outline-none focus:border-[#AFA9EC] text-[#3C3489] bg-white placeholder-[#CECBF6]"
            placeholder="What do you want to know? ✨"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && send()}
          />
          <button
            onClick={send}
            disabled={loading}
            className="bg-[#7F77DD] hover:bg-[#534AB7] disabled:bg-[#CECBF6] text-white px-6 py-3 rounded-full font-extrabold text-lg"
          >Ask!</button>
        </div>
        <div className="flex justify-center gap-2 mb-4">
          {[1,2,3].map(n => (
            <div key={n} className={`w-2.5 h-2.5 rounded-full ${count >= n ? "bg-[#7F77DD]" : "bg-[#EEEDFE]"}`} />
          ))}
        </div>
        <button onClick={onBack} className="text-[#AFA9EC] text-sm w-full text-center hover:text-[#7F77DD]">← Back to home</button>
      </div>
    </div>
  );
}
