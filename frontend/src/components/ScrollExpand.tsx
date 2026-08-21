"use client";

import React, { useRef } from "react";
import { motion, useScroll, useTransform, useSpring } from "framer-motion";

interface ScrollExpandProps {
  children?: React.ReactNode;
  src?: string;
  alt?: string;
  title?: string;
  scrollHint?: string;
  useWindowScroll?: boolean;
  startWidth?: number;
  startHeight?: number;
  startRadius?: number;
  endRadius?: number;
  mediaZoom?: number;
  scrollDistance?: number;
  holdDistance?: number;
  smoothing?: number;
  overlayScrim?: number;
  enabled?: boolean;
  className?: string;
}

export default function ScrollExpand({
  children,
  src,
  alt = "Media",
  title,
  scrollHint,
  useWindowScroll = true,
  startWidth = 42,
  startHeight = 58,
  startRadius = 24,
  endRadius = 0,
  mediaZoom = 1.35,
  scrollDistance = 1.2,
  holdDistance = 0.35,
  smoothing = 0.1,
  overlayScrim = 0.45,
  enabled = true,
  className = "",
}: ScrollExpandProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  const { scrollYProgress } = useScroll({
    target: useWindowScroll ? undefined : containerRef,
    offset: ["start end", "end start"],
  });

  const smoothProgress = useSpring(scrollYProgress, {
    damping: 20,
    stiffness: 100,
    mass: smoothing * 10,
  });

  // Calculate width from startWidth vw to 100vw
  const width = useTransform(
    smoothProgress,
    [0, scrollDistance],
    [`${startWidth}vw`, "100vw"]
  );

  // Calculate height from startHeight vh to 100vh
  const height = useTransform(
    smoothProgress,
    [0, scrollDistance],
    [`${startHeight}vh`, "100vh"]
  );

  const borderRadius = useTransform(
    smoothProgress,
    [0, scrollDistance],
    [startRadius, endRadius]
  );

  const scale = useTransform(
    smoothProgress,
    [0, scrollDistance + holdDistance],
    [mediaZoom, 1]
  );

  const scrimOpacity = useTransform(
    smoothProgress,
    [0, scrollDistance],
    [0, overlayScrim]
  );

  const contentOpacity = useTransform(
    smoothProgress,
    [scrollDistance - 0.2, scrollDistance],
    [0, 1]
  );

  const contentY = useTransform(
    smoothProgress,
    [scrollDistance - 0.2, scrollDistance],
    [40, 0]
  );

  if (!enabled) {
    return <div className={className}>{children}</div>;
  }

  return (
    <div 
      ref={containerRef} 
      className={`relative w-full flex items-center justify-center min-h-[150vh] ${className}`}
    >
      <div className="sticky top-0 w-full h-screen flex flex-col items-center justify-center overflow-hidden">
        
        {/* Title & Hint (fade out as scroll begins) */}
        <motion.div 
          className="absolute top-[10%] flex flex-col items-center z-20 text-center"
          style={{
            opacity: useTransform(smoothProgress, [0, 0.2], [1, 0])
          }}
        >
          {title && <h2 className="text-4xl font-bold text-foreground mb-4">{title}</h2>}
          {scrollHint && <p className="text-muted-foreground uppercase tracking-widest text-sm">{scrollHint}</p>}
        </motion.div>

        {/* Media Container */}
        <motion.div
          className="relative overflow-hidden shadow-2xl flex items-center justify-center"
          style={{
            width,
            height,
            borderRadius,
          }}
        >
          {src && (
            <motion.img
              src={src}
              alt={alt}
              className="absolute inset-0 w-full h-full object-cover"
              style={{ scale }}
            />
          )}

          {/* Overlay Scrim */}
          <motion.div 
            className="absolute inset-0 bg-black pointer-events-none z-10"
            style={{ opacity: scrimOpacity }}
          />

          {/* Revealed Content */}
          <motion.div
            className="relative z-20 flex flex-col items-center justify-center text-white text-center p-8 max-w-4xl"
            style={{
              opacity: contentOpacity,
              y: contentY,
            }}
          >
            {children}
          </motion.div>

        </motion.div>
      </div>
    </div>
  );
}
