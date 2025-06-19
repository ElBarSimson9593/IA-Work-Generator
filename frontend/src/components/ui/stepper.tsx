interface StepperProps {
  steps: string[];
  current: number;
}

export function Stepper({ steps, current }: StepperProps) {
  return (
    <div className="flex gap-4 mb-4">
      {steps.map((s, i) => (
        <div key={i} className="flex items-center gap-2">
          <div
            className={`w-6 h-6 rounded-full text-center text-sm ${
              i <= current ? "bg-gray-500 text-white" : "bg-gray-300"
            }`}
          >
            {i + 1}
          </div>
          <span>{s}</span>
        </div>
      ))}
    </div>
  );
}
