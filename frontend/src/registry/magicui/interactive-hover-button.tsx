import React from "react";
import { ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import GridLoader from "@/components/GridLoader";

interface InteractiveHoverButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  text?: string;
  loaderColor?: string;
  loaderPattern?: string;
}

export const InteractiveHoverButton = React.forwardRef<
  HTMLButtonElement,
  InteractiveHoverButtonProps
>(({ text = "Button", loaderColor = "blue", loaderPattern = "pulse", className, ...props }, ref) => {
  return (
    <button
      ref={ref}
      className={cn(
        "group relative w-40 cursor-pointer overflow-hidden rounded-full border border-border bg-background/50 backdrop-blur-md p-3 text-center font-semibold hover:border-primary/50 transition-all",
        className,
      )}
      {...props}
    >
      <span className="inline-flex items-center justify-center gap-2 w-full translate-x-1 transition-all duration-300 group-hover:translate-x-12 group-hover:opacity-0">
        <GridLoader color={loaderColor} mode="stagger" size="sm" rounded />
        {text}
      </span>
      <div className="absolute top-0 z-10 flex h-full w-full translate-x-12 items-center justify-center gap-2 text-primary-foreground opacity-0 transition-all duration-300 group-hover:-translate-x-1 group-hover:opacity-100">
        <span>{text}</span>
        <ArrowRight size={16} />
      </div>
      <div className="absolute left-[20%] top-[40%] h-2 w-2 scale-[1] rounded-lg bg-primary/80 transition-all duration-300 group-hover:left-[0%] group-hover:top-[0%] group-hover:h-full group-hover:w-full group-hover:scale-[1.8] z-[-1]"></div>
    </button>
  );
});

InteractiveHoverButton.displayName = "InteractiveHoverButton";
