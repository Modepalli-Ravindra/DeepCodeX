// frontend/pages/CodeAnalysis.tsx

import React, { useState, useRef, useEffect, useCallback } from "react";
import Editor from "@monaco-editor/react";
import { Upload, Play, Zap, Code2, FileCode } from "lucide-react";
import { analyzeCode } from "../services/apiService";
import { AnalysisResult } from "../types";
import { Loader } from "../components/ui/Loader";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

/* ---------- ENHANCED LANGUAGE DETECTION ---------- */
interface LanguageInfo {
  name: string;
  monacoId: string;
  icon: string;
  color: string;
}

const LANGUAGE_PATTERNS: { pattern: RegExp; lang: LanguageInfo }[] = [
  // === HIGH PRIORITY: Languages with very specific markers (check first) ===

  // Java - Check BEFORE Python because System.out.print contains "print("
  {
    pattern: /public\s+(class|static|void)|private\s+(class|static|void)|System\.out\.print|class\s+\w+\s*(extends|implements)?\s*\{|void\s+main\s*\(\s*String/,
    lang: { name: "Java", monacoId: "java", icon: "☕", color: "#B07219" }
  },
  // C++ - Check before C (more specific markers)
  {
    pattern: /#include\s*<(iostream|vector|string|algorithm|map|set|queue|stack)>|std::|cout\s*<<|cin\s*>>|using\s+namespace\s+std|nullptr|::\w+\(|template\s*</,
    lang: { name: "C++", monacoId: "cpp", icon: "⚡", color: "#F34B7D" }
  },
  // C - Check after C++ 
  {
    pattern: /#include\s*<(stdio|stdlib|string|math|ctype|time)\.h>|printf\s*\(|scanf\s*\(|int\s+main\s*\(\s*(void)?\s*\)|malloc\s*\(|free\s*\(/,
    lang: { name: "C", monacoId: "c", icon: "🔧", color: "#555555" }
  },
  // TypeScript - Check before JavaScript (has type annotations)
  {
    pattern: /:\s*(string|number|boolean|void|any|never)\s*[;,\)=\{]|interface\s+\w+\s*\{|type\s+\w+\s*=|<\w+>\s*\(|React\.(FC|Component)|:\s*\w+\[\]/,
    lang: { name: "TypeScript", monacoId: "typescript", icon: "📘", color: "#3178C6" }
  },
  // Go
  {
    pattern: /^package\s+\w+|func\s+\w+\s*\([^)]*\)\s*\{|func\s+\(\w+\s+\*?\w+\)|fmt\.(Print|Scan)|:=\s*|import\s+\(/m,
    lang: { name: "Go", monacoId: "go", icon: "🐹", color: "#00ADD8" }
  },
  // Rust
  {
    pattern: /fn\s+\w+\s*\([^)]*\)\s*(->\s*\w+)?\s*\{|let\s+mut\s+|println!\s*\(|impl\s+\w+|pub\s+fn|use\s+std::|match\s+\w+\s*\{/,
    lang: { name: "Rust", monacoId: "rust", icon: "🦀", color: "#DEA584" }
  },

  // === MEDIUM PRIORITY: Common languages ===

  // Python - More specific pattern to avoid matching other languages
  {
    pattern: /^\s*def\s+\w+\s*\(|^\s*class\s+\w+\s*:|^\s*import\s+\w+|^\s*from\s+\w+\s+import|(?<![.\w])print\s*\(|if\s+__name__\s*==\s*["']__main__["']|^\s*elif\s+|:\s*$/m,
    lang: { name: "Python", monacoId: "python", icon: "🐍", color: "#3572A5" }
  },
  // JavaScript
  {
    pattern: /\bfunction\s+\w+\s*\(|\bconst\s+\w+\s*=|\blet\s+\w+\s*=|console\.(log|error|warn)\s*\(|=>\s*[\{\(]|module\.exports|require\s*\(['"]|document\.|window\./,
    lang: { name: "JavaScript", monacoId: "javascript", icon: "📜", color: "#F7DF1E" }
  },
  // Ruby
  {
    pattern: /^\s*def\s+\w+|^\s*end\s*$|puts\s+|require\s+['"]|class\s+\w+\s*<|attr_(accessor|reader|writer)|\.each\s+do/m,
    lang: { name: "Ruby", monacoId: "ruby", icon: "💎", color: "#CC342D" }
  },
  // PHP
  {
    pattern: /<\?php|\$\w+\s*=|echo\s+['"\$]|function\s+\w+\s*\(.*\)\s*\{|\$this->|namespace\s+\w+;/,
    lang: { name: "PHP", monacoId: "php", icon: "🐘", color: "#4F5D95" }
  },
];

const isPlainText = (code: string): boolean => {
  // Check if the content is prose/natural language rather than code
  const lines = code.trim().split('\n').filter(l => l.trim());

  if (lines.length < 2) {
    // Very short - check for obvious code patterns
    const text = code.trim();
    if (/^(def|function|class|public|private)\s+\w+/.test(text)) return false;
    if (/[{};]\s*$/.test(text)) return false;
    return true;
  }

  let proseLines = 0;
  let codeLines = 0;

  for (const line of lines) {
    const trimmed = line.trim();

    // Prose indicators
    const isProse =
      // Sentence-like (starts capital, ends punctuation)
      /^[A-Z][a-zA-Z\s,'"]+[.!?]$/.test(trimmed) ||
      // Common prose phrases (but not on lines with code structure)
      (!/[=\[\]{}();]/.test(trimmed) && /\b(your|you're|what's|here's|that's|it's|how to|this is|problem|issue)\b/i.test(trimmed)) ||
      // Bullet points or emojis
      /^[•\-\*✅❌]\s+/.test(trimmed) ||
      // ALLCAPS headers
      /^[A-Z][A-Z\s]+$/.test(trimmed) ||
      // Short word-only lines (not code keywords)
      (trimmed.length < 30 && /^[a-zA-Z\s]+$/.test(trimmed) && !/^(if|for|while|def|class|return|import|from)\s/.test(trimmed));

    // Code indicators
    const isCode =
      /^\s*(def|function|class|public|private|void|int|bool)\s+\w+/.test(trimmed) ||
      /^\s*(if|for|while|elif|else|switch|match|try|catch|finally|with|func|fn)\b/.test(trimmed) ||
      /^\s*(import|from\s+\w+\s+import|#include|require|use|package)\s/.test(trimmed) ||
      /[{};:]\s*$/.test(trimmed) ||
      (/=/.test(trimmed) && /[a-z_]\w*\s*(=|\+=|-=)/i.test(trimmed));

    if (isProse && !isCode) proseLines++;
    else if (isCode && !isProse) codeLines++;
  }

  // If 40%+ are prose lines, it's plain text
  const total = proseLines + codeLines;
  if (total > 0) {
    return proseLines / total > 0.4;
  }

  // Default: no clear structure = plain text
  return lines.length > 3 && code.match(/[{};]/g)?.length < 3;
};

const detectLanguage = (code: string): LanguageInfo => {
  // FIRST: Check if it's plain text
  if (isPlainText(code)) {
    return { name: "Plain Text", monacoId: "plaintext", icon: "📄", color: "#6B7280" };
  }

  // Then check language patterns
  for (const { pattern, lang } of LANGUAGE_PATTERNS) {
    if (pattern.test(code)) {
      return lang;
    }
  }
  return { name: "Plain Text", monacoId: "plaintext", icon: "📄", color: "#6B7280" };
};

export const CodeAnalysis: React.FC = () => {
  const [code, setCode] = useState(
    "// Paste your code here\nfunction example() {\n  return \"Hello World\";\n}"
  );
  const [detectedLanguage, setDetectedLanguage] = useState<LanguageInfo>(
    detectLanguage("// Paste your code here\nfunction example() {\n  return \"Hello World\";\n}")
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [showLanguageAnimation, setShowLanguageAnimation] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAnalyze = useCallback(async (codeToAnalyze: string) => {
    if (!codeToAnalyze.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeCode(codeToAnalyze);
      setResult({
        ...data,
        language: detectedLanguage.name,
      });
      setIsDirty(false);
    } catch (err: any) {
      setError(err.message || "Analysis failed");
    } finally {
      setLoading(false);
    }
  }, [detectedLanguage.name]);

  useEffect(() => {
    if (!isDirty || code.length < 15) return;
    const timer = setTimeout(() => handleAnalyze(code), 2000);
    return () => clearTimeout(timer);
  }, [code, isDirty, handleAnalyze]);

  // Auto-detect language when code changes
  useEffect(() => {
    const newLang = detectLanguage(code);
    if (newLang.name !== detectedLanguage.name) {
      setDetectedLanguage(newLang);
      setShowLanguageAnimation(true);
      setTimeout(() => setShowLanguageAnimation(false), 1500);
    }
  }, [code, detectedLanguage.name]);

  const handleEditorChange = (value?: string) => {
    const newCode = value || "";
    setCode(newCode);
    setIsDirty(true);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result;
      if (typeof text === "string") {
        setCode(text);
        setIsDirty(true);
        handleAnalyze(text);
      }
    };
    reader.readAsText(file);
  };

  const metricData = result
    ? [
      { name: "LoC", value: result.metrics.linesOfCode },
      { name: "Fun", value: result.metrics.functionCount },
      { name: "Loops", value: result.metrics.loopCount },
      { name: "Con", value: result.metrics.conditionalCount },
      { name: "Cyc", value: result.metrics.cyclomaticComplexity },
    ]
    : [];

  const optimizationData = result
    ? [
      { name: "Optimized", value: result.optimizationPercentage },
      { name: "Remaining", value: 100 - result.optimizationPercentage },
    ]
    : [];

  return (
    <div className="flex h-full w-full bg-background">
      {/* EDITOR */}
      <div className="flex-1 flex flex-col bg-[#1e1e1e]">
        {/* LANGUAGE DETECTION BADGE - TOP OF EDITOR */}
        <div className="flex items-center justify-between px-4 py-2 bg-gradient-to-r from-[#1a1a2e] to-[#16213e] border-b border-gray-700/50">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <FileCode className="w-4 h-4 text-gray-400" />
              <span className="text-xs text-gray-400 uppercase tracking-wider">Language Detected</span>
            </div>
            <div
              className={`
                flex items-center gap-2 px-3 py-1.5 rounded-full 
                transition-all duration-300 ease-out
                ${showLanguageAnimation ? 'scale-110 ring-2 ring-offset-2 ring-offset-[#1a1a2e]' : 'scale-100'}
              `}
              style={{
                backgroundColor: `${detectedLanguage.color}20`,
                borderColor: detectedLanguage.color,
                border: `1px solid ${detectedLanguage.color}`,
                boxShadow: showLanguageAnimation ? `0 0 20px ${detectedLanguage.color}40` : 'none'
              }}
            >
              <span className="text-lg">{detectedLanguage.icon}</span>
              <span
                className="font-semibold text-sm"
                style={{ color: detectedLanguage.color }}
              >
                {detectedLanguage.name}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Code2 className="w-3 h-3" />
            <span>Auto-detection enabled</span>
          </div>
        </div>

        {/* MONACO EDITOR */}
        <div className="flex-1">
          <Editor
            height="100%"
            theme="vs-dark"
            language={detectedLanguage.monacoId}
            value={code}
            onChange={handleEditorChange}
            options={{
              fontSize: 14,
              minimap: { enabled: true },
              scrollBeyondLastLine: false,
              wordWrap: "on",
              automaticLayout: true,
            }}
          />
        </div>

        {/* BOTTOM TOOLBAR */}
        <div className="p-3 flex justify-between items-center bg-[#252526] border-t border-gray-700/50">
          <div className="flex items-center gap-3">
            <button
              onClick={() => handleAnalyze(code)}
              disabled={loading}
              className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-lg font-medium flex items-center gap-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-500/20"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {loading ? "Analyzing..." : "Analyze"}
            </button>
            <span className="text-xs text-gray-500">
              {code.split('\n').length} lines • {code.length} chars
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg flex items-center gap-2 transition-colors"
            >
              <Upload className="w-4 h-4" />
              <span className="text-sm">Upload</span>
            </button>
          </div>
          <input ref={fileInputRef} type="file" hidden onChange={handleFileUpload} />
        </div>
      </div>

      {/* ANALYSIS INSIGHTS */}
      <div className="w-[580px] p-6 space-y-6 bg-gradient-to-b from-[#0b1220] to-[#0e1627] overflow-y-auto">
        {loading && <Loader />}
        {error && <div className="text-red-500">{error}</div>}

        {result && (
          <>
            {/* CHECK IF IT'S ACTUALLY CODE */}
            {result.isCode === false ? (
              /* NO CODE DETECTED */
              <div className="flex flex-col items-center justify-center h-full text-center space-y-6 py-12">
                <div className="w-24 h-24 rounded-full bg-gray-800/50 flex items-center justify-center">
                  <span className="text-5xl">📄</span>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-300 mb-2">No Code Detected</h2>
                  <p className="text-gray-500 max-w-xs">
                    The input appears to be plain text, not source code.
                  </p>
                </div>
                <div className="bg-surface rounded-xl p-5 border border-gray-800 w-full max-w-sm">
                  <p className="text-xs text-gray-400 mb-3">SUPPORTED LANGUAGES</p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {["🐍 Python", "☕ Java", "⚡ C++", "🔧 C", "📜 JavaScript", "📘 TypeScript", "🐹 Go", "🦀 Rust", "💎 Ruby", "🐘 PHP"].map((lang) => (
                      <span key={lang} className="px-2 py-1 bg-gray-800 rounded text-xs text-gray-400">
                        {lang}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 max-w-sm">
                  <p className="text-yellow-500 text-sm">
                    💡 Tip: Paste code with functions, loops, or class definitions for complexity analysis.
                  </p>
                </div>
              </div>
            ) : (
              /* NORMAL CODE ANALYSIS RESULTS */
              <>
                <div className="space-y-8">
                  {/* BIG METRICS: TIME & SPACE */}
                  <div className="grid grid-cols-2 gap-6">
                    <div className="bg-surface/50 border border-gray-800 rounded-3xl p-8 hover:border-indigo-500/50 transition-all group relative overflow-hidden">
                      <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                        <Zap className="w-20 h-20" />
                      </div>
                      <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold mb-3">Worst-Case Time</p>
                      <h2 className="text-5xl font-black text-indigo-400 tracking-tighter">{result.timeComplexity}</h2>
                      <p className="text-xs text-gray-400 mt-4 font-mono group-hover:text-indigo-300/70 transition-colors">
                        Driver: {result.worstTimeFunction?.split(', ')[0] || "main"}()
                      </p>
                    </div>

                    <div className="bg-surface/50 border border-gray-800 rounded-3xl p-8 hover:border-emerald-500/50 transition-all group relative overflow-hidden">
                      <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                        <Code2 className="w-20 h-20" />
                      </div>
                      <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold mb-3">Worst-Case Space</p>
                      <h2 className="text-5xl font-black text-emerald-400 tracking-tighter">{result.spaceComplexity}</h2>
                      <p className="text-xs text-gray-400 mt-4 font-mono group-hover:text-emerald-300/70 transition-colors">
                        Driver: {result.worstSpaceFunction?.split(', ')[0] || "main"}()
                      </p>
                    </div>
                  </div>

                  {/* SUMMARY NOTE */}
                  {result.summary && (
                    <div className="px-6 py-4 bg-white/[0.03] border border-white/5 rounded-2xl">
                      <p className="text-xs text-indigo-300/80 leading-relaxed font-medium italic">
                        {result.summary}
                      </p>
                    </div>
                  )}

                  {/* CORE STATISTICS GRID */}
                  {/* CORE STATISTICS GRID */}
                  <div className="bg-surface border border-gray-800 rounded-3xl overflow-hidden">
                    <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-gray-800">
                      {/* Left: Text Stats */}
                      <div className="divide-y divide-gray-800 h-full flex flex-col justify-center">
                        <div className="grid grid-cols-2 divide-x divide-gray-800 flex-1">
                          <div className="p-6 flex flex-col justify-center text-center hover:bg-white/[0.02] transition-colors">
                            <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold mb-1">Lines of Code</p>
                            <p className="text-3xl font-bold text-gray-100">{result.metrics.linesOfCode}</p>
                          </div>
                          <div className="p-6 flex flex-col justify-center text-center hover:bg-white/[0.02] transition-colors">
                            <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold mb-1">Functions</p>
                            <p className="text-3xl font-bold text-gray-100">{result.metrics.functionCount}</p>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 divide-x divide-gray-800 flex-1">
                          <div className="p-6 flex flex-col justify-center text-center hover:bg-white/[0.02] transition-colors">
                            <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold mb-1">Number of Loops</p>
                            <p className="text-3xl font-bold text-gray-100">{result.metrics.loopCount}</p>
                          </div>
                          <div className="p-6 flex flex-col justify-center text-center hover:bg-white/[0.02] transition-colors">
                            <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold mb-1">Number of Conditions</p>
                            <p className="text-3xl font-bold text-gray-100">{result.metrics.conditionalCount}</p>
                          </div>
                        </div>
                      </div>

                      {/* Right: Chart */}
                      <div className="p-6 h-[250px] bg-white/[0.01] flex items-center justify-center relative group">
                        <div className="absolute top-3 right-4">
                          <span className="text-[9px] font-bold text-gray-600 uppercase tracking-wider">Metrics Visualizer</span>
                        </div>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={metricData} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                            <XAxis
                              dataKey="name"
                              stroke="#6b7280"
                              fontSize={11}
                              tickLine={false}
                              axisLine={false}
                              dy={10}
                            />
                            <YAxis
                              stroke="#6b7280"
                              fontSize={11}
                              tickLine={false}
                              axisLine={false}
                            />
                            <Tooltip
                              cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                              contentStyle={{
                                backgroundColor: '#0f172a',
                                borderColor: '#1e293b',
                                color: '#f8fafc',
                                borderRadius: '8px',
                                fontSize: '12px'
                              }}
                              itemStyle={{ color: '#818cf8' }}
                            />
                            <Bar
                              dataKey="value"
                              fill="#6366f1"
                              radius={[4, 4, 0, 0]}
                              barSize={30}
                              animationDuration={1500}
                            >
                              {metricData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={['#6366f1', '#a855f7', '#ec4899', '#10b981', '#f59e0b'][index % 5]} />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>

                  {/* OPTIMIZATION & SUGGESTIONS */}
                  <div className="bg-gradient-to-br from-indigo-600/10 to-purple-600/10 border border-indigo-500/20 rounded-3xl p-8 relative overflow-hidden">
                    <div className="flex justify-between items-start mb-8">
                      <div>
                        <p className="text-[10px] text-indigo-400 uppercase tracking-widest font-bold mb-2">Peak Optimization Potential</p>
                        <h3 className="text-4xl font-black text-white">{result.optimizationPercentage}%</h3>
                      </div>
                      <div className="bg-indigo-500/20 px-3 py-1 rounded-full border border-indigo-500/30">
                        <span className="text-[10px] font-bold text-indigo-300 uppercase tracking-tighter">Optimization Insights</span>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Improvement Roadmap</p>
                      <div className="grid gap-3">
                        {result.suggestions.map((s: string, i: number) => (
                          <div key={i} className="flex gap-4 p-4 bg-white/5 rounded-2xl border border-white/5 hover:bg-white/10 transition-colors">
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-600/50 text-[10px] font-bold flex items-center justify-center">
                              0{i + 1}
                            </span>
                            <p className="text-sm text-gray-200 leading-relaxed font-medium">{s}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>


                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
};

