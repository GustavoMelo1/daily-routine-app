import { useEffect, useState } from 'react'
import { ChevronDown, ChevronRight, Plus, Pencil, Trash2 } from 'lucide-react'
import { listLearningNodes, createLearningNode, updateLearningNode, deleteLearningNode, getApiErrorMessage } from '../../api/client'
import ConfirmDialog from '../ConfirmDialog'
import StatusMessage from '../StatusMessage'

const button = 'rounded-lg border border-zinc-300 px-3 py-2 text-sm hover:bg-zinc-50 disabled:opacity-50 dark:border-zinc-700 dark:hover:bg-zinc-800'

function TreeNode({ node, childrenByParent, busy, onToggle, onEdit, onAdd, onDelete }) {
  const [expanded, setExpanded] = useState(true)
  const children = childrenByParent.get(node.id) || []
  return <li>
    <div className="flex flex-wrap items-center gap-2 rounded-lg border border-zinc-200 bg-white p-3 dark:border-zinc-800 dark:bg-zinc-900">
      <button type="button" disabled={!children.length} onClick={() => setExpanded(!expanded)} aria-label={`${expanded ? 'Recolher' : 'Expandir'} ${node.title}`} aria-expanded={children.length ? expanded : undefined} className="rounded p-1 disabled:opacity-0">
        {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
      </button>
      <label className="flex min-w-0 flex-1 items-center gap-3">
        <input type="checkbox" checked={node.completed} disabled={busy} onChange={() => onToggle(node)} className="size-4 shrink-0 accent-blue-600" />
        <span className={`break-words text-sm font-medium ${node.completed ? 'text-zinc-500 line-through dark:text-zinc-400' : ''}`}>{node.title}</span>
      </label>
      <div className="flex gap-1">
        <button className={button} disabled={busy} onClick={() => onAdd(node)} aria-label={`Adicionar subtópico em ${node.title}`}><Plus size={15} /></button>
        <button className={button} disabled={busy} onClick={() => onEdit(node)} aria-label={`Renomear ${node.title}`}><Pencil size={15} /></button>
        <button className={button} disabled={busy} onClick={() => onDelete(node)} aria-label={`Excluir ${node.title}`}><Trash2 size={15} /></button>
      </div>
    </div>
    {expanded && children.length > 0 && <ul className="ml-3 mt-2 space-y-2 border-l border-zinc-200 pl-3 dark:border-zinc-700 sm:ml-5">{children.map((child) => <TreeNode key={child.id} node={child} childrenByParent={childrenByParent} busy={busy} onToggle={onToggle} onEdit={onEdit} onAdd={onAdd} onDelete={onDelete} />)}</ul>}
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
  const dirty = form !== null && title !== (form.node?.title || '')
  useEffect(() => {
    const guard = () => !busy && (!dirty || window.confirm('Descartar o tópico não salvo?'))
    onNavigationGuardChange(guard)
    function unload(event) { if (dirty || busy) { event.preventDefault(); event.returnValue = '' } }
    window.addEventListener('beforeunload', unload)
    return () => { onNavigationGuardChange(null); window.removeEventListener('beforeunload', unload) }
  }, [dirty, busy, onNavigationGuardChange])
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
    }, 'Tópico e seus subtópicos excluídos.')
    if (ok) setDeleting(null)
  }
  const completed = nodes.filter((node) => node.completed).length
  return <section>
    <header className="flex flex-wrap items-start justify-between gap-4">
      <div><p className="text-sm font-medium text-blue-600 dark:text-blue-400">Seu caminho de estudo</p><h1 className="mt-1 text-2xl font-semibold">Árvore de aprendizado</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500 dark:text-zinc-400">Organize áreas, assuntos e subtópicos. Cada checkbox é independente: marcar Python não marca automaticamente tudo dentro dele.</p></div>
      <button disabled={busy || loading || Boolean(form)} onClick={() => openForm({})} className={`${button} text-blue-600 dark:text-blue-400`}>Nova área</button>
    </header>
    {error && <div className="mt-4"><StatusMessage title="Não foi possível concluir a operação" description={error} onRetry={() => { setError(''); setRevision((v) => v + 1) }} /></div>}
    <p role="status" className="mt-4 min-h-5 text-sm text-blue-700 dark:text-blue-300">{message}</p>
    {form && <form onSubmit={save} className="my-4 space-y-3 rounded-xl border border-blue-200 bg-white p-5 dark:border-blue-900 dark:bg-zinc-900">
      <h2 className="font-semibold">{form.node ? 'Renomear tópico' : form.parent ? `Novo subtópico em ${form.parent.title}` : 'Nova área de aprendizado'}</h2>
      <label className="block text-sm">Nome do tópico<input autoFocus required maxLength={160} value={title} disabled={busy} onChange={(e) => setTitle(e.target.value)} placeholder="Ex.: Engenharia de dados, Python, Funções…" className="mt-2 w-full rounded-lg border border-zinc-300 bg-transparent px-3 py-2 dark:border-zinc-700" /></label>
      <div className="flex gap-2"><button type="submit" className={button} disabled={busy || !title.trim()}>{busy ? 'Salvando…' : 'Salvar tópico'}</button><button type="button" disabled={busy} className={button} onClick={() => { if (!dirty || window.confirm('Descartar o tópico não salvo?')) setForm(null) }}>Cancelar</button></div>
    </form>}
    {loading ? <p role="status" className="py-6">Carregando sua árvore…</p> : <>
      <div className="my-4 flex items-center justify-between border-b border-zinc-200 pb-3 text-sm text-zinc-500 dark:border-zinc-800"><span>{(childrenByParent.get(null) || []).length} áreas</span><span>{completed} de {nodes.length} itens marcados · checklist pessoal</span></div>
      {!nodes.length && !error && <div className="rounded-xl border border-dashed border-zinc-300 p-8 dark:border-zinc-700"><h2 className="font-semibold">Por onde você quer começar?</h2><p className="mt-2 text-sm leading-7 text-zinc-500">Crie “Engenharia de dados”. Depois use o botão + para adicionar “Python” e, dentro dele, “Variáveis”, “Funções” e o que mais quiser aprender.</p></div>}
      <div className="overflow-x-auto pb-4"><ul className="space-y-3">{(childrenByParent.get(null) || []).map((node) => <TreeNode key={node.id} node={node} childrenByParent={childrenByParent} busy={busy || Boolean(form)} onToggle={toggle} onEdit={(item) => openForm({ node: item })} onAdd={(parent) => openForm({ parent })} onDelete={setDeleting} />)}</ul></div>
    </>}
    <ConfirmDialog open={Boolean(deleting)} title={`Excluir ${deleting?.title || 'tópico'}?`} description={`Serão excluídos este item e seus subtópicos (${descendants.size} itens no total). Não é possível desfazer.`} confirmLabel="Excluir árvore" busy={busy} onConfirm={remove} onCancel={() => setDeleting(null)} />
  </section>
}
