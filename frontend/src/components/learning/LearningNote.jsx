import { useState } from 'react'
import { saveLearningNotes, getApiErrorMessage } from '../../api/client'
import ReportMarkdown from '../evolution/ReportMarkdown'

export default function LearningNote({ node, onSaved, onDirtyChange, onBusyChange }) {
  const [text, setText] = useState(node.notes || '')
  const [savedText, setSavedText] = useState(node.notes || '')
  const [version, setVersion] = useState(node.notes_version || 1)
  const [preview, setPreview] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const dirty = text !== savedText
  async function save() {
    setSaving(true); onBusyChange(true); setError('')
    try {
      const result = await saveLearningNotes(node.id, { notes: text, version })
      setSavedText(text); setVersion(result.notes_version); onDirtyChange(false)
      onSaved(node.id, result)
    } catch (failure) { setError(getApiErrorMessage(failure)) }
    finally { setSaving(false); onBusyChange(false) }
  }
  function download() {
    const url = URL.createObjectURL(new Blob([text], { type: 'text/markdown;charset=utf-8' }))
    const link = document.createElement('a')
    link.href = url; link.download = `topico-${node.id}.md`; link.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
  return <section aria-label={`Nota de ${node.title}`} className="min-w-0 rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
    <p className="text-xs font-medium uppercase tracking-wide text-blue-600 dark:text-blue-400">Sua base de conhecimento</p>
    <h2 className="mt-2 break-words text-xl font-semibold">{node.title}</h2>
    <p className="mt-2 text-sm leading-6 text-zinc-500">Escreva o que aprendeu, exemplos e referências. Esta nota é local: não é enviada à IA.</p>
    <div className="my-4 flex flex-wrap gap-2">
      <button type="button" onClick={() => setPreview(false)} aria-pressed={!preview} className="rounded-lg border px-3 py-2 text-sm dark:border-zinc-700">Editar Markdown</button>
      <button type="button" onClick={() => setPreview(true)} aria-pressed={preview} className="rounded-lg border px-3 py-2 text-sm dark:border-zinc-700">Ler nota</button>
      <button type="button" onClick={download} className="rounded-lg border px-3 py-2 text-sm dark:border-zinc-700">Baixar .md</button>
    </div>
    {preview ? <div className="min-h-72"><ReportMarkdown content={text || '*Esta nota ainda está vazia.*'} /></div> : <>
      <label htmlFor="learning-note" className="text-sm font-medium">Anotações</label>
      <textarea id="learning-note" rows={18} maxLength={100000} disabled={saving} value={text} onChange={(event) => { setText(event.target.value); onDirtyChange(event.target.value !== savedText) }} placeholder={'## O que aprendi\n\n- Conceito principal\n\n## Exemplo\n\n## Referências\n[Documentação](https://...)'} className="mt-2 w-full resize-y rounded-lg border border-zinc-300 bg-transparent p-3 font-mono text-sm leading-6 dark:border-zinc-700" />
      <p className="mt-1 text-xs text-zinc-500">Markdown: ## título · - lista · **destaque** · [texto](link)</p>
    </>}
    {error && <p role="alert" className="mt-4 text-sm text-red-600 dark:text-red-400">{error} Seu texto continua no editor; você também pode baixar uma cópia.</p>}
    <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
      <p role="status" className="text-xs text-zinc-500">{saving ? 'Salvando…' : dirty ? 'Alterações não salvas' : 'Sem alterações pendentes'} · {text.length.toLocaleString('pt-BR')} caracteres</p>
      <button disabled={!dirty || saving} onClick={save} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50">Salvar nota</button>
    </div>
  </section>
}
