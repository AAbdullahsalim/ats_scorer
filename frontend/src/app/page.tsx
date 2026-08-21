"use client";

import React, { useState, useRef } from "react";
import { Upload, FileText, ChevronRight, Download, Menu, X, Search, LayoutGrid, List } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { analyzeCandidates } from "@/lib/api";

import SpecularButton from "@/components/SpecularButton";
import GamerProfileModal from "@/components/GamerProfileModal";
import CircularGallery from "@/components/CircularGallery";
import CVPreviewModal from "@/components/CVPreviewModal";
import ProgressBar from "@/components/ProgressBar";

export default function Home() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [cvFiles, setCvFiles] = useState<File[]>([]);
  
  // Cumulative state
  const [jdAnalysis, setJdAnalysis] = useState<any>(null);
  const [candidates, setCandidates] = useState<any[]>([]);
  
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const [previewCandidate, setPreviewCandidate] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [newSkill, setNewSkill] = useState("");

  const jdInputRef = useRef<HTMLInputElement>(null);
  const cvInputRef = useRef<HTMLInputElement>(null);

  const handleProcess = async () => {
    if (!jdFile || cvFiles.length === 0) return;
    
    setIsProcessing(true);
    
    try {
      const data = await analyzeCandidates(jdFile, cvFiles, 1.0);
      
      if (data.jd_analysis && !jdAnalysis) {
        setJdAnalysis(data.jd_analysis);
      }

      // Append new candidates and resort
      setCandidates(prev => {
        const combined = [...prev, ...data.candidates];
        return combined.sort((a, b) => b.final_score_pct - a.final_score_pct);
      });
      
      // Clear current CV batch so they can upload more
      setCvFiles([]);
      if (window.innerWidth < 768) setIsSidebarOpen(false); // auto close sidebar on mobile
      
    } catch (err) {
      console.error(err);
      alert("Failed to analyze candidates.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExportCSV = async () => {
    if (candidates.length === 0) return;
    
    try {
      const response = await fetch("http://localhost:8001/export-json", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(candidates),
      });

      if (!response.ok) throw new Error("Export failed");

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "ats_candidates_report.xlsx";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Failed to export Excel report. Is your backend running on 8001?");
    }
  };

  const removeSkill = (skill: string) => {
    if (!jdAnalysis) return;
    setJdAnalysis({
      ...jdAnalysis,
      must_have_skills: jdAnalysis.must_have_skills.filter((s: string) => s !== skill)
    });
  };

  const addSkill = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && newSkill.trim() !== '' && jdAnalysis) {
      if (!jdAnalysis.must_have_skills.includes(newSkill.trim())) {
        setJdAnalysis({
          ...jdAnalysis,
          must_have_skills: [...(jdAnalysis.must_have_skills || []), newSkill.trim()]
        });
      }
      setNewSkill("");
    }
  };

  return (
    <div className="flex h-screen w-full bg-[#0D1117] text-gray-300 font-sans overflow-hidden">
      
      {/* ========================================== */}
      {/* SIDEBAR: BATCH UPLOADS */}
      {/* ========================================== */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div 
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 320, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="h-full bg-[#161B22] border-r border-white/5 flex flex-col shrink-0 relative"
          >
            <div className="p-6 border-b border-white/5 flex justify-between items-center">
              <h2 className="font-bold text-lg m-0">Batch Pipeline</h2>
              <button onClick={() => setIsSidebarOpen(false)} className="text-gray-400 hover:text-white">
                <X size={20} />
              </button>
            </div>

            <div className="p-6 flex flex-col gap-6 overflow-y-auto flex-1">
              {/* JD Upload */}
              <div>
                <h3 className="text-sm text-gray-400 mb-3 font-medium uppercase tracking-wider">Job Description</h3>
                <div 
                  onClick={() => jdInputRef.current?.click()}
                  className={`w-full p-4 border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-colors ${jdFile ? 'border-indigo-500 bg-indigo-500/10' : 'border-gray-700 hover:border-gray-500 bg-black/20'}`}
                >
                  <FileText className={jdFile ? "text-indigo-400 mb-2" : "text-gray-500 mb-2"} size={24} />
                  <span className="text-sm font-medium text-center break-all">
                    {jdFile ? jdFile.name : "Upload JD (PDF/TXT)"}
                  </span>
                </div>
                <input type="file" ref={jdInputRef} className="hidden" accept=".pdf,.docx,.txt" onChange={(e) => setJdFile(e.target.files?.[0] || null)} />
              </div>

              {/* CV Upload */}
              <div>
                <h3 className="text-sm text-gray-400 mb-3 font-medium uppercase tracking-wider">Candidate CVs</h3>
                <div 
                  onClick={() => cvInputRef.current?.click()}
                  className={`w-full p-4 border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-colors ${cvFiles.length > 0 ? 'border-green-500 bg-green-500/10' : 'border-gray-700 hover:border-gray-500 bg-black/20'}`}
                >
                  <Upload className={cvFiles.length > 0 ? "text-green-400 mb-2" : "text-gray-500 mb-2"} size={24} />
                  <span className="text-sm font-medium text-center">
                    {cvFiles.length > 0 ? `${cvFiles.length} CVs added to batch` : "Upload CVs (PDF/DOCX)"}
                  </span>
                </div>
                <input type="file" ref={cvInputRef} className="hidden" multiple accept=".pdf,.docx" onChange={(e) => setCvFiles(e.target.files ? Array.from(e.target.files) : [])} />
              </div>
            </div>

            <div className="p-6 border-t border-white/5 flex flex-col gap-3">
              {isProcessing && <ProgressBar className="mt-0" />}
              <SpecularButton 
                onClick={handleProcess} 
                disabled={!jdFile || cvFiles.length === 0 || isProcessing}
                className="w-full justify-center"
                baseColor="#4f46e5"
              >
                {isProcessing ? "Processing..." : "Process Batch"} <ChevronRight size={16} className="ml-1" />
              </SpecularButton>
            </div>
          </motion.div>
        )}
      </AnimatePresence>


      {/* ========================================== */}
      {/* MAIN DASHBOARD */}
      {/* ========================================== */}
      <div className="flex-1 h-full overflow-y-auto flex flex-col relative">
        {/* Header bar */}
        <div className="sticky top-0 z-20 bg-[#0F1115]/80 backdrop-blur-md p-6 border-b border-white/5 flex items-center gap-4">
          {!isSidebarOpen && (
            <button onClick={() => setIsSidebarOpen(true)} className="p-2 bg-white/5 hover:bg-white/10 rounded-md">
              <Menu size={20} />
            </button>
          )}
          <div>
            <h1 className="text-2xl font-bold m-0 tracking-tight">AI-Powered ATS Resume Matcher & Scorer</h1>
            <p className="text-sm text-gray-400 m-0">Upload a Job Description to auto-extract requirements, then score candidates using AI.</p>
          </div>
        </div>

        <div className="p-8 max-w-7xl mx-auto w-full flex flex-col gap-10 pb-32">
          
          {/* JD Requirements */}
          {jdAnalysis && (
            <div className="flex flex-col gap-4">
              <div>
                <h2 className="text-xl font-bold text-white">Auto-Extracted Job Requirements</h2>
                <p className="text-sm text-gray-500">Review and modify requirements before processing the next batch.</p>
              </div>
              
              <div className="bg-[#161B22] border border-white/5 rounded-xl p-6">
                <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center mb-4">
                  <p className="text-sm text-gray-400 font-medium">Must-Have Skills:</p>
                  <input 
                    type="text" 
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    onKeyDown={addSkill}
                    placeholder="Type skill & press Enter..."
                    className="bg-[#0D1117] border border-white/10 rounded-md py-1.5 px-3 text-sm focus:border-indigo-500 outline-none w-full md:w-64"
                  />
                </div>
                
                <div className="flex flex-wrap gap-2">
                  {jdAnalysis.must_have_skills?.map((skill: string) => (
                    <span key={skill} className="flex items-center gap-1.5 bg-red-950/40 text-red-400 border border-red-900/50 px-2.5 py-1 rounded text-xs font-medium">
                      {skill} <X size={12} className="opacity-60 hover:opacity-100 cursor-pointer" onClick={() => removeSkill(skill)} />
                    </span>
                  ))}
                  {(!jdAnalysis.must_have_skills || jdAnalysis.must_have_skills.length === 0) && <span className="text-gray-500 text-sm">None</span>}
                </div>
              </div>
            </div>
          )}

          {/* Candidates View */}
          <div className="flex flex-col gap-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <h2 className="text-xl font-bold text-white">Candidate Ranking Results</h2>
              
              {/* Search Controls */}
              {candidates.length > 0 && (
                <div className="flex items-center gap-4 w-full md:w-auto">
                  <div className="relative flex-1 md:w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
                    <input 
                      type="text" 
                      placeholder="Search by name..." 
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full bg-[#161B22] border border-white/5 rounded-lg py-2 pl-9 pr-4 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
                    />
                  </div>
                </div>
              )}
            </div>
            
            {/* VIEW MODE RENDERER */}
            {(() => {
              const filtered = candidates.filter(c => c.candidate_name?.toLowerCase().includes(searchQuery.toLowerCase()));
              
              if (candidates.length === 0) {
                return (
                  <div className="bg-[#161B22] border border-white/5 rounded-xl p-16 text-center text-gray-500 shadow-xl">
                    {isProcessing ? "Processing batch..." : "No candidates processed yet. Open the sidebar to upload a batch."}
                  </div>
                );
              }

              if (filtered.length === 0) {
                return <div className="text-gray-500 p-8 text-center bg-[#161B22] rounded-xl border border-white/5">No candidates match your search.</div>;
              }

              return (
                <div className="flex flex-col gap-10">
                  {/* TABLE VIEW */}
                  <div className="bg-[#161B22] border border-white/5 rounded-xl overflow-hidden shadow-xl">
                    <table className="w-full text-left text-sm">
                      <thead className="bg-[#0D1117] text-gray-400 border-b border-white/5">
                        <tr>
                          <th className="py-4 px-6 font-medium">Rank</th>
                          <th className="py-4 px-6 font-medium">Candidate File</th>
                          <th className="py-4 px-6 font-medium text-right">Final Match %</th>
                          <th className="py-4 px-6 font-medium text-right">Est. YOE</th>
                          <th className="py-4 px-6 font-medium">Skills Validated</th>
                          <th className="py-4 px-6 font-medium">Missing Skills</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5">
                        {filtered.map((cand, idx) => (
                          <tr 
                            key={idx} 
                            onClick={() => setSelectedCandidate(cand)}
                            className="hover:bg-white/[0.02] cursor-pointer transition-colors group"
                          >
                            <td className="py-4 px-6 font-mono text-gray-500 group-hover:text-white transition-colors">
                              {candidates.indexOf(cand) + 1}
                            </td>
                            <td className="py-4 px-6 font-medium text-gray-200">{cand.candidate_name || "Unknown Candidate"}</td>
                            <td className="py-4 px-6 text-right font-mono font-bold text-emerald-400">{cand.final_score_pct?.toFixed(2)}</td>
                            <td className="py-4 px-6 text-right font-mono text-gray-300">{cand.candidate_yoe} yrs</td>
                            <td className="py-4 px-6 text-gray-400 text-xs">
                              {cand.contextual_skills?.length} Verified, {cand.stuffed_skills?.length} Stuffed
                            </td>
                            <td className="py-4 px-6 text-gray-400 text-xs">
                              <span className="truncate block max-w-[200px]">
                                {cand.missing_skills?.length > 0 
                                  ? `${cand.missing_skills[0]}${cand.missing_skills.length > 1 ? `, (+${cand.missing_skills.length - 1} more)` : ''}`
                                  : "None"}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* GALLERY VIEW BELOW TABLE */}
                  <div className="flex flex-col gap-4">
                    <h3 className="text-lg font-bold text-white">Visual CV Preview Gallery</h3>
                    <p className="text-xs text-gray-500 -mt-2 mb-2">Click a card below to read the original extracted text from their CV.</p>
                    <CircularGallery items={filtered} onItemClick={(item) => setPreviewCandidate(item)} />
                  </div>
                </div>
              );
            })()}

            {candidates.length > 0 && (
              <div className="mt-4">
                <SpecularButton 
                  baseColor="#ef4444" 
                  textColor="#ffffff"
                  onClick={handleExportCSV}
                >
                  <Download size={16} className="mr-2" />
                  Download Styled Excel Recruiter Report (.xlsx)
                </SpecularButton>
              </div>
            )}
          </div>

        </div>
      </div>

      {/* ========================================== */}
      {/* MODAL: GAMER PROFILE DOSSIER */}
      {/* ========================================== */}
      {selectedCandidate && (
        <GamerProfileModal 
          candidate={selectedCandidate} 
          onClose={() => setSelectedCandidate(null)} 
          rank={candidates.indexOf(selectedCandidate) + 1}
        />
      )}

      {/* ========================================== */}
      {/* MODAL: CV PREVIEW */}
      {/* ========================================== */}
      {previewCandidate && (() => {
        const fileObj = cvFiles.find(f => f.name === previewCandidate.file_name);
        const fileUrl = fileObj ? URL.createObjectURL(fileObj) : undefined;
        return (
          <CVPreviewModal 
            candidate={previewCandidate} 
            fileUrl={fileUrl}
            onClose={() => setPreviewCandidate(null)} 
          />
        );
      })()}

    </div>
  );
}
