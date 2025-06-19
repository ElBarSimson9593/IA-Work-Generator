import { ReactNode } from "react";
import { Stepper } from "./ui/stepper";

interface MainLayoutProps {
  stepTitles: string[];
  currentIndex: number;
  header: string;
  children: ReactNode;
}

export default function MainLayout({ stepTitles, currentIndex, header, children }: MainLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col items-center p-8">
      <h1 className="text-2xl font-semibold mb-4">{header}</h1>
      <Stepper steps={stepTitles} current={currentIndex} />
      <div className="mt-6 w-full max-w-2xl">{children}</div>
    </div>
  );
}
