import { useEffect, useMemo, useState } from "react"

import { getApiErrorMessage, getDay, getDaysByMonth } from "./api/client"
import AppShell from "./components/AppShell"
import CalendarToolbar from "./components/CalendarToolbar"
import Dashboard from "./components/Dashboard"
import DayPanel from "./components/DayPanel"
import MonthView from "./components/MonthView"
import StatusMessage from "./components/StatusMessage"
import WeekView from "./components/WeekView"
import {
  getPeriodTitle,
  getRequiredMonths,
  shiftDate,
  toIsoDate,
} from "./utils/date"

function App() {
  const [activeSection, setActiveSection] = useState("calendar")
  const [view, setView] = useState("month")
  const [cursorDate, setCursorDate] = useState(() => new Date())
  const [records, setRecords] = useState([])
  const [recordsLoading, setRecordsLoading] = useState(true)
  const [recordsError, setRecordsError] = useState("")
  const [selectedDay, setSelectedDay] = useState(undefined)
  const [dayLoading, setDayLoading] = useState(true)
  const [dayError, setDayError] = useState("")
  const [refreshKey, setRefreshKey] = useState(0)

  const selectedDate = toIsoDate(cursorDate)
  const requiredMonths = useMemo(
    () => getRequiredMonths(cursorDate, view),
    [cursorDate, view],
  )
  useEffect(() => {
    const controller = new AbortController()

    async function loadRecords() {
      setRecordsLoading(true)
      setRecordsError("")
      try {
        const responses = await Promise.all(
          requiredMonths.map(({ year, month }) =>
            getDaysByMonth(year, month, controller.signal),
          ),
        )
        const merged = new Map()
        responses.flat().forEach((record) => merged.set(record.data, record))
        setRecords([...merged.values()])
      } catch (error) {
        if (error.name !== "AbortError") setRecordsError(getApiErrorMessage(error))
      } finally {
        if (!controller.signal.aborted) setRecordsLoading(false)
      }
    }

    loadRecords()
    return () => controller.abort()
  }, [requiredMonths, refreshKey])

  useEffect(() => {
    const controller = new AbortController()

    async function loadSelectedDay() {
      setDayLoading(true)
      setDayError("")
      setSelectedDay(undefined)
      try {
        setSelectedDay(await getDay(selectedDate, controller.signal))
      } catch (error) {
        if (error.name !== "AbortError") setDayError(getApiErrorMessage(error))
      } finally {
        if (!controller.signal.aborted) setDayLoading(false)
      }
    }

    loadSelectedDay()
    return () => controller.abort()
  }, [selectedDate, refreshKey])

  const recordsMap = useMemo(
    () => new Map(records.map((record) => [record.data, record])),
    [records],
  )

  function refreshData() {
    setRefreshKey((current) => current + 1)
  }

  function handleSelectDate(date) {
    setCursorDate(date)
  }

  const dayPanel = (
    <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">
      <DayPanel
        date={selectedDate}
        day={selectedDay}
        loading={dayLoading}
        error={dayError}
        onRetry={refreshData}
        onChanged={refreshData}
      />
    </div>
  )

  return (
    <AppShell activeSection={activeSection} onSectionChange={setActiveSection}>
      {activeSection === "dashboard" ? (
        <Dashboard />
      ) : (
        <div>
          <CalendarToolbar
            title={getPeriodTitle(cursorDate, view)}
            view={view}
            onViewChange={setView}
            onPrevious={() => setCursorDate((current) => shiftDate(current, view, -1))}
            onNext={() => setCursorDate((current) => shiftDate(current, view, 1))}
            onToday={() => setCursorDate(new Date())}
          />

          {recordsError && (
            <div className="mt-5">
              <StatusMessage
                title="Não foi possível carregar o calendário"
                description={recordsError}
                onRetry={refreshData}
              />
            </div>
          )}

          {recordsLoading && !recordsError && (
            <div className="mt-5 h-1 overflow-hidden rounded-full bg-zinc-200" aria-label="Carregando calendário">
              <div className="h-full w-1/3 animate-pulse rounded-full bg-blue-600" />
            </div>
          )}

          <div className="mt-5">
            {view === "day" ? (
              <div className="mx-auto max-w-3xl">{dayPanel}</div>
            ) : (
              <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
                <div className="min-w-0">
                  {view === "month" ? (
                    <MonthView
                      cursorDate={cursorDate}
                      selectedDate={selectedDate}
                      records={recordsMap}
                      onSelect={handleSelectDate}
                    />
                  ) : (
                    <WeekView
                      cursorDate={cursorDate}
                      selectedDate={selectedDate}
                      records={recordsMap}
                      onSelect={handleSelectDate}
                    />
                  )}
                </div>
                <aside className="min-w-0 xl:sticky xl:top-7 xl:self-start">{dayPanel}</aside>
              </div>
            )}
          </div>
        </div>
      )}
    </AppShell>
  )
}

export default App
