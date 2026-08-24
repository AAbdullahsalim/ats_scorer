"use client";

import React, { useState } from "react";
import { X, FileText, Download, Copy, Check, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import BorderGlow from "@/components/BorderGlow";
import SpecularButton from "@/components/SpecularButton";
import { cn } from "@/lib/utils";

interface CVPreviewModalProps {
  candidate: any;
  fileUrl?: string;
  onClose: () => void;
}

export default function CVPreviewModal({
  candidate,
  fileUrl,
  onClose,
}: CVPreviewModalProps) {
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState<"document" | "raw">("document");

  if (!candidate) return null;

  const fileName = candidate.file_name || "";
  const isPdf = fileName.toLowerCase().endsWith(".pdf");
  const isDocx =
    fileName.toLowerCase().endsWith(".docx") || fileName.toLowerCase().endsWith(".doc");

  const handleCopyText = () => {
    if (candidate.full_text) {
      navigator.clipboard.writeText(candidate.full_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/85 backdrop-blur-md p-3 md:p-6">
      <div className="relative z-10 w-full max-w-6xl h-[92vh] flex flex-col">
        <BorderGlow
          glowColor="94 141 119"
          backgroundColor="#0d1415"
          className="w-full h-full flex flex-col"
          contentClassName="flex flex-col h-full"
        >
          {/* Header Bar */}
          <div className="flex flex-wrap justify-between items-center px-6 py-4 border-b border-white/10 bg-background/80 backdrop-blur-md gap-4">
            {/* Candidate Title & File Tag */}
            <div className="flex items-center gap-3.5">
              <div className="p-2.5 bg-accent/15 border border-accent/30 rounded-2xl text-accent shadow-[0_0_15px_rgba(94,141,119,0.2)]">
                <FileText size={20} />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2 tracking-tight">
                  {candidate.candidate_name}'s Original CV
                </h2>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-xs text-muted-foreground font-mono truncate max-w-[260px]">
                    {fileName || "Document Preview"}
                  </span>
                  <span className="text-[10px] px-2.5 py-0.5 rounded-full uppercase font-bold tracking-wider bg-white/5 border border-white/10 text-accent">
                    {isPdf ? "PDF Document" : isDocx ? "Word DOCX" : "Extracted"}
                  </span>
                </div>
              </div>
            </div>

            {/* Dynamic Actions Bar (React Bits Powered) */}
            <div className="flex items-center gap-3 flex-wrap">
              {/* React Bits Sliding Pill Tab Toggle with Grain Texture */}
              <div className="relative overflow-hidden flex items-center bg-black/60 border border-white/10 rounded-full p-1 shadow-[inset_0_2px_8px_rgba(0,0,0,0.6)]">
                <div 
                  className="absolute inset-0 pointer-events-none opacity-25 mix-blend-overlay"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
                    backgroundRepeat: "repeat",
                  }}
                />
                <button
                  onClick={() => setViewMode("document")}
                  className={cn(
                    "relative px-4 py-2 rounded-full text-xs font-semibold transition-colors duration-200 z-10",
                    viewMode === "document" ? "text-white" : "text-muted-foreground hover:text-white"
                  )}
                >
                  {viewMode === "document" && (
                    <motion.div
                      layoutId="active-cv-tab"
                      className="absolute inset-0 bg-accent rounded-full shadow-[0_0_12px_rgba(94,141,119,0.6)] -z-10"
                      transition={{ type: "spring", stiffness: 450, damping: 30 }}
                    />
                  )}
                  Document View
                </button>

                <button
                  onClick={() => setViewMode("raw")}
                  className={cn(
                    "relative px-4 py-2 rounded-full text-xs font-semibold transition-colors duration-200 z-10",
                    viewMode === "raw" ? "text-white" : "text-muted-foreground hover:text-white"
                  )}
                >
                  {viewMode === "raw" && (
                    <motion.div
                      layoutId="active-cv-tab"
                      className="absolute inset-0 bg-accent rounded-full shadow-[0_0_12px_rgba(94,141,119,0.6)] -z-10"
                      transition={{ type: "spring", stiffness: 450, damping: 30 }}
                    />
                  )}
                  Parsed Text
                </button>
              </div>

              {/* Copy Extracted Text Specular Button */}
              <SpecularButton
                size="sm"
                onClick={handleCopyText}
                baseColor="#0a0f10"
                lineColor="#5e8d77"
                textColor="#d1d5db"
                className="!py-2.5 !px-4 !rounded-full text-xs font-semibold transition-all"
                title="Copy full CV text"
              >
                {copied ? <Check size={14} className="text-accent" /> : <Copy size={14} />}
                {copied ? "Copied!" : "Copy Text"}
              </SpecularButton>

              {/* Download File Specular Button */}
              {fileUrl && (
                <a
                  href={fileUrl}
                  download={fileName || "CV_Document"}
                  className="inline-block"
                  title="Download File"
                >
                  <SpecularButton
                    size="sm"
                    baseColor="#0a0f10"
                    lineColor="#5e8d77"
                    textColor="#d1d5db"
                    className="!py-2.5 !px-4 !rounded-full text-xs font-semibold transition-all"
                  >
                    <Download size={14} />
                    Download
                  </SpecularButton>
                </a>
              )}

              {/* Refined-Height Matching Close Button */}
              <button
                onClick={onClose}
                className="relative overflow-hidden w-[34px] h-[34px] flex items-center justify-center bg-white/5 hover:bg-red-500/20 hover:text-red-400 rounded-full text-gray-300 hover:border-red-500/40 border border-white/10 transition-all active:scale-95 shadow-sm"
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
            </div>
          </div>

          {/* Main Viewer Body (Full Height) */}
          <div className="flex-1 w-full h-full min-h-0 bg-background overflow-hidden relative">
            {viewMode === "document" && isPdf && fileUrl ? (
              /* Full-height PDF viewer */
              <div className="w-full h-full bg-[#525659]">
                <iframe
                  src={`${fileUrl}#view=FitH&toolbar=1&navpanes=0`}
                  className="w-full h-full border-none block"
                  title="PDF Preview"
                />
              </div>
            ) : viewMode === "document" && isDocx ? (
              /* Formatted In-App Document Paper for Word .docx files */
              <div className="w-full h-full overflow-y-auto p-4 md:p-8 bg-black/60 flex justify-center items-start">
                <div className="w-full max-w-4xl bg-[#0f1719] text-gray-100 rounded-2xl shadow-2xl p-8 md:p-12 border border-white/10 my-4 flex flex-col gap-6 font-sans">
                  <div className="border-b border-white/10 pb-6 mb-2">
                    <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
                      {candidate.candidate_name || "Candidate Resume"}
                      <span className="text-xs px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono">
                        DOCX Preview
                      </span>
                    </h1>
                    <p className="text-sm font-semibold text-accent uppercase tracking-wider mt-1.5">
                      {candidate.current_role || "Professional Candidate"}
                    </p>
                    {candidate.contact && (
                      <div className="flex flex-wrap gap-4 text-xs font-mono text-gray-400 mt-3 bg-black/40 p-3 rounded-xl border border-white/5">
                        {candidate.contact.email && <span>✉ {candidate.contact.email}</span>}
                        {candidate.contact.phone && <span>☎ {candidate.contact.phone}</span>}
                        {candidate.contact.location && <span>📍 {candidate.contact.location}</span>}
                      </div>
                    )}
                  </div>

                  <div className="text-sm text-gray-300 font-mono whitespace-pre-wrap leading-relaxed select-text space-y-4">
                    {candidate.full_text || "No extracted text available for this Word document."}
                  </div>
                </div>
              </div>
            ) : (
              /* Extracted Clean Text View */
              <div className="w-full h-full overflow-y-auto p-6 md:p-10 bg-black/60 text-gray-200 font-mono text-sm leading-relaxed whitespace-pre-wrap select-text">
                {candidate.full_text || "No text could be extracted from this document."}
              </div>
            )}
          </div>
        </BorderGlow>
      </div>
    </div>
  );
}
