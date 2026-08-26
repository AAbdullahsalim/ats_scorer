import React from "react";
import { motion } from "framer-motion";
import SpecularButton from "@/components/SpecularButton";
import CountUp from "@/components/CountUp";
import UniversityFilter from "@/components/UniversityFilter";
import { cn } from "@/lib/utils";

interface ActionControlsProps {
  yoe: number;
  setYoe: (val: number) => void;
  strictMode: boolean;
  setStrictMode: (val: boolean) => void;
  selectedUniversities: string[];
  setSelectedUniversities: (val: string[]) => void;
}

export default function ActionControls({
  yoe,
  setYoe,
  strictMode,
  setStrictMode,
  selectedUniversities,
  setSelectedUniversities
}: ActionControlsProps) {
  return (
    <div className="flex items-center justify-end w-full max-w-7xl mt-4 gap-6">
      {/* Sleek Min YOE Control */}
      <div className="flex items-center gap-5 bg-white/[0.03] p-2 rounded-full border border-white/10 backdrop-blur-sm shadow-[inset_0_1px_2px_rgba(255,255,255,0.05)] transition-all hover:bg-white/[0.05]">
        <span className="text-sm font-bold text-muted-foreground uppercase tracking-widest pl-4">Min YOE</span>
        <div className="flex items-center bg-black/60 rounded-full border border-black/50 shadow-inner p-1 gap-1">
          <SpecularButton
            size="sm"
            onClick={() => setYoe(Math.max(0, yoe - 1))}
            baseColor="#0a0f10"
            lineColor="#5e8d77"
            textColor="#a3a3a3"
            className="!w-10 !h-10 !p-0 !rounded-full flex items-center justify-center text-xl font-bold active:scale-95 transition-transform"
          >
            -
          </SpecularButton>

          <div className="w-14 flex justify-center items-center font-mono text-2xl font-bold text-accent drop-shadow-[0_0_10px_rgba(94,141,119,0.5)]">
            <CountUp to={yoe} duration={0.4} />
          </div>

          <SpecularButton
            size="sm"
            onClick={() => setYoe(yoe + 1)}
            baseColor="#0a0f10"
            lineColor="#5e8d77"
            textColor="#a3a3a3"
            className="!w-10 !h-10 !p-0 !rounded-full flex items-center justify-center text-xl font-bold active:scale-95 transition-transform"
          >
            +
          </SpecularButton>
        </div>
      </div>

      {/* Premium Strict Mode Toggle */}
      <div className="flex items-center gap-4 bg-white/[0.03] p-1.5 pr-2 rounded-full border border-white/10 backdrop-blur-sm shadow-[inset_0_1px_2px_rgba(255,255,255,0.05)] transition-all hover:bg-white/[0.05]">
        <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest pl-3">Strict Mode</span>
        <button
          onClick={() => setStrictMode(!strictMode)}
          className={cn(
            "w-12 h-6 rounded-full transition-all duration-300 relative shadow-inner overflow-hidden",
            strictMode ? "bg-accent/80 border border-accent/50" : "bg-black/60 border border-white/5"
          )}
        >
          <motion.div
            layout
            transition={{ type: "spring", stiffness: 500, damping: 30 }}
            className={cn(
              "absolute top-0.5 bottom-0.5 w-5 rounded-full bg-white transition-all",
              strictMode ? "left-[22px] shadow-[0_0_10px_rgba(255,255,255,0.8)]" : "left-0.5 opacity-60 shadow-none"
            )}
          />
        </button>
      </div>

      {/* University Filter */}
      <div className="flex items-center">
        <UniversityFilter 
          selectedUniversities={selectedUniversities}
          onChange={setSelectedUniversities}
        />
      </div>
    </div>
  );
}
