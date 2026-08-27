"use client";

import React, { useRef, useState, useEffect } from 'react';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';
import { cn } from "@/lib/utils";

interface CircularGalleryProps {
  items: any[];
  onItemClick: (item: any, index: number) => void;
}

export default function CircularGallery({ items, onItemClick }: CircularGalleryProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollXProgress } = useScroll({ container: containerRef });
  
  if (items.length === 0) return null;

  return (
    <div className="relative w-full h-[450px] flex items-center justify-center overflow-hidden bg-background rounded-2xl shadow-[inset_0_0_40px_rgba(0,0,0,0.8)] border border-border">
      <div 
        ref={containerRef}
        className="flex w-full overflow-x-auto snap-x snap-mandatory scrollbar-hide py-10 px-8 items-center gap-6"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {items.map((item, i) => (
          <GalleryItem key={i} item={item} index={i} onClick={() => onItemClick(item, i)} progress={scrollXProgress} total={items.length} />
        ))}
      </div>
      
      {/* Scroll indicator instructions */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-gray-500 text-xs font-mono tracking-widest pointer-events-none">
        SWIPE / SCROLL TO BROWSE
      </div>
    </div>
  );
}

function GalleryItem({ item, index, onClick, progress, total }: any) {
  const isLowScore = item.final_score_pct < 20;

  return (
    <motion.div 
      onClick={onClick}
      className="shrink-0 snap-center w-[280px] h-[360px] bg-secondary/30 rounded-[2rem] border border-border shadow-2xl cursor-pointer overflow-hidden flex flex-col group relative transition-transform"
      whileHover={{ y: -10, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {/* Badge at top */}
      <div className="absolute top-4 left-4 z-10">
        <span className={cn(
          "px-3 py-1 text-xs font-bold uppercase tracking-wider rounded-full backdrop-blur-md shadow-sm border",
          isLowScore ? "bg-red-500/20 text-red-400 border-red-500/30" : "bg-accent/20 text-accent border-accent/30"
        )}>
          {item.final_score_pct?.toFixed(1)}% Match
        </span>
      </div>

      <div className="absolute top-4 right-4 z-10">
        <div className="w-8 h-8 rounded-full bg-background border border-border flex items-center justify-center text-xs font-bold text-muted-foreground">
          #{index + 1}
        </div>
      </div>

      {/* Background Graphic */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/40 to-background opacity-80" />
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjIiIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSIvPjwvc3ZnPg==')] opacity-30 mix-blend-overlay" />

      {/* Content */}
      <div className="relative z-10 flex-1 flex flex-col justify-end p-6 bg-gradient-to-t from-background/90 via-background/40 to-transparent">
        <h3 className="text-2xl font-bold text-foreground mb-1 tracking-tight drop-shadow-md">{item.candidate_name || "Unknown"}</h3>
        <p className="text-sm text-muted-foreground mb-3 font-medium">{item.current_role || "Candidate"}</p>
        
        <div className="flex items-center justify-between mt-2 pt-4 border-t border-white/10">
          <span className="text-xs text-muted-foreground uppercase tracking-widest">{item.candidate_yoe} YOE</span>
          <span className="text-xs text-accent font-semibold flex items-center gap-1 group-hover:underline transition-all">
            📄 View CV Document →
          </span>
        </div>
      </div>
      
      {/* Hover glow effect */}
      <div className="absolute inset-0 bg-white/0 group-hover:bg-white/5 transition-colors pointer-events-none" />
    </motion.div>
  );
}
