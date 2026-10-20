import { useEffect, useState } from 'react'
import { listWeeklyReports, getWeeklyReport, saveWeeklyReport, deleteWeeklyReport, getWeeklyComparison, compareWeeklyReports, getApiErrorMessage } from '../../api/client'
import ReportEditor from './ReportEditor'
import ReportMarkdown from './ReportMarkdown'
import ComparisonView from './ComparisonView'

const emptyReport = { report_date: '', title: '', filename: 'relato.md', content: '' }
const buttonClass = 'rounded-lg border border-zinc-300 px-3 py-2 text-sm disabled:opacity-50 dark:border-zinc-700'

export default function WeeklyEvolution({ onNavigationGuardChange }) {
  const [reports, setReports] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [selected, setSelected] = useState(null)
  const [previousId, setPreviousId] = useState('')
  const [comparison, setComparison] = useState(null)
  const [editor, setEditor] = useState(null)
  const [editorRevision, setEditorRevision] = useState(0)
  const [dirty, setDirty] = useState(false)
  const [busy, setBusy] = useState(false)
  const [loading, setLoading] = useState(true)
  const [comparisonLoading, setComparisonLoading] = useState(false)
  const [comparisonError, setComparisonError] = useState('')
  const [comparisonLookupFailed, setComparisonLookupFailed] = useState(false)
  const [comparisonRevision, setComparisonRevision] = useState(0)
  const [detailError, setDetailError] = useState('')
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  useEffect(() => {
    const guard = () => !busy && (!dirty || window.confirm('Descartar alterações não salvas?'))
    onNavigationGuardChange(guard)
    function beforeUnload(event) { if (dirty || busy) { event.preventDefault(); event.returnValue = '' } }
    window.addEventListener('beforeunload', beforeUnload)
    return () => { onNavigationGuardChange(null); window.removeEventListener('beforeunload', beforeUnload) }
  }, [dirty, busy, onNavigationGuardChange])
  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    listWeeklyReports(controller.signal).then((data) => {
      setReports(data)
      setSelectedId((id) => data.some((item) => item.id === id) ? id : data[0]?.id ?? null)
    }).catch((failure) => { if (failure.name !== 'AbortError') setError(getApiErrorMessage(failure)) })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [revision])
  useEffect(() => {
    const controller = new AbortController()
    setSelected(null)
    setDetailError('')
    setComparison(null)
    setPreviousId('')
    if (selectedId !== null) getWeeklyReport(selectedId, controller.signal).then(setSelected)
      .catch((failure) => { if (failure.name !== 'AbortError') setDetailError(getApiErrorMessage(failure)) })
    return () => controller.abort()
  }, [selectedId, revision])
  const earlier = selected ? reports.filter((report) => report.report_date < selected.report_date) : []
  const comparisonId = Number(previousId || earlier[0]?.id || 0)
  useEffect(() => {
    const controller = new AbortController()
    setComparison(null)
    setComparisonError('')
    setComparisonLookupFailed(false)
    setComparisonLoading(Boolean(selected && comparisonId))
    if (selected && comparisonId) getWeeklyComparison(selected.id, comparisonId, controller.signal)
      .then(setComparison).catch((failure) => {
        if (failure.name !== 'AbortError') {
          setComparisonError(getApiErrorMessage(failure))
          setComparisonLookupFailed(true)
        }
      })
      .finally(() => { if (!controller.signal.aborted) setComparisonLoading(false) })
    return () => controller.abort()
  }, [selected, comparisonId, comparisonRevision])
  function canLeave() { return !busy && (!dirty || window.confirm('Descartar alterações não salvas?')) }
  function openEditor(value) { if (canLeave()) { setEditor(value); setEditorRevision((v) => v + 1); setDirty(false); setError('') } }
  function select(id) { if (canLeave()) { setSelectedId(id); setEditor(null); setDirty(false); setError('') } }
  async function save(form) {
    setBusy(true); setError('')
    try {
      const saved = await saveWeeklyReport(form)
      setSelectedId(saved.id); setEditor(null); setDirty(false); setRevision((value) => value + 1)
    } catch (failure) { setError(getApiErrorMessage(failure)) }
    finally { setBusy(false) }
  }
  async function remove() {
    if (!window.confirm('Excluir este relato e suas comparações? Essa ação não pode ser desfeita.')) return
    setBusy(true); setError('')
    try { await deleteWeeklyReport(selected.id); setSelected(null); setSelectedId(null); setRevision((value) => value + 1) }
    catch (failure) { setError(getApiErrorMessage(failure)) }
    finally { setBusy(false) }
  }
  async function compare() {
    setBusy(true); setComparisonError('')
    try { setComparison(await compareWeeklyReports(selected.id, comparisonId)) }
    catch (failure) { setComparisonError(getApiErrorMessage(failure)) }
    finally { setBusy(false) }
  }
  return <div>
    <header className="flex flex-wrap items-start justify-between gap-4">
      <div><h1 className="text-2xl font-semibold tracking-tight">Evolução semanal</h1><p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Seus relatos e as mudanças entre uma semana e outra.</p></div>
      <button disabled={busy} onClick={() => openEditor({ ...emptyReport })} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50">Importar relato</button>
    </header>
    {error && <div role="alert" className="mt-5 rounded-lg border border-red-200 p-4 text-sm text-red-700 dark:border-red-900 dark:text-red-300">{error}<button className="ml-3 underline" disabled={busy} onClick={() => { setError(''); setRevision((v) => v + 1) }}>Recarregar dados</button></div>}
    <div className="mt-6 grid items-start gap-5 lg:grid-cols-[260px_minmax(0,1fr)]">
      <aside className="border-b border-zinc-200 pb-4 dark:border-zinc-800 lg:border-b-0 lg:border-r lg:pr-4">
        <h2 className="px-2 py-2 text-xs font-medium text-zinc-500 dark:text-zinc-400">Relatos · {reports.length}</h2>
        {loading && <p role="status" className="p-2 text-sm">Carregando…</p>}
        {!loading && !reports.length && <p className="p-2 text-sm leading-6 text-zinc-500">Importe a primeira semana para começar. Você poderá comparar quando tiver dois relatos.</p>}
        <nav aria-label="Relatos semanais" className="max-h-[65vh] space-y-1 overflow-y-auto">{reports.map((report) => <button key={report.id} disabled={busy} onClick={() => select(report.id)} aria-current={selectedId === report.id ? 'true' : undefined} className={`block w-full rounded-lg p-3 text-left disabled:opacity-50 ${selectedId === report.id ? 'bg-blue-50 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300' : 'hover:bg-zinc-50 dark:hover:bg-zinc-800'}`}>
          <span className="block text-xs">{report.report_date.split('-').reverse().join('/')}</span><span className="mt-1 block break-words text-sm font-medium">{report.title}</span>
        </button>)}</nav>
      </aside>
      <section className="min-w-0 lg:pl-2">
        {editor ? <ReportEditor key={editorRevision} initial={editor} busy={busy} onSave={save} onDirty={setDirty} onCancel={() => { if (canLeave()) { setEditor(null); setDirty(false) } }} /> : selected ? <>
          <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-xs text-zinc-500">{selected.report_date.split('-').reverse().join('/')} · Versão {selected.version}</p><h2 className="mt-1 break-words text-xl font-semibold">{selected.title}</h2></div><div className="flex gap-2"><button disabled={busy} onClick={() => openEditor(selected)} className={buttonClass}>Editar</button><button disabled={busy} onClick={remove} className={buttonClass}>Excluir</button></div></div>
          <details className="mt-5 border-y border-zinc-200 py-3 dark:border-zinc-800"><summary className="cursor-pointer break-words text-sm font-medium">Ler relato · {selected.filename}</summary><ReportMarkdown content={selected.content} /></details>
          <div className="mt-6 border-t border-zinc-200 pt-6 dark:border-zinc-800">
            <h3 className="font-semibold">Comparar com uma semana anterior</h3>
            {comparisonError && <div role="alert" className="mt-3 border-l-2 border-red-500 pl-3 text-sm text-red-700 dark:text-red-300">
              <p className="font-medium">{comparisonLookupFailed ? 'Não foi possível buscar a comparação salva.' : 'A comparação não foi gerada.'}</p>
              <p className="mt-1">{comparisonError}</p>
              {comparisonLookupFailed && <button className="mt-2 underline underline-offset-4" onClick={() => setComparisonRevision((v) => v + 1)}>Buscar novamente</button>}
            </div>}
            {earlier.length ? <>
              <label className="mt-3 block text-sm">Relato de referência<select disabled={busy} value={comparisonId} onChange={(e) => { setPreviousId(e.target.value); setError('') }} className="mt-1 w-full rounded-lg border border-zinc-300 bg-white p-2 dark:border-zinc-700 dark:bg-zinc-950">{earlier.map((item) => <option key={item.id} value={item.id}>{item.report_date} — {item.title}</option>)}</select></label>
              {comparisonLoading ? <p role="status" className="mt-4 text-sm">Buscando comparação salva…</p> : comparison ? <ComparisonView comparison={comparison} /> : !comparisonLookupFailed && <>
                <p className="mt-4 max-w-xl text-xs leading-5 text-zinc-500 dark:text-zinc-400">Os dois textos serão enviados ao Google Gemini e a análise ficará salva. O uso está sujeito aos limites e à cobrança do seu projeto. Revise informações pessoais antes de enviar.</p>
                <button disabled={busy} onClick={compare} className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50">{busy ? 'Gerando comparação…' : 'Gerar comparação com IA'}</button>
              </>}
            </> : <p className="mt-3 text-sm leading-6 text-zinc-500">Este é o primeiro relato disponível. Importe uma semana anterior ou uma nova semana para visualizar mudanças.</p>}
          </div>
        </> : detailError ? <div role="alert" className="text-sm text-red-700 dark:text-red-300"><p>Não foi possível abrir o relato. {detailError}</p><button className="mt-3 underline underline-offset-4" onClick={() => setRevision((v) => v + 1)}>Tentar novamente</button></div> : <p role="status" className="py-6 text-sm leading-6 text-zinc-500 dark:text-zinc-400">{selectedId ? 'Carregando relato…' : 'Importe um arquivo .md para guardar sua primeira semana.'}</p>}
      </section>
    </div>
  </div>
}
