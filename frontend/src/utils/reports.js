export function dateFromFilename(filename) {
  const stem = filename.replace(/\.md$/i, '')
  let match = stem.match(/^(\d{4})-(\d{2})-(\d{2})$/)
  if (!match) {
    const brazilian = stem.match(/^(\d{2})-(\d{2})-(\d{4})$/)
    if (brazilian) match = [stem, brazilian[3], brazilian[2], brazilian[1]]
  }
  if (!match) return ''
  const date = `${match[1]}-${match[2]}-${match[3]}`
  const parsed = new Date(`${date}T12:00:00Z`)
  return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === date ? date : ''
}

export async function readReportFile(file) {
  if (!/\.md$/i.test(file.name)) throw new Error('Escolha um arquivo Markdown (.md).')
  if (file.size > 400_000) throw new Error('O arquivo deve ter até 400 KB e 100 mil caracteres.')
  let content
  try {
    content = new TextDecoder('utf-8', { fatal: true }).decode(await file.arrayBuffer())
  } catch {
    throw new Error('Salve o arquivo com codificação UTF-8 e tente novamente.')
  }
  if (!content.trim() || content.includes('\0') || [...content].length > 100_000) {
    throw new Error('O relato deve conter texto válido, até 100 mil caracteres.')
  }
  return { filename: file.name, content, report_date: dateFromFilename(file.name),
    title: content.match(/^#\s+(.+)$/m)?.[1]?.slice(0, 160) || file.name.replace(/\.md$/i, '') }
}
