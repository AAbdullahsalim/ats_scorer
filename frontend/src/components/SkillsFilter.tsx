import React, { useState } from "react";
import { Trash2, Plus } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import CountUp from "@/components/CountUp";
import { MagneticButton } from "@/registry/magicui/magnetic-button";
import SpecularButton from "@/components/SpecularButton";

interface SkillsFilterProps {
  skills: string[];
  setSkills: React.Dispatch<React.SetStateAction<string[]>>;
  jdFile: File | null;
}

export default function SkillsFilter({ skills, setSkills, jdFile }: SkillsFilterProps) {
  const [newSkill, setNewSkill] = useState("");
  const [explodingSkills, setExplodingSkills] = useState<string[]>([]);
  const [isDeleteMode, setIsDeleteMode] = useState(false);
  const [selectedForDeletion, setSelectedForDeletion] = useState<string[]>([]);

  if (skills.length === 0 && !jdFile) {
    return null; // Only render if we have skills or a JD uploaded
  }

  const handleRemoveSkill = (skillToRemove: string) => {
    if (isDeleteMode) {
      if (selectedForDeletion.includes(skillToRemove)) {
        setSelectedForDeletion(prev => prev.filter(s => s !== skillToRemove));
      } else {
        setSelectedForDeletion(prev => [...prev, skillToRemove]);
      }
      return;
    }

    // Single item explosion on double click (non-delete mode)
    setExplodingSkills(prev => [...prev, skillToRemove]);
    setTimeout(() => {
      setSkills(prev => prev.filter(s => s !== skillToRemove));
      setExplodingSkills(prev => prev.filter(s => s !== skillToRemove));
    }, 400);
  };

  const handleAddSkill = (e: React.FormEvent) => {
    e.preventDefault();
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      setSkills([...skills, newSkill.trim()]);
    }
    setNewSkill("");
  };

  const handleTrashClick = () => {
    if (!isDeleteMode) {
      setIsDeleteMode(true);
      return;
    }

    if (selectedForDeletion.length === 0) {
      setIsDeleteMode(false);
      return;
    }

    // Explode selected skills!
    setExplodingSkills(prev => [...prev, ...selectedForDeletion]);

    // Clear state after animation
    setTimeout(() => {
      setSkills(prev => prev.filter(s => !selectedForDeletion.includes(s)));
      setExplodingSkills(prev => prev.filter(s => !selectedForDeletion.includes(s)));
      setSelectedForDeletion([]);
      setIsDeleteMode(false);
    }, 400);
  };

  return (
    <div className="p-8 rounded-3xl bg-secondary/10 border border-border shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between mb-6 pl-2 border-b border-white/5 pb-4">
        <div className="flex items-center gap-4">
          <p className="text-sm font-bold text-foreground uppercase tracking-widest">Required Skills</p>
          <div className="flex items-center justify-center min-w-[28px] h-6 px-2 rounded-full bg-white/[0.04] border border-white/10 text-xs font-mono text-muted-foreground shadow-[inset_0_1px_2px_rgba(0,0,0,0.3)]">
            <CountUp to={skills.length} duration={0.4} />
          </div>
        </div>

        <button
          onClick={handleTrashClick}
          title={isDeleteMode ? "Delete Selected" : "Select to Delete"}
          className={cn(
            "relative overflow-hidden w-[34px] h-[34px] flex items-center justify-center rounded-full transition-all shadow-sm active:scale-95 group",
            isDeleteMode
              ? "bg-red-500 text-white border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.55)]"
              : "bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500 hover:text-white hover:border-red-500"
          )}
        >
          <div
            className="absolute inset-0 pointer-events-none opacity-20 mix-blend-overlay"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
              backgroundRepeat: "repeat",
            }}
          />
          <Trash2 size={17} className="relative z-10 group-hover:scale-110 transition-transform" />
        </button>
      </div>

      <div className="flex flex-wrap gap-3 mb-6 min-h-[48px]">
        {skills.length === 0 && (
          <span className="text-sm text-muted-foreground/50 italic">No skills added yet.</span>
        )}
        {skills.map((skill: string, idx: number) => {
          const isExploding = explodingSkills.includes(skill);
          const isSelected = selectedForDeletion.includes(skill);
          return (
            <motion.div
              key={skill}
              initial={{ opacity: 0, scale: 0.8, y: 10 }}
              animate={
                isExploding
                  ? { opacity: 0, scale: 2.5, filter: "blur(8px)", y: -20 }
                  : { opacity: 1, scale: 1, y: 0, filter: "blur(0px)" }
              }
              transition={{
                duration: isExploding ? 0.4 : 0.5,
                delay: isExploding ? 0 : idx * 0.05,
                type: isExploding ? "tween" : "spring",
                stiffness: 200,
                damping: 15
              }}
              onClick={() => isDeleteMode && handleRemoveSkill(skill)}
              onDoubleClick={() => !isDeleteMode && handleRemoveSkill(skill)}
              className={cn(
                "relative group transition-all duration-300 rounded-full",
                isDeleteMode ? "cursor-pointer" : "cursor-default"
              )}
              title={isDeleteMode ? "Click to select for deletion" : "Double-click to remove"}
            >
              <MagneticButton
                className={cn(
                  "transition-all duration-300",
                  isSelected
                    ? "bg-red-500/20 border-red-500/50 text-red-400 shadow-[0_0_10px_rgba(239,68,68,0.2)]"
                    : "border-accent/30 bg-accent/10 text-accent group-hover:bg-black/60 group-hover:border-accent/50 group-hover:text-accent-foreground"
                )}
              >
                {skill}
              </MagneticButton>
            </motion.div>
          );
        })}
      </div>

      <form onSubmit={handleAddSkill} className="flex gap-2 relative mt-4">
        <input
          type="text"
          value={newSkill}
          onChange={(e) => setNewSkill(e.target.value)}
          placeholder="Add a missing skill..."
          className="bg-black/40 border border-white/10 rounded-full pl-6 pr-24 py-3.5 text-sm w-full focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/30 text-foreground transition-all shadow-[inset_0_2px_10px_rgba(0,0,0,0.5)] placeholder:text-muted-foreground/50"
        />
        <div className="absolute right-1.5 top-1.5 bottom-1.5 flex items-center">
          <SpecularButton
            type="submit"
            disabled={!newSkill.trim()}
            baseColor="#0d1415"
            lineColor="#5e8d77"
            textColor="#5e8d77"
            className="rounded-full !py-2 !px-5 text-xs font-bold tracking-wider disabled:opacity-50"
          >
            <Plus size={14} /> ADD
          </SpecularButton>
        </div>
      </form>
    </div>
  );
}
