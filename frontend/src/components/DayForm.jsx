import { useEffect, useState } from "react"

import { createDay, getApiErrorMessage } from "../api/client"
import { formatLongDate } from "../utils/date"

const initialForm = {
  minutos_estudados: "0",
  frase_do_dia: "",
  autor_frase: "",
  tipo: "normal",
}

export default function DayForm({ date, onCreated }) {
  const [form, setForm] = useState(initialForm)
  const [error, setError] = useState("")
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    setForm(initialForm)
    setError("")
  }, [date])

  function updateField(event) {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const minutes = Number(form.minutos_estudados)

    if (!Number.isInteger(minutes) || minutes < 0 || minutes > 1440) {
      setError("Informe minutos entre 0 e 1440.")
      return
    }

    setSubmitting(true)
    setError("")

    try {
      await createDay({
        data: date,
        minutos_estudados: minutes,
        frase_do_dia: form.frase_do_dia.trim(),
        autor_frase: form.autor_frase.trim(),
        tipo: form.tipo.trim(),
      })
      onCreated()
    } catch (requestError) {
      setError(getApiErrorMessage(requestError))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      <div className="border-b border-zinc-200 px-5 py-4 dark:border-zinc-800">
        <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">Novo dia</p>
        <h2 className="mt-1 text-lg font-semibold capitalize text-zinc-950 dark:text-zinc-100">
          {formatLongDate(date)}
        </h2>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4 p-5">
        <label className="block">
          <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Minutos estudados</span>
          <input
            type="number"
            name="minutos_estudados"
            min="0"
            max="1440"
            step="1"
            value={form.minutos_estudados}
            onChange={updateField}
            className="mt-1.5 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-100 dark:focus:ring-blue-950"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Frase do dia</span>
          <textarea
            name="frase_do_dia"
            rows="3"
            value={form.frase_do_dia}
            onChange={updateField}
            className="mt-1.5 w-full resize-none rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-100 dark:focus:ring-blue-950"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Autor da frase</span>
          <input
            type="text"
            name="autor_frase"
            value={form.autor_frase}
            onChange={updateField}
            className="mt-1.5 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-100 dark:focus:ring-blue-950"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Tipo</span>
          <input
            type="text"
            name="tipo"
            value={form.tipo}
            onChange={updateField}
            className="mt-1.5 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-100 dark:focus:ring-blue-950"
          />
        </label>

        {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-wait disabled:opacity-60"
        >
          {submitting ? "Criando..." : "Criar registro do dia"}
        </button>
      </form>
    </div>
  )
}
