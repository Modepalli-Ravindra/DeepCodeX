import React from 'react';
import { BookOpen, Code2, Zap, LayoutTemplate } from 'lucide-react';

export const Docs: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto p-6 md:p-8 space-y-12 animate-fade-in pb-20">
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-textPrimary tracking-tight">Documentation</h1>
        <p className="text-textSecondary mt-2 max-w-2xl">
          Everything you need to know about DeepCodeX. From getting started to understanding our advanced AI complexity metrics.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        {/* Sidebar Navigation */}
        <div className="md:col-span-1 space-y-2 sticky top-8 h-fit">
          <div className="text-[10px] font-bold text-textMuted uppercase tracking-wider mb-4 px-2">Table of Contents</div>
          <button onClick={() => document.getElementById('getting-started')?.scrollIntoView({ behavior: 'smooth' })} className="w-full text-left px-4 py-2 text-sm text-primary bg-primary/10 rounded-lg font-medium">Getting Started</button>
          <button onClick={() => document.getElementById('supported-languages')?.scrollIntoView({ behavior: 'smooth' })} className="w-full text-left px-4 py-2 text-sm text-textSecondary hover:bg-surface hover:text-textPrimary rounded-lg transition-colors">Supported Languages</button>
          <button onClick={() => document.getElementById('understanding-metrics')?.scrollIntoView({ behavior: 'smooth' })} className="w-full text-left px-4 py-2 text-sm text-textSecondary hover:bg-surface hover:text-textPrimary rounded-lg transition-colors">Understanding Metrics</button>
          <button onClick={() => document.getElementById('api-reference')?.scrollIntoView({ behavior: 'smooth' })} className="w-full text-left px-4 py-2 text-sm text-textSecondary hover:bg-surface hover:text-textPrimary rounded-lg transition-colors">API Reference</button>
        </div>

        {/* Content Area */}
        <div className="md:col-span-2 space-y-12">
          
          <section id="getting-started" className="space-y-4">
            <div className="flex items-center gap-3 border-b border-borderSubtle pb-4">
              <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center text-blue-500">
                <BookOpen className="w-4 h-4" />
              </div>
              <h2 className="text-xl font-bold text-textPrimary">Getting Started</h2>
            </div>
            <p className="text-textSecondary text-sm leading-relaxed">
              DeepCodeX analyzes your source code using advanced AI algorithms to determine its time complexity, space complexity, and overall maintainability.
            </p>
            <div className="bg-surface border border-borderSubtle rounded-xl p-4 mt-4">
              <h3 className="text-sm font-semibold text-textPrimary mb-2">Quick Start Guide</h3>
              <ol className="list-decimal list-inside text-sm text-textSecondary space-y-2">
                <li>Navigate to the <span className="text-primary font-medium">Analyze</span> page from the top navigation.</li>
                <li>Paste your code directly into the editor, or upload a file using the upload button.</li>
                <li>Our system will automatically detect the programming language.</li>
                <li>Click <span className="text-primary font-medium">Analyze</span> to generate insights.</li>
              </ol>
            </div>
          </section>

          <section id="supported-languages" className="space-y-4">
            <div className="flex items-center gap-3 border-b border-borderSubtle pb-4">
              <div className="w-8 h-8 rounded-lg bg-yellow-500/20 flex items-center justify-center text-yellow-500">
                <Code2 className="w-4 h-4" />
              </div>
              <h2 className="text-xl font-bold text-textPrimary">Supported Languages</h2>
            </div>
            <p className="text-textSecondary text-sm leading-relaxed">
              Our AI engine natively supports formatting and deep complexity analysis for the following languages. Plain text or pseudo-code can also be analyzed but may yield less accurate metrics.
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-4">
              {['JavaScript', 'Python', 'Java', 'C++', 'C', 'Go', 'TypeScript', 'PHP', 'Ruby', 'Rust'].map(lang => (
                <div key={lang} className="bg-secondaryBg border border-borderSubtle rounded-lg px-3 py-2 text-xs font-medium text-textPrimary text-center">
                  {lang}
                </div>
              ))}
            </div>
          </section>

          <section id="understanding-metrics" className="space-y-4">
            <div className="flex items-center gap-3 border-b border-borderSubtle pb-4">
              <div className="w-8 h-8 rounded-lg bg-[#D946EF]/20 flex items-center justify-center text-[#D946EF]">
                <Zap className="w-4 h-4" />
              </div>
              <h2 className="text-xl font-bold text-textPrimary">Understanding Metrics</h2>
            </div>
            <div className="space-y-6 text-sm text-textSecondary">
              <div>
                <h3 className="text-textPrimary font-semibold mb-1">Time & Space Complexity</h3>
                <p>We use standard Big O notation (e.g., <code className="bg-surface px-1.5 py-0.5 rounded border border-borderSubtle text-primary">O(N)</code>) to describe the worst-case performance of your algorithms.</p>
              </div>
              <div>
                <h3 className="text-textPrimary font-semibold mb-1">Cyclomatic Complexity</h3>
                <p>A quantitative measure of the number of linearly independent paths through a program's source code. A lower number indicates code that is easier to test and maintain.</p>
                <ul className="list-disc list-inside mt-2 space-y-1 pl-2">
                  <li><span className="text-success font-medium">1-10:</span> Simple procedure, low risk.</li>
                  <li><span className="text-warning font-medium">11-20:</span> More complex, moderate risk.</li>
                  <li><span className="text-danger font-medium">21+:</span> Highly complex, high risk. Refactoring recommended.</li>
                </ul>
              </div>
            </div>
          </section>

          <section id="api-reference" className="space-y-4">
            <div className="flex items-center gap-3 border-b border-borderSubtle pb-4">
              <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center text-green-500">
                <LayoutTemplate className="w-4 h-4" />
              </div>
              <h2 className="text-xl font-bold text-textPrimary">API Reference</h2>
            </div>
            <p className="text-textSecondary text-sm leading-relaxed mb-4">
              DeepCodeX exposes a RESTful API for integrating our complexity engine directly into your CI/CD pipelines.
            </p>
            
            <div className="bg-[#0D0D12] border border-borderSubtle rounded-xl overflow-hidden">
              <div className="bg-surfaceElevated px-4 py-2 border-b border-borderSubtle flex items-center gap-2">
                <span className="text-xs font-bold text-success">POST</span>
                <span className="text-xs font-mono text-textPrimary">/api/v1/analyze</span>
              </div>
              <div className="p-4 font-mono text-xs text-textSecondary overflow-x-auto">
                <pre>
<span className="text-primary">curl</span> -X POST https://api.deepcodex.com/v1/analyze \
  -H <span className="text-green-400">"Authorization: Bearer YOUR_API_KEY"</span> \
  -H <span className="text-green-400">"Content-Type: application/json"</span> \
  -d <span className="text-yellow-300">'{'{'}
    "code": "function sum(a, b) {'{'} return a + b; {'}'}",
    "language": "javascript"
  {'}'}'</span>
                </pre>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
};
