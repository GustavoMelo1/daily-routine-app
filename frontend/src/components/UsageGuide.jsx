const guides = {
  learning: {
    title: 'Como montar sua árvore',
    steps: [
      ['Crie uma área', 'Comece por uma área, como Engenharia de dados.'],
      ['Divida em tópicos', 'Use + ao lado de cada item para criar filhos: Python → Funções → Parâmetros. Até 32 níveis.'],
      ['Marque o que já aprendeu', 'Marcar um tópico não marca seus subtópicos. Você pode desmarcar a qualquer momento.'],
    ],
  },
  calendar: {
    title: 'Como usar a agenda',
    steps: [
      ['Escolha um dia', 'Navegue por mês, semana ou dia. Selecione uma data para ver seus registros.'],
      ['Planeje um dia', 'Selecione a data e escreva uma tarefa por linha. Depois marque as concluídas e registre o tempo estudado.'],
      ['Importe o caderno', 'Fotos vão na pasta backend/images do computador. A importação é feita pelo lote; esta tela não recebe fotos.'],
    ],
  },
  dashboard: {
    title: 'Como interpretar o painel',
    steps: [
      ['Escolha o mês', 'Os números consideram os registros disponíveis no período selecionado.'],
      ['Entenda a sequência', 'Um dia conta quando tem minutos de estudo acima de zero e pelo menos uma tarefa concluída.'],
      ['Confira os registros', 'Use “Ver dia” para consultar as tarefas e o tempo estudado.'],
    ],
  },
  evolution: {
    title: 'Como acompanhar sua evolução',
    steps: [
      ['Importe seu relato', 'Traga o arquivo .md que você preparou fora do app. Revise a data e o texto antes de salvar.'],
      ['Escolha duas semanas', 'Abra o relato mais recente e selecione um anterior como referência.'],
      ['Compare com evidências', 'Só “Gerar comparação com IA” envia os textos ao Gemini. A análise fica salva para consultar depois.'],
    ],
  },
}

export default function UsageGuide({ section }) {
  const guide = guides[section]
  if (!guide) return null
  return (
    <details key={section} className="mt-8 border-t border-zinc-200 dark:border-zinc-800">
      <summary className="w-fit cursor-pointer py-3 text-xs font-medium text-zinc-500 dark:text-zinc-400">
        {guide.title}
      </summary>
      <ol className="grid gap-5 pb-4 pt-2 lg:grid-cols-3">
        {guide.steps.map(([title, description], index) => (
          <li key={title} className="flex gap-3">
            <span aria-hidden="true" className="pt-0.5 text-xs tabular-nums text-zinc-400">{index + 1}.</span>
            <div><h2 className="text-sm font-semibold">{title}</h2><p className="mt-1 text-sm leading-6 text-zinc-500 dark:text-zinc-400">{description}</p></div>
          </li>
        ))}
      </ol>
    </details>
  )
}
