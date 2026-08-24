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
        "group relative w-auto px-4 py-2 text-xs font-bold tracking-wide whitespace-nowrap cursor-pointer overflow-hidden rounded-full border border-white/10 bg-background/40 backdrop-blur-md text-center hover:border-primary/50 transition-all",
        className,
      )}
      {...props}
    >
      <span className="inline-flex items-center justify-center gap-2.5 w-full whitespace-nowrap transition-all duration-300 group-hover:translate-x-8 group-hover:opacity-0">
        <GridLoader color={loaderColor} mode="stagger" size="sm" rounded className="shrink-0" />
        <span>{text}</span>
      </span>
      <div className="absolute inset-0 z-10 flex h-full w-full items-center justify-center gap-2 whitespace-nowrap text-primary-foreground opacity-0 transition-all duration-300 translate-x-8 group-hover:translate-x-0 group-hover:opacity-100">
        <span>{text}</span>
        <ArrowRight size={13} />
      </div>
      <div className="absolute inset-0 bg-primary/80 opacity-0 transition-opacity duration-300 group-hover:opacity-100 -z-10 rounded-full"></div>
    </button>
  );
});

InteractiveHoverButton.displayName = "InteractiveHoverButton";
