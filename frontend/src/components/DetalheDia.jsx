import { useEffect, useState } from "react";
import { Check } from "lucide-react";
import {
  formatarDataISO,
  buscarDia,
  criarDia,
  criarTarefa,
  atualizarTarefa,
} from "../api";

export default function DetalheDia({ data, onVoltar }) {
  const dataISO = formatarDataISO(data);
  const ehDomingo = data.getDay() === 0;

  const [dia, setDia] = useState(undefined); // undefined = carregando, null = nao existe
  const [novaTarefa, setNovaTarefa] = useState("");
  const [formNovoDia, setFormNovoDia] = useState({
    minutos_estudados: 0,
    frase_do_dia: "",
    autor_frase: "",
    tipo: "normal",
  });

  useEffect(() => {
    setDia(undefined);
    buscarDia(dataISO).then(setDia);
  }, [dataISO]);

  async function handleCriarDia(e) {
    e.preventDefault();
    await criarDia({ data: dataISO, ...formNovoDia });
    const diaCriado = await buscarDia(dataISO);
    setDia(diaCriado);
  }

  async function handleAdicionarTarefa(e) {
    e.preventDefault();
    if (!novaTarefa.trim()) return;
    await criarTarefa({ dia_id: dia.id, descricao: novaTarefa, cumprida: 0 });
    setNovaTarefa("");
    setDia(await buscarDia(dataISO));
  }

  async function handleToggleTarefa(tarefa) {
    await atualizarTarefa(tarefa.id, tarefa.cumprida ? 0 : 1);
    setDia(await buscarDia(dataISO));
  }

  return (
    <div className="max-w-xl mx-auto mt-12 pb-20">
      <header className="flex items-center gap-4 mb-10">
        <button
          onClick={onVoltar}
          className="text-zinc-500 hover:text-amber-500 flex items-center text-sm font-mono tracking-wide"
        >
          ← voltar
        </button>
        <div className="h-px bg-zinc-800 flex-1" />
        <span className="text-zinc-400 font-mono tracking-widest text-xs uppercase">
          {data.toLocaleDateString("pt-BR", { weekday: "long", day: "2-digit", month: "long" })}
        </span>
      </header>

      {dia === undefined && <p className="text-zinc-600 font-mono text-sm">carregando...</p>}

      {dia === null && (
        <form onSubmit={handleCriarDia} className="space-y-4">
          <p className="text-zinc-500 text-sm">Esse dia ainda não existe. Cria ele:</p>
          <input
            type="number"
            placeholder="Minutos estudados"
            value={formNovoDia.minutos_estudados}
            onChange={(e) => setFormNovoDia({ ...formNovoDia, minutos_estudados: Number(e.target.value) })}
            className="w-full bg-transparent border border-zinc-800 px-3 py-2 text-zinc-200 outline-none focus:border-amber-600"
          />
          <input
            type="text"
            placeholder="Frase do dia"
            value={formNovoDia.frase_do_dia}
            onChange={(e) => setFormNovoDia({ ...formNovoDia, frase_do_dia: e.target.value })}
            className="w-full bg-transparent border border-zinc-800 px-3 py-2 text-zinc-200 outline-none focus:border-amber-600"
          />
          <input
            type="text"
            placeholder="Autor da frase"
            value={formNovoDia.autor_frase}
            onChange={(e) => setFormNovoDia({ ...formNovoDia, autor_frase: e.target.value })}
            className="w-full bg-transparent border border-zinc-800 px-3 py-2 text-zinc-200 outline-none focus:border-amber-600"
          />
          <button type="submit" className="border border-amber-700 text-amber-500 px-4 py-2 text-sm hover:bg-amber-950/30">
            Criar dia
          </button>
        </form>
      )}

      {dia && (
        <>
          <section className="mb-12 border-l-2 border-zinc-700 pl-6 py-2">
            <h2 className="font-serif text-2xl italic text-zinc-200 leading-relaxed mb-2">
              "{dia.frase_do_dia}"
            </h2>
            {dia.autor_frase && <p className="text-zinc-500 text-sm">— {dia.autor_frase}</p>}
          </section>

          <section className="mb-12">
            <h3 className="text-xs font-mono text-zinc-600 tracking-widest uppercase mb-4">
              Tarefas do dia
            </h3>
            <ul className="space-y-3">
              {dia.tarefas.map((tarefa) => (
                <li key={tarefa.id} className="flex items-start gap-4">
                  <button
                    onClick={() => handleToggleTarefa(tarefa)}
                    className={`mt-0.5 w-5 h-5 flex items-center justify-center border transition-colors ${
                      tarefa.cumprida
                        ? "bg-amber-700 border-amber-700 text-zinc-950"
                        : "border-zinc-700 hover:border-amber-600 text-transparent"
                    }`}
                  >
                    <Check size={14} className={tarefa.cumprida ? "opacity-100" : "opacity-0"} />
                  </button>
                  <span className={tarefa.cumprida ? "text-zinc-600 line-through" : "text-zinc-300"}>
                    {tarefa.descricao}
                  </span>
                </li>
              ))}
            </ul>

            <form onSubmit={handleAdicionarTarefa} className="flex items-center gap-4 mt-4">
              <div className="w-5 h-5 border border-dashed border-zinc-700 flex-shrink-0" />
              <input
                type="text"
                value={novaTarefa}
                onChange={(e) => setNovaTarefa(e.target.value)}
                placeholder="Novo compromisso..."
                className="bg-transparent border-none outline-none text-zinc-300 w-full placeholder-zinc-700"
              />
            </form>
          </section>

          <section className="flex items-center justify-between border-t border-zinc-900 pt-6">
            <span className="text-sm text-zinc-500 font-mono">foco e estudo</span>
            <div className="flex items-baseline gap-1 text-zinc-300">
              <span className="text-2xl font-mono">{dia.minutos_estudados}</span>
              <span className="text-zinc-600 text-sm">min</span>
            </div>
          </section>

          {ehDomingo && (
            <section className="mt-16 border border-dashed border-amber-800 p-6">
              <h3 className="text-xs font-mono text-amber-600 tracking-widest uppercase mb-3">
                Conferência semanal
              </h3>
              <p className="text-zinc-500 text-sm">
                Metas da semana ainda não têm rota na API — fica pra um próximo bloco.
              </p>
            </section>
          )}
        </>
      )}
    </div>
  );
}
