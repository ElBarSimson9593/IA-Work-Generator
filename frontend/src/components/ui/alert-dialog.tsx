import { ReactNode, useState } from "react";
import { Button } from "./button";

interface AlertDialogProps {
  trigger?: ReactNode;
  children: ReactNode;
  open?: boolean;
  onClose?: () => void;
}

export function AlertDialog({ trigger, children, open: controlled, onClose }: AlertDialogProps) {
  const [internal, setInternal] = useState(false);
  const open = controlled ?? internal;

  function close() {
    if (onClose) onClose();
    else setInternal(false);
  }

  return (
    <div className="inline-block">
      {trigger && !controlled && <div onClick={() => setInternal(true)}>{trigger}</div>}
      {open && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/50">
          <div className="bg-white p-6 rounded-2xl shadow-md">
            {children}
            <div className="mt-4 text-right">
              <Button onClick={close}>Cerrar</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
