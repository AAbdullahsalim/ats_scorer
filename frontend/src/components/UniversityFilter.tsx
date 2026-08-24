"use client";

import { useState, useRef, useEffect } from "react";
import { Search, ChevronDown, Check, X, GraduationCap } from "lucide-react";
import { UNIVERSITIES } from "@/lib/constants/universities";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

interface UniversityFilterProps {
  selectedUniversities: string[];
  onChange: (universities: string[]) => void;
}

export default function UniversityFilter({ selectedUniversities, onChange }: UniversityFilterProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filteredUniversities = UNIVERSITIES.filter(uni => 
    uni.label.toLowerCase().includes(search.toLowerCase()) || 
    uni.value.toLowerCase().includes(search.toLowerCase())
  );

  const toggleUniversity = (value: string) => {
    if (selectedUniversities.includes(value)) {
      onChange(selectedUniversities.filter(u => u !== value));
    } else {
      onChange([...selectedUniversities, value]);
    }
  };

  const clearFilter = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange([]);
    setSearch("");
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center justify-between min-w-[200px] h-10 px-4 text-xs font-bold uppercase tracking-wider rounded-full border backdrop-blur-sm transition-all shadow-[inset_0_1px_2px_rgba(255,255,255,0.05)] focus:outline-none",
          isOpen || selectedUniversities.length > 0
            ? "bg-accent/10 border-accent/30 text-accent shadow-[0_0_15px_rgba(94,141,119,0.15)]"
            : "bg-white/[0.03] border-white/10 text-muted-foreground hover:bg-white/[0.05] hover:border-white/20 hover:text-white/80"
        )}
      >
        <div className="flex items-center gap-2 truncate">
          <GraduationCap size={14} className={selectedUniversities.length > 0 ? "text-accent" : "text-muted-foreground"} />
          <span className="truncate max-w-[120px]">
            {selectedUniversities.length > 0 
              ? `${selectedUniversities.length} Selected` 
              : "University"}
          </span>
        </div>
        <div className="flex items-center ml-3">
          {selectedUniversities.length > 0 && (
            <div 
              onClick={clearFilter}
              className="p-1 -ml-1 mr-1 rounded-full hover:bg-accent/20 transition-colors"
            >
              <X size={12} className="text-accent hover:text-accent/80 cursor-pointer" />
            </div>
          )}
          <ChevronDown size={14} className={cn("transition-transform duration-300", isOpen && "rotate-180")} />
        </div>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute left-0 mt-3 w-80 p-3 rounded-2xl bg-black/90 border border-accent/30 backdrop-blur-xl shadow-[0_10px_30px_rgba(0,0,0,0.8)] z-50 flex flex-col gap-2 overflow-hidden"
          >
            {/* Search Input */}
            <div className="relative flex items-center bg-white/[0.04] p-1 rounded-xl border border-white/5">
              <Search size={14} className="absolute left-3 text-white/40" />
              <input
                type="text"
                placeholder="Search universities..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs bg-transparent border-none text-white/90 placeholder:text-white/30 focus:outline-none focus:ring-0"
              />
            </div>
            
            {/* Options List */}
            <div className="max-h-60 overflow-y-auto pr-1 flex flex-col gap-1 mt-1 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
              {filteredUniversities.length === 0 ? (
                <div className="px-3 py-4 text-xs text-center text-white/40 font-mono">
                  No universities found
                </div>
              ) : (
                filteredUniversities.map((uni) => {
                  const isSelected = selectedUniversities.includes(uni.value);
                  return (
                    <div
                      key={uni.value}
                      onClick={() => toggleUniversity(uni.value)}
                      className={cn(
                        "flex items-center justify-between px-3 py-2.5 text-xs font-medium cursor-pointer rounded-lg transition-all",
                        isSelected 
                          ? "bg-accent/20 text-accent border border-accent/20" 
                          : "text-white/60 hover:bg-white/5 hover:text-white/90 border border-transparent"
                      )}
                    >
                      <span className="truncate pr-3 tracking-wide">{uni.label}</span>
                      {isSelected && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ type: "spring", stiffness: 500, damping: 30 }}
                        >
                          <Check size={14} className="text-accent flex-shrink-0" />
                        </motion.div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
