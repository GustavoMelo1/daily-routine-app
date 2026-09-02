import { AlertCircle, RefreshCw } from "lucide-react"

export default function StatusMessage({ title, description, onRetry }) {
  return (
    <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-900 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200" role="alert">
      <div className="flex items-start gap-3">
        <AlertCircle className="mt-0.5 shrink-0" size={18} />
        <div className="min-w-0">
          <p className="text-sm font-semibold">{title}</p>
          {description && <p className="mt-1 text-sm text-red-700 dark:text-red-300">{description}</p>}
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="mt-3 inline-flex items-center gap-2 rounded-lg border border-red-300 bg-white px-3 py-1.5 text-xs font-semibold hover:bg-red-100 dark:border-red-800 dark:bg-red-950 dark:hover:bg-red-900"
            >
              <RefreshCw size={14} />
              Tentar novamente
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
