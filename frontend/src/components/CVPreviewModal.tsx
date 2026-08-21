"use client";

import { X, FileText } from "lucide-react";
import BorderGlow from "@/components/BorderGlow";

interface CVPreviewModalProps {
  candidate: any;
  fileUrl?: string;
  onClose: () => void;
}

export default function CVPreviewModal({ candidate, fileUrl, onClose }: CVPreviewModalProps) {
  if (!candidate) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 md:p-8">
      <div className="relative z-10 w-full max-w-5xl h-[90vh] flex flex-col">
        <BorderGlow glowColor="79 70 229" backgroundColor="#0D1117" className="w-full h-full flex flex-col">
          <div className="flex justify-between items-center p-6 border-b border-white/10 bg-[#161B22]">
            <h2 className="text-xl font-semibold text-white flex items-center gap-3">
              <FileText className="text-indigo-400" />
              {candidate.candidate_name}'s Original CV
            </h2>
            <button 
              onClick={onClose}
              className="p-2 bg-white/5 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-colors"
            >
              <X size={20} />
            </button>
          </div>
          
          <div className="flex-1 bg-[#0D1117] overflow-hidden">
            {fileUrl ? (
              <iframe src={fileUrl} className="w-full h-full border-none" title="CV Preview" />
            ) : (
              <div className="w-full h-full overflow-y-auto p-8 text-gray-300 font-mono text-sm leading-relaxed whitespace-pre-wrap">
                {candidate.full_text || "No CV text extracted."}
              </div>
            )}
          </div>
        </BorderGlow>
      </div>
    </div>
  );
}
