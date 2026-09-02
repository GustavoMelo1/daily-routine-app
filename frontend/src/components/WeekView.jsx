import { WEEKDAYS_SHORT, getWeekDates, isToday, toIsoDate } from "../utils/date"

export default function WeekView({ cursorDate, selectedDate, records, onSelect }) {
  const dates = getWeekDates(cursorDate)

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-7">
      {dates.map((date, index) => {
        const isoDate = toIsoDate(date)
        const record = records.get(isoDate)
        const selected = selectedDate === isoDate

        return (
          <button
            key={isoDate}
            type="button"
            onClick={() => onSelect(date)}
            className={`min-h-36 rounded-xl border p-4 text-left transition-colors ${
              selected
                ? "border-blue-300 bg-blue-50"
                : "border-zinc-200 bg-white hover:border-zinc-300 hover:bg-zinc-50"
            }`}
            aria-pressed={selected}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                {WEEKDAYS_SHORT[index]}
              </span>
              <span
                className={`flex h-8 min-w-8 items-center justify-center rounded-full px-2 text-sm font-semibold ${
                  isToday(date) ? "bg-blue-600 text-white" : "text-zinc-900"
                }`}
              >
                {date.getDate()}
              </span>
            </div>
            <div className="mt-7">
              {record ? (
                <>
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-blue-600">
                    Registrado
                  </span>
                  <p className="mt-1 line-clamp-2 text-sm font-medium text-zinc-800">
                    {record.marcador || "Sem tarefa de destaque"}
                  </p>
                </>
              ) : (
                <p className="text-sm text-zinc-400">Sem registro</p>
              )}
            </div>
          </button>
        )
      })}
    </div>
  )
}
