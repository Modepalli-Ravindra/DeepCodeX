import { AnalysisResult } from "../types";

export const analyzeCode = async (code: string): Promise<AnalysisResult> => {
  const token = localStorage.getItem('auth_token');

  const res = await fetch("http://127.0.0.1:5000/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ code }),
  });

  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(`Analysis failed: ${res.status} ${res.statusText} - ${errorBody}`);
  }

  return res.json();
};

export const getHistory = async () => {
  const token = localStorage.getItem('auth_token');

  const res = await fetch("http://127.0.0.1:5000/history", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error("Failed to fetch history");
  }

  return res.json();
};
