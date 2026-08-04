import { useEffect, useState } from "react";
import Calendario from "./components/Calendario";
import DetalheDia from "./components/DetalheDia";
import { listarDiasDoMes } from "./api";

export default function App() {
  const [mesAtual, setMesAtual] = useState(new Date());
  const [diaSelecionado, setDiaSelecionado] = useState(null);
  const [marcadores, setMarcadores] = useState({});

  useEffect(() => {
    const ano = mesAtual.getFullYear();
    const mes = mesAtual.getMonth() + 1;
    listarDiasDoMes(ano, mes).then(setMarcadores);
  }, [mesAtual, diaSelecionado]);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-200 px-6 pb-20">
      {diaSelecionado ? (
        <DetalheDia data={diaSelecionado} onVoltar={() => setDiaSelecionado(null)} />
      ) : (
        <Calendario
          mesAtual={mesAtual}
          onMudarMes={setMesAtual}
          onSelecionarDia={setDiaSelecionado}
          marcadores={marcadores}
        />
      )}
    </div>
  );
}
