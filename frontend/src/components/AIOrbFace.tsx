"use client";

import React, { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

type AIState = "idle" | "listening" | "thinking" | "streaming" | "done" | "error";

interface AIOrbFaceProps {
  state?: AIState;
  size?: number;
  className?: string;
}

const STATE_COLORS: Record<AIState, string> = {
  idle: "#5e8d77",
  listening: "#0d3b45",
  thinking: "#56616c",
  streaming: "#5e8d77",
  done: "#5e8d77",
  error: "#ef4444",
};

const STATE_PULSES: Record<AIState, boolean> = {
  idle: false,
  listening: true,
  thinking: false,
  streaming: true,
  done: false,
  error: true,
};

const STATES: AIState[] = ["idle", "listening", "thinking", "streaming", "done"];

export default function AIOrbFace({ state = "idle", size = 80, className }: AIOrbFaceProps) {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [currentState, setCurrentState] = useState<AIState>(state);
  const orbRef = useRef<HTMLDivElement>(null);

  // Auto-cycle states every 20 seconds
  useEffect(() => {
    if (state !== "idle") {
      setCurrentState(state);
      return;
    }
    let i = 0;
    const interval = setInterval(() => {
      i = (i + 1) % STATES.length;
      setCurrentState(STATES[i]);
    }, 20000);
    return () => clearInterval(interval);
  }, [state]);

  // Mouse tracking for gaze
  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!orbRef.current) return;
      const { left, top, width, height } = orbRef.current.getBoundingClientRect();
      const cx = left + width / 2;
      const cy = top + height / 2;
      const dx = e.clientX - cx;
      const dy = e.clientY - cy;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const range = Math.min(size * 0.12, 8);
      setMousePos({ x: (dx / dist) * range, y: (dy / dist) * range });
    };
    window.addEventListener("mousemove", onMove);
    return () => window.removeEventListener("mousemove", onMove);
  }, [size]);

  const color = STATE_COLORS[currentState];
  const pulse = STATE_PULSES[currentState];
  const eyeSize = size * 0.12;
  const eyeOffsetX = size * 0.15;
  const eyeOffsetY = -size * 0.06;

  return (
    <div
      ref={orbRef}
      className={cn("relative flex flex-col items-center gap-2", className)}
      style={{ width: size, height: size }}
    >
      {/* Outer glow ring */}
      {pulse && (
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{ background: `radial-gradient(circle, ${color}33 0%, transparent 70%)` }}
          animate={{ scale: [1, 1.3, 1], opacity: [0.4, 0, 0.4] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />
      )}

      {/* Main orb body */}
      <motion.div
        className="absolute inset-0 rounded-full"
        style={{
          background: `radial-gradient(circle at 38% 35%, ${color}cc, ${color}44, #0d1415)`,
          boxShadow: `0 0 ${size * 0.3}px ${color}55, inset 0 0 ${size * 0.15}px rgba(255,255,255,0.08)`,
        }}
        animate={{ scale: currentState === "thinking" ? [1, 0.97, 1] : 1 }}
        transition={{ duration: 1.5, repeat: currentState === "thinking" ? Infinity : 0 }}
      />

      {/* Eyes */}
      {currentState !== "thinking" && (
        <>
          {/* Left eye */}
          <motion.div
            className="absolute rounded-full bg-white"
            style={{
              width: eyeSize,
              height: eyeSize,
              top: "50%",
              left: "50%",
              marginTop: eyeOffsetY - eyeSize / 2,
              marginLeft: -eyeOffsetX - eyeSize / 2,
            }}
            animate={{ x: mousePos.x * 0.5, y: mousePos.y * 0.5 }}
            transition={{ type: "spring", stiffness: 200, damping: 20 }}
          >
            <div
              className="absolute rounded-full bg-[#0d1415]"
              style={{ width: eyeSize * 0.5, height: eyeSize * 0.5, top: "25%", left: "25%" }}
            />
          </motion.div>

          {/* Right eye */}
          <motion.div
            className="absolute rounded-full bg-white"
            style={{
              width: eyeSize,
              height: eyeSize,
              top: "50%",
              left: "50%",
              marginTop: eyeOffsetY - eyeSize / 2,
              marginLeft: eyeOffsetX - eyeSize / 2,
            }}
            animate={{ x: mousePos.x * 0.5, y: mousePos.y * 0.5 }}
            transition={{ type: "spring", stiffness: 200, damping: 20 }}
          >
            <div
              className="absolute rounded-full bg-[#0d1415]"
              style={{ width: eyeSize * 0.5, height: eyeSize * 0.5, top: "25%", left: "25%" }}
            />
          </motion.div>
        </>
      )}

      {/* Thinking: two moving dots */}
      {currentState === "thinking" && (
        <div className="absolute inset-0 flex items-center justify-center gap-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="rounded-full bg-white/80"
              style={{ width: eyeSize * 0.5, height: eyeSize * 0.5 }}
              animate={{ y: [0, -eyeSize * 0.5, 0], opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 0.9, delay: i * 0.2, repeat: Infinity }}
            />
          ))}
        </div>
      )}

      {/* State label */}
      <div
        className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] font-medium capitalize tracking-widest"
        style={{ color: color, whiteSpace: "nowrap" }}
      >
        {currentState}
      </div>
    </div>
  );
}
