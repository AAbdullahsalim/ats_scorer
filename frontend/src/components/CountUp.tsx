"use client";

import { useEffect, useRef } from "react";
import { useInView, useMotionValue, useSpring } from "framer-motion";

interface CountUpProps {
  to: number;
  from?: number;
  direction?: "up" | "down";
  delay?: number;
  duration?: number;
  className?: string;
  separator?: string;
  decimals?: number;
  onStart?: () => void;
  onEnd?: () => void;
}

export default function CountUp({
  to,
  from = 0,
  direction = "up",
  delay = 0,
  duration = 2,
  className = "",
  separator = "",
  decimals = 0,
  onStart,
  onEnd,
}: CountUpProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const motionValue = useMotionValue(direction === "down" ? to : from);

  const damp = 20;
  const mass = 1;
  const stiffness = 100;

  const springValue = useSpring(motionValue, {
    damping: damp,
    mass,
    stiffness,
  });

  const isInView = useInView(ref, { once: true, margin: "0px" });

  useEffect(() => {
    if (isInView) {
      setTimeout(() => {
        motionValue.set(direction === "down" ? from : to);
      }, delay * 1000);
    }
  }, [motionValue, isInView, delay, to, from, direction]);

  useEffect(() => {
    springValue.on("change", (latest) => {
      if (ref.current) {
        const formattedNumber = Intl.NumberFormat("en-US", {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals,
        })
          .format(Number(latest.toFixed(decimals)))
          .replace(/,/g, separator);

        ref.current.textContent = formattedNumber;
      }
    });
  }, [springValue, decimals, separator]);

  return <span className={className} ref={ref} />;
}
