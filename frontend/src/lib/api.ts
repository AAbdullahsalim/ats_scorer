const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";

export async function analyzeCandidates(
  jdFile: File,
  cvFiles: File[],
  targetYoe: number = 0
) {
  const formData = new FormData();
  formData.append("jd_file", jdFile);
  
  cvFiles.forEach(file => {
    formData.append("cv_files", file);
  });
  
  formData.append("target_yoe", targetYoe.toString());

  const response = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}
