"use client";

import React from 'react';
import { cn } from "@/lib/utils";

export interface GlassIconItem {
  icon: React.ReactNode;
  color: string;
  label: string;
  onClick?: () => void;
}

export default function GlassIcons({ 
  items, 
  className, 
  colorful = true 
}: { 
  items: GlassIconItem[], 
  className?: string, 
  colorful?: boolean 
}) {
  
  // Helper to map color strings to tailwind hex/vars for the glow effect
  const getColorGlow = (color: string) => {
    switch(color) {
      case 'blue': return 'rgba(59, 130, 246, 0.5)';
      case 'purple': return 'rgba(168, 85, 247, 0.5)';
      case 'red': return 'rgba(239, 68, 68, 0.5)';
      case 'green': return 'rgba(34, 197, 94, 0.5)';
      case 'indigo': return 'rgba(99, 102, 241, 0.5)';
      case 'orange': return 'rgba(249, 115, 22, 0.5)';
      default: return 'rgba(94, 141, 119, 0.5)'; // accent
    }
  };

  const getTextColor = (color: string) => {
    switch(color) {
      case 'blue': return '#60a5fa';
      case 'purple': return '#c084fc';
      case 'red': return '#f87171';
      case 'green': return '#4ade80';
      case 'indigo': return '#818cf8';
      case 'orange': return '#fb923c';
      default: return '#5e8d77';
    }
  };

  return (
    <div className={cn("flex gap-3 items-center", className)}>
      {items.map((item, idx) => (
        <button
          key={idx}
          onClick={(e) => {
            // Prevent event from bubbling up to row click (if any)
            e.stopPropagation();
            if (item.onClick) item.onClick();
          }}
          title={item.label}
          className={cn(
            "relative group flex items-center justify-center p-2.5 rounded-[1rem] transition-all duration-300",
            "bg-white/[0.03] backdrop-blur-md border border-white/[0.08] shadow-[inset_0_1px_1px_rgba(255,255,255,0.1),0_4px_15px_rgba(0,0,0,0.5)]",
            "hover:bg-white/[0.08] hover:-translate-y-1 hover:border-white/[0.15]"
          )}
          style={{
            ['--glow-color' as any]: colorful ? getColorGlow(item.color) : 'rgba(255,255,255,0.2)',
            ['--text-color' as any]: colorful ? getTextColor(item.color) : '#fff'
          }}
        >
          {/* Inner glow mask */}
          <div className="absolute inset-0 rounded-[1rem] opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" 
               style={{ boxShadow: '0 0 15px var(--glow-color)' }} 
          />
          
          <div 
            className="relative z-10 text-muted-foreground transition-colors duration-300"
            style={{ color: 'inherit' }}
            onMouseEnter={(e) => {
              if (colorful) e.currentTarget.style.color = getTextColor(item.color);
              else e.currentTarget.style.color = '#fff';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = '';
            }}
          >
            {item.icon}
          </div>
        </button>
      ))}
    </div>
  );
}
