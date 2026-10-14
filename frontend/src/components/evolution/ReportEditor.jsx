import { useState } from 'react'
import { readReportFile } from '../../utils/reports'
import ReportMarkdown from './ReportMarkdown'

const inputClass = 'mt-1 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 dark:border-zinc-700 dark:bg-zinc-950'

export default function ReportEditor({ initial, busy, onSave, onCancel, onDirty }) {
  const [form, setForm] = useState(initial)
  const [error, setError] = useState('')
  const [reading, setReading] = useState(false)
  const [preview, setPreview] = useState(false)
  function change(key, value) {
    setForm((current) => ({ ...current, [key]: value }))
    onDirty(true)
  }
  async function loadFile(event) {
    const file = event.target.files[0]
    if (!file) return
    setReading(true)
    setError('')
    try {
      const imported = await readReportFile(file)
      setForm((current) => ({ ...current, ...imported }))
      onDirty(true)
    } catch (failure) { setError(failure.message) }
    finally { setReading(false); event.target.value = '' }
  }
  function submit(event) {
    event.preventDefault()
    if (!form.content.trim()) { setError('Escreva ou importe o relato.'); return }
    if (!/\.md$/i.test(form.filename) || /[/\\]/.test(form.filename)) { setError('Use apenas o nome de um arquivo .md, sem pastas.'); return }
    onSave(form)
  }
  return (
    <form onSubmit={submit} className="space-y-5">
      <h2 className="text-xl font-semibold">{form.id ? 'Editar relato' : 'Importar relato semanal'}</h2>
      <p className="text-sm text-zinc-500">Importe o Markdown que você já prepara fora do app. Confira a data antes de salvar; nada é enviado ao Gemini nesta etapa.</p>
      <fieldset disabled={busy || reading} className="space-y-4 disabled:opacity-60">
        <label className="block text-sm font-medium">Arquivo .md (UTF-8)
          <input type="file" accept=".md,text/markdown" onChange={loadFile} className="mt-2 block w-full text-sm file:mr-3 file:rounded-lg file:border file:border-zinc-300 file:px-3 file:py-2" />
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="text-sm">Data de referência<input type="date" required value={form.report_date} onChange={(e) => change('report_date', e.target.value)} className={inputClass} /></label>
          <label className="text-sm">Título<input required maxLength={160} value={form.title} onChange={(e) => change('title', e.target.value)} className={inputClass} /></label>
        </div>
        <label className="block text-sm">Nome do arquivo<input required maxLength={255} value={form.filename} onChange={(e) => change('filename', e.target.value)} className={inputClass} /></label>
        <div className="flex items-center justify-between"><span className="text-sm">Conteúdo original</span><button type="button" className="text-sm text-blue-600" onClick={() => setPreview(!preview)}>{preview ? 'Editar texto' : 'Pré-visualizar'}</button></div>
        {preview ? <ReportMarkdown content={form.content} /> : <textarea aria-label="Conteúdo do relato" required rows={14} maxLength={100000} value={form.content} onChange={(e) => change('content', e.target.value)} className={`${inputClass} font-mono text-sm`} />}
        {form.id && <p className="text-xs text-zinc-500">Salvar uma edição remove comparações antigas que usam este relato.</p>}
        <div className="flex gap-3"><button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white" type="submit">{busy ? 'Salvando…' : 'Salvar relato'}</button><button type="button" onClick={onCancel} className="rounded-lg border border-zinc-300 px-4 py-2 text-sm dark:border-zinc-700">Cancelar</button></div>
      </fieldset>
      {reading && <p role="status">Lendo arquivo…</p>}
      {error && <p role="alert" className="text-sm text-red-600 dark:text-red-400">{error}</p>}
    </form>
  )
}
