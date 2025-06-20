export interface Mensaje {
  role: 'user' | 'bot';
  text: string;
}

export interface EstadoConversacion {
  respuesta: string;
  mensajeActual: string;
  historial: Mensaje[];
}
