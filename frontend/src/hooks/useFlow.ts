import { useState } from "react";

export type Step = "context" | "generation" | "editor" | "export";

const steps: Step[] = ["context", "generation", "editor", "export"];

export function useFlow() {
  const [currentStep, setCurrentStep] = useState<Step>("context");

  function next() {
    setCurrentStep((prev) => {
      const idx = steps.indexOf(prev);
      return steps[Math.min(idx + 1, steps.length - 1)];
    });
  }

  function prev() {
    setCurrentStep((prev) => {
      const idx = steps.indexOf(prev);
      return steps[Math.max(idx - 1, 0)];
    });
  }

  function goTo(step: Step) {
    if (steps.includes(step)) setCurrentStep(step);
  }

  return { currentStep, next, prev, goTo, steps };
}
