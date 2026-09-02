import { WEEKDAYS_SHORT, getMonthGrid, isToday, toIsoDate } from "../utils/date"

export default function MonthView({ cursorDate, selectedDate, records, onSelect }) {
  const dates = getMonthGrid(cursorDate)

  return (
    <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">
      <div className="grid grid-cols-7 border-b border-zinc-200 bg-zinc-50">
        {WEEKDAYS_SHORT.map((weekday) => (
          <div
            key={weekday}
            className="px-2 py-2.5 text-center text-[11px] font-semibold uppercase tracking-wider text-zinc-500"
          >
            {weekday}
          </div>
        ))}
      </div>
      <div className="grid grid-cols-7">
        {dates.map((date) => {
          const isoDate = toIsoDate(date)
          const record = records.get(isoDate)
          const outsideMonth = date.getMonth() !== cursorDate.getMonth()
          const selected = isoDate === selectedDate

          return (
            <button
              key={isoDate}
              type="button"
              onClick={() => onSelect(date)}
              className={`group min-h-24 border-b border-r border-zinc-200 p-2 text-left transition-colors sm:min-h-28 lg:min-h-32 ${
                selected ? "bg-blue-50" : "hover:bg-zinc-50"
              } ${outsideMonth ? "text-zinc-400" : "text-zinc-900"}`}
              aria-label={`${isoDate}${record ? `, ${record.marcador || "dia registrado"}` : ", sem registro"}`}
              aria-pressed={selected}
            >
              <span
                className={`inline-flex h-7 min-w-7 items-center justify-center rounded-full px-1.5 text-xs font-semibold ${
                  isToday(date)
                    ? "bg-blue-600 text-white"
                    : selected
                      ? "text-blue-700"
                      : "text-inherit"
                }`}
              >
                {date.getDate()}
              </span>
              {record && (
                <div className="mt-2 rounded-md border border-blue-100 bg-blue-50 px-2 py-1.5 text-xs text-blue-800">
                  <span className="block truncate font-medium">
                    {record.marcador || "Dia registrado"}
                  </span>
                </div>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}
