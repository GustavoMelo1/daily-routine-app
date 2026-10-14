import { describe, it, expect } from 'vitest'
import { dateFromFilename, readReportFile } from './reports'

describe('weekly report files', () => {
  it('recognizes both date formats and rejects impossible dates', () => {
    expect(dateFromFilename('04-10-2026.md')).toBe('2026-10-04')
    expect(dateFromFilename('2026-10-04.md')).toBe('2026-10-04')
    expect(dateFromFilename('31-02-2026.md')).toBe('')
    expect(dateFromFilename('weekly.md')).toBe('')
  })
  it('preserves the original Markdown', async () => {
    const content = '# Semana\n\nPratiquei SQL.\n'
    const result = await readReportFile({ name: '04-10-2026.md', size: 40,
      arrayBuffer: async () => new TextEncoder().encode(content).buffer })
    expect(result.content).toBe(content)
    expect(result.title).toBe('Semana')
    expect(result.report_date).toBe('2026-10-04')
  })
  it('rejects unsupported and oversized files', async () => {
    await expect(readReportFile({ name: 'file.pdf', size: 10 })).rejects.toThrow('Markdown')
    await expect(readReportFile({ name: 'file.md', size: 400001 })).rejects.toThrow('400 KB')
  })
})
