import { CheckCircle2, Clock3, Plus, Quote, Tag, Trash2 } from "lucide-react"
import { useEffect, useState } from "react"

import {
  createTask,
  getApiErrorMessage,
  removeDay,
  removeTask,
  updateTask,
} from "../api/client"
import { formatLongDate } from "../utils/date"
import ConfirmDialog from "./ConfirmDialog"
import DayForm from "./DayForm"
import StatusMessage from "./StatusMessage"

function LoadingPanel() {
  return (
    <div className="animate-pulse space-y-4 p-5" aria-label="Carregando detalhes do dia">
      <div className="h-4 w-28 rounded bg-zinc-200 dark:bg-zinc-700" />
      <div className="h-7 w-3/4 rounded bg-zinc-200 dark:bg-zinc-700" />
      <div className="h-20 rounded bg-zinc-100 dark:bg-zinc-800" />
      <div className="h-12 rounded bg-zinc-100 dark:bg-zinc-800" />
      <div className="h-12 rounded bg-zinc-100 dark:bg-zinc-800" />
    </div>
  )
}

export default function DayPanel({ date, day, loading, error, onRetry, onChanged }) {
  const [taskDescription, setTaskDescription] = useState("")
  const [actionError, setActionError] = useState("")
  const [busyAction, setBusyAction] = useState("")
  const [confirmation, setConfirmation] = useState(null)

  useEffect(() => {
    setTaskDescription("")
    setActionError("")
    setBusyAction("")
    setConfirmation(null)
  }, [date])

  if (loading) return <LoadingPanel />
  if (error) {
    return (
      <div className="p-5">
        <StatusMessage title="Não foi possível carregar este dia" description={error} onRetry={onRetry} />
      </div>
    )
  }
  if (!day) return <DayForm date={date} onCreated={onChanged} />

  async function handleCreateTask(event) {
    event.preventDefault()
    const description = taskDescription.trim()
    if (!description) {
      setActionError("Digite uma descrição para a tarefa.")
      return
    }

    setBusyAction("create-task")
    setActionError("")
    try {
      await createTask({ dia_id: day.id, descricao: description, cumprida: 0 })
      setTaskDescription("")
      onChanged()
    } catch (requestError) {
      setActionError(getApiErrorMessage(requestError))
    } finally {
      setBusyAction("")
    }
  }

  async function handleToggleTask(task) {
    setBusyAction(`task-${task.id}`)
    setActionError("")
    try {
      await updateTask(task.id, Number(task.cumprida) !== 1)
      onChanged()
    } catch (requestError) {
      setActionError(getApiErrorMessage(requestError))
    } finally {
      setBusyAction("")
    }
  }

  async function confirmDelete() {
    const target = confirmation
    if (!target) return

    setBusyAction("delete")
    setActionError("")

    try {
      if (target.type === "task") {
        await removeTask(target.task.id)
      } else {
        for (const task of day.tarefas) {
          await removeTask(task.id)
        }
        await removeDay(day.data)
      }
      setConfirmation(null)
      onChanged()
    } catch (requestError) {
      setConfirmation(null)
      setActionError(
        target.type === "day"
          ? `A exclusão foi interrompida. Os dados serão recarregados. ${getApiErrorMessage(requestError)}`
          : getApiErrorMessage(requestError),
      )
      onChanged()
    } finally {
      setBusyAction("")
    }
  }

  const completedTasks = day.tarefas.filter((task) => Number(task.cumprida) === 1).length

  return (
    <div>
      <div className="border-b border-zinc-200 px-5 py-4 dark:border-zinc-800">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-blue-600">Dia registrado</p>
            <h2 className="mt-1 text-lg font-semibold capitalize text-zinc-950 dark:text-zinc-100">
              {formatLongDate(day.data)}
            </h2>
          </div>
          <button
            type="button"
            onClick={() => setConfirmation({ type: "day" })}
            className="rounded-lg p-2 text-zinc-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/50 dark:hover:text-red-400"
            aria-label="Excluir dia"
          >
            <Trash2 size={17} />
          </button>
        </div>
      </div>

      <div className="space-y-5 p-5">
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-3 dark:border-zinc-800 dark:bg-zinc-950">
            <div className="flex items-center gap-2 text-xs font-medium text-zinc-500 dark:text-zinc-400">
              <Clock3 size={15} />
              Estudo
            </div>
            <p className="mt-2 text-xl font-semibold text-zinc-950 dark:text-zinc-100">{day.minutos_estudados} min</p>
          </div>
          <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-3 dark:border-zinc-800 dark:bg-zinc-950">
            <div className="flex items-center gap-2 text-xs font-medium text-zinc-500 dark:text-zinc-400">
              <CheckCircle2 size={15} />
              Tarefas
            </div>
            <p className="mt-2 text-xl font-semibold text-zinc-950 dark:text-zinc-100">
              {completedTasks}/{day.tarefas.length}
            </p>
          </div>
        </div>

        <div className="rounded-xl border border-zinc-200 p-4 dark:border-zinc-800">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            <Quote size={15} />
            Frase do dia
          </div>
          <blockquote className="mt-3 text-sm leading-6 text-zinc-800 dark:text-zinc-200">
            {day.frase_do_dia ? `“${day.frase_do_dia}”` : "Nenhuma frase informada."}
          </blockquote>
          <p className="mt-2 text-xs text-zinc-500 dark:text-zinc-400">
            {day.autor_frase ? `— ${day.autor_frase}` : "Autor não informado"}
          </p>
        </div>

        <div className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400">
          <Tag size={15} />
          <span className="rounded-md bg-zinc-100 px-2 py-1 font-medium dark:bg-zinc-800">{day.tipo || "Sem tipo"}</span>
        </div>

        <section aria-labelledby="tasks-title">
          <div className="flex items-center justify-between">
            <h3 id="tasks-title" className="text-sm font-semibold text-zinc-950 dark:text-zinc-100">
              Tarefas do dia
            </h3>
            <span className="text-xs text-zinc-500 dark:text-zinc-400">{completedTasks} concluídas</span>
          </div>

          <div className="mt-3 space-y-2">
            {day.tarefas.length === 0 && (
              <p className="rounded-lg border border-dashed border-zinc-300 px-3 py-4 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:text-zinc-400">
                Nenhuma tarefa cadastrada.
              </p>
            )}
            {day.tarefas.map((task) => {
              const completed = Number(task.cumprida) === 1
              const taskBusy = busyAction === `task-${task.id}`
              return (
                <div key={task.id} className="flex items-center gap-3 rounded-lg border border-zinc-200 px-3 py-2.5 dark:border-zinc-800">
                  <input
                    type="checkbox"
                    checked={completed}
                    disabled={taskBusy || busyAction === "delete"}
                    onChange={() => handleToggleTask(task)}
                    className="h-4 w-4 rounded border-zinc-300 text-blue-600 focus:ring-blue-500"
                    aria-label={`Marcar ${task.descricao} como ${completed ? "pendente" : "concluída"}`}
                  />
                  <span className={`min-w-0 flex-1 text-sm ${completed ? "text-zinc-400 line-through dark:text-zinc-600" : "text-zinc-800 dark:text-zinc-200"}`}>
                    {task.descricao || "Tarefa sem descrição"}
                  </span>
                  <button
                    type="button"
                    onClick={() => setConfirmation({ type: "task", task })}
                    disabled={busyAction === "delete"}
                    className="rounded-md p-1.5 text-zinc-400 hover:bg-red-50 hover:text-red-600 disabled:opacity-50 dark:hover:bg-red-950/50 dark:hover:text-red-400"
                    aria-label={`Excluir tarefa ${task.descricao}`}
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              )
            })}
          </div>

          <form onSubmit={handleCreateTask} className="mt-3 flex gap-2">
            <input
              type="text"
              value={taskDescription}
              onChange={(event) => setTaskDescription(event.target.value)}
              placeholder="Nova tarefa"
              disabled={busyAction === "create-task"}
              className="min-w-0 flex-1 rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm outline-none placeholder:text-zinc-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-100 dark:placeholder:text-zinc-600 dark:focus:ring-blue-950"
            />
            <button
              type="submit"
              disabled={busyAction === "create-task"}
              className="inline-flex items-center gap-2 rounded-lg bg-zinc-900 px-3 py-2 text-sm font-semibold text-white hover:bg-zinc-800 disabled:cursor-wait disabled:opacity-60 dark:bg-zinc-100 dark:text-zinc-950 dark:hover:bg-white"
            >
              <Plus size={16} />
              Adicionar
            </button>
          </form>
        </section>

        {actionError && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300">{actionError}</p>}

        <p className="border-t border-zinc-200 pt-4 text-xs leading-5 text-zinc-500 dark:border-zinc-800 dark:text-zinc-400">
          Os dados principais do dia são somente leitura. Para alterá-los, exclua este registro e crie outro.
        </p>
      </div>

      <ConfirmDialog
        open={Boolean(confirmation)}
        title={confirmation?.type === "day" ? "Excluir este dia?" : "Excluir esta tarefa?"}
        description={
          confirmation?.type === "day"
            ? `As ${day.tarefas.length} tarefas vinculadas também serão excluídas. Essa ação não pode ser desfeita.`
            : `A tarefa “${confirmation?.task?.descricao || ""}” será removida permanentemente.`
        }
        confirmLabel={confirmation?.type === "day" ? "Excluir dia" : "Excluir tarefa"}
        busy={busyAction === "delete"}
        onConfirm={confirmDelete}
        onCancel={() => setConfirmation(null)}
      />
    </div>
  )
}
