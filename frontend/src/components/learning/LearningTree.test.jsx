import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LearningTree from './LearningTree'
import * as api from '../../api/client'

vi.mock('../../api/client', () => ({ listLearningNodes: vi.fn(), createLearningNode: vi.fn(),
  updateLearningNode: vi.fn(), deleteLearningNode: vi.fn(), getApiErrorMessage: (e) => e.message }))
const nodes = [{ id: 1, title: 'Dados', parent_id: null, completed: false },
  { id: 2, title: 'Python', parent_id: 1, completed: false },
  { id: 3, title: 'Funções', parent_id: 2, completed: false }]
beforeEach(() => { vi.resetAllMocks(); api.listLearningNodes.mockResolvedValue(nodes) })
afterEach(cleanup)

it('marks only the chosen topic and preserves hierarchy', async () => {
  render(<LearningTree onNavigationGuardChange={() => {}} />)
  await userEvent.click(await screen.findByRole('checkbox', { name: 'Python' }))
  await waitFor(() => expect(screen.getByRole('checkbox', { name: 'Python' }).checked).toBe(true))
  expect(screen.getByRole('checkbox', { name: 'Funções' }).checked).toBe(false)
  expect(api.updateLearningNode).toHaveBeenCalledWith(2, { title: 'Python', completed: true })
})

it('creates a nested topic', async () => {
  api.createLearningNode.mockResolvedValue({ id: 4, title: 'Parâmetros', parent_id: 3, completed: false })
  render(<LearningTree onNavigationGuardChange={() => {}} />)
  await userEvent.click(await screen.findByRole('button', { name: 'Adicionar subtópico em Funções' }))
  await userEvent.type(screen.getByLabelText('Nome do tópico'), 'Parâmetros')
  await userEvent.click(screen.getByRole('button', { name: 'Salvar tópico' }))
  expect(await screen.findByRole('checkbox', { name: 'Parâmetros' })).toBeTruthy()
  expect(api.createLearningNode).toHaveBeenCalledWith({ title: 'Parâmetros', parent_id: 3 })
})

it('confirms deletion of descendants and keeps unrelated parent', async () => {
  render(<LearningTree onNavigationGuardChange={() => {}} />)
  await userEvent.click(await screen.findByRole('button', { name: 'Excluir Python' }))
  expect(screen.getByRole('dialog').textContent).toContain('2 itens')
  expect(api.deleteLearningNode).not.toHaveBeenCalled()
  await userEvent.click(screen.getByRole('button', { name: 'Excluir árvore' }))
  await waitFor(() => expect(screen.queryByRole('checkbox', { name: 'Funções' })).toBeNull())
  expect(screen.getByRole('checkbox', { name: 'Dados' })).toBeTruthy()
})

it('preserves the checkbox when saving fails', async () => {
  api.updateLearningNode.mockRejectedValue(new Error('API indisponível'))
  render(<LearningTree onNavigationGuardChange={() => {}} />)
  await userEvent.click(await screen.findByRole('checkbox', { name: 'Python' }))
  expect(await screen.findByRole('alert')).toBeTruthy()
  expect(screen.getByRole('checkbox', { name: 'Python' }).checked).toBe(false)
})
