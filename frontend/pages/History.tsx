import React, { useEffect, useState } from 'react';
import { AnalysisResult } from '../types';
import { Clock, Search, ChevronRight, FileCode } from 'lucide-react';

export const History: React.FC = () => {
  const [history, setHistory] = useState<AnalysisResult[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const data = localStorage.getItem('analysis_history');
    if (data) {
      try {
        setHistory(JSON.parse(data));
      } catch (e) {
        console.error('Failed to parse history', e);
      }
    }
  }, []);

  const filteredHistory = history.filter(item => 
    item.fileName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.language.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto p-6 md:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Analysis History</h1>
          <p className="text-gray-400">Review your past code inspections.</p>
        </div>
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-4 h-4" />
          <input
            type="text"
            placeholder="Search files..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-surface border border-gray-800 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-primary text-white placeholder-gray-600"
          />
        </div>
      </div>

      <div className="bg-surface rounded-xl border border-gray-800 overflow-hidden">
        {filteredHistory.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No history found. Run an analysis to get started!</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-800 bg-gray-900/50">
                  <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">File / Date</th>
                  <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Complexity</th>
                  <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Score</th>
                  <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Language</th>
                  <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Metrics</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {filteredHistory.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-800/50 transition-colors group cursor-default">
                    <td className="p-4">
                      <div className="flex items-center">
                        <div className="bg-primary/10 p-2 rounded mr-3">
                           <FileCode className="w-4 h-4 text-primary" />
                        </div>
                        <div>
                          <div className="font-medium text-white">{item.fileName}</div>
                          <div className="text-xs text-gray-500">{new Date(item.timestamp).toLocaleDateString()}</div>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                        ${item.complexityLevel === 'High' ? 'bg-red-500/10 text-red-400' : 
                          item.complexityLevel === 'Medium' ? 'bg-yellow-500/10 text-yellow-400' : 
                          'bg-green-500/10 text-green-400'}`}>
                        {item.complexityLevel}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center">
                        <span className="font-mono font-medium text-gray-300">{item.score}</span>
                        <span className="text-gray-600 text-xs ml-1">/100</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="text-gray-400 capitalize">{item.language}</span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                         <span>LO: {item.timeComplexity}</span>
                         <span>LOC: {item.metrics.linesOfCode}</span>
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