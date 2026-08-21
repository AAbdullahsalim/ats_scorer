"use client";

import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface SplitFlapTextProps {
  words: string[];
  flipDuration?: number;
  stagger?: number;
  cycleDelay?: number;
  charset?: "alphanumeric" | "numeric" | "alpha";
  flipsPerChar?: number;
  tileColor?: string;
  textColor?: string;
  tileRadius?: number;
  gap?: number;
  fontSize?: number;
  loop?: boolean;
  padTo?: number;
}

const ALPHANUMERIC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ".split("");
const NUMERIC = "0123456789 ".split("");
const ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ ".split("");

export default function SplitFlapText({
  words,
  flipDuration = 0.12,
  stagger = 0.06,
  cycleDelay = 2400,
  charset = "alphanumeric",
  flipsPerChar = 8,
  tileColor = "#111827",
  textColor = "#f8fafc",
  tileRadius = 8,
  gap = 6,
  fontSize = 52,
  loop = true,
  padTo = 12,
}: SplitFlapTextProps) {
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [targetString, setTargetString] = useState(words[0].padEnd(padTo, " "));

  const charPool = 
    charset === "numeric" ? NUMERIC : 
    charset === "alpha" ? ALPHA : ALPHANUMERIC;

  useEffect(() => {
    if (words.length <= 1 && !loop) return;

    const interval = setInterval(() => {
      setCurrentWordIndex((prev) => {
        const next = (prev + 1) % words.length;
        if (!loop && next === 0) {
          clearInterval(interval);
          return prev;
        }
        setTargetString(words[next].padEnd(padTo, " "));
        return next;
      });
    }, cycleDelay);

    return () => clearInterval(interval);
  }, [words, cycleDelay, loop, padTo]);

  return (
    <div className="flex" style={{ gap }}>
      {targetString.split("").map((char, index) => (
        <FlapCharacter
          key={index}
          targetChar={char}
          pool={charPool}
          duration={flipDuration}
          staggerDelay={index * stagger}
          flips={flipsPerChar}
          tileColor={tileColor}
          textColor={textColor}
          tileRadius={tileRadius}
          fontSize={fontSize}
        />
      ))}
    </div>
  );
}

function FlapCharacter({
  targetChar,
  pool,
  duration,
  staggerDelay,
  flips,
  tileColor,
  textColor,
  tileRadius,
  fontSize,
}: {
  targetChar: string;
  pool: string[];
  duration: number;
  staggerDelay: number;
  flips: number;
  tileColor: string;
  textColor: string;
  tileRadius: number;
  fontSize: number;
}) {
  const [displayChar, setDisplayChar] = useState(" ");
  const timeoutRef = useRef<NodeJS.Timeout>(null);

  const [flipCount, setFlipCount] = useState(0);

  useEffect(() => {
    let currentFlip = 0;
    
    // Initial delay for stagger
    const startDelay = setTimeout(() => {
      const flipInterval = setInterval(() => {
        if (currentFlip >= flips) {
          setDisplayChar(targetChar);
          setFlipCount(prev => prev + 1);
          clearInterval(flipInterval);
        } else {
          setDisplayChar(pool[Math.floor(Math.random() * pool.length)]);
          setFlipCount(prev => prev + 1);
          currentFlip++;
        }
      }, duration * 1000);

      return () => clearInterval(flipInterval);
    }, staggerDelay * 1000);

    return () => clearTimeout(startDelay);
  }, [targetChar, pool, duration, staggerDelay, flips]);

  return (
    <div
      className="relative flex items-center justify-center font-mono font-bold overflow-hidden"
      style={{
        backgroundColor: tileColor,
        color: textColor,
        borderRadius: tileRadius,
        fontSize: fontSize,
        width: fontSize * 0.7,
        height: fontSize * 1.1,
      }}
    >
      <AnimatePresence mode="popLayout">
        <motion.span
          key={`${displayChar}-${flipCount}`}
          initial={{ rotateX: -90, opacity: 0 }}
          animate={{ rotateX: 0, opacity: 1 }}
          exit={{ rotateX: 90, opacity: 0 }}
          transition={{ duration: duration * 0.8 }}
          className="absolute"
        >
          {displayChar}
        </motion.span>
      </AnimatePresence>
      
      {/* Middle line separator typical in split-flaps */}
      <div 
        className="absolute w-full h-[2px] bg-black/40 z-10 top-1/2 -translate-y-1/2"
      />
    </div>
  );
}
