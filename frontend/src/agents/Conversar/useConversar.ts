import { useState } from 'react';
import { request } from '../../request';
import { useConversarStore } from './store';

export function useConversar() {
  const { respuesta, mensajeActual, historial, setMensajeActual, addMensaje, setRespuesta } = useConversarStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function enviarMensaje() {
    if (!mensajeActual.trim() || loading) return;
    const texto = mensajeActual;
    setMensajeActual('');
    addMensaje({ role: 'user', text: texto });
    setLoading(true);
    setError(null);
    try {
      const data = await request<{ respuesta?: string; reply?: string }>('/conversar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensaje: texto }),
      });
      const reply = data.respuesta || data.reply || '';
      setRespuesta(reply);
      addMensaje({ role: 'bot', text: reply });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return {
    respuesta,
    mensajeActual,
    historial,
    setMensajeActual,
    enviarMensaje,
    estado: { loading, error },
  };
}
