import { afterEach, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ConfirmDialog from './ConfirmDialog'

afterEach(cleanup)

it('keeps keyboard focus inside the confirmation and restores it on close', async () => {
  const user = userEvent.setup()
  const props = { title: 'Excluir dia?', description: 'As tarefas serão excluídas.', confirmLabel: 'Excluir', busy: false, onConfirm: vi.fn(), onCancel: vi.fn() }
  const { rerender } = render(<><button>Abrir</button><ConfirmDialog {...props} open={false} /></>)
  await user.click(screen.getByRole('button', { name: 'Abrir' }))
  rerender(<><button>Abrir</button><ConfirmDialog {...props} open /></>)
  expect(document.activeElement).toBe(screen.getByRole('button', { name: 'Cancelar' }))
  await user.tab({ shift: true })
  expect(document.activeElement).toBe(screen.getByRole('button', { name: 'Excluir' }))
  await user.tab()
  expect(document.activeElement).toBe(screen.getByRole('button', { name: 'Cancelar' }))
  await user.keyboard('{Escape}')
  expect(props.onCancel).toHaveBeenCalledOnce()
  rerender(<><button>Abrir</button><ConfirmDialog {...props} open={false} /></>)
  expect(document.activeElement).toBe(screen.getByRole('button', { name: 'Abrir' }))
})
