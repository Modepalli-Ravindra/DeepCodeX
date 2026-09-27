import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { Activity, Clock, FileCode, Shield, ArrowRight, ChevronDown, CheckCircle, Code2, AlertTriangle, Zap, FileText } from 'lucide-react';
import { Link } from 'react-router-dom';

const MOCK_METRICS = [
  { name: 'Mon', analyses: 4 },
  { name: 'Tue', analyses: 7 },
  { name: 'Wed', analyses: 5 },
  { name: 'Thu', analyses: 12 },
  { name: 'Fri', analyses: 9 },
  { name: 'Sat', analyses: 3 },
  { name: 'Sun', analyses: 2 },
];

const COMPLEXITY_DISTRIBUTION = [
  { name: 'Low Complexity', value: 42, color: '#10B981' },
  { name: 'Medium Complexity', value: 35, color: '#F59E0B' },
  { name: 'High Complexity', value: 23, color: '#EF4444' },
];

const MINI_CHART_GREEN = [{v:1},{v:2},{v:1.5},{v:3},{v:2.5},{v:4},{v:3.5},{v:5}];
const MINI_CHART_YELLOW = [{v:1},{v:1.5},{v:2.5},{v:2},{v:3},{v:4},{v:3.5},{v:5}];
const MINI_CHART_PURPLE = [{v:1},{v:2},{v:3},{v:2.5},{v:4},{v:3},{v:4.5},{v:5}];

