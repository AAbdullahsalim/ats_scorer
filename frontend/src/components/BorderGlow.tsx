"use client";

import React, { useRef, useState, useEffect } from "react";
import { cn } from "@/lib/utils";

interface BorderGlowProps {
  children: React.ReactNode;
  className?: string;
  edgeSensitivity?: number;
  glowColor?: string;
  backgroundColor?: string;
  borderRadius?: number;
  glowRadius?: number;
  glowIntensity?: number;
  coneSpread?: number;
  animated?: boolean;
  colors?: string[];
}

export default function BorderGlow({
  children,
  className,
  edgeSensitivity = 30,
  glowColor = "40 80 80",
  backgroundColor = "#120F17",
  borderRadius = 28,
  glowRadius = 40,
  glowIntensity = 1,
  coneSpread = 25,
  animated = false,
  colors = ['#c084fc', '#f472b6', '#38bdf8'],
}: BorderGlowProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: -1000, y: -1000 });
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      
      // Calculate distance to edge
      const isNearEdge = 
        e.clientX >= rect.left - edgeSensitivity &&
        e.clientX <= rect.right + edgeSensitivity &&
        e.clientY >= rect.top - edgeSensitivity &&
        e.clientY <= rect.bottom + edgeSensitivity;

      if (isNearEdge) {
        setMousePosition({
          x: e.clientX - rect.left,
          y: e.clientY - rect.top,
        });
      }
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [edgeSensitivity]);

  // Construct glow gradient based on single color or colors array
  const colorStops = colors 
    ? colors.join(", ") 
    : `rgb(${glowColor}), rgba(${glowColor}, 0)`;

  return (
    <div
      ref={containerRef}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={cn("relative group", className)}
      style={{
        borderRadius: borderRadius,
      }}
    >
      {/* Outer Glow Mask */}
      <div
        className="absolute inset-0 pointer-events-none transition-opacity duration-300 opacity-0 group-hover:opacity-100 z-0"
        style={{
          borderRadius: borderRadius,
          padding: "2px", // Border thickness
          background: `radial-gradient(${glowRadius * 2}px circle at ${mousePosition.x}px ${mousePosition.y}px, ${colors ? colors[0] : `rgb(${glowColor})`} ${glowIntensity * 100}%, transparent 100%)`,
          WebkitMask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
          WebkitMaskComposite: "xor",
          maskComposite: "exclude",
        }}
      />
      
      {/* Content Container */}
      <div
        className="relative z-10 w-full h-full overflow-hidden"
        style={{
          backgroundColor,
          borderRadius: borderRadius,
        }}
      >
        {children}
      </div>
    </div>
  );
}
