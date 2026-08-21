import React from "react";
import { cn } from "@/lib/utils";

interface AnimatedCircularProgressBarProps {
  value: number;
  gaugePrimaryColor?: string;
  gaugeSecondaryColor?: string;
  className?: string;
}

export function AnimatedCircularProgressBar({
  value,
  gaugePrimaryColor = "rgb(79 70 229)",
  gaugeSecondaryColor = "rgba(0, 0, 0, 0.1)",
  className,
}: AnimatedCircularProgressBarProps) {
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (value / 100) * circumference;

  return (
    <div className={cn("relative flex items-center justify-center", className)}>
      <svg
        className="h-full w-full transform -rotate-90"
        viewBox="0 0 100 100"
      >
        <circle
          cx="50"
          cy="50"
          r={radius}
          stroke={gaugeSecondaryColor}
          strokeWidth="10"
          fill="transparent"
        />
        <circle
          cx="50"
          cy="50"
          r={radius}
          stroke={gaugePrimaryColor}
          strokeWidth="10"
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          className="transition-all duration-500 ease-in-out"
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center font-bold">
        {Math.round(value)}%
      </div>
    </div>
  );
}
