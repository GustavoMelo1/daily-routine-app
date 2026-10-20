import { CircleHelp } from 'lucide-react'

const guides = {
  learning: {
    title: 'Como montar sua árvore',
    steps: [
      ['Crie uma área', 'Comece por uma direção, como Engenharia de dados. A árvore é sua: nenhum roteiro é imposto.'],
      ['Divida em tópicos', 'Use + ao lado de cada item para criar filhos: Python → Funções → Parâmetros. Até 32 níveis.'],
      ['Marque o que já aprendeu', 'Cada marcação é independente e pode ser desfeita. O contador é um checklist, não uma avaliação de domínio.'],
    ],
  },
  calendar: {
    title: 'Como usar a agenda',
    steps: [
      ['Escolha um dia', 'Navegue por mês, semana ou dia. Selecione uma data para ver seus registros.'],
      ['Planeje antes de começar', 'Use “Planejar amanhã”, escreva uma tarefa por linha e salve tudo junto. Depois marque o que concluiu e atualize os minutos estudados.'],
      ['Importe o caderno', 'Fotos vão na pasta backend/images do computador. A importação é feita pelo lote; esta tela não recebe fotos.'],
    ],
  },
  dashboard: {
    title: 'Como interpretar o painel',
    steps: [
      ['Escolha o mês', 'Os números consideram os registros disponíveis no período selecionado.'],
      ['Entenda a sequência', 'Um dia conta quando tem minutos de estudo acima de zero e pelo menos uma tarefa concluída.'],
      ['Confira o contexto', 'Use “Ver dia” para abrir um registro. Os totais mostram atividade, não uma nota de aprendizado.'],
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
    <details key={section} className="mb-6 rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <summary className="cursor-pointer px-4 py-3 text-sm font-medium text-zinc-600 dark:text-zinc-300">
        <CircleHelp size={16} aria-hidden="true" className="mx-2 inline-block align-text-bottom text-blue-600 dark:text-blue-400" />
        {guide.title}
      </summary>
      <ol className="grid gap-5 border-t border-zinc-100 p-5 dark:border-zinc-800 lg:grid-cols-3">
        {guide.steps.map(([title, description], index) => (
          <li key={title} className="flex gap-3">
            <span aria-hidden="true" className="flex size-7 shrink-0 items-center justify-center rounded-full bg-blue-50 text-xs font-semibold text-blue-700 dark:bg-blue-950 dark:text-blue-300">{index + 1}</span>
            <div><h2 className="text-sm font-semibold">{title}</h2><p className="mt-1 text-sm leading-6 text-zinc-500 dark:text-zinc-400">{description}</p></div>
          </li>
        ))}
      </ol>
    </details>
  )
}
