import { useEffect, useState } from "react";
import { Card } from "./ui/card";
import { Progress } from "./ui/progress";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";

interface Props {
  onGenerationComplete: () => void;
}

export default function AnimatedWriter({ onGenerationComplete }: Props) {
  const sections = ["Introducción", "Desarrollo", "Conclusión"];
  const [currentSection, setCurrentSection] = useState(0);
  const [finished, setFinished] = useState(false);

  // Invocado cuando se completa la redacción y el usuario pasa al editor
  function goToNextStep() {
    onGenerationComplete();
  }

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSection((s) => {
        if (s < sections.length - 1) return s + 1;
        clearInterval(timer);
        setFinished(true);
        return s;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [sections.length]);

  const progress = ((currentSection + 1) / sections.length) * 100;

  return (
    <Card className="relative">
      <div className="space-y-4">
        <div className="flex gap-2">
          {sections.map((s, i) => (
            <Badge key={i} className={i === currentSection ? "bg-gray-200" : "bg-white"}>
              {s}
            </Badge>
          ))}
        </div>
        <Progress value={progress} />
        {finished && (
          <Button className="absolute bottom-4 right-4" onClick={goToNextStep}>
            Ir al editor
          </Button>
        )}
      </div>
    </Card>
  );
}
