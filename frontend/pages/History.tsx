import React, { useEffect, useState } from "react";
import { AnalysisResult } from "../types";
import { Clock, Search, FileCode } from "lucide-react";
import { getHistory } from "../services/apiService"; // ✅ ADD

export const History: React.FC = () => {
  const [history, setHistory] = useState<AnalysisResult[]>([]);
  const [searchTerm, setSearchTerm] = useState("");

  // ✅ FIX: Load history from backend (Supabase), NOT localStorage
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await getHistory();

        const adapted: AnalysisResult[] = data.map((item: any) => ({
          id: item.id,
          fileName: "Code Analysis",
          timestamp: item.created_at,

          language: item.language,
          timeComplexity: item.time_complexity,
          spaceComplexity: item.space_complexity,

          complexityLevel:
            item.cyclomatic > 15
              ? "High"
              : item.cyclomatic > 7
              ? "Medium"
              : "Low",

          score: item.optimization_score ?? 0,

          metrics: {
            linesOfCode: item.lines ?? 0,
            functionCount: item.functions ?? 0,
            loopCount: item.loops ?? 0,
            conditionalCount: item.conditions ?? 0,
            cyclomaticComplexity: item.cyclomatic ?? 0,
          },

          suggestions: item.ai_suggestions
            ? item.ai_suggestions.split("\n")
            : [],
        }));

        setHistory(adapted);
      } catch (e) {
        console.error("Failed to fetch history", e);
      }
    };

    fetchHistory();
  }, []);

  const filteredHistory = history.filter(
    (item) =>
      item.fileName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.language.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto p-8 space-y-8 animate-fade-in pb-20">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-6 pt-4">
        <div>
          <h2 className="text-textSecondary text-sm font-medium tracking-wide uppercase mb-2">Recent</h2>
          <h1 className="text-3xl font-semibold text-textPrimary tracking-tight">Analysis History</h1>
          <p className="text-textMuted mt-2 max-w-md">Review your past code inspections and complexity trends.</p>
        </div>
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-textMuted w-4 h-4" />
          <input
            type="text"
            placeholder="Search analyses..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-secondaryBg border border-borderSubtle rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary/50 focus:border-primary/50 text-textPrimary placeholder:text-textMuted transition-all shadow-sm"
          />
        </div>
      </div>

      <div className="bg-surface rounded-xl border border-borderSubtle overflow-hidden">
        {filteredHistory.length === 0 ? (
          <div className="p-16 text-center text-textMuted flex flex-col items-center">
            <div className="w-16 h-16 rounded-full bg-secondaryBg flex items-center justify-center mb-4 border border-borderSubtle">
              <Clock className="w-8 h-8 opacity-50" />
            </div>
            <h3 className="text-lg font-medium text-textPrimary mb-2">No analyses yet</h3>
            <p className="max-w-xs">Run your first code analysis to start building your history.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-borderSubtle bg-surfaceElevated">
                  <th className="p-4 text-xs font-medium text-textSecondary uppercase tracking-wider">
                    File / Date
                  </th>
                  <th className="p-4 text-xs font-medium text-textSecondary uppercase tracking-wider">
                    Complexity
                  </th>
                  <th className="p-4 text-xs font-medium text-textSecondary uppercase tracking-wider">
                    Score
                  </th>
                  <th className="p-4 text-xs font-medium text-textSecondary uppercase tracking-wider">
                    Language
                  </th>
                  <th className="p-4 text-xs font-medium text-textSecondary uppercase tracking-wider">
                    Metrics
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-borderSubtle">
                {filteredHistory.map((item) => (
                  <tr
                    key={item.id}
                    className="hover:bg-surfaceElevated/50 transition-colors group cursor-pointer"
                  >
                    <td className="p-4">
                      <div className="flex items-center">
                        <div className="bg-secondaryBg border border-borderSubtle p-2.5 rounded-lg mr-3 group-hover:bg-surfaceElevated group-hover:border-primary/20 transition-colors">
                          <FileCode className="w-4 h-4 text-primary" />
                        </div>
                        <div>
                          <div className="font-medium text-textPrimary text-sm">
                            {item.fileName}
                          </div>
                          <div className="text-xs text-textMuted mt-0.5">
                            {new Date(item.timestamp).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                    </td>

                    <td className="p-4">
                      <span
                        className={`px-2.5 py-1 rounded-md text-xs font-medium border
                        ${
                          item.complexityLevel === "High"
                            ? "bg-danger/10 text-danger border-danger/20"
                            : item.complexityLevel === "Medium"
                            ? "bg-warning/10 text-warning border-warning/20"
                            : "bg-success/10 text-success border-success/20"
                        }`}
                      >
                        {item.complexityLevel}
                      </span>
                    </td>

                    <td className="p-4">
                      <span className="font-mono text-textPrimary font-medium text-sm">
                        {item.score}<span className="text-textMuted">/100</span>
                      </span>
                    </td>

                    <td className="p-4 text-textSecondary capitalize text-sm">
                      {item.language}
                    </td>

                    <td className="p-4 text-xs text-textSecondary">
                      <div className="flex items-center gap-2">
                        <span className="bg-secondaryBg px-2 py-1 rounded border border-borderSubtle font-mono text-[11px] group-hover:border-primary/20 transition-colors">
                          {item.timeComplexity}
                        </span>
                        <span className="bg-secondaryBg px-2 py-1 rounded border border-borderSubtle font-mono text-[11px] group-hover:border-primary/20 transition-colors">
                          {item.metrics.linesOfCode} LOC
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
