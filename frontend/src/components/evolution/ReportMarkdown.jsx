import Markdown from 'react-markdown'

export default function ReportMarkdown({ content }) {
  return (
    <div className="break-words text-sm leading-7 [&_h1]:mb-4 [&_h1]:text-xl [&_h1]:font-semibold [&_h2]:mb-2 [&_h2]:mt-6 [&_h2]:text-lg [&_h2]:font-semibold [&_h3]:mt-4 [&_h3]:font-semibold [&_p]:my-3 [&_ul]:list-disc [&_ul]:pl-6 [&_ol]:list-decimal [&_ol]:pl-6 [&_pre]:overflow-x-auto [&_pre]:rounded-lg [&_pre]:bg-zinc-100 [&_pre]:p-3 dark:[&_pre]:bg-zinc-800 [&_blockquote]:border-l-2 [&_blockquote]:border-blue-300 [&_blockquote]:pl-4 [&_a]:text-blue-600 [&_a]:underline">
      <Markdown skipHtml components={{
        img: ({ alt }) => <span className="text-zinc-500">[Imagem externa não carregada: {alt || 'sem descrição'}]</span>,
        a: ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>,
      }}>{content}</Markdown>
    </div>
  )
}
