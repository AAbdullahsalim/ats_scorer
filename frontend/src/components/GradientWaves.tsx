"use client";

import React, { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

interface GradientWavesProps {
  horizonColor?: string;
  waveColor?: string;
  crestColor?: string;
  speed?: number;
  amplitude?: number;
  waveScale?: number;
  waveRatio?: number;
  swell?: number;
  turbulence?: number;
  tilt?: number;
  zoom?: number;
  height?: number;
  fogDepth?: number;
  detail?: "low" | "medium" | "high";
  brightness?: number;
  opacity?: number;
  mouseInteraction?: boolean;
  parallaxStrength?: number;
  grain?: boolean;
  grainIntensity?: number;
  className?: string;
}

export default function GradientWaves({
  horizonColor = "#5227FF",
  waveColor = "#FF9FFC",
  crestColor = "#FFFFFF",
  speed = 0.4,
  opacity = 1,
  className,
}: GradientWavesProps) {
  // Pure CSS fluid gradient approximation of the WebGL wave effect
  // for stability and performance without Three.js dependencies
  
  return (
    <div 
      className={cn("absolute inset-0 overflow-hidden", className)}
      style={{ opacity, backgroundColor: horizonColor }}
    >
      <div 
        className="absolute inset-0 opacity-50 blur-[80px]"
        style={{
          background: `radial-gradient(circle at 50% 120%, ${crestColor} 0%, transparent 50%)`,
        }}
      />
      
      {/* Animated wave layers using CSS keyframes and transforms */}
      <div 
        className="absolute inset-0 blur-[40px] animate-wave-slow"
        style={{
          background: `conic-gradient(from 90deg at 50% 100%, ${waveColor}, ${horizonColor}, ${waveColor})`,
          transformOrigin: "50% 100%",
          animation: `wave ${10 / speed}s ease-in-out infinite alternate`,
        }}
      />
      
      <div 
        className="absolute -inset-[50%] blur-[60px]"
        style={{
          background: `radial-gradient(ellipse at 50% 80%, ${crestColor} 0%, transparent 60%)`,
          animation: `pulse-wave ${8 / speed}s cubic-bezier(0.4, 0, 0.6, 1) infinite alternate`,
        }}
      />
      
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes wave {
          0% { transform: scaleY(1) rotate(-5deg); }
          100% { transform: scaleY(1.2) rotate(5deg); }
        }
        @keyframes pulse-wave {
          0% { transform: scale(1) translateY(10%); opacity: 0.4; }
          100% { transform: scale(1.1) translateY(-5%); opacity: 0.8; }
        }
      `}} />
    </div>
  );
}
