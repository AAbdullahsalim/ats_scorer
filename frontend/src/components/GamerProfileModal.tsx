"use client";

import { X, Mail, Phone, Link, MapPin, Award, CheckCircle2, XCircle } from "lucide-react";
import BorderGlow from "@/components/BorderGlow";
import CountUp from "@/components/CountUp";
import SplitFlapText from "@/components/SplitFlapText";
import GradientWaves from "@/components/GradientWaves";

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

  const totalSkills = contextual_skills.length + missing_skills.length + stuffed_skills.length;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0D1117]/95 backdrop-blur-sm p-4 md:p-8 overflow-y-auto">
      <div className="relative z-10 w-full max-w-6xl">
        <BorderGlow glowColor="79 70 229" backgroundColor="#161B22" className="w-full">
          <div className="relative w-full p-8 md:p-10 text-gray-200">
            
            {/* Close Button */}
            <button 
              onClick={onClose}
              className="absolute top-6 right-6 p-2 bg-white/5 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-colors z-20"
            >
              <X size={20} />
            </button>

            {/* HEADER: Rank & Name */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-white/5 pb-8 mb-8">
              <div className="flex items-center gap-6">
                <div className="flex flex-col items-center justify-center w-16 h-16 rounded-xl bg-[#21262D] border border-white/10 font-bold text-3xl text-indigo-400 shadow-md">
                  #{rank}
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-white tracking-tight">{candidate_name}</h1>
                  <p className="text-gray-400 text-sm mt-1 uppercase tracking-wider font-medium">{current_role || "Candidate"}</p>
                </div>
              </div>
              
              <div className="mt-6 md:mt-0 text-right">
                <p className="text-gray-500 uppercase tracking-widest text-xs mb-1 font-semibold">Final Match Score</p>
                <div className="text-5xl font-bold text-emerald-400 flex items-end justify-end">
                  <CountUp to={final_score_pct} decimals={1} duration={1} />
                  <span className="text-2xl ml-1 mb-1">%</span>
                </div>
              </div>
            </div>

            {/* CONTACT INFO */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 bg-[#0D1117] p-4 rounded-xl border border-white/5">
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Mail className="text-gray-500" size={16} />
                <span className="truncate">{contact?.email || "N/A"}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Phone className="text-gray-500" size={16} />
                <span className="truncate">{contact?.phone || "N/A"}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Link className="text-gray-500" size={16} />
                <span className="truncate">{contact?.linkedin || "N/A"}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <MapPin className="text-gray-500" size={16} />
                <span className="truncate">{contact?.location || "N/A"}</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
              {/* LEFT COLUMN: Summary & Sub-scores */}
              <div className="flex flex-col gap-8">
                <div>
                  <h3 className="text-xl font-bold flex items-center gap-2 mb-4 text-white/90">
                    <Award className="text-yellow-500" /> AI Candidate Summary
                  </h3>
                  <div className="p-6 bg-indigo-950/30 rounded-xl border border-indigo-500/20 text-gray-300 leading-relaxed text-lg">
                    {candidate_summary || "No summary available."}
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-bold mb-4 text-white/90">Explainable Sub-Scores</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <ScoreCard label="Skill Match" value={audit?.subscores?.skill_match} max={35} />
                    <ScoreCard label="Recent Exp Match" value={audit?.subscores?.recent_exp} max={45} />
                    <ScoreCard label="Older Exp Match" value={audit?.subscores?.older_exp} max={20} />
                    <ScoreCard label="Keyword (BM25)" value={audit?.subscores?.bm25_keyword} max={100} />
                  </div>
                </div>
              </div>

              {/* RIGHT COLUMN: Skills Analysis */}
              <div className="flex flex-col gap-8">
                <div>
                  <h3 className="text-xl font-bold mb-6 text-white/90">Section Match Analysis</h3>
                  <div className="flex flex-col gap-5">
                    <ProgressBarItem label="Skills Section" pct={(audit?.subscores?.skill_match / 35) * 100 || 0} color="bg-blue-500" />
                    <ProgressBarItem label="Recent Experience" pct={(audit?.subscores?.recent_exp / 45) * 100 || 0} color="bg-green-500" />
                    <ProgressBarItem label="Older Experience" pct={(audit?.subscores?.older_exp / 20) * 100 || 0} color="bg-purple-500" />
                    <ProgressBarItem label="BM25 Keywords" pct={audit?.subscores?.bm25_keyword || 0} color="bg-yellow-500" />
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-bold mb-6 text-white/90 flex justify-between items-end">
                    Skill Badge Matrix
                    <span className="text-sm font-normal text-gray-400">{candidate_yoe} Est. Years Experience</span>
                  </h3>
                  
                  <div className="flex flex-wrap gap-2">
                    {contextual_skills.map((s: string) => (
                      <Badge key={s} type="verified">{s} (Verified)</Badge>
                    ))}
                    {stuffed_skills.map((s: string) => (
                      <Badge key={s} type="stuffed">{s} (Listed Only)</Badge>
                    ))}
                    {missing_skills.map((s: string) => (
                      <Badge key={s} type="missing">{s} (Missing)</Badge>
                    ))}
                    {nice_to_have_matched.map((s: string) => (
                      <Badge key={s} type="bonus">{s} (Bonus)</Badge>
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

function ScoreCard({ label, value, max }: { label: string, value: number, max: number }) {
  return (
    <div className="bg-[#0D1117] border border-white/5 rounded-xl p-4 flex flex-col justify-between">
      <span className="text-xs text-gray-500 uppercase tracking-wider font-medium">{label}</span>
      <div className="mt-2 text-2xl font-bold text-gray-200 flex items-baseline gap-1">
        <CountUp to={value || 0} decimals={1} duration={1} />
        <span className="text-xs text-gray-600 font-normal">/ {max} pts</span>
      </div>
    </div>
  );
}

function ProgressBarItem({ label, pct, color }: { label: string, pct: number, color: string }) {
  return (
    <div className="w-full">
      <div className="flex justify-between text-xs mb-1.5">
        <span className="text-gray-400">{label}</span>
        <span className="text-gray-300 font-mono">{pct.toFixed(1)}%</span>
      </div>
      <div className="w-full h-2 bg-[#0D1117] rounded-full overflow-hidden border border-white/5">
        <div 
          className={`h-full rounded-full ${color} transition-all duration-1000 ease-out opacity-80`} 
          style={{ width: `${Math.min(100, Math.max(0, pct))}%` }} 
        />
      </div>
    </div>
  );
}

function Badge({ children, type }: { children: React.ReactNode, type: 'verified' | 'stuffed' | 'missing' | 'bonus' }) {
  const styles = {
    verified: "bg-emerald-950/30 border-emerald-900/50 text-emerald-400",
    stuffed: "bg-yellow-950/30 border-yellow-900/50 text-yellow-400",
    missing: "bg-red-950/30 border-red-900/50 text-red-400",
    bonus: "bg-indigo-950/30 border-indigo-900/50 text-indigo-400",
  };

  const icons = {
    verified: <CheckCircle2 size={12} className="mr-1.5 opacity-70" />,
    stuffed: <div className="w-1.5 h-1.5 rounded-full bg-yellow-500/70 mr-2" />,
    missing: <XCircle size={12} className="mr-1.5 opacity-70" />,
    bonus: <Award size={12} className="mr-1.5 opacity-70" />,
  };

  return (
    <span className={`flex items-center px-2.5 py-1 rounded-md border text-xs font-medium ${styles[type]}`}>
      {icons[type]}
      {children}
    </span>
  );
}
