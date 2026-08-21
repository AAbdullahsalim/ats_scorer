"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface ProgressBarProps {
  isFinished?: boolean;
  className?: string;
}

export default function ProgressBar({ isFinished = false, className }: ProgressBarProps) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (isFinished) {
      setProgress(100);
      return;
    }

    // Simulate progress that slows down as it gets closer to 90%
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) return prev;
        
        // Add a random amount, smaller as it gets higher
        const remaining = 90 - prev;
        const increment = Math.max(0.5, Math.random() * (remaining / 10));
        return Math.min(90, prev + increment);
      });
    }, 500);

    return () => clearInterval(interval);
  }, [isFinished]);

  return (
    <div className={cn("w-full max-w-md mt-8 flex flex-col items-center", className)}>
      <div className="w-full h-2 bg-white/20 rounded-full overflow-hidden backdrop-blur-sm">
        <motion.div
          className="h-full bg-white rounded-full shadow-[0_0_10px_rgba(255,255,255,0.8)]"
          initial={{ width: "0%" }}
          animate={{ width: `${progress}%` }}
          transition={{ ease: "easeOut", duration: 0.5 }}
        />
      </div>
      <div className="mt-3 text-white/70 font-mono text-sm uppercase tracking-widest flex w-full justify-between">
        <span>Processing...</span>
        <span>{Math.round(progress)}%</span>
      </div>
    </div>
  );
}
