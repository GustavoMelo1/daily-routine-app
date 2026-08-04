import { useState } from "react";
import Calendario from "./components/Calendario";
import DetalheDia from "./components/DetalheDia";

export default function App() {
  const [mesAtual, setMesAtual] = useState(new Date());
  const [diaSelecionado, setDiaSelecionado] = useState(null);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-200 px-6 pb-20">
      {diaSelecionado ? (
        <DetalheDia data={diaSelecionado} onVoltar={() => setDiaSelecionado(null)} />
      ) : (
        <Calendario
          mesAtual={mesAtual}
          onMudarMes={setMesAtual}
          onSelecionarDia={setDiaSelecionado}
          marcadores={{}}
        />
      )}
    </div>
  );
}
