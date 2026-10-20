import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import WeeklyEvolution from './WeeklyEvolution'
import ReportMarkdown from './ReportMarkdown'
import * as api from '../../api/client'

vi.mock('../../api/client', () => ({
  listWeeklyReports: vi.fn(), getWeeklyReport: vi.fn(), saveWeeklyReport: vi.fn(),
  deleteWeeklyReport: vi.fn(), getWeeklyComparison: vi.fn(), compareWeeklyReports: vi.fn(),
  getApiErrorMessage: (error) => error.message,
}))
const older = { id: 1, report_date: '2026-10-04', title: 'Primeira semana', filename: 'first.md', content: 'SELECT', version: 1 }
const newer = { ...older, id: 2, report_date: '2026-10-11', title: 'Segunda semana', content: 'JOIN' }
beforeEach(() => {
  vi.resetAllMocks()
  api.listWeeklyReports.mockResolvedValue([newer, older])
  api.getWeeklyReport.mockImplementation(async (id) => id === 2 ? newer : older)
  api.getWeeklyComparison.mockResolvedValue(null)
})
afterEach(cleanup)

describe('weekly evolution', () => {
  it('requires explicit consent action and does not generate on mount', async () => {
    render(<WeeklyEvolution onNavigationGuardChange={() => {}} />)
    await screen.findByRole('button', { name: 'Gerar comparação com IA' })
    expect(api.compareWeeklyReports).not.toHaveBeenCalled()
    expect(screen.getByText(/dois textos serão enviados/i)).toBeTruthy()
    api.compareWeeklyReports.mockResolvedValue({ model: 'test', created_at: '2026-10-14', result: {
      summary: 'Praticou JOIN', advances: [], consolidations: [], pending: [], limitations: 'Só relatos.',
    } })
    await userEvent.click(screen.getByRole('button', { name: 'Gerar comparação com IA' }))
    expect(await screen.findByText('Praticou JOIN')).toBeTruthy()
    expect(api.compareWeeklyReports).toHaveBeenCalledWith(2, 1)
  })
  it('saves an edited report with its original version', async () => {
    render(<WeeklyEvolution onNavigationGuardChange={() => {}} />)
    await userEvent.click(await screen.findByRole('button', { name: 'Editar' }))
    const title = screen.getByLabelText('Título')
    await userEvent.clear(title)
    await userEvent.type(title, 'Semana revisada')
    api.saveWeeklyReport.mockResolvedValue({ ...newer, title: 'Semana revisada', version: 2 })
    await userEvent.click(screen.getByRole('button', { name: 'Salvar relato' }))
    await waitFor(() => expect(api.saveWeeklyReport).toHaveBeenCalledWith(expect.objectContaining({ id: 2, version: 1, title: 'Semana revisada' })))
  })
  it('shows provider failure and lets the user retry', async () => {
    api.compareWeeklyReports.mockRejectedValue(new Error('Cota indisponível'))
    render(<WeeklyEvolution onNavigationGuardChange={() => {}} />)
    await userEvent.click(await screen.findByRole('button', { name: 'Gerar comparação com IA' }))
    expect(await screen.findByRole('alert')).toBeTruthy()
    expect(screen.getByRole('button', { name: 'Gerar comparação com IA' }).disabled).toBe(false)
    expect(screen.queryByRole('button', { name: 'Recarregar dados' })).toBeNull()
  })
  it('retries a failed report load instead of leaving a loading message', async () => {
    api.getWeeklyReport.mockRejectedValueOnce(new Error('Sem conexão'))
    render(<WeeklyEvolution onNavigationGuardChange={() => {}} />)
    await screen.findByRole('alert')
    expect(screen.queryByText('Carregando relato…')).toBeNull()
    await userEvent.click(screen.getByRole('button', { name: 'Tentar novamente' }))
    expect(await screen.findByRole('button', { name: 'Editar' })).toBeTruthy()
  })
  it('does not offer generation when the saved comparison could not be loaded', async () => {
    api.getWeeklyComparison.mockRejectedValueOnce(new Error('Sem conexão'))
    render(<WeeklyEvolution onNavigationGuardChange={() => {}} />)
    await screen.findByRole('alert')
    expect(screen.queryByRole('button', { name: 'Gerar comparação com IA' })).toBeNull()
    await userEvent.click(screen.getByRole('button', { name: 'Buscar novamente' }))
    expect(await screen.findByRole('button', { name: 'Gerar comparação com IA' })).toBeTruthy()
    expect(api.compareWeeklyReports).not.toHaveBeenCalled()
  })
  it('does not render raw HTML or remote images', () => {
    const { container } = render(<ReportMarkdown content={'<script>alert(1)</script>\n\n![tracking](https://example.com/pixel.png)\n\n[link](javascript:alert(1))'} />)
    expect(container.querySelector('script')).toBeNull()
    expect(container.querySelector('img')).toBeNull()
    expect(container.querySelector('a')?.getAttribute('href')).not.toContain('javascript:')
  })
})
