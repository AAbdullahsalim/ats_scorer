"use client";

import React, { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

interface CosmicDustProps {
  className?: string;
  particleCount?: number;
  particleColors?: string[];
  minSize?: number;
  maxSize?: number;
  speed?: number;
  opacity?: number;
}

export default function CosmicDust({
  className,
  particleCount = 70,
  particleColors = ["#5e8d77", "#34d399", "#10b981", "#6ee7b7", "#a7f3d0", "#ffffff"],
  minSize = 0.8,
  maxSize = 2.4,
  speed = 0.25,
  opacity = 0.6,
}: CosmicDustProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = canvas.parentElement?.clientWidth || window.innerWidth);
    let height = (canvas.height = canvas.parentElement?.clientHeight || window.innerHeight);

    const handleResize = () => {
      if (!canvas || !canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth;
      height = canvas.height = canvas.parentElement.clientHeight;
    };

    window.addEventListener("resize", handleResize);

    // Initialize particles
    const particles = Array.from({ length: particleCount }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * (maxSize - minSize) + minSize,
      color: particleColors[Math.floor(Math.random() * particleColors.length)],
      vx: (Math.random() - 0.5) * speed,
      vy: -Math.random() * speed - 0.05, // gentle upward drift
      alpha: Math.random() * 0.7 + 0.3,
      alphaSpeed: (Math.random() * 0.01 + 0.003) * (Math.random() > 0.5 ? 1 : -1),
      glow: Math.random() > 0.6,
    }));

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      particles.forEach((p) => {
        // Move
        p.x += p.vx;
        p.y += p.vy;

        // Twinkle
        p.alpha += p.alphaSpeed;
        if (p.alpha > 1 || p.alpha < 0.2) {
          p.alphaSpeed = -p.alphaSpeed;
        }

        // Wrap around boundaries
        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.save();
        ctx.globalAlpha = p.alpha * opacity;

        if (p.glow) {
          ctx.shadowBlur = 8;
          ctx.shadowColor = p.color;
        }

        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, [particleCount, particleColors, minSize, maxSize, speed, opacity]);

  return (
    <canvas
      ref={canvasRef}
      className={cn("pointer-events-none absolute inset-0 z-0 h-full w-full", className)}
    />
  );
}
