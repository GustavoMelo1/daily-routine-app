export const WEEKDAYS_SHORT = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]

function localDate(year, monthIndex, day) {
  return new Date(year, monthIndex, day, 12)
}

export function toIsoDate(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, "0")
  const day = String(date.getDate()).padStart(2, "0")
  return `${year}-${month}-${day}`
}

export function fromIsoDate(value) {
  const [year, month, day] = value.split("-").map(Number)
  return localDate(year, month - 1, day)
}

export function addDays(date, amount) {
  return localDate(date.getFullYear(), date.getMonth(), date.getDate() + amount)
}

export function startOfWeek(date) {
  return addDays(date, -date.getDay())
}

export function getWeekDates(date) {
  const start = startOfWeek(date)
  return Array.from({ length: 7 }, (_, index) => addDays(start, index))
}

export function getMonthGrid(date) {
  const first = localDate(date.getFullYear(), date.getMonth(), 1)
  const gridStart = startOfWeek(first)
  return Array.from({ length: 42 }, (_, index) => addDays(gridStart, index))
}

export function shiftDate(date, view, amount) {
  if (view === "week") return addDays(date, amount * 7)
  if (view === "day") return addDays(date, amount)

  const target = localDate(date.getFullYear(), date.getMonth() + amount, 1)
  const lastDay = new Date(target.getFullYear(), target.getMonth() + 1, 0).getDate()
  target.setDate(Math.min(date.getDate(), lastDay))
  return target
}

export function formatMonthYear(date) {
  return new Intl.DateTimeFormat("pt-BR", {
    month: "long",
    year: "numeric",
  }).format(date)
}

export function formatLongDate(value) {
  const date = typeof value === "string" ? fromIsoDate(value) : value
  return new Intl.DateTimeFormat("pt-BR", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    year: "numeric",
  }).format(date)
}

export function formatCompactDate(value) {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
  }).format(fromIsoDate(value))
}

export function getPeriodTitle(date, view) {
  if (view === "month") return formatMonthYear(date)
  if (view === "day") return formatLongDate(date)

  const dates = getWeekDates(date)
  const start = dates[0]
  const end = dates[6]
  const formatter = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short" })
  return `${formatter.format(start)} – ${formatter.format(end)}`
}

export function isToday(date) {
  return toIsoDate(date) === toIsoDate(new Date())
}

export function getRequiredMonths(date, view) {
  const dates =
    view === "month"
      ? getMonthGrid(date)
      : view === "week"
        ? getWeekDates(date)
        : [date]
  const unique = new Map()

  for (const current of dates) {
    const year = current.getFullYear()
    const month = current.getMonth() + 1
    unique.set(`${year}-${month}`, { year, month })
  }

  return [...unique.values()]
}

export function calculateLongestStreak(days) {
  const qualifyingDates = days
    .filter(
      (day) =>
        day.minutos_estudados > 0 &&
        day.tarefas.some((task) => Number(task.cumprida) === 1),
    )
    .map((day) => day.data)
    .sort()

  let longest = 0
  let current = 0
  let previous = null

  for (const date of qualifyingDates) {
    if (!previous) {
      current = 1
    } else {
      const difference = Math.round(
        (fromIsoDate(date) - fromIsoDate(previous)) / 86_400_000,
      )
      current = difference === 1 ? current + 1 : 1
    }

    longest = Math.max(longest, current)
    previous = date
  }

  return longest
}