const StatCard = ({ icon: Icon, iconBg, iconColor, label, value, trend, chartData, chartColor }: any) => (
  <div className="bg-surface p-5 rounded-2xl border border-borderSubtle flex flex-col justify-between relative overflow-hidden group hover:border-primary/30 transition-colors">
    <div className="flex items-center gap-4 mb-4 z-10">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${iconBg} ${iconColor} shadow-inner`}>
        <Icon className="w-6 h-6 stroke-[1.5px]" />
      </div>
      <div>
        <p className="text-xs font-medium text-textSecondary uppercase tracking-wider mb-1">{label}</p>
        <div className="flex items-baseline gap-2">
          <h3 className="text-2xl font-bold text-textPrimary">{value}</h3>
          <span className="text-[10px] font-semibold text-success flex items-center">
            ▲ {trend}
          </span>
        </div>
      </div>
    </div>
    
    <div className="h-10 w-full absolute bottom-4 right-4 z-0 flex justify-end">
      <div className="w-1/2 h-full opacity-60">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <Line type="monotone" dataKey="v" stroke={chartColor} strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  </div>
);

const LANGS = [
  { name: 'JavaScript', icon: 'JS', color: '#F7DF1E' },
  { name: 'Python', icon: 'PY', color: '#3776AB' },
  { name: 'Java', icon: '☕', color: '#B07219' },
  { name: 'C++', icon: 'C++', color: '#00599C' },
  { name: 'C', icon: 'C', color: '#A8B9CC' },
  { name: 'Go', icon: 'GO', color: '#00ADD8' },
  { name: 'TypeScript', icon: 'TS', color: '#3178C6' },
  { name: 'PHP', icon: 'php', color: '#777BB4' },
  { name: 'Ruby', icon: '♦', color: '#CC342D' },
  { name: 'Rust', icon: 'R', color: '#DEA584' },
];

export const Dashboard: React.FC = () => {
  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-8 space-y-6 animate-fade-in pb-20">
      
      {/* Hero Section */}
      <div className="relative w-full rounded-3xl bg-surface border border-borderSubtle overflow-hidden p-8 lg:p-12 flex flex-col lg:flex-row items-center justify-between gap-12">
        {/* Background glow for hero */}
        <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-primary/20 blur-[150px] rounded-full pointer-events-none mix-blend-screen"></div>
        <div className="absolute bottom-0 left-1/4 w-[400px] h-[400px] bg-accent/20 blur-[120px] rounded-full pointer-events-none mix-blend-screen"></div>

        <div className="relative z-10 max-w-xl">
          <div className="flex items-center gap-3 text-xs font-semibold text-textSecondary uppercase tracking-widest mb-6">
            <span>Analyze</span> <span className="w-1 h-1 rounded-full bg-textMuted"></span> 
            <span>Understand</span> <span className="w-1 h-1 rounded-full bg-textMuted"></span> 
            <span>Improve</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-textPrimary mb-6 leading-[1.1] tracking-tight">
            Write Better Code<br />
            with <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-[#D946EF] to-accent">AI Insights</span>
          </h1>
          <p className="text-textSecondary text-base mb-8 max-w-md leading-relaxed">
            Analyze code complexity, detect issues, get AI-powered suggestions and improve your code quality instantly.
          </p>
          <div className="flex items-center gap-4">
            <Link 
              to="/analyze" 
              className="inline-flex items-center gap-2 bg-gradient-to-r from-primary to-accent hover:opacity-90 text-white px-6 py-3 rounded-xl font-medium text-sm transition-opacity shadow-glow"
            >
              Analyze Code
              <ArrowRight className="w-4 h-4 stroke-[2px]" />
            </Link>
            <Link 
              to="/history" 
              className="inline-flex items-center gap-2 bg-secondaryBg hover:bg-surfaceElevated border border-borderSubtle text-textPrimary px-6 py-3 rounded-xl font-medium text-sm transition-colors"
            >
              <Clock className="w-4 h-4 stroke-[2px]" />
              View History
            </Link>
          </div>
        </div>

        {/* Right side mockups */}
        <div className="relative z-10 flex-1 w-full max-w-2xl hidden md:flex items-center gap-4">
          {/* Mock Editor */}
          <div className="bg-[#0D0D12] border border-borderSubtle rounded-xl flex-1 overflow-hidden shadow-2xl">
            <div className="h-8 bg-[#1A1A24] flex items-center px-4 gap-2">
              <div className="w-3 h-3 rounded-full bg-danger"></div>
              <div className="w-3 h-3 rounded-full bg-warning"></div>
              <div className="w-3 h-3 rounded-full bg-success"></div>
            </div>
            <div className="p-4 font-mono text-xs leading-loose text-textSecondary">
              <div className="flex">
                <span className="w-6 opacity-30 select-none">1</span>
                <span className="text-primary">function</span> <span className="text-blue-400">analyzeCode</span>() {'{'}
              </div>
              <div className="flex">
                <span className="w-6 opacity-30 select-none">2</span>
                <span className="text-primary ml-4">const</span> <span className="text-blue-300">code</span> = <span className="text-blue-400">getInput</span>();
              </div>
              <div className="flex">
                <span className="w-6 opacity-30 select-none">3</span>
                <span className="text-primary ml-4">const</span> <span className="text-blue-300">complexity</span> = <span className="text-blue-400">calculateComplexity</span>(<span className="text-blue-300">code</span>);
              </div>
              <div className="flex">
                <span className="w-6 opacity-30 select-none">4</span>
                <span className="text-primary ml-4">return</span> {'{'}
              </div>
              <div className="flex">
                <span className="w-6 opacity-30 select-none">5</span>
                <span className="text-accent ml-8">score:</span> <span className="text-blue-300">complexity.score</span>,
              </div>
              <div className="flex">
                <span className="w-6 opacity-30 select-none">6</span>
                <span className="text-accent ml-8">issues:</span> <span className="text-blue-300">complexity.issues</span>,
              </div>
              <div className="flex">
                <span className="w-6 opacity-30 select-none">7</span>
                <span className="text-accent ml-8">suggestions:</span> <span className="text-blue-300">complexity.suggestions</span>
              </div>
              <div className="flex">
                <span className="w-6 opacity-30 select-none">8</span>
                <span className="ml-4">{'}'};</span>
              </div>
              <div className="flex">
                <span className="w-6 opacity-30 select-none">9</span>
                <span>{'}'}</span>
              </div>
            </div>
          </div>

          {/* Feature Pills */}
          <div className="flex flex-col gap-3 shrink-0">
            <div className="bg-surfaceElevated border border-borderSubtle p-3 rounded-xl flex items-center gap-4 pr-10 shadow-lg backdrop-blur-md">
              <div className="w-10 h-10 rounded-lg bg-primary/20 text-primary flex items-center justify-center">
                <Zap className="w-5 h-5 fill-primary/20" />
              </div>
              <div>
                <p className="text-sm font-semibold text-textPrimary">AI Analysis</p>
                <p className="text-[10px] text-textSecondary">Deep code understanding</p>
              </div>
            </div>
            <div className="bg-surfaceElevated border border-borderSubtle p-3 rounded-xl flex items-center gap-4 pr-10 shadow-lg backdrop-blur-md">
              <div className="w-10 h-10 rounded-lg bg-[#D946EF]/20 text-[#D946EF] flex items-center justify-center">
                <BarChart className="w-5 h-5" />
              </div>
              <div>
                <p className="text-sm font-semibold text-textPrimary">Complexity Metrics</p>
                <p className="text-[10px] text-textSecondary">Time, Space & Structure</p>
              </div>
            </div>
            <div className="bg-surfaceElevated border border-borderSubtle p-3 rounded-xl flex items-center gap-4 pr-10 shadow-lg backdrop-blur-md">
              <div className="w-10 h-10 rounded-lg bg-warning/20 text-warning flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 fill-warning/20" />
              </div>
              <div>
                <p className="text-sm font-semibold text-textPrimary">Smart Suggestions</p>
                <p className="text-[10px] text-textSecondary">Improve code quality</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard icon={Code2} iconBg="bg-blue-500/20" iconColor="text-blue-500" label="Total Analyses" value="128" trend="12%" chartData={MINI_CHART_GREEN} chartColor="#10B981" />
        <StatCard icon={Clock} iconBg="bg-orange-500/20" iconColor="text-orange-500" label="Avg Processing Time" value="1.2s" trend="32%" chartData={MINI_CHART_GREEN} chartColor="#10B981" />
        <StatCard icon={FileText} iconBg="bg-yellow-500/20" iconColor="text-yellow-500" label="Lines Analyzed" value="14.2k" trend="18%" chartData={MINI_CHART_YELLOW} chartColor="#F59E0B" />
        <StatCard icon={Shield} iconBg="bg-purple-500/20" iconColor="text-purple-500" label="Optimization Score" value="84%" trend="6%" chartData={MINI_CHART_PURPLE} chartColor="#8B5CF6" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Chart */}
        <div className="bg-surface p-6 rounded-2xl border border-borderSubtle">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="text-warning">
                <BarChart className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-textPrimary">Weekly Activity</h2>
                <p className="text-[11px] text-textSecondary">Code analyses over the last 7 days</p>
              </div>
            </div>
            <button className="flex items-center gap-2 text-xs font-medium text-textSecondary bg-secondaryBg border border-borderSubtle px-3 py-1.5 rounded-lg hover:text-textPrimary transition-colors">
              Last 7 days <ChevronDown className="w-3 h-3" />
            </button>
          </div>
          
          <div className="h-[220px] w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={MOCK_METRICS} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#FF7A59" />
                    <stop offset="100%" stopColor="#635BFF" />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                <XAxis 
                  dataKey="name" 
                  stroke="#71717A" 
                  tick={{ fill: '#71717A', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  dy={10}
                />
                <YAxis 
                  stroke="#71717A" 
                  tick={{ fill: '#71717A', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                  contentStyle={{ 
                    backgroundColor: '#1A1D27', 
                    borderColor: 'rgba(255,255,255,0.08)', 
                    color: '#F5F5F5', 
                    borderRadius: '8px',
                    fontSize: '12px',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.4)'
                  }}
                  itemStyle={{ color: '#FF7A59' }}
                />
                <Bar 
                  dataKey="analyses" 
                  fill="url(#barGradient)" 
                  radius={[4, 4, 0, 0]} 
                  barSize={32}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Complexity Distribution */}
        <div className="bg-surface p-6 rounded-2xl border border-borderSubtle flex flex-col">
          <div className="flex items-center gap-3 mb-6">
            <div className="text-[#D946EF]">
              <PieChart className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-textPrimary">Complexity Distribution</h2>
              <p className="text-[11px] text-textSecondary">Distribution of code complexity levels</p>
            </div>
          </div>
          
          <div className="flex-1 flex flex-col md:flex-row items-center justify-center md:justify-between px-2 md:px-8 gap-8 mt-4 md:mt-0">
            <div className="w-48 h-48 relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={COMPLEXITY_DISTRIBUTION}
                    cx="50%"
                    cy="50%"
                    innerRadius={65}
                    outerRadius={85}
                    paddingAngle={0}
                    dataKey="value"
                    stroke="none"
                    cornerRadius={0}
                  >
                    {COMPLEXITY_DISTRIBUTION.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1A1D27', 
                      borderColor: 'rgba(255,255,255,0.08)', 
                      color: '#F5F5F5', 
                      borderRadius: '8px',
                      fontSize: '12px',
                      boxShadow: '0 4px 20px rgba(0,0,0,0.4)'
                    }} 
                    itemStyle={{ color: '#F5F5F5' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              
              {/* Center Label */}
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-2xl font-bold text-textPrimary tracking-tight">128</span>
                <span className="text-[10px] text-textSecondary uppercase tracking-wider font-semibold mt-1">Analyses</span>
              </div>
            </div>
            
            <div className="flex flex-col gap-4">
              {COMPLEXITY_DISTRIBUTION.map((entry) => (
                <div key={entry.name} className="flex items-center justify-between w-40">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full shadow-glow" style={{ backgroundColor: entry.color }} />
                    <span className="text-xs font-medium text-textPrimary">{entry.name}</span>
                  </div>
                  <span className="text-xs text-textSecondary font-semibold">{entry.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Analyses */}
        <div className="bg-surface p-6 rounded-2xl border border-borderSubtle">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="text-textSecondary">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-textPrimary">Recent Analyses</h2>
                <p className="text-[11px] text-textSecondary">Your latest code analysis results</p>
              </div>
            </div>
            <button className="flex items-center gap-2 text-xs font-medium text-textSecondary hover:text-textPrimary transition-colors">
              View All <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-3">
            {[
              { file: 'example.js', lang: 'JS', langColor: 'text-yellow-400', bg: 'bg-yellow-400/10', time: '2 minutes ago', lines: '124 lines', comp: 'Medium', compColor: 'text-warning border-warning', score: 72, scoreColor: 'text-warning border-warning' },
              { file: 'auth.py', lang: 'PY', langColor: 'text-blue-400', bg: 'bg-blue-400/10', time: '1 hour ago', lines: '86 lines', comp: 'Low', compColor: 'text-success border-success', score: 88, scoreColor: 'text-success border-success' },
              { file: 'api.go', lang: 'GO', langColor: 'text-cyan-400', bg: 'bg-cyan-400/10', time: '3 hours ago', lines: '210 lines', comp: 'High', compColor: 'text-danger border-danger', score: 54, scoreColor: 'text-danger border-danger' },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-secondaryBg border border-borderSubtle hover:border-primary/30 transition-colors cursor-pointer group">
                <div className="flex items-center gap-2 md:gap-4 flex-1">
                  <div className={`w-10 h-10 shrink-0 rounded-lg ${item.bg} flex items-center justify-center`}>
                    <FileText className={`w-5 h-5 ${item.langColor}`} />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-semibold text-textPrimary truncate">{item.file}</span>
                      <span className={`text-[10px] shrink-0 font-bold px-1.5 py-0.5 rounded ${item.bg} ${item.langColor}`}>{item.lang}</span>
                    </div>
                    <div className="hidden sm:flex items-center gap-3 text-[11px] text-textSecondary font-medium">
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {item.time}</span>
                      <span className="flex items-center gap-1"><Code2 className="w-3 h-3" /> {item.lines}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 md:gap-6 shrink-0">
                  <span className={`text-[10px] font-bold uppercase tracking-wider px-2 md:px-3 py-1 rounded-full border ${item.compColor}`}>
                    {item.comp}
                  </span>
                  <div className={`w-9 h-9 rounded-full border-2 ${item.scoreColor} flex items-center justify-center text-xs font-bold`}>
                    {item.score}%
                  </div>
                  <ArrowRight className="w-4 h-4 text-textSecondary group-hover:text-primary transition-colors" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Supported Languages */}
        <div className="bg-surface p-6 rounded-2xl border border-borderSubtle">
          <div className="flex items-center gap-3 mb-6">
            <div className="text-textSecondary">
              <Code2 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-textPrimary">Supported Languages</h2>
              <p className="text-[11px] text-textSecondary">Analyze code in multiple programming languages</p>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {LANGS.map((lang, i) => (
              <div key={i} className="bg-secondaryBg border border-borderSubtle rounded-xl p-3 flex flex-col items-center justify-center gap-2 hover:border-primary/50 transition-colors group cursor-pointer h-20">
                <span className="text-xl font-bold transition-transform group-hover:scale-110" style={{ color: lang.color }}>
                  {lang.icon}
                </span>
                <span className="text-[10px] font-medium text-textSecondary group-hover:text-textPrimary transition-colors text-center leading-tight">
                  {lang.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

    </div>
  );
};