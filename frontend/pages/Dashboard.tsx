import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, Clock, FileCode, CheckCircle } from 'lucide-react';

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
  { name: 'Low', value: 45 },
  { name: 'Medium', value: 30 },
  { name: 'High', value: 25 },
];

const COLORS = ['#22c55e', '#eab308', '#ef4444'];

const StatCard = ({ icon: Icon, label, value, color }: any) => (
  <div className="bg-surface p-6 rounded-xl border border-gray-800 shadow-sm hover:border-gray-700 transition-colors">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-400">{label}</p>
        <h3 className="text-2xl font-bold mt-2 text-white">{value}</h3>
      </div>
      <div className={`p-3 rounded-lg bg-opacity-20 ${color}`}>
        <Icon className={`w-6 h-6 ${color.replace('bg-', 'text-')}`} />
      </div>
    </div>
  </div>
);

export const Dashboard: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto p-6 md:p-8 space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-gray-400">Welcome back! Here's an overview of your code analysis activity.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard icon={Activity} label="Total Analyses" value="128" color="bg-primary text-primary" />
        <StatCard icon={Clock} label="Avg Processing Time" value="1.2s" color="bg-accent text-accent" />
        <StatCard icon={FileCode} label="Lines Analyzed" value="14.2k" color="bg-warning text-warning" />
        <StatCard icon={CheckCircle} label="Optimization Score" value="84%" color="bg-success text-success" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Activity Chart */}
        <div className="bg-surface p-6 rounded-xl border border-gray-800">
          <h2 className="text-lg font-semibold mb-6">Weekly Activity</h2>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={MOCK_METRICS}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
                <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
                  cursor={{ fill: '#334155', opacity: 0.4 }}
                />
                <Bar dataKey="analyses" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Complexity Distribution */}
        <div className="bg-surface p-6 rounded-xl border border-gray-800">
          <h2 className="text-lg font-semibold mb-6">Complexity Distribution</h2>
          <div className="h-[300px] flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={COMPLEXITY_DISTRIBUTION}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {COMPLEXITY_DISTRIBUTION.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-6 mt-4">
            {COMPLEXITY_DISTRIBUTION.map((entry, index) => (
              <div key={entry.name} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index] }} />
                <span className="text-sm text-gray-400">{entry.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};