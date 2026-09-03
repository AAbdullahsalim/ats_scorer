"use client";

import React from "react";
import { X, Mail, Phone, Link, MapPin, Award, CheckCircle2, XCircle } from "lucide-react";
import BorderGlow from "@/components/BorderGlow";
import CountUp from "@/components/CountUp";
import { cn } from "@/lib/utils";

interface GamerProfileModalProps {
  candidate: any;
  onClose: () => void;
  rank: number;
}

export default function GamerProfileModal({ candidate, onClose, rank }: GamerProfileModalProps) {
  if (!candidate) return null;

  const {
    candidate_name,
    contact,
    final_score_pct,
    candidate_yoe,
    current_role,
    contextual_skills = [],
    missing_skills = [],
    stuffed_skills = [],
    nice_to_have_matched = [],
    audit,
    candidate_summary,
  } = candidate;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/85 backdrop-blur-md p-4 md:p-8 flex justify-center items-start">
      <div className="relative z-10 w-full max-w-6xl my-auto">
        <BorderGlow glowColor="94 141 119" backgroundColor="#0d1415" className="w-full">
          <div className="relative w-full p-8 md:p-10 text-gray-200">
            
            {/* Close Button */}
            <button 
              onClick={onClose}
              className="absolute top-7 right-7 overflow-hidden w-[34px] h-[34px] flex items-center justify-center bg-white/5 hover:bg-red-500/20 hover:text-red-400 rounded-full text-gray-300 hover:border-red-500/40 border border-white/10 transition-all active:scale-95 shadow-sm z-20"
              title="Close"
            >
              <div 
                className="absolute inset-0 pointer-events-none opacity-25 mix-blend-overlay"
                style={{
                  backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
                  backgroundRepeat: "repeat",
                }}
              />
              <X size={17} className="relative z-10" />
            </button>

            {/* HEADER: Rank, Name & Score */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-white/10 pb-7 mb-7 pr-12 gap-6">
              <div className="flex items-center gap-5">
                <div className="flex flex-col items-center justify-center w-16 h-16 rounded-2xl bg-primary/20 border border-primary/40 font-black text-3xl text-accent shadow-[0_0_20px_rgba(94,141,119,0.25)]">
                  #{rank}
                </div>
                <div>
                  <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
                    {candidate_name}
                  </h1>
                  <p className="text-gray-400 text-sm mt-1 uppercase tracking-widest font-semibold">
                    {current_role || "Candidate"}
                  </p>
                </div>
              </div>
              
              <div className="text-left md:text-right">
                <p className="text-gray-400 uppercase tracking-widest text-xs mb-1 font-semibold">
                  Final Match Score
                </p>
                <div className="text-4xl md:text-5xl font-black text-emerald-400 flex items-end md:justify-end drop-shadow-[0_0_25px_rgba(52,211,153,0.35)]">
                  <CountUp to={final_score_pct} decimals={1} duration={1} />
                  <span className="text-2xl md:text-3xl ml-1 mb-1 font-bold">%</span>
                </div>
              </div>
            </div>

            {/* CONTACT INFO BAR */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 bg-black/30 p-4 rounded-2xl border border-white/5 text-xs font-medium">
              <div className="flex items-center gap-2.5 text-gray-300">
                <Mail className="text-accent shrink-0" size={15} />
                <span className="truncate">{contact?.email || "N/A"}</span>
              </div>
              <div className="flex items-center gap-2.5 text-gray-300">
                <Phone className="text-accent shrink-0" size={15} />
                <span className="truncate">{contact?.phone || "N/A"}</span>
              </div>
              <div className="flex items-center gap-2.5 text-gray-300">
                <Link className="text-accent shrink-0" size={15} />
                <span className="truncate">{contact?.linkedin || "N/A"}</span>
              </div>
              <div className="flex items-center gap-2.5 text-gray-300">
                <MapPin className="text-accent shrink-0" size={15} />
                <span className="truncate">{contact?.location || "N/A"}</span>
              </div>
            </div>

            {/* 2-COLUMN BALANCED CONTENT GRID */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-10">
              
              {/* LEFT COLUMN: Summary & Score Modifiers */}
              <div className="flex flex-col gap-8">
                <div>
                  <h3 className="text-base font-bold flex items-center gap-2.5 mb-3.5 text-white">
                    <Award className="text-accent" size={18} /> AI Candidate Summary
                  </h3>
                  <div className="p-6 bg-secondary/10 rounded-2xl border border-border text-gray-300 leading-relaxed text-sm shadow-[inset_0_2px_8px_rgba(0,0,0,0.4)]">
                    {candidate_summary || "No summary available."}
                  </div>
                </div>

                <div>
                  <h3 className="text-base font-bold mb-3.5 text-white">Score Modifiers (How skills affected the score)</h3>
                  <div className="flex flex-col gap-3 p-6 bg-secondary/10 rounded-2xl border border-border text-gray-300 text-sm shadow-[inset_0_2px_8px_rgba(0,0,0,0.4)]">
                    <div className="flex justify-between items-center border-b border-border/50 pb-2">
                      <span className="text-gray-400">Mandatory Skill Penalty</span>
                      <span className="font-mono font-bold text-red-400">
                        {audit?.must_have_penalty_pct < 0 ? "" : "-"}{audit?.must_have_penalty_pct || 0}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Role Match Booster</span>
                      <span className="font-mono font-bold text-emerald-400">
                        +{audit?.role_match_bonus_pct || 0}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* RIGHT COLUMN: Section Match & Skill Badges */}
              <div className="flex flex-col gap-8">
                <div>
                  <h3 className="text-base font-bold mb-3.5 text-white flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
                    Section Match Analysis
                  </h3>
                  <div className="flex flex-col gap-4 bg-black/30 p-5 rounded-2xl border border-white/10 shadow-[inset_0_2px_10px_rgba(0,0,0,0.5)]">
                    <ProgressBarItem 
                      label="Tech Stack Alignment" 
                      pct={(audit?.subscores?.skill_match / 35) * 100 || 0} 
                      gradient="bg-gradient-to-r from-[#2d6a4f] to-[#52b788]"
                      glowColor="rgba(82,183,136,0.3)" 
                    />
                    <ProgressBarItem 
                      label="Recent Role Relevance" 
                      pct={(audit?.subscores?.recent_exp / 45) * 100 || 0} 
                      gradient="bg-gradient-to-r from-[#1b4332] to-[#40916c]"
                      glowColor="rgba(64,145,108,0.3)" 
                    />
                    <ProgressBarItem 
                      label="Past Role Relevance" 
                      pct={(audit?.subscores?.older_exp / 20) * 100 || 0} 
                      gradient="bg-gradient-to-r from-[#081c15] to-[#2d6a4f]"
                      glowColor="rgba(45,106,79,0.25)" 
                    />
                    <ProgressBarItem 
                      label="Keyword Matching" 
                      pct={audit?.subscores?.bm25_keyword || 0} 
                      gradient="bg-gradient-to-r from-[#1f4e5b] to-[#5e8d77]"
                      glowColor="rgba(94,141,119,0.35)" 
                    />
                  </div>
                </div>

                <div>
                  <h3 className="text-base font-bold mb-3.5 text-white flex justify-between items-end">
                    <span className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-accent" />
                      Skill Badge Matrix
                    </span>
                    <span className="text-xs font-mono font-normal text-accent">{candidate_yoe} Est. Years Experience</span>
                  </h3>
                  
                  <div className="bg-black/30 p-5 rounded-2xl border border-white/10 shadow-[inset_0_2px_10px_rgba(0,0,0,0.5)] flex flex-wrap gap-2.5 max-h-60 overflow-y-auto scrollbar-thin">
                    {contextual_skills.map((s: string) => (
                      <Badge key={s} type="verified">{s}</Badge>
                    ))}
                    {stuffed_skills.map((s: string) => (
                      <Badge key={s} type="stuffed">{s}</Badge>
                    ))}
                    {missing_skills.map((s: string) => (
                      <Badge key={s} type="missing">{s}</Badge>
                    ))}
                    {nice_to_have_matched.map((s: string) => (
                      <Badge key={s} type="bonus">{s}</Badge>
                    ))}
                  </div>
                </div>
              </div>

            </div>

          </div>
        </BorderGlow>
      </div>
    </div>
  );
}

// Helpers

function ProgressBarItem({ 
  label, 
  pct, 
  gradient, 
  glowColor 
}: { 
  label: string, 
  pct: number, 
  gradient: string, 
  glowColor: string 
}) {
  const safePct = Math.max(0, Math.min(100, isNaN(pct) ? 0 : pct));
  return (
    <div className="w-full">
      <div className="flex justify-between text-xs mb-1.5 font-medium">
        <span className="text-gray-300 font-mono text-xs">{label}</span>
        <span className="text-accent font-mono font-bold">{safePct.toFixed(1)}%</span>
      </div>
      <div className="w-full h-2.5 bg-black/60 rounded-full overflow-hidden border border-white/5 p-0.5 shadow-[inset_0_1px_3px_rgba(0,0,0,0.8)]">
        <div 
          className={cn("h-full rounded-full transition-all duration-1000 ease-out", gradient)} 
          style={{ 
            width: `${safePct}%`,
            boxShadow: `0 0 12px ${glowColor}`
          }} 
        />
      </div>
    </div>
  );
}

function Badge({ children, type }: { children: React.ReactNode, type: 'verified' | 'stuffed' | 'missing' | 'bonus' }) {
  const styles = {
    verified: "bg-emerald-950/60 border-emerald-500/40 text-emerald-300 shadow-[0_0_12px_rgba(16,185,129,0.18)] hover:border-emerald-400 hover:bg-emerald-900/50",
    stuffed: "bg-amber-950/60 border-amber-500/40 text-amber-300 shadow-[0_0_12px_rgba(245,158,11,0.18)] hover:border-amber-400 hover:bg-amber-900/50",
    missing: "bg-rose-950/60 border-rose-500/40 text-rose-300 shadow-[0_0_12px_rgba(244,63,94,0.18)] hover:border-rose-400 hover:bg-rose-900/50",
    bonus: "bg-cyan-950/60 border-cyan-500/40 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.18)] hover:border-cyan-400 hover:bg-cyan-900/50",
  };

  const labels = {
    verified: "Verified",
    stuffed: "Listed Only",
    missing: "Missing",
    bonus: "Bonus",
  };

  const icons = {
    verified: <CheckCircle2 size={13} className="mr-1.5 text-emerald-400 shrink-0" />,
    stuffed: <div className="w-2 h-2 rounded-full bg-amber-400 mr-1.5 shrink-0 shadow-[0_0_6px_rgba(245,158,11,0.8)]" />,
    missing: <XCircle size={13} className="mr-1.5 text-rose-400 shrink-0" />,
    bonus: <Award size={13} className="mr-1.5 text-cyan-400 shrink-0" />,
  };

  return (
    <span className={cn(
      "relative inline-flex items-center px-3.5 py-1.5 rounded-full border text-xs font-semibold overflow-hidden transition-all backdrop-blur-md",
      styles[type]
    )}>
      {/* Subtle micro-grain overlay */}
      <div 
        className="absolute inset-0 pointer-events-none opacity-[0.16] mix-blend-overlay"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          backgroundRepeat: "repeat",
        }}
      />
      <span className="relative z-10 flex items-center gap-1">
        {icons[type]}
        <span className="text-white/95 font-medium">{children}</span>
        <span className="text-[10px] font-mono font-bold opacity-80 ml-1">({labels[type]})</span>
      </span>
    </span>
  );
}
