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

const detectLanguage = (code: string): LanguageInfo => {
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
                <div className="grid grid-cols-3 gap-4 w-full opacity-30">
                  <div className="bg-surface rounded-xl p-5 border border-gray-800">
                    <p className="text-xs text-gray-400">Time Complexity</p>
                    <p className="text-2xl font-bold text-gray-600">N/A</p>
                  </div>
                  <div className="bg-surface rounded-xl p-5 border border-gray-800">
                    <p className="text-xs text-gray-400">Space Complexity</p>
                    <p className="text-2xl font-bold text-gray-600">N/A</p>
                  </div>
                  <div className="bg-surface rounded-xl p-5 border border-gray-800">
                    <p className="text-xs text-gray-400">Score</p>
                    <p className="text-2xl font-bold text-gray-600">0</p>
                  </div>
                </div>
              </div>
            ) : (
              /* NORMAL CODE ANALYSIS RESULTS */
              <>
                {/* TOP SUMMARY */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-surface rounded-xl p-5 border border-gray-800">
                    <p className="text-xs text-gray-400">COMPLEXITY</p>
                    <div className="flex items-center justify-between">
                      <h2 className="text-3xl font-bold text-yellow-400">
                        {result.complexityLevel}
                      </h2>
                      <Zap className="text-yellow-400" />
                    </div>
                    <p className="text-sm text-gray-400">
                      Score: {result.score}/100
                    </p>
                    <div className="mt-3 h-2 bg-gray-800 rounded">
                      <div
                        className="h-2 bg-primary rounded"
                        style={{ width: `${result.score}%` }}
                      />
                    </div>
                  </div>

                  <div className="bg-surface rounded-xl p-5 border border-gray-800">
                    <p className="text-xs text-gray-400">Time Complexity</p>
                    <p className="text-2xl font-bold text-blue-400">
                      {result.timeComplexity}
                    </p>
                  </div>

                  <div className="bg-surface rounded-xl p-5 border border-gray-800">
                    <p className="text-xs text-gray-400">Space Complexity</p>
                    <p className="text-2xl font-bold text-green-400">
                      {result.spaceComplexity}
                    </p>
                  </div>
                </div>

                {/* EFFICIENCY METRICS */}
                <div className="bg-surface rounded-xl p-6 border border-gray-800">
                  <h3 className="text-sm font-semibold mb-4">Efficiency Metrics</h3>
                  <div className="grid grid-cols-2 gap-y-3 text-sm text-gray-300">
                    <div>Score</div><div>{result.score}/100</div>
                    <div>Optimization</div><div>{result.optimizationPercentage}%</div>
                    <div>Language</div>
                    <div className="flex items-center gap-2">
                      <span>{detectedLanguage.icon}</span>
                      <span style={{ color: detectedLanguage.color }}>{result.language}</span>
                    </div>
                    <div>Engine</div>
                    <div>AST + Rule Engine + Regex + LLM (suggestions only)</div>
                  </div>
                </div>

                {/* STRUCTURAL ANALYSIS */}
                <div className="bg-surface rounded-xl p-6 border border-gray-800">
                  <h3 className="text-sm font-semibold mb-4">Structural Analysis</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="h-[220px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={metricData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis
                            dataKey="name"
                            interval={0}
                            tick={{ fill: "#94a3b8", fontSize: 12 }}
                            axisLine={false}
                            tickLine={false}
                          />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="value" fill="#6366f1" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="text-sm text-gray-300 space-y-2">
                      <div>Total Code Volume: {result.metrics.linesOfCode}</div>
                      <div>Functional Units: {result.metrics.functionCount}</div>
                      <div>Iterative Density: {result.metrics.loopCount}</div>
                      <div>Logical Branches: {result.metrics.conditionalCount}</div>
                      <div>Cyclomatic Index: {result.metrics.cyclomaticComplexity}</div>
                    </div>
                  </div>
                </div>

                {/* REFACTOR POTENTIAL */}
                <div className="bg-surface rounded-xl p-6 border border-gray-800">
                  <h3 className="text-sm font-semibold mb-4">Refactor Potential</h3>
                  <div className="h-[180px] relative">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={optimizationData}
                          dataKey="value"
                          innerRadius={70}
                          outerRadius={90}
                        >
                          <Cell fill="#6366f1" />
                          <Cell fill="#1e293b" />
                        </Pie>
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="absolute inset-0 flex items-center justify-center text-xl font-bold">
                      {result.optimizationPercentage}%
                    </div>
                  </div>
                </div>

                {/* REFACTOR STRATEGY */}
                <div className="bg-surface rounded-xl p-6 border border-gray-800">
                  <h3 className="text-sm font-semibold mb-3">Refactor Strategy</h3>
                  <ul className="space-y-2 text-sm text-gray-300">
                    {result.suggestions.map((s, i) => (
                      <li key={i}>• {s}</li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
};

