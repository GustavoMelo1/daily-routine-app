import { BarChart3, CalendarDays, Moon, Sun, TrendingUp, GitBranch } from "lucide-react"
import UsageGuide from './UsageGuide'

const navigation = [
  { id: "calendar", label: "Calendário", icon: CalendarDays },
  { id: "dashboard", label: "Painel", icon: BarChart3 },
  { id: "evolution", label: "Evolução", icon: TrendingUp },
  { id: "learning", label: "Aprendizado", icon: GitBranch },
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
            ? "bg-blue-50 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300"
            : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-950 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100"
        }`}
        aria-current={active ? "page" : undefined}
      >
        <Icon size={18} strokeWidth={1.8} aria-hidden="true" className="shrink-0" />
        {label}
      </button>
    )
  })
}

function ThemeToggle({ theme, onToggle }) {
  const dark = theme === "dark"

  return (
    <button
      type="button"
      onClick={onToggle}
      className="inline-flex items-center gap-2 rounded-lg border border-zinc-300 bg-white p-2 text-sm font-medium text-zinc-600 transition-colors hover:bg-zinc-100 hover:text-zinc-950 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800 dark:hover:text-white md:w-full md:px-3"
      aria-label={dark ? "Ativar modo claro" : "Ativar modo escuro"}
      title={dark ? "Ativar modo claro" : "Ativar modo escuro"}
    >
      {dark ? <Sun size={17} /> : <Moon size={17} />}
      <span className="hidden md:inline">{dark ? "Modo claro" : "Modo escuro"}</span>
    </button>
  )
}

export default function AppShell({ activeSection, onSectionChange, theme, onThemeToggle, children }) {
  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-950 transition-colors dark:bg-zinc-950 dark:text-zinc-100">
      <a href="#main-content" className="sr-only fixed left-4 top-4 z-50 rounded-lg bg-blue-600 px-4 py-3 text-white focus:not-sr-only">Pular para o conteúdo</a>
      <aside className="fixed inset-y-0 left-0 hidden w-60 border-r border-zinc-200 bg-white px-4 py-6 dark:border-zinc-800 dark:bg-zinc-900 md:flex md:flex-col">
        <div className="px-3">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-600">
            Daily Routine
          </p>
          <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">Agenda e consistência</p>
        </div>
        <nav className="mt-8 flex flex-col gap-1" aria-label="Navegação principal">
          <Navigation activeSection={activeSection} onChange={onSectionChange} />
        </nav>
        <div className="mt-auto border-t border-zinc-200 px-3 pt-4 text-xs leading-5 text-zinc-500 dark:border-zinc-800 dark:text-zinc-400">
          <ThemeToggle theme={theme} onToggle={onThemeToggle} />
          <p className="mt-3 font-medium">Seu espaço de estudo</p>
          <p>Agenda, registros e evolução. Para carregar os dados, mantenha a API local ligada.</p>
        </div>
      </aside>

      <div className="md:pl-60">
        <header className="sticky top-0 z-30 border-b border-zinc-200 bg-white/95 px-4 py-3 backdrop-blur dark:border-zinc-800 dark:bg-zinc-900/95 md:hidden">
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-3">
            <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">Daily Routine</span>
              <ThemeToggle theme={theme} onToggle={onThemeToggle} />
          </div>
          <nav className="mt-3 grid grid-cols-2 gap-1 [&_button]:justify-center [&_button]:gap-1.5 [&_button]:px-1 sm:grid-cols-4" aria-label="Navegação principal">
            <Navigation activeSection={activeSection} onChange={onSectionChange} />
          </nav>
        </header>
        <main id="main-content" tabIndex={-1} className="mx-auto max-w-[1500px] px-4 py-5 sm:px-6 lg:px-8 lg:py-7">
          <UsageGuide section={activeSection} />
          {children}
        </main>
      </div>
    </div>
  )
}
