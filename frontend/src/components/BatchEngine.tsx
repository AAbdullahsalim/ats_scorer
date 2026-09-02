import React from "react";
import { X } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { AnimatedCircularProgressBar } from "@/registry/magicui/animated-circular-progress-bar";
import AIOrbFace from "@/components/AIOrbFace";
import BorderGlow from "@/components/BorderGlow";

interface BatchEngineProps {
  isProcessing: boolean;
  progress: number;
  errorMsg: string | null;
  handleRunAnalysis: () => void;
}

export default function BatchEngine({
  isProcessing,
  progress,
  errorMsg,
  handleRunAnalysis,
}: BatchEngineProps) {
  return (
    <div className="flex flex-col items-center p-8 bg-black/40 border border-border rounded-3xl backdrop-blur-md shadow-2xl">
      <h2 className="text-xl font-semibold mb-8 text-center text-foreground/90">Batch Processing Engine</h2>

      <div className="h-48 flex items-center justify-center">
        {isProcessing ? (
          <AnimatedCircularProgressBar
            value={progress}
            gaugePrimaryColor="#0d3b45"
            gaugeSecondaryColor="rgba(86, 97, 108, 0.2)"
            className="w-40 h-40 text-2xl font-mono text-primary-foreground"
          />
        ) : (
          <AIOrbFace size={140} state="idle" />
        )}
      </div>

      {errorMsg && (
        <motion.div
          initial={{ opacity: 0, y: 6, scale: 0.92 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, scale: 0.92 }}
          className="mt-4 flex justify-center w-full max-w-sm"
        >
          <BorderGlow
            borderRadius={9999}
            glowColor="239 68 68"
            colors={["#ef4444", "#dc2626", "#991b1b"]}
            backgroundColor="rgba(24, 9, 13, 0.9)"
            className="shadow-[0_0_15px_rgba(239,68,68,0.3)] backdrop-blur-md"
            contentClassName="px-4 py-2 flex items-center justify-center gap-2 border border-red-500/40"
          >
            <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping shrink-0" />
            <span className="text-[11px] font-mono font-bold tracking-wider text-red-300 uppercase text-center">
              {errorMsg}
            </span>
          </BorderGlow>
        </motion.div>
      )}

      <button
        className={cn(
          "mt-10 px-8 py-4 rounded-full font-bold tracking-wide transition-all active:scale-95 cursor-pointer flex items-center gap-2 backdrop-blur-md",
          isProcessing
            ? "bg-red-950/40 text-red-300 hover:bg-red-900/60 hover:text-red-200 border border-red-500/30 hover:border-red-500/60 shadow-[0_0_20px_rgba(239,68,68,0.2)]"
            : "bg-accent text-accent-foreground hover:opacity-90 shadow-[0_0_20px_rgba(94,141,119,0.4)] border border-white/5"
        )}
        onClick={handleRunAnalysis}
      >
        {isProcessing ? (
          <>
            <X size={18} /> CANCEL BATCH ANALYSIS
          </>
        ) : (
          "RUN BATCH ANALYSIS"
        )}
      </button>
    </div>
  );
}
