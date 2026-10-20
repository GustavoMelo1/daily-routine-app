import { useEffect, useState } from 'react'
import { ChevronDown, ChevronRight, Plus, Pencil, Trash2 } from 'lucide-react'
import { listLearningNodes, createLearningNode, updateLearningNode, deleteLearningNode, getApiErrorMessage } from '../../api/client'
import ConfirmDialog from '../ConfirmDialog'
import StatusMessage from '../StatusMessage'
import LearningNote from './LearningNote'

const button = 'rounded-lg border border-zinc-300 px-3 py-2 text-sm hover:bg-zinc-50 disabled:opacity-50 dark:border-zinc-700 dark:hover:bg-zinc-800'

function TreeNode({ node, childrenByParent, busy, onToggle, onEdit, onAdd, onDelete, onSelect, selectedId }) {
  const [expanded, setExpanded] = useState(true)
  const children = childrenByParent.get(node.id) || []
  return <li>
    <div className={`flex flex-wrap items-center gap-2 rounded-md px-2 py-2 ${selectedId === node.id ? 'bg-blue-50 dark:bg-blue-950/40' : 'hover:bg-zinc-100 dark:hover:bg-zinc-900'}`}>
      <button type="button" disabled={!children.length} onClick={() => setExpanded(!expanded)} aria-label={`${expanded ? 'Recolher' : 'Expandir'} ${node.title}`} aria-expanded={children.length ? expanded : undefined} className="rounded p-1 disabled:opacity-0">
        {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
      </button>
      <label className="flex min-w-0 flex-1 items-center gap-3">
        <input type="checkbox" checked={node.completed} disabled={busy} onChange={() => onToggle(node)} className="size-4 shrink-0 accent-blue-600" />
        <span className={`break-words text-sm font-medium ${node.completed ? 'text-zinc-500 line-through dark:text-zinc-400' : ''}`}>{node.title}</span>
      </label>
      <div className="flex gap-1 [&_button]:border-transparent [&_button]:px-2 [&_button]:text-zinc-500 dark:[&_button]:text-zinc-400">
        <button className={`${button} ${selectedId === node.id ? 'text-blue-600 dark:text-blue-400' : ''}`} disabled={busy} onClick={() => onSelect(node)} aria-label={`Abrir nota de ${node.title}`} aria-pressed={selectedId === node.id}>Nota</button>
        <button className={button} disabled={busy} onClick={() => onAdd(node)} aria-label={`Adicionar subtópico em ${node.title}`}><Plus size={15} /></button>
        <button className={button} disabled={busy} onClick={() => onEdit(node)} aria-label={`Renomear ${node.title}`}><Pencil size={15} /></button>
        <button className={button} disabled={busy} onClick={() => onDelete(node)} aria-label={`Excluir ${node.title}`}><Trash2 size={15} /></button>
      </div>
    </div>
    {expanded && children.length > 0 && <ul className="ml-3 mt-2 space-y-2 border-l border-zinc-200 pl-3 dark:border-zinc-700 sm:ml-5">{children.map((child) => <TreeNode key={child.id} node={child} childrenByParent={childrenByParent} busy={busy} onToggle={onToggle} onEdit={onEdit} onAdd={onAdd} onDelete={onDelete} onSelect={onSelect} selectedId={selectedId} />)}</ul>}
  </li>
}

export default function LearningTree({ onNavigationGuardChange }) {
  const [nodes, setNodes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [revision, setRevision] = useState(0)
  const [form, setForm] = useState(null)
  const [title, setTitle] = useState('')
  const [deleting, setDeleting] = useState(null)
  const [message, setMessage] = useState('')
  const [selectedId, setSelectedId] = useState(null)
  const [noteDirty, setNoteDirty] = useState(false)
  const [noteBusy, setNoteBusy] = useState(false)
  const [search, setSearch] = useState('')
  const selected = nodes.find((node) => node.id === selectedId)
  const dirty = form !== null && title !== (form.node?.title || '')
  useEffect(() => {
    const guard = () => !busy && !noteBusy && (!(dirty || noteDirty) || window.confirm('Descartar alterações não salvas?'))
    onNavigationGuardChange(guard)
    function unload(event) { if (dirty || busy || noteDirty || noteBusy) { event.preventDefault(); event.returnValue = '' } }
    window.addEventListener('beforeunload', unload)
    return () => { onNavigationGuardChange(null); window.removeEventListener('beforeunload', unload) }
  }, [dirty, busy, noteDirty, noteBusy, onNavigationGuardChange])
  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    listLearningNodes(controller.signal).then(setNodes)
      .catch((failure) => { if (failure.name !== 'AbortError') setError(getApiErrorMessage(failure)) })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [revision])
  const childrenByParent = new Map()
  for (const node of nodes) {
    if (!childrenByParent.has(node.parent_id)) childrenByParent.set(node.parent_id, [])
    childrenByParent.get(node.parent_id).push(node)
  }
  function openForm(next) {
    if (dirty && !window.confirm('Descartar o tópico não salvo?')) return
    setForm(next); setTitle(next.node?.title || ''); setMessage('')
  }
  function selectNote(node) {
    if (node.id === selectedId || noteBusy) return
    if (noteDirty && !window.confirm('Descartar as alterações da nota atual?')) return
    setNoteDirty(false); setSelectedId(node.id)
  }
  async function mutate(action, success) {
    setBusy(true); setError(''); setMessage('')
    try { await action(); setMessage(success); return true }
    catch (failure) { setError(getApiErrorMessage(failure)); return false }
    finally { setBusy(false) }
  }
  async function save(event) {
    event.preventDefault()
    if (!title.trim()) return
    const ok = await mutate(async () => {
      if (form.node) {
        await updateLearningNode(form.node.id, { title: title.trim(), completed: form.node.completed })
        setNodes((all) => all.map((node) => node.id === form.node.id ? { ...node, title: title.trim() } : node))
      } else {
        const created = await createLearningNode({ title: title.trim(), parent_id: form.parent?.id ?? null })
        setNodes((all) => [...all, created])
      }
    }, 'Tópico salvo.')
    if (ok) { setForm(null); setTitle('') }
  }
  function toggle(node) {
    mutate(async () => {
      await updateLearningNode(node.id, { title: node.title, completed: !node.completed })
      setNodes((all) => all.map((item) => item.id === node.id ? { ...item, completed: !node.completed } : item))
    }, node.completed ? 'Tópico reaberto.' : 'Tópico concluído.')
  }
  const descendants = new Set()
  if (deleting) {
    const pending = [deleting.id]
    while (pending.length) {
      const id = pending.pop(); descendants.add(id)
      for (const child of childrenByParent.get(id) || []) pending.push(child.id)
    }
  }
  async function remove() {
    const ok = await mutate(async () => {
      await deleteLearningNode(deleting.id)
      setNodes((all) => all.filter((node) => !descendants.has(node.id)))
      if (descendants.has(selectedId)) { setSelectedId(null); setNoteDirty(false) }
    }, 'Tópico e seus subtópicos excluídos.')
    if (ok) setDeleting(null)
  }
  const completed = nodes.filter((node) => node.completed).length
  return <section>
    <header className="flex flex-wrap items-start justify-between gap-4">
      <div><h1 className="text-2xl font-semibold tracking-tight">Árvore de aprendizado</h1><p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Assuntos para estudar, com suas notas em cada tópico.</p></div>
      <button disabled={busy || loading || Boolean(form)} onClick={() => openForm({})} className={`${button} text-blue-600 dark:text-blue-400`}>Nova área</button>
    </header>
    {error && <div className="mt-4"><StatusMessage title="Não foi possível concluir a operação" description={error} onRetry={() => { setError(''); setRevision((v) => v + 1) }} /></div>}
    <p role="status" className="mt-4 min-h-5 text-sm text-blue-700 dark:text-blue-300">{message}</p>
    {form && <form onSubmit={save} className="my-4 space-y-3 rounded-xl border border-blue-200 bg-white p-5 dark:border-blue-900 dark:bg-zinc-900">
      <h2 className="font-semibold">{form.node ? 'Renomear tópico' : form.parent ? `Novo subtópico em ${form.parent.title}` : 'Nova área de aprendizado'}</h2>
      <label className="block text-sm">Nome do tópico<input autoFocus required maxLength={160} value={title} disabled={busy} onChange={(e) => setTitle(e.target.value)} placeholder="Ex.: Engenharia de dados, Python, Funções…" className="mt-2 w-full rounded-lg border border-zinc-300 bg-transparent px-3 py-2 dark:border-zinc-700" /></label>
      <div className="flex gap-2"><button type="submit" className={button} disabled={busy || !title.trim()}>{busy ? 'Salvando…' : 'Salvar tópico'}</button><button type="button" disabled={busy} className={button} onClick={() => { if (!dirty || window.confirm('Descartar o tópico não salvo?')) setForm(null) }}>Cancelar</button></div>
    </form>}
    {loading && !nodes.length ? <p role="status" className="py-6">Carregando sua árvore…</p> : <>
      <div className="my-4 flex items-center justify-between border-b border-zinc-200 pb-3 text-sm text-zinc-500 dark:border-zinc-800"><span>{(childrenByParent.get(null) || []).length} áreas</span><span>{completed} de {nodes.length} itens marcados · checklist pessoal</span></div>
      {!nodes.length && !error && <div className="rounded-xl border border-dashed border-zinc-300 p-8 dark:border-zinc-700"><h2 className="font-semibold">Por onde você quer começar?</h2><p className="mt-2 text-sm leading-7 text-zinc-500">Crie “Engenharia de dados”. Depois use o botão + para adicionar “Python” e, dentro dele, “Variáveis”, “Funções” e o que mais quiser aprender.</p></div>}
      <label className="mb-4 block text-sm font-medium">Buscar tópicos e notas<input type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Ex.: Python, SQL, parâmetros…" className="mt-2 w-full rounded-lg border border-zinc-300 bg-transparent px-3 py-2 dark:border-zinc-700" /></label>
      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <div className="min-w-0 overflow-x-auto pb-4">
          {search.trim() ? <ul className="space-y-2" aria-label="Resultados da busca">
            {nodes.filter((node) => `${node.title} ${node.notes || ''}`.toLocaleLowerCase('pt-BR').includes(search.trim().toLocaleLowerCase('pt-BR'))).map((node) => <li key={node.id}><button disabled={noteBusy || busy || Boolean(form)} className={`${button} w-full text-left`} onClick={() => selectNote(node)}>{node.title}<span className="ml-2 text-xs text-zinc-500">{nodes.find((parent) => parent.id === node.parent_id)?.title || 'Área principal'}</span></button></li>)}
            {!nodes.some((node) => `${node.title} ${node.notes || ''}`.toLocaleLowerCase('pt-BR').includes(search.trim().toLocaleLowerCase('pt-BR'))) && <li className="p-4 text-sm text-zinc-500">Nenhum tópico ou nota encontrado.</li>}
          </ul> : <ul className="space-y-3">{(childrenByParent.get(null) || []).map((node) => <TreeNode key={node.id} node={node} childrenByParent={childrenByParent} busy={busy || noteBusy || Boolean(form)} onToggle={toggle} onEdit={(item) => openForm({ node: item })} onAdd={(parent) => openForm({ parent })} onSelect={selectNote} selectedId={selectedId} onDelete={(item) => { if (!noteDirty || window.confirm('A exclusão pode remover a nota em edição. Continuar?')) setDeleting(item) }} />)}</ul>}
        </div>
        {selected ? <LearningNote key={selected.id} node={selected} onDirtyChange={setNoteDirty} onBusyChange={setNoteBusy} onSaved={(id, result) => setNodes((all) => all.map((node) => node.id === id ? { ...node, ...result } : node))} /> : <div className="border-l border-zinc-200 px-6 py-4 text-sm leading-6 text-zinc-500 dark:border-zinc-800 dark:text-zinc-400"><h2 className="font-medium text-zinc-800 dark:text-zinc-200">Notas do tópico</h2><p className="mt-2">Selecione “Nota” em um tópico para escrever ou consultar suas anotações.</p></div>}
      </div>
    </>}
    <ConfirmDialog open={Boolean(deleting)} title={`Excluir ${deleting?.title || 'tópico'}?`} description={`Serão excluídos este item e seus subtópicos (${descendants.size} itens no total). Não é possível desfazer.`} confirmLabel="Excluir árvore" busy={busy} onConfirm={remove} onCancel={() => setDeleting(null)} />
  </section>
}
