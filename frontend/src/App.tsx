import ContextAssistant from "./components/ContextAssistant";
import AnimatedWriter from "./components/AnimatedWriter";
import InteractiveEditor from "./components/InteractiveEditor";
import ExportScreen from "./components/ExportScreen";
import MainLayout from "./components/MainLayout";
import { useFlow } from "./hooks/useFlow";

export default function App() {
  const { currentStep, next, steps } = useFlow();
  const titles = ["Contexto", "Generación", "Edición", "Exportar"];
  const currentIndex = steps.indexOf(currentStep);

  return (
    <MainLayout stepTitles={titles} currentIndex={currentIndex} header="IA Work Generator">
      {currentStep === "context" && <ContextAssistant onContextConfirmed={next} />}
      {currentStep === "generation" && <AnimatedWriter onGenerationComplete={next} />}
      {currentStep === "editor" && <InteractiveEditor onEditConfirmed={next} />}
      {currentStep === "export" && <ExportScreen onExported={() => {}} />}
    </MainLayout>
  );
}
