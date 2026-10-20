import { afterEach, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CalendarToolbar from './CalendarToolbar'

afterEach(cleanup)

it('keeps date navigation without a separate planning shortcut', async () => {
  const onNext = vi.fn()
  const onToday = vi.fn()
  const onViewChange = vi.fn()
  render(<CalendarToolbar title="Outubro de 2026" view="month" onPrevious={vi.fn()} onNext={onNext} onToday={onToday} onViewChange={onViewChange} />)
  expect(screen.queryByRole('button', { name: /Planejar amanhã/i })).toBeNull()
  await userEvent.click(screen.getByRole('button', { name: 'Próximo período' }))
  await userEvent.click(screen.getByRole('button', { name: 'Hoje' }))
  await userEvent.click(screen.getByRole('button', { name: 'Dia' }))
  expect(onNext).toHaveBeenCalledOnce()
  expect(onToday).toHaveBeenCalledOnce()
  expect(onViewChange).toHaveBeenCalledWith('day')
})
