"use client";

import React, { useRef, useState, useEffect } from 'react';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';

interface CircularGalleryProps {
  items: any[];
  onItemClick: (item: any, index: number) => void;
}

export default function CircularGallery({ items, onItemClick }: CircularGalleryProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollXProgress } = useScroll({ container: containerRef });
  
  if (items.length === 0) return null;

  return (
    <div className="relative w-full h-[400px] flex items-center justify-center overflow-hidden bg-[#15181E] rounded-xl border border-white/10 shadow-2xl">
      <div 
        ref={containerRef}
        className="flex w-full overflow-x-auto snap-x snap-mandatory scrollbar-hide py-10 px-[calc(50%-120px)] items-center gap-8"
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
  return (
    <motion.div 
      onClick={onClick}
      className="shrink-0 snap-center w-[240px] h-[320px] bg-gradient-to-b from-[#1C2028] to-[#12141A] rounded-2xl border border-white/10 shadow-xl cursor-pointer overflow-hidden flex flex-col hover:border-indigo-500/50 transition-colors group relative"
      whileHover={{ y: -10, scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {/* Decorative top header */}
      <div className="h-24 bg-gradient-to-r from-indigo-900/50 to-purple-900/50 w-full relative">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjIiIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSIvPjwvc3ZnPg==')] opacity-50" />
        <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 w-20 h-20 bg-[#15181E] rounded-full border-4 border-[#1C2028] flex items-center justify-center text-2xl font-bold text-white shadow-lg">
          #{index + 1}
        </div>
      </div>
      
      <div className="flex-1 flex flex-col items-center justify-center p-6 mt-6 text-center">
        <h3 className="text-lg font-bold text-white mb-1">{item.candidate_name || "Unknown"}</h3>
        <p className="text-xs text-gray-400 mb-4 uppercase tracking-wider">{item.current_role || "Candidate"}</p>
        
        <div className="w-full bg-black/30 rounded-lg p-3 border border-white/5">
          <p className="text-[10px] text-gray-500 uppercase mb-1">Match Score</p>
          <p className="text-2xl font-mono text-emerald-400 font-bold">{item.final_score_pct?.toFixed(1)}%</p>
        </div>
      </div>
      
      {/* Hover glow effect */}
      <div className="absolute inset-0 bg-indigo-500/0 group-hover:bg-indigo-500/10 transition-colors pointer-events-none" />
    </motion.div>
  );
}
