import { useState } from "react";
import Calendario from "./components/Calendario";

// marcadores mockados por enquanto — vem da API depois (rota GET /dias)
const MARCADORES_MOCK = {
  "2026-08-01": "revisão sem.",
  "2026-08-12": "dentista",
  "2026-08-19": "revisão api",
  "2026-08-20": "revisão",
};

export default function App() {
  const [mesAtual, setMesAtual] = useState(new Date(2026, 7, 1));
  const [diaSelecionado, setDiaSelecionado] = useState(null);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-200 px-6 pb-20">
      {diaSelecionado ? (
        <div className="max-w-xl mx-auto mt-12">
          <button
            onClick={() => setDiaSelecionado(null)}
            className="text-zinc-500 hover:text-amber-500 text-sm font-mono mb-8"
          >
            ← voltar
          </button>
          <p className="text-zinc-400">
            {diaSelecionado.toLocaleDateString("pt-BR", {
              weekday: "long",
              day: "2-digit",
              month: "long",
            })}
          </p>
          <p className="text-zinc-600 text-sm mt-2">detalhe do dia — próximo bloco</p>
        </div>
      ) : (
        <Calendario
          mesAtual={mesAtual}
          onMudarMes={setMesAtual}
          onSelecionarDia={setDiaSelecionado}
          marcadores={MARCADORES_MOCK}
        />
      )}
    </div>
  );
}
