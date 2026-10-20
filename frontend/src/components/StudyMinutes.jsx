import { useState } from 'react'
import { updateDayMinutes, getApiErrorMessage } from '../api/client'

export default function StudyMinutes({ day, onChanged }) {
  const [minutes, setMinutes] = useState(String(day.minutos_estudados))
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function save(event) {
    event.preventDefault()
    const value = Number(minutes)
    if (!minutes.trim() || !Number.isInteger(value) || value < 0 || value > 1440) {
      setError('Informe minutos entre 0 e 1440.'); return
    }
    setBusy(true); setError('')
    try { await updateDayMinutes(day.data, value); onChanged() }
    catch (failure) { setError(getApiErrorMessage(failure)) }
    finally { setBusy(false) }
  }
  return <form onSubmit={save} className="space-y-2 rounded-xl border border-zinc-200 p-4 dark:border-zinc-800">
    <label className="block text-sm font-medium">Tempo estudado de verdade (minutos)
      <input type="number" min={0} max={1440} step={1} required disabled={busy} value={minutes} onChange={(event) => setMinutes(event.target.value)} className="mt-2 w-full rounded-lg border border-zinc-300 bg-transparent px-3 py-2 dark:border-zinc-700" />
    </label>
    <p className="text-xs leading-5 text-zinc-500">Atualize depois de estudar. Planejar tarefas não soma minutos nem conclui tarefas automaticamente.</p>
    <button disabled={busy || Number(minutes) === day.minutos_estudados} className="rounded-lg bg-blue-600 px-3 py-2 text-sm text-white disabled:opacity-50">{busy ? 'Salvando…' : 'Salvar minutos'}</button>
    {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
  </form>
}
