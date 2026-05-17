export default function Home({ onSelect, username, onLogout }) {
  return (
    <div className="min-h-screen bg-[#fffbf4] flex flex-col items-center justify-center px-6 py-12">
      <div className="absolute top-6 right-6 flex items-center gap-4">
        <span className="text-sm text-[#AFA9EC]">👋 {username}</span>
        <button onClick={onLogout} className="text-sm text-[#AFA9EC] hover:text-[#7F77DD] underline">Logout</button>
      </div>

      <h1 className="text-5xl font-extrabold text-[#3C3489] mb-2">👋 Welcome!</h1>
      <p className="text-xl text-[#AFA9EC] mb-12">What do you want to do today?</p>

      <div className="flex flex-col sm:flex-row gap-6">
        <button
          onClick={() => onSelect("eli3")}
          className="bg-white border-2 border-[#EEEDFE] rounded-3xl p-8 w-72 flex flex-col items-center gap-4 hover:-translate-y-2 transition-transform cursor-pointer"
        >
          <span className="text-6xl">🧸</span>
          <h2 className="text-2xl font-extrabold text-[#3C3489]">Explain Like I'm 3</h2>
          <p className="text-sm text-gray-400 text-center">Ask anything and get a super simple explanation</p>
          <span className="bg-[#7F77DD] text-white px-6 py-2 rounded-full font-bold text-lg">Let's learn!</span>
        </button>

        <button
          onClick={() => onSelect("spanish")}
          className="bg-white border-2 border-[#9FE1CB] rounded-3xl p-8 w-72 flex flex-col items-center gap-4 hover:-translate-y-2 transition-transform cursor-pointer"
        >
          <span className="text-6xl">🇪🇸</span>
          <h2 className="text-2xl font-extrabold text-[#0F6E56]">Spanish Tutor</h2>
          <p className="text-sm text-gray-400 text-center">Chat, speak and learn Spanish with live corrections</p>
          <span className="bg-[#1D9E75] text-white px-6 py-2 rounded-full font-bold text-lg">Hola!</span>
        </button>
      </div>
    </div>
  );
}
