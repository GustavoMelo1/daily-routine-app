import { BookOpen, CheckCircle2, ChevronLeft, ChevronRight, Flame, ListChecks } from "lucide-react"
import { useEffect, useMemo, useState } from "react"

import { getApiErrorMessage, getDay, getDaysByMonth } from "../api/client"
import {
  calculateLongestStreak,
  formatCompactDate,
  formatMonthYear,
  shiftDate,
} from "../utils/date"
import StatusMessage from "./StatusMessage"

function StatCard({ label, value, helper, icon: Icon }) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-zinc-600 dark:text-zinc-400">{label}</span>
        <Icon size={18} className="text-blue-600" strokeWidth={1.8} />
      </div>
      <p className="mt-4 text-3xl font-semibold tracking-tight text-zinc-950 dark:text-zinc-100">{value}</p>
      <p className="mt-1 text-xs leading-5 text-zinc-500 dark:text-zinc-400">{helper}</p>
    </div>
  )
}

export default function Dashboard() {
  const [periodDate, setPeriodDate] = useState(() => new Date())
  const [days, setDays] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [partialFailures, setPartialFailures] = useState(0)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    async function loadDashboard() {
      setLoading(true)
      setError("")
      setPartialFailures(0)

      try {
        const records = await getDaysByMonth(
          periodDate.getFullYear(),
          periodDate.getMonth() + 1,
          controller.signal,
        )
        const results = await Promise.allSettled(
          records.map((record) => getDay(record.data, controller.signal)),
        )
        const loadedDays = results
          .filter((result) => result.status === "fulfilled" && result.value)
          .map((result) => result.value)
        const failures = results.filter((result) => result.status === "rejected").length

        if (controller.signal.aborted) return
        setDays(loadedDays)
        setPartialFailures(failures)
      } catch (requestError) {
        if (requestError.name !== "AbortError") setError(getApiErrorMessage(requestError))
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }

    loadDashboard()
    return () => controller.abort()
  }, [periodDate, refreshKey])

  const metrics = useMemo(() => {
    const totalMinutes = days.reduce((total, day) => total + day.minutos_estudados, 0)
    const tasks = days.flatMap((day) => day.tarefas)
    const completed = tasks.filter((task) => Number(task.cumprida) === 1).length
    const percentage = tasks.length ? Math.round((completed / tasks.length) * 100) : 0

    return {
      totalMinutes,
      totalTasks: tasks.length,
      completed,
      percentage,
      streak: calculateLongestStreak(days),
    }
  }, [days])

  const sortedDays = useMemo(() => [...days].sort((a, b) => a.data.localeCompare(b.data)), [days])

  return (
    <div>
      <div className="flex flex-col gap-4 border-b border-zinc-200 pb-5 dark:border-zinc-800 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-medium text-blue-600">Visão do período</p>
          <h1 className="mt-1 text-2xl font-semibold capitalize tracking-tight text-zinc-950 dark:text-zinc-100">
            {formatMonthYear(periodDate)}
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setPeriodDate((current) => shiftDate(current, "month", -1))}
            className="rounded-lg border border-zinc-300 bg-white p-2 text-zinc-600 hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800"
            aria-label="Mês anterior"
          >
            <ChevronLeft size={18} />
          </button>
          <button
            type="button"
            onClick={() => setPeriodDate(new Date())}
            className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800"
          >
            Mês atual
          </button>
          <button
            type="button"
            onClick={() => setPeriodDate((current) => shiftDate(current, "month", 1))}
            className="rounded-lg border border-zinc-300 bg-white p-2 text-zinc-600 hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800"
            aria-label="Próximo mês"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      </div>

      {error ? (
        <div className="mt-6">
          <StatusMessage
            title="Não foi possível montar o painel"
            description={error}
            onRetry={() => setRefreshKey((current) => current + 1)}
          />
        </div>
      ) : (
        <>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              label="Minutos estudados"
              value={loading ? "—" : metrics.totalMinutes}
              helper="Soma dos registros do período"
              icon={BookOpen}
            />
            <StatCard
              label="Tarefas concluídas"
              value={loading ? "—" : `${metrics.completed}/${metrics.totalTasks}`}
              helper={`${metrics.percentage}% das tarefas cadastradas`}
              icon={CheckCircle2}
            />
            <StatCard
              label="Maior sequência"
              value={loading ? "—" : `${metrics.streak} dias`}
              helper="Minutos acima de zero + ao menos 1 tarefa feita"
              icon={Flame}
            />
            <StatCard
              label="Dias registrados"
              value={loading ? "—" : days.length}
              helper="Registros detalhados carregados da API"
              icon={ListChecks}
            />
          </div>

          {partialFailures > 0 && (
            <p className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-300">
              {partialFailures} registro(s) não puderam ser carregados. Os totais exibidos são parciais.
            </p>
          )}

          <section className="mt-6 overflow-hidden rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900" aria-labelledby="activity-title">
            <div className="border-b border-zinc-200 px-5 py-4 dark:border-zinc-800">
              <h2 id="activity-title" className="font-semibold text-zinc-950 dark:text-zinc-100">Atividade diária</h2>
              <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Estudo e execução classificados separadamente.</p>
            </div>

            {loading ? (
              <div className="space-y-3 p-5" aria-label="Carregando atividade">
                {[1, 2, 3].map((item) => <div key={item} className="h-12 animate-pulse rounded-lg bg-zinc-100 dark:bg-zinc-800" />)}
              </div>
            ) : sortedDays.length === 0 ? (
              <p className="p-8 text-center text-sm text-zinc-500 dark:text-zinc-400">Nenhum dia registrado neste período.</p>
            ) : (
              <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
                {sortedDays.map((day) => {
                  const completed = day.tarefas.filter((task) => Number(task.cumprida) === 1).length
                  const qualifies = day.minutos_estudados > 0 && completed > 0
                  return (
                    <div key={day.id} className="grid gap-3 px-5 py-4 sm:grid-cols-[110px_1fr_1fr_auto] sm:items-center">
                      <span className="text-sm font-semibold capitalize text-zinc-800 dark:text-zinc-200">{formatCompactDate(day.data)}</span>
                      <span className="text-sm text-zinc-600 dark:text-zinc-400">Estudo: {day.minutos_estudados} min</span>
                      <span className="text-sm text-zinc-600 dark:text-zinc-400">Tarefas: {completed}/{day.tarefas.length}</span>
                      <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-semibold ${
                        qualifies ? "bg-blue-50 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300" : "bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400"
                      }`}>
                        {qualifies ? "Conta na sequência" : "Fora da sequência"}
                      </span>
                    </div>
                  )
                })}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  )
}
