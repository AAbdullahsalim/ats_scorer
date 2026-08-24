const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export async function analyzeCandidates(
  jdFile: File,
  cvFiles: File[],
  targetYoe: number = 0,
  mustHaveSkills: string = "",
  niceToHaveSkills: string = "",
  signal?: AbortSignal
) {
  const formData = new FormData();
  formData.append("jd_file", jdFile);
  
  cvFiles.forEach(file => {
    formData.append("cv_files", file);
  });
  
  formData.append("target_yoe", targetYoe.toString());
  if (mustHaveSkills) formData.append("must_have_skills", mustHaveSkills);
  if (niceToHaveSkills) formData.append("nice_to_have_skills", niceToHaveSkills);

  const response = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    body: formData,
    signal,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}

export async function parseJd(jdFile: File) {
  const formData = new FormData();
  formData.append("file", jdFile);

  const response = await fetch(`${API_URL}/parse-jd`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}

export async function exportReport(candidates: any[]) {
  const response = await fetch(`${API_URL}/export-json`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(candidates),
  });

  if (!response.ok) {
    throw new Error(`Export failed: ${response.statusText}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `ats_recruitment_report_${new Date().toISOString().slice(0, 10)}.xlsx`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  a.remove();
}
