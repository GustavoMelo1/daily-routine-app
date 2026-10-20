import { afterEach, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LearningNote from './LearningNote'
import { saveLearningNotes } from '../../api/client'

vi.mock('../../api/client', () => ({ saveLearningNotes: vi.fn(), getApiErrorMessage: (error) => error.message }))
afterEach(() => { cleanup(); vi.resetAllMocks() })
const node = { id: 1, title: 'Python', notes: 'Original', notes_version: 1 }

it('saves notes with the expected version', async () => {
  saveLearningNotes.mockResolvedValue({ notes: 'Original novo', notes_version: 2 })
  const saved = vi.fn()
  render(<LearningNote node={node} onSaved={saved} onDirtyChange={() => {}} onBusyChange={() => {}} />)
  await userEvent.type(screen.getByLabelText('Anotações'), ' novo')
  await userEvent.click(screen.getByRole('button', { name: 'Salvar nota' }))
  expect(await screen.findByText(/Sem alterações pendentes/)).toBeTruthy()
  expect(saveLearningNotes).toHaveBeenCalledWith(1, { notes: 'Original novo', version: 1 })
  expect(saved).toHaveBeenCalledWith(1, { notes: 'Original novo', notes_version: 2 })
})

it('preserves the draft after a conflict', async () => {
  saveLearningNotes.mockRejectedValue(new Error('Nota alterada em outra aba'))
  render(<LearningNote node={node} onSaved={() => {}} onDirtyChange={() => {}} onBusyChange={() => {}} />)
  await userEvent.type(screen.getByLabelText('Anotações'), ' novo')
  await userEvent.click(screen.getByRole('button', { name: 'Salvar nota' }))
  expect(await screen.findByRole('alert')).toBeTruthy()
  expect(screen.getByLabelText('Anotações').value).toBe('Original novo')
  expect(screen.getByRole('button', { name: 'Salvar nota' }).disabled).toBe(false)
})
