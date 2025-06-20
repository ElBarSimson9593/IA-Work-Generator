import { create } from 'zustand';
import { Mensaje, EstadoConversacion } from './types';

interface ConversarStore extends EstadoConversacion {
  setMensajeActual: (msg: string) => void;
  addMensaje: (msg: Mensaje) => void;
  setRespuesta: (resp: string) => void;
  clear: () => void;
}

export const useConversarStore = create<ConversarStore>((set) => ({
  respuesta: '',
  mensajeActual: '',
  historial: [],
  setMensajeActual: (mensajeActual) => set({ mensajeActual }),
  addMensaje: (msg) => set((state) => ({ historial: [...state.historial, msg] })),
  setRespuesta: (respuesta) => set({ respuesta }),
  clear: () => set({ respuesta: '', mensajeActual: '', historial: [] }),
}));
