export default function ComparisonView({ comparison }) {
  const { result } = comparison
  return (
    <section className="mt-6 space-y-6" aria-label="Comparação dos relatos">
      <div><h3 className="text-lg font-semibold">O que mudou</h3><p className="mt-2 whitespace-pre-wrap text-sm leading-7">{result.summary}</p></div>
      {[['advances', 'Avanços documentados'], ['consolidations', 'Práticas consolidadas'], ['pending', 'Pendências e próximos passos']].map(([key, title]) => (
        <section key={key}><h4 className="font-medium">{title}</h4>
          {!result[key].length && <p className="mt-2 text-sm text-zinc-500">Sem evidências suficientes nesta comparação.</p>}
          {result[key].map((item, index) => <article key={index} className="mt-3 rounded-lg border border-zinc-200 p-4 dark:border-zinc-700">
            <h5 className="text-sm font-semibold">{item.title}</h5><p className="mt-2 text-sm leading-6">{item.explanation}</p>
            <div className="mt-3 grid gap-3 text-sm sm:grid-cols-2">
              <div><p className="text-xs font-medium text-zinc-500">RELATO ANTERIOR</p><blockquote className="mt-1 whitespace-pre-wrap border-l-2 border-zinc-300 pl-3">{item.previous_evidence || 'Não documentado no relato anterior.'}</blockquote></div>
              <div><p className="text-xs font-medium text-blue-600 dark:text-blue-400">RELATO ATUAL</p><blockquote className="mt-1 whitespace-pre-wrap border-l-2 border-blue-400 pl-3">{item.current_evidence}</blockquote></div>
            </div>
          </article>)}
        </section>
      ))}
      <p className="text-sm leading-6 text-zinc-500 dark:text-zinc-400">{result.limitations}</p>
      <p className="text-xs text-zinc-500">Análise por IA · {comparison.model} · {comparison.created_at} UTC. Confira a interpretação nos relatos originais.</p>
    </section>
  )
}
