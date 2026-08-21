"use client";

import React, { useMemo } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface GridLoaderProps {
  color?: string;
  size?: number | "sm" | "md" | "lg";
  pattern?: string;
  gap?: number;
  mode?: "stagger" | "pulse" | "sequence";
  blur?: number;
  rounded?: boolean;
  className?: string;
}

export default function GridLoader({
  color = "white",
  size = "md",
  pattern = "sparkle",
  gap = 1,
  mode = "pulse",
  blur = 0,
  rounded = false,
  className,
}: GridLoaderProps) {
  const sizeMap = {
    sm: 16,
    md: 24,
    lg: 32,
  };
  const actualSize = typeof size === "number" ? size : sizeMap[size];
  const itemSize = (actualSize - gap * 2) / 3;

  const colorMap: Record<string, string> = {
    white: "#f5f5f4",
    blue: "#38bdf8",
    red: "#f87171",
    green: "#4ade80",
    amber: "#fbbf24",
  };
  const actualColor = colorMap[color] || color;

  const items = useMemo(() => {
    return Array.from({ length: 9 }).map((_, i) => {
      // Create interesting patterns based on the index
      let delay = 0;
      if (mode === "stagger") {
        delay = i * 0.1;
      } else if (mode === "pulse") {
        delay = (i % 3) * 0.2;
      } else {
        delay = Math.random() * 0.5;
      }

      return (
        <motion.div
          key={i}
          className={cn(rounded ? "rounded-full" : "rounded-sm")}
          style={{
            width: itemSize,
            height: itemSize,
            backgroundColor: actualColor,
            filter: blur > 0 ? `blur(${blur}px)` : "none",
          }}
          animate={{
            opacity: [0.2, 1, 0.2],
            scale: [0.8, 1, 0.8],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            delay: delay,
            ease: "easeInOut",
          }}
        />
      );
    });
  }, [mode, actualColor, itemSize, blur, rounded]);

  return (
    <div
      className={cn("grid grid-cols-3 grid-rows-3", className)}
      style={{
        width: actualSize,
        height: actualSize,
        gap: gap,
      }}
    >
      {items}
    </div>
  );
}
