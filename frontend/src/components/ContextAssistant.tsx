import Chat, { Contexto } from "./Chat";

interface Props {
  onContextConfirmed: () => void;
}

export default function ContextAssistant({ onContextConfirmed }: Props) {
  function handleCompleted(_ctx: Contexto) {
    onContextConfirmed();
  }
  return <Chat onCompleted={handleCompleted} />;
}
