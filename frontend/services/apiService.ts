import { AnalysisResult } from "../types";
import { supabase } from "../supabaseClient"; // 🔐 ADDED

export const analyzeCode = async (code: string): Promise<AnalysisResult> => {
  // 🔐 ADDED: get current session
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    throw new Error("User not logged in");
  }

  const res = await fetch("http://192.168.43.60:5000/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session.access_token}`, // 🔐 ADDED
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
  // 🔐 ADDED: get current session
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    throw new Error("User not logged in");
  }

  const res = await fetch("http://192.168.43.60:5000/history", {
    headers: {
      Authorization: `Bearer ${session.access_token}`, // 🔐 ADDED
    },
  });

  if (!res.ok) {
    throw new Error("Failed to fetch history");
  }

  return res.json();
};
