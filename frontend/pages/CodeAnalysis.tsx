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
      <div className="flex flex-col lg:flex-row min-h-full w-full bg-background lg:overflow-hidden">
      {/* EDITOR */}
      <div className="flex flex-col bg-background h-[50vh] lg:h-auto lg:flex-1 shrink-0">
        {/* LANGUAGE DETECTION BADGE - TOP OF EDITOR */}
        <div className="flex items-center justify-between px-4 py-2 bg-surface border-b border-borderSubtle">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <FileCode className="w-4 h-4 text-textSecondary" />
              <span className="text-xs text-textSecondary uppercase tracking-wider">Language Detected</span>
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
                className="font-medium text-sm"
                style={{ color: detectedLanguage.color }}
              >
                {detectedLanguage.name}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-textSecondary">
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
        <div className="p-3 flex justify-between items-center bg-surface border-t border-borderSubtle">
          <div className="flex items-center gap-3">
            <button
              onClick={() => handleAnalyze(code)}
              disabled={loading}
              className="px-4 py-2 bg-primary hover:bg-primarySubtle text-background rounded-md font-medium flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-background/30 border-t-background rounded-full animate-spin" />
              ) : (
                <Play className="w-4 h-4 fill-current" />
              )}
              {loading ? "Analyzing..." : "Analyze"}
            </button>
            <span className="text-xs text-textSecondary">
              {code.split('\n').length} lines • {code.length} chars
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-3 py-2 bg-secondaryBg hover:bg-surfaceElevated border border-borderSubtle text-textSecondary rounded-md flex items-center gap-2 transition-colors"
            >
              <Upload className="w-4 h-4" />
              <span className="text-sm">Upload</span>
            </button>
          </div>
          <input ref={fileInputRef} type="file" hidden onChange={handleFileUpload} />
        </div>
      </div>

      {/* ANALYSIS INSIGHTS */}
      <div className="w-full lg:w-[480px] xl:w-[580px] shrink-0 p-4 md:p-6 space-y-6 bg-background border-t lg:border-t-0 lg:border-l border-borderSubtle lg:overflow-y-auto lg:h-full">
        {loading && <Loader />}
        {error && <div className="text-danger">{error}</div>}

        {result && (
          <>
            {/* CHECK IF IT'S ACTUALLY CODE */}
            {result.isCode === false ? (
              /* NO CODE DETECTED */
              <div className="flex flex-col items-center justify-center h-full text-center space-y-6 py-12">
                <div className="w-24 h-24 rounded-full bg-surface border border-borderSubtle flex items-center justify-center">
                  <span className="text-5xl">📄</span>
                </div>
                <div>
                  <h2 className="text-xl font-medium text-textPrimary mb-2">No Code Detected</h2>
                  <p className="text-textSecondary max-w-xs text-sm">
                    The input appears to be plain text, not source code.
                  </p>
                </div>
                <div className="bg-surface rounded-xl p-5 border border-borderSubtle w-full max-w-sm">
                  <p className="text-[10px] uppercase tracking-wider text-textSecondary mb-3 font-medium">SUPPORTED LANGUAGES</p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {["🐍 Python", "☕ Java", "⚡ C++", "🔧 C", "📜 JavaScript", "📘 TypeScript", "🐹 Go", "🦀 Rust", "💎 Ruby", "🐘 PHP"].map((lang) => (
                      <span key={lang} className="px-2 py-1 bg-secondaryBg border border-borderSubtle rounded text-xs text-textSecondary">
                        {lang}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="bg-warning/10 border border-warning/20 rounded-md p-4 max-w-sm">
                  <p className="text-warning text-xs font-medium">
                    💡 Tip: Paste code with functions, loops, or class definitions for complexity analysis.
                  </p>
                </div>
              </div>
            ) : (
              /* NORMAL CODE ANALYSIS RESULTS */
              <>
                <div className="space-y-6">
                  {/* BIG METRICS: TIME & SPACE */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-surface border border-borderSubtle rounded-xl p-5 group relative overflow-hidden shadow-sm">
                      <div className="absolute top-0 right-0 p-3 opacity-[0.03]">
                        <Zap className="w-12 h-12" />
                      </div>
                      <p className="text-xs text-textSecondary font-medium mb-2">Worst-Case Time</p>
                      <h2 className="text-3xl font-semibold text-primary tracking-tighter">{result.timeComplexity}</h2>
                      <p className="text-xs text-textMuted mt-2 font-mono truncate">
                        Driver: {result.worstTimeFunction?.split(', ')[0] || "main"}()
                      </p>
                    </div>

                    <div className="bg-surface border border-borderSubtle rounded-xl p-5 group relative overflow-hidden shadow-sm">
                      <div className="absolute top-0 right-0 p-3 opacity-[0.03]">
                        <Code2 className="w-12 h-12" />
                      </div>
                      <p className="text-xs text-textSecondary font-medium mb-2">Worst-Case Space</p>
                      <h2 className="text-3xl font-semibold text-success tracking-tighter">{result.spaceComplexity}</h2>
                      <p className="text-xs text-textMuted mt-2 font-mono truncate">
                        Driver: {result.worstSpaceFunction?.split(', ')[0] || "main"}()
                      </p>
                    </div>
                  </div>

                  {/* SUMMARY NOTE */}
                  {result.summary && (
                    <div className="px-5 py-4 bg-surface border border-borderSubtle rounded-xl shadow-sm">
                      <p className="text-sm text-textPrimary leading-relaxed">
                        {result.summary}
                      </p>
                    </div>
                  )}

                  {/* CORE STATISTICS GRID */}
                  <div className="bg-surface border border-borderSubtle rounded-xl overflow-hidden shadow-sm">
                    <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-borderSubtle">
                      {/* Left: Text Stats */}
                      <div className="divide-y divide-borderSubtle h-full flex flex-col justify-center">
                        <div className="grid grid-cols-2 divide-x divide-borderSubtle flex-1">
                          <div className="p-5 flex flex-col justify-center text-center">
                            <p className="text-[10px] uppercase text-textSecondary font-medium tracking-wider mb-1">Lines of Code</p>
                            <p className="text-2xl font-semibold text-textPrimary">{result.metrics.linesOfCode}</p>
                          </div>
                          <div className="p-5 flex flex-col justify-center text-center">
                            <p className="text-[10px] uppercase text-textSecondary font-medium tracking-wider mb-1">Functions</p>
                            <p className="text-2xl font-semibold text-textPrimary">{result.metrics.functionCount}</p>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 divide-x divide-borderSubtle flex-1">
                          <div className="p-5 flex flex-col justify-center text-center">
                            <p className="text-[10px] uppercase text-textSecondary font-medium tracking-wider mb-1">Loops</p>
                            <p className="text-2xl font-semibold text-textPrimary">{result.metrics.loopCount}</p>
                          </div>
                          <div className="p-5 flex flex-col justify-center text-center">
                            <p className="text-[10px] uppercase text-textSecondary font-medium tracking-wider mb-1">Conditions</p>
                            <p className="text-2xl font-semibold text-textPrimary">{result.metrics.conditionalCount}</p>
                          </div>
                        </div>
                      </div>

                      {/* Right: Chart */}
                      <div className="p-6 h-[250px] bg-secondaryBg flex items-center justify-center relative group">
                        <div className="absolute top-3 right-4">
                          <span className="text-[10px] font-medium text-textSecondary uppercase tracking-wider">Metrics Visualizer</span>
                        </div>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={metricData} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                            <XAxis
                              dataKey="name"
                              stroke="#71717A"
                              fontSize={11}
                              tickLine={false}
                              axisLine={false}
                              dy={10}
                            />
                            <YAxis
                              stroke="#71717A"
                              fontSize={11}
                              tickLine={false}
                              axisLine={false}
                            />
                            <Tooltip
                              cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                              contentStyle={{
                                backgroundColor: '#19191C',
                                borderColor: 'rgba(255,255,255,0.08)',
                                color: '#F5F5F5',
                                borderRadius: '8px',
                                fontSize: '12px'
                              }}
                              itemStyle={{ color: '#FF7A59' }}
                            />
                            <Bar
                              dataKey="value"
                              fill="#FF7A59"
                              radius={[2, 2, 0, 0]}
                              barSize={24}
                              animationDuration={1500}
                            >
                              {metricData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={['#FF7A59', '#34D399', '#FBBF24', '#F87171', '#FF9B7A'][index % 5]} />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>

                  {/* OPTIMIZATION & SUGGESTIONS */}
                  <div className="bg-surface border border-borderSubtle rounded-xl p-6 shadow-sm">
                    <div className="flex justify-between items-start mb-6">
                      <div>
                        <p className="text-xs text-textSecondary font-medium mb-1">Peak Optimization Potential</p>
                        <h3 className="text-4xl font-semibold text-textPrimary">{result.optimizationPercentage}%</h3>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <p className="text-xs font-medium text-textSecondary mb-3 uppercase tracking-wider">Improvement Roadmap</p>
                      <div className="grid gap-2">
                        {result.suggestions.map((s: string, i: number) => (
                          <div key={i} className="flex gap-4 p-3 bg-secondaryBg rounded-lg border border-borderSubtle">
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-surfaceElevated border border-borderSubtle text-xs font-medium flex items-center justify-center text-textPrimary">
                              {i + 1}
                            </span>
                            <p className="text-sm text-textPrimary leading-relaxed pt-0.5">{s}</p>
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

