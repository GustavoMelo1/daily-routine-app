import { ChevronLeft, ChevronRight } from "lucide-react";

const MESES = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

const DIAS_SEMANA = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

function gerarGradeDoMes(ano, mes) {
  const primeiroDiaSemana = new Date(ano, mes, 1).getDay();
  const totalDias = new Date(ano, mes + 1, 0).getDate();

  const celulas = [];
  for (let i = 0; i < primeiroDiaSemana; i++) {
    celulas.push(null);
  }
  for (let dia = 1; dia <= totalDias; dia++) {
    celulas.push(dia);
  }
  return celulas;
}

export default function Calendario({ mesAtual, onMudarMes, onSelecionarDia, marcadores }) {
  const ano = mesAtual.getFullYear();
  const mes = mesAtual.getMonth();
  const celulas = gerarGradeDoMes(ano, mes);

  const hoje = new Date();
  const ehHoje = (dia) =>
    dia === hoje.getDate() && mes === hoje.getMonth() && ano === hoje.getFullYear();

  const irParaMesAnterior = () => onMudarMes(new Date(ano, mes - 1, 1));
  const irParaProximoMes = () => onMudarMes(new Date(ano, mes + 1, 1));

  return (
    <div className="max-w-2xl mx-auto mt-12">
      <header className="flex justify-between items-center mb-8 border-b border-zinc-800 pb-4">
        <button
          onClick={irParaMesAnterior}
          className="text-zinc-500 hover:text-amber-500 transition-colors"
          aria-label="Mês anterior"
        >
          <ChevronLeft size={20} />
        </button>
        <h1 className="font-mono text-sm tracking-[0.2em] uppercase text-zinc-300">
          {MESES[mes]} {ano}
        </h1>
        <button
          onClick={irParaProximoMes}
          className="text-zinc-500 hover:text-amber-500 transition-colors"
          aria-label="Próximo mês"
        >
          <ChevronRight size={20} />
        </button>
      </header>

      <div className="grid grid-cols-7 gap-2 mb-3 text-center">
        {DIAS_SEMANA.map((d) => (
          <div key={d} className="text-[11px] font-mono tracking-widest text-zinc-600">
            {d}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-2">
        {celulas.map((dia, i) => {
          if (dia === null) return <div key={`vazio-${i}`} className="h-16" />;

          const dataISO = `${ano}-${String(mes + 1).padStart(2, "0")}-${String(dia).padStart(2, "0")}`;
          const marcador = marcadores?.[dataISO];
          const ehDomingo = new Date(ano, mes, dia).getDay() === 0;

          return (
            <button
              key={dataISO}
              onClick={() => onSelecionarDia(new Date(ano, mes, dia))}
              className={`h-16 flex flex-col items-center justify-center border text-sm transition-colors
                ${ehHoje(dia) ? "border-amber-600 text-amber-500" : "border-zinc-900 text-zinc-400"}
                ${ehDomingo ? "bg-zinc-900/40" : ""}
                hover:border-zinc-700 hover:bg-zinc-900 hover:text-zinc-200`}
            >
              <span>{dia}</span>
              {marcador && (
                <span className="text-[10px] font-mono text-amber-600 mt-1 truncate max-w-full px-1">
                  {marcador}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
