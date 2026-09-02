import { BarChart3, CalendarDays } from "lucide-react"

const navigation = [
  { id: "calendar", label: "Calendário", icon: CalendarDays },
  { id: "dashboard", label: "Painel", icon: BarChart3 },
]

function Navigation({ activeSection, onChange }) {
  return navigation.map(({ id, label, icon: Icon }) => {
    const active = activeSection === id
    return (
      <button
        key={id}
        type="button"
        onClick={() => onChange(id)}
        className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
          active
            ? "bg-blue-50 text-blue-700"
            : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-950"
        }`}
        aria-current={active ? "page" : undefined}
      >
        <Icon size={18} strokeWidth={1.8} />
        {label}
      </button>
    )
  })
}

export default function AppShell({ activeSection, onSectionChange, children }) {
  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-950">
      <aside className="fixed inset-y-0 left-0 hidden w-60 border-r border-zinc-200 bg-white px-4 py-6 md:flex md:flex-col">
        <div className="px-3">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-600">
            Daily Routine
          </p>
          <p className="mt-2 text-sm text-zinc-500">Agenda e consistência</p>
        </div>
        <nav className="mt-8 flex flex-col gap-1" aria-label="Navegação principal">
          <Navigation activeSection={activeSection} onChange={onSectionChange} />
        </nav>
        <div className="mt-auto border-t border-zinc-200 px-3 pt-4 text-xs leading-5 text-zinc-500">
          Dados sincronizados com a API local.
        </div>
      </aside>

      <div className="md:pl-60">
        <header className="sticky top-0 z-30 border-b border-zinc-200 bg-white/95 px-4 py-3 backdrop-blur md:hidden">
          <div className="mx-auto flex max-w-7xl items-center justify-between">
            <span className="text-sm font-semibold text-zinc-900">Daily Routine</span>
            <nav className="flex gap-1" aria-label="Navegação principal">
              <Navigation activeSection={activeSection} onChange={onSectionChange} />
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-[1500px] px-4 py-5 sm:px-6 lg:px-8 lg:py-7">
          {children}
        </main>
      </div>
    </div>
  )
}
