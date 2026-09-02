import { useEffect, useRef } from "react"

export default function ConfirmDialog({ open, title, description, confirmLabel, busy, onConfirm, onCancel }) {
  const cancelButtonRef = useRef(null)

  useEffect(() => {
    if (!open) return undefined

    cancelButtonRef.current?.focus()
    function handleKeyDown(event) {
      if (event.key === "Escape" && !busy) onCancel()
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [busy, onCancel, open])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-zinc-950/50 p-4">
      <div
        className="w-full max-w-md rounded-2xl border border-zinc-200 bg-white p-5 dark:border-zinc-700 dark:bg-zinc-900"
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
      >
        <h2 id="confirm-dialog-title" className="text-lg font-semibold text-zinc-950 dark:text-zinc-100">
          {title}
        </h2>
        <p className="mt-2 text-sm leading-6 text-zinc-600 dark:text-zinc-400">{description}</p>
        <div className="mt-6 flex justify-end gap-2">
          <button
            ref={cancelButtonRef}
            type="button"
            onClick={onCancel}
            disabled={busy}
            className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50 disabled:opacity-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={busy}
            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:cursor-wait disabled:opacity-60"
          >
            {busy ? "Excluindo..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
