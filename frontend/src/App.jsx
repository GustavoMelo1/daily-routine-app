// mock estático — sem lógica, sem chamadas à API
// referência de layout: calendário do mês + detalhe do dia ao clicar

function App() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-200 px-6 py-16">
      <div className="max-w-2xl mx-auto">
        <header className="flex justify-between items-center mb-8 border-b border-zinc-800 pb-4">
          <span className="text-zinc-600">‹</span>
          <h1 className="font-mono text-sm tracking-[0.2em] uppercase text-zinc-300">
            Agosto 2026
          </h1>
          <span className="text-zinc-600">›</span>
        </header>

        <div className="grid grid-cols-7 gap-2 mb-3 text-center">
          {["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"].map((d) => (
            <div key={d} className="text-[11px] font-mono tracking-widest text-zinc-600">
              {d}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7 gap-2">
          {Array.from({ length: 31 }, (_, i) => i + 1).map((dia) => (
            <div
              key={dia}
              className="h-16 flex items-center justify-center border border-zinc-900 text-sm text-zinc-500"
            >
              {dia}
            </div>
          ))}
        </div>

        <p className="text-zinc-700 text-xs font-mono mt-10">
          mock estático — sem funcionalidade real
        </p>
      </div>
    </div>
  );
}

export default App;
