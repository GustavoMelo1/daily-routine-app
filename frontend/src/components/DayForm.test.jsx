import { afterEach, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DayForm from './DayForm'
import StudyMinutes from './StudyMinutes'
import { createDayPlan, updateDayMinutes } from '../api/client'

vi.mock('../api/client', () => ({ createDayPlan: vi.fn(), updateDayMinutes: vi.fn(), getApiErrorMessage: (e) => e.message }))
afterEach(() => { cleanup(); vi.resetAllMocks() })

it('saves tomorrow and all planned tasks in one request', async () => {
  const created = vi.fn()
  render(<DayForm date="2099-10-20" onCreated={created} onNavigationGuardChange={() => {}} />)
  await userEvent.type(screen.getByLabelText(/Tarefas planejadas/), 'Python\nSQL')
  await userEvent.click(screen.getByRole('button', { name: 'Salvar dia e tarefas' }))
  expect(createDayPlan).toHaveBeenCalledWith(expect.objectContaining({ data: '2099-10-20', minutos_estudados: 0, tarefas: ['Python', 'SQL'] }))
  expect(created).toHaveBeenCalled()
})

it('preserves the plan if saving fails', async () => {
  createDayPlan.mockRejectedValue(new Error('API indisponível'))
  render(<DayForm date="2099-10-20" onCreated={() => {}} />)
  await userEvent.type(screen.getByLabelText(/Tarefas planejadas/), 'SQL')
  await userEvent.click(screen.getByRole('button', { name: 'Salvar dia e tarefas' }))
  expect(await screen.findByRole('alert')).toBeTruthy()
  expect(screen.getByLabelText(/Tarefas planejadas/).value).toBe('SQL')
})

it('records actual study time without recreating the day', async () => {
  const changed = vi.fn()
  render(<StudyMinutes day={{ data: '2099-10-20', minutos_estudados: 0 }} onChanged={changed} />)
  await userEvent.clear(screen.getByRole('spinbutton'))
  await userEvent.type(screen.getByRole('spinbutton'), '45')
  await userEvent.click(screen.getByRole('button', { name: 'Salvar minutos' }))
  expect(updateDayMinutes).toHaveBeenCalledWith('2099-10-20', 45)
  expect(changed).toHaveBeenCalled()
})
