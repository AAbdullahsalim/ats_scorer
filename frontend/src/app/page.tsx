"use client";

import React, { useState, useEffect, useRef } from "react";
import { InteractiveHoverButton } from "@/registry/magicui/interactive-hover-button";
import { AnimatedCircularProgressBar } from "@/registry/magicui/animated-circular-progress-bar";
import AIOrbFace from "@/components/AIOrbFace";
import CircularGallery from "@/components/CircularGallery";
import GamerProfileModal from "@/components/GamerProfileModal";
import CVPreviewModal from "@/components/CVPreviewModal";
import { MagneticButton } from "@/registry/magicui/magnetic-button";
import { analyzeCandidates, parseJd } from "@/lib/api";
import { X, Plus, User, Trash2 } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import GlassIcons from "@/components/GlassIcons";
import SpecularButton from "@/components/SpecularButton";
import BorderGlow from "@/components/BorderGlow";
import CountUp from "@/components/CountUp";
import { NoiseTexture } from "@/registry/magicui/noise-texture";
import CosmicDust from "@/components/lightswind/cosmic-dust";

export default function Home() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [candidates, setCandidates] = useState<any[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const [showCV, setShowCV] = useState(false);
  const [yoe, setYoe] = useState(0);
  const [strictMode, setStrictMode] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [jdAnalysis, setJdAnalysis] = useState<any>(null);
  const [fileUrls, setFileUrls] = useState<Record<string, string>>({});

  // Custom skills state for editing before analysis
  const [skills, setSkills] = useState<string[]>([]);
  const [newSkill, setNewSkill] = useState("");
  const [isParsingJd, setIsParsingJd] = useState(false);
  const [explodingSkills, setExplodingSkills] = useState<string[]>([]);
  const [isDeleteMode, setIsDeleteMode] = useState(false);
  const [selectedForDeletion, setSelectedForDeletion] = useState<string[]>([]);

  // Dummy data for testing the UI
  const dummyCandidates = [
    { candidate_name: "John Doe", current_role: "Frontend Engineer", final_score_pct: 85, candidate_yoe: 3 },
    { candidate_name: "Jane Smith", current_role: "Backend Developer", final_score_pct: 92, candidate_yoe: 5 },
    { candidate_name: "Mike Johnson", current_role: "Fullstack Dev", final_score_pct: 15, candidate_yoe: 1 },
    { candidate_name: "Emily Davis", current_role: "UI/UX Designer", final_score_pct: 78, candidate_yoe: 4 }
  ];

  const [jdFile, setJdFile] = useState<File | null>(null);
  const [cvFiles, setCvFiles] = useState<File[]>([]);

  const jdInputRef = useRef<HTMLInputElement>(null);
  const cvInputRef = useRef<HTMLInputElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (errorMsg) {
      const timer = setTimeout(() => {
        setErrorMsg(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [errorMsg]);

  const handleCancelAnalysis = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }
    setIsProcessing(false);
    setProgress(0);
    setErrorMsg("Batch analysis cancelled by user.");
  };

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

  const handleJdUpload = async (file: File) => {
    setJdFile(file);
    setErrorMsg(null);
    setIsParsingJd(true);
    try {
      const parsed = await parseJd(file);
      setJdAnalysis(parsed);
      setSkills(parsed.must_have_skills || []);
    } catch (error) {
      console.error("Failed to parse JD:", error);
      setErrorMsg("Failed to auto-parse JD. Please check backend connection.");
    }
    setIsParsingJd(false);
  };

  const handleRunAnalysis = async () => {
    if (isProcessing) {
      handleCancelAnalysis();
      return;
    }

    setErrorMsg(null);
    if (!jdFile) {
      setErrorMsg("Please upload a Job Description first.");
      return;
    }
    if (cvFiles.length === 0) {
      setErrorMsg("Please upload at least one CV.");
      return;
    }

    setIsProcessing(true);
    setProgress(10); // Start progress

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      progressIntervalRef.current = setInterval(() => {
        setProgress(p => Math.min(p + 2, 90)); // cap at 90% until done
      }, 500);

      const customSkillsStr = skills.join(",");
      const results = await analyzeCandidates(
        jdFile,
        cvFiles,
        yoe,
        customSkillsStr,
        "",
        controller.signal
      );

      let processedCandidates = results.candidates || [];
      if (strictMode) {
        processedCandidates = processedCandidates.filter(
          (c: any) => c.candidate_yoe >= yoe && (!c.missing_skills || c.missing_skills.length === 0)
        );
      }

      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      setProgress(100);

      if (processedCandidates.length === 0 && strictMode && (results.candidates?.length > 0)) {
        setErrorMsg("Strict mode filtered out all candidates (missing skills or below minimum YOE).");
      }

      // Update state with actual backend results
      setCandidates(processedCandidates);
      setJdAnalysis(results.jd_analysis || null);

      // Create object URLs for actual document preview
      const urls: Record<string, string> = {};
      cvFiles.forEach(file => {
        urls[file.name] = URL.createObjectURL(file);
      });
      setFileUrls(urls);

      // Stop processing state after a short delay to show 100%
      setTimeout(() => {
        setIsProcessing(false);
      }, 1000);

    } catch (error: any) {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      if (error.name === "AbortError" || controller.signal.aborted) {
        console.log("Analysis aborted by user.");
        setErrorMsg("Batch analysis cancelled by user.");
      } else {
        console.error("Analysis failed:", error);
        setErrorMsg("Analysis failed. Please check the backend connection.");
      }
      setIsProcessing(false);
      setProgress(0);
    } finally {
      abortControllerRef.current = null;
    }
  };

  return (
    <main className="relative min-h-screen flex flex-col items-center p-8 lg:p-24 pb-32 overflow-hidden bg-background">
      {/* Dynamic Cosmic Dust Particles (Theme Color Palettes) */}
      <CosmicDust
        className="fixed inset-0 pointer-events-none z-0"
        particleColors={["#5e8d77", "#34d399", "#10b981", "#6ee7b7", "#a7f3d0", "#ffffff"]}
        particleCount={80}
        speed={0.2}
        opacity={0.5}
        minSize={0.8}
        maxSize={2.2}
      />

      {/* MagicUI Noise Texture with prominent tactile feel */}
      <NoiseTexture
        className={cn(
          "fixed inset-0 pointer-events-none z-0 opacity-45 mix-blend-overlay",
          "mask-[radial-gradient(circle_at_center,white_75%,transparent_100%)]"
        )}
      />

      {/* Content Layer */}
      <div className="relative z-10 w-full flex flex-col items-center">
        {/* Startup Template Hero Section */}
        <div className="flex flex-col md:flex-row items-center justify-between w-full max-w-7xl mt-6 border-b border-white/10 pb-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center font-black text-primary-foreground shadow-lg shadow-primary/20">
              AI
            </div>
            <h1 className="text-3xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-br from-white to-white/40">
              ATS<span className="text-primary">SCORER</span>
            </h1>
          </div>

          <div className="flex gap-4 mt-8 lg:mt-0">
            <input
              type="file"
              ref={jdInputRef}
              className="hidden"
              accept=".pdf,.docx,.txt"
              onChange={(e) => {
                if (e.target.files && e.target.files.length > 0) {
                  handleJdUpload(e.target.files[0]);
                }
              }}
            />
            <input
              type="file"
              ref={cvInputRef}
              className="hidden"
              multiple
              accept=".pdf,.docx,.txt"
              onChange={(e) => {
                if (e.target.files) {
                  setCvFiles(Array.from(e.target.files));
                }
              }}
            />
            <InteractiveHoverButton
              text={isParsingJd ? "Parsing JD..." : jdFile ? "JD Selected ✓" : "Upload JD"}
              loaderColor="amber"
              onClick={() => jdInputRef.current?.click()}
              disabled={isParsingJd}
            />
            <InteractiveHoverButton
              text={cvFiles.length > 0 ? `${cvFiles.length} CVs ✓` : "Upload CVs"}
              loaderColor="green"
              onClick={() => cvInputRef.current?.click()}
            />
          </div>
        </div>

        {/* Global Controls (Below Header Line) */}
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
        </div>

        {/* Main Content Area - Golden Ratio Layout */}
        <div className="flex flex-col lg:flex-row items-start justify-center gap-12 w-full max-w-7xl mt-16">

          {/* Left Column (Input & Processing) - 38.2% */}
          <div className="flex flex-col gap-8 w-full lg:w-[38.2%]">

            {/* Processing Engine */}
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

            {/* Dynamic Skills Filter always visible when JD is uploaded, or when user adds manual skills */}
            {(skills.length > 0 || jdFile) && (
              <div className="p-8 rounded-3xl bg-secondary/10 border border-border shadow-xl backdrop-blur-sm">
                <div className="flex items-center justify-between mb-6 pl-2 border-b border-white/5 pb-4">
                  <div className="flex items-center gap-4">
                    <p className="text-sm font-bold text-foreground uppercase tracking-widest">Required Skills</p>
                    {/* Subtle, dynamic count badge positioned using visual balance */}
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
            )}
          </div>

          {/* Right Column (Outputs & Results) - 61.8% */}
          <div className="flex flex-col flex-grow w-full lg:w-[61.8%] min-h-[500px]">

            {candidates.length > 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="w-full flex flex-col gap-8"
              >
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
                  Analysis Complete
                  <span className="text-xs bg-accent/20 text-accent px-3 py-1 rounded-full border border-accent/30 font-mono">
                    {candidates.length} Found
                  </span>
                </h2>

                {/* Detailed Results Table */}
                <div className="overflow-x-auto rounded-3xl bg-secondary/10 border border-border shadow-xl backdrop-blur-sm">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-white/5 bg-black/20 text-xs uppercase tracking-wider text-muted-foreground font-semibold">
                        <th className="p-4 pl-6 w-16">Rank</th>
                        <th className="p-4 w-48">Candidate</th>
                        <th className="p-4 w-24">Match</th>
                        <th className="p-4 w-24">YOE</th>
                        <th className="p-4">Skills (Found / Missing)</th>
                        <th className="p-4 pr-6 text-right w-32">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {candidates.map((cand: any, idx: number) => {
                        const isLowScore = cand.final_score_pct < 20;
                        return (
                          <tr key={idx} className="hover:bg-white/5 transition-colors group">
                            <td className="p-4 pl-6 font-mono text-sm text-muted-foreground">#{idx + 1}</td>
                            <td className="p-4">
                              <div className="font-bold text-foreground text-sm truncate max-w-[200px]" title={cand.candidate_name}>{cand.candidate_name || "Unknown"}</div>
                              <div className="text-xs text-muted-foreground truncate max-w-[200px]" title={cand.current_role}>{cand.current_role || "Candidate"}</div>
                            </td>
                            <td className="p-4">
                              <span className={`px-2 py-1 text-xs font-bold rounded-full border ${isLowScore ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-accent/20 text-accent border-accent/30'}`}>
                                {cand.final_score_pct?.toFixed(1)}%
                              </span>
                            </td>
                            <td className="p-4 text-sm font-mono text-muted-foreground">{cand.candidate_yoe}</td>
                            <td className="p-4">
                              <div className="flex items-center gap-2 text-xs">
                                <span className="text-accent bg-accent/10 px-3 py-1 rounded-full border border-accent/20" title={cand.contextual_skills?.join(", ")}>
                                  {cand.contextual_skills?.length || 0} Found
                                </span>
                                <span className="text-red-400 bg-red-500/10 px-3 py-1 rounded-full border border-red-500/20" title={cand.missing_skills?.join(", ")}>
                                  {cand.missing_skills?.length || 0} Missing
                                </span>
                              </div>
                            </td>
                            <td className="p-4 pr-6 text-right flex justify-end">
                              <GlassIcons
                                colorful={true}
                                items={[
                                  {
                                    icon: <User size={18} strokeWidth={2.5} />,
                                    color: 'indigo',
                                    label: 'View Profile',
                                    onClick: () => setSelectedCandidate(cand)
                                  }
                                ]}
                              />
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                <div className="mt-4">
                  <h3 className="text-xl font-bold mb-6 text-foreground flex items-center gap-3">
                    <span className="w-2 h-8 bg-accent rounded-full"></span>
                    Visual Candidate Gallery
                  </h3>
                  <CircularGallery
                    items={candidates}
                    onItemClick={(item) => {
                      setSelectedCandidate(item);
                      setShowCV(true);
                    }}
                  />
                </div>
              </motion.div>
            ) : (
              <div className="flex items-center justify-center h-[300px] w-full border border-dashed border-border rounded-2xl bg-black/20 text-muted-foreground">
                No candidates processed yet. Upload JD and CVs, then run analysis.
              </div>
            )}
          </div>
        </div>

        {/* Modals */}
        {selectedCandidate && !showCV && (
          <GamerProfileModal
            candidate={selectedCandidate}
            onClose={() => {
              setSelectedCandidate(null);
              setShowCV(false);
            }}
            rank={candidates.indexOf(selectedCandidate) + 1}
          />
        )}

        {/* Real CV Document Preview */}
        {selectedCandidate && showCV && (
          <CVPreviewModal
            candidate={selectedCandidate}
            fileUrl={fileUrls[selectedCandidate.file_name]}
            onClose={() => {
              setSelectedCandidate(null);
              setShowCV(false);
            }}
          />
        )}
      </div>
    </main>
  );
}
