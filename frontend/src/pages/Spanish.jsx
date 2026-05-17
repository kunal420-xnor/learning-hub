import { useState, useRef, useEffect } from "react";

export default function Spanish({ onBack, token }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState("");
  const [count, setCount] = useState(0);
  const bottomRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function extractSection(text, label) {
    const regex = new RegExp(label + ':\\s*(.+?)(?=\\n[A-Z]+:|$)', 'si');
    const match = text.match(regex);
    return match ? match[1].replace(/\*([^*]+)\*/g, '$1').trim() : '';
  }

  function speakSpanish(rawText) {
    window.speechSynthesis.cancel();
    const spanish = extractSection(rawText, 'SPANISH');
    if (!spanish) return;
    const utterance = new SpeechSynthesisUtterance(spanish);
    utterance.lang = 'es-ES';
    utterance.rate = 0.8;
    const voices = window.speechSynthesis.getVoices();
    const voice = voices.find(v => v.name === 'Monica') ||
                  voices.find(v => v.name === 'Paulina') ||
                  voices.find(v => v.lang === 'es-ES');
    if (voice) utterance.voice = voice;
    window.speechSynthesis.speak(utterance);
  }

  function formatReply(text) {
    const spanish = extractSection(text, 'SPANISH');
    const english = extractSection(text, 'ENGLISH');
    const tip = extractSection(text, 'TIP');
    return { spanish, english, tip };
  }

  function toggleMic() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;
    if (listening) {
      recognitionRef.current?.stop();
      return;
    }
    const r = new SR();
    r.lang = 'es-ES';
    r.interimResults = true;
    r.onstart = () => { setListening(true); setVoiceStatus('Listening... speak now'); };
    r.onresult = (e) => {
      const t = Array.from(e.results).map(r => r[0].transcript).join('');
      setInput(t);
    };
    r.onend = () => {
      setListening(false);
      setVoiceStatus('');
    };
    r.onerror = () => {
      setListening(false);
      setVoiceStatus('Could not hear you, try again');
      setTimeout(() => setVoiceStatus(''), 2000);
    };
    recognitionRef.current = r;
    r.start();
  }

  async function send() {
    if (!input.trim()) return;
    const text = input.trim();
    setMessages(m => [...m, { role: "user", text }]);
    setInput("");
    setCount(c => c + 1);
    setLoading(true);

    const res = await fetch("/spanish/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    const parsed = formatReply(data.reply);
    setMessages(m => [...m, { role: "ai", raw: data.reply, ...parsed }]);
    setLoading(false);
    speakSpanish(data.reply);
  }

  return (
    <div className="min-h-screen bg-[#f0fdf4] flex flex-col items-center px-4 py-8">
      <h1 className="text-4xl font-extrabold text-[#0F6E56] mb-1">🇪🇸 Spanish Tutor</h1>
      <p className="text-lg text-[#5DCAA5] mb-6">Type or speak — I'll teach and correct you ✨</p>

      <div className="w-full max-w-xl bg-white rounded-3xl border-2 border-[#9FE1CB] p-5 flex flex-col gap-4 min-h-64 mb-4">
        {messages.length === 0 && (
          <p className="text-[#9FE1CB] text-center my-auto text-lg">Say anything!<br/>Try "Hello" or "What is your name?" 👋</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex items-end gap-2 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-lg flex-shrink-0 ${m.role === "user" ? "bg-[#5DCAA5]" : "bg-[#E1F5EE]"}`}>
              {m.role === "user" ? "😊" : "🇪🇸"}
            </div>
            {m.role === "user" ? (
              <div className="bg-[#5DCAA5] text-[#04342C] px-4 py-2 rounded-2xl rounded-br-sm text-lg max-w-[80%]">{m.text}</div>
            ) : (
              <div className="bg-[#E1F5EE] px-4 py-3 rounded-2xl rounded-bl-sm max-w-[80%] flex flex-col gap-1">
                {m.spanish && <span className="text-xl font-extrabold text-[#085041]">{m.spanish}</span>}
                {m.english && <span className="text-sm text-gray-400 italic bg-[#f1f0eb] px-2 py-1 rounded-lg">{m.english}</span>}
                {m.tip && <span className="text-xs text-[#1D9E75] italic bg-[#E1F5EE] px-2 py-1 rounded-lg">Tip: {m.tip}</span>}
                <button onClick={() => speakSpanish(m.raw)} className="text-left text-sm opacity-50 hover:opacity-100 mt-1">🔊 Listen</button>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-end gap-2">
            <div className="w-8 h-8 rounded-full bg-[#E1F5EE] flex items-center justify-center">🇪🇸</div>
            <div className="bg-[#E1F5EE] text-[#5DCAA5] px-4 py-2 rounded-2xl italic text-lg">pensando...</div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="w-full max-w-xl">
        <div className="flex gap-2 mb-2">
          <button
            onClick={toggleMic}
            className={`border-2 px-4 py-3 rounded-full text-xl transition-all ${listening ? "bg-[#1D9E75] border-[#1D9E75] animate-pulse" : "bg-white border-[#9FE1CB] text-[#1D9E75]"}`}
          >🎤</button>
          <input
            className="flex-1 px-5 py-3 rounded-full border-2 border-[#9FE1CB] text-lg outline-none focus:border-[#5DCAA5] text-[#085041] bg-white placeholder-[#9FE1CB]"
            placeholder="Type or speak in English or Spanish..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && send()}
          />
          <button
            onClick={send}
            disabled={loading}
            className="bg-[#1D9E75] hover:bg-[#0F6E56] disabled:bg-[#9FE1CB] text-white px-6 py-3 rounded-full font-extrabold text-lg"
          >Send!</button>
        </div>
        {voiceStatus && <p className="text-center text-sm text-[#5DCAA5] mb-2">{voiceStatus}</p>}
        <div className="flex justify-center gap-2 mb-4">
          {[1,2,3].map(n => (
            <div key={n} className={`w-2.5 h-2.5 rounded-full ${count >= n ? "bg-[#1D9E75]" : "bg-[#9FE1CB]"}`} />
          ))}
        </div>
        <button onClick={onBack} className="text-[#5DCAA5] text-sm w-full text-center hover:text-[#0F6E56]">← Back to home</button>
      </div>
    </div>
  );
}
