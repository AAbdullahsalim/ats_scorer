"use client";

import React, { useRef, useState, useEffect } from "react";
import { cn } from "@/lib/utils";

interface SpecularButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  size?: "sm" | "md" | "lg";
  radius?: number;
  tint?: string;
  tintOpacity?: number;
  blur?: number;
  textColor?: string;
  lineColor?: string;
  baseColor?: string;
  intensity?: number;
  shineSize?: number;
  shineFade?: number;
  thickness?: number;
  speed?: number;
  followMouse?: boolean;
  proximity?: number;
  autoAnimate?: boolean;
}

export default function SpecularButton({
  children,
  className,
  size = "md",
  radius = 18,
  tint = "#ffffff",
  tintOpacity = 0,
  blur = 0,
  textColor = "#f5f5f5",
  lineColor = "#ffffff",
  baseColor = "#525252",
  intensity = 1,
  shineSize = 10,
  shineFade = 40,
  thickness = 1,
  speed = 0.35,
  followMouse = true,
  proximity = 250,
  autoAnimate = false,
  ...props
}: SpecularButtonProps) {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: -1000, y: -1000 });
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    if (!followMouse || !buttonRef.current) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (!buttonRef.current) return;
      const rect = buttonRef.current.getBoundingClientRect();
      
      // Calculate distance to button center
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const distance = Math.sqrt(
        Math.pow(e.clientX - centerX, 2) + Math.pow(e.clientY - centerY, 2)
      );

      // Only update if within proximity
      if (distance < proximity || isHovered) {
        setMousePosition({
          x: e.clientX - rect.left,
          y: e.clientY - rect.top,
        });
      }
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [followMouse, proximity, isHovered]);

  const sizeClasses = {
    sm: "px-4 py-2 text-sm",
    md: "px-6 py-3 text-base",
    lg: "px-8 py-4 text-lg font-medium",
  };

  return (
    <button
      ref={buttonRef}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={cn(
        "relative overflow-hidden group transition-all duration-300",
        sizeClasses[size],
        className
      )}
      style={{
        borderRadius: radius,
        backgroundColor: baseColor,
        color: textColor,
        boxShadow: `0 0 ${blur}px ${tint}${Math.round(tintOpacity * 255).toString(16).padStart(2, '0')}`,
        border: `${thickness}px solid rgba(255, 255, 255, 0.1)`,
      }}
      {...props}
    >
      {/* Glow effect */}
      <div
        className="absolute inset-0 pointer-events-none transition-opacity duration-300 opacity-0 group-hover:opacity-100"
        style={{
          background: `radial-gradient(${shineSize * 10}px circle at ${mousePosition.x}px ${mousePosition.y}px, ${lineColor}${Math.round(intensity * 100).toString(16).padStart(2, '0')}, transparent ${shineFade}%)`,
        }}
      />
      
      <span className="relative z-10 flex items-center justify-center gap-2">
        {children}
      </span>
    </button>
  );
}
