import { ChevronLeft, ChevronRight } from "lucide-react"

const views = [
  { id: "month", label: "Mês" },
  { id: "week", label: "Semana" },
  { id: "day", label: "Dia" },
]

export default function CalendarToolbar({ title, view, onViewChange, onPrevious, onNext, onToday }) {
  return (
    <div className="flex flex-col gap-4 border-b border-zinc-200 pb-5 lg:flex-row lg:items-center lg:justify-between">
      <div className="flex min-w-0 items-center gap-2">
        <button
          type="button"
          onClick={onPrevious}
          className="rounded-lg border border-zinc-300 bg-white p-2 text-zinc-600 hover:bg-zinc-50 hover:text-zinc-950"
          aria-label="Período anterior"
        >
          <ChevronLeft size={18} />
        </button>
        <button
          type="button"
          onClick={onNext}
          className="rounded-lg border border-zinc-300 bg-white p-2 text-zinc-600 hover:bg-zinc-50 hover:text-zinc-950"
          aria-label="Próximo período"
        >
          <ChevronRight size={18} />
        </button>
        <button
          type="button"
          onClick={onToday}
          className="ml-1 rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50"
        >
          Hoje
        </button>
        <h1 className="ml-2 truncate text-xl font-semibold capitalize tracking-tight text-zinc-950 sm:text-2xl">
          {title}
        </h1>
      </div>

      <div className="inline-flex w-fit rounded-lg border border-zinc-300 bg-white p-1" aria-label="Visualização do calendário">
        {views.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => onViewChange(item.id)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
              view === item.id
                ? "bg-zinc-900 text-white"
                : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-950"
            }`}
            aria-pressed={view === item.id}
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  )
}
