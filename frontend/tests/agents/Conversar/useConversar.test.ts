import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useConversar } from '../../../src/agents/Conversar/useConversar';
import { useConversarStore } from '../../../src/agents/Conversar/store';

vi.mock('../../../src/request', () => ({
  request: vi.fn(() => Promise.resolve({ respuesta: 'ok' })),
}));

describe('useConversar', () => {
  it('updates state after sending message', async () => {
    const { result } = renderHook(() => useConversar());
    act(() => {
      result.current.setMensajeActual('hola');
    });
    await act(async () => {
      await result.current.enviarMensaje();
    });
    expect(result.current.respuesta).toBe('ok');
    expect(useConversarStore.getState().historial).toHaveLength(2);
    expect(useConversarStore.getState().historial[1].text).toBe('ok');
  });
});
