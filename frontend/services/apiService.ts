import { AnalysisResult } from "../types";

export const analyzeCode = async (code: string): Promise<AnalysisResult> => {
  const res = await fetch("http://localhost:5000/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });

  if (!res.ok) {
    throw new Error("Analysis failed");
  }

  return res.json();
};
