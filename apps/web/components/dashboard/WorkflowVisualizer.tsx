'use client';

import React, { useState } from 'react';
import { CheckCircle2, Circle, Loader2, AlertCircle, ChevronUp, Clock } from 'lucide-react';

interface AgentState {
  status: string;
  done: boolean;
  error: boolean;
  data: any;
  elapsed: number;
}

interface WorkflowVisualizerProps {
  agents: Record<string, AgentState>;
}

export default function WorkflowVisualizer({ agents }: WorkflowVisualizerProps) {
  const [expandedLog, setExpandedLog] = useState<string | null>(null);

  // Define the workflow order and expected times (in seconds)
  const steps = [
    { key: 'cad', label: 'CAD', est: 12 },
    { key: 'physics', label: 'Physics', est: 18 },
    { key: 'business', label: 'Business', est: 8 },
    { key: 'research', label: 'Research', est: 10 },
    { key: 'patent', label: 'Patent', est: 15 },
    { key: 'report', label: 'Report', est: 5 },
  ];

  return (
    <div className="w-full flex flex-col gap-4">
      {/* Horizontal Stepper */}
      <div className="flex items-center justify-between w-full overflow-x-auto pb-4 pt-2 scrollbar-hide px-2">
        {steps.map((step, index) => {
          const state = agents[step.key];
          const isDone = state?.done && !state?.error;
          const isError = state?.error;
          const isRunning = !state?.done && !state?.error && state?.status !== 'Queued' && !!state?.status;
          
          let Icon = Circle;
          let iconColor = 'text-slate-300';
          let bgColor = 'bg-slate-50';
          let borderColor = 'border-slate-200';
          
          if (isDone) {
            Icon = CheckCircle2;
            iconColor = 'text-emerald-600';
            bgColor = 'bg-emerald-50';
            borderColor = 'border-emerald-200';
          } else if (isError) {
            Icon = AlertCircle;
            iconColor = 'text-red-600';
            bgColor = 'bg-red-50';
            borderColor = 'border-red-200';
          } else if (isRunning) {
            Icon = Loader2;
            iconColor = 'text-blue-600 animate-spin';
            bgColor = 'bg-blue-50';
            borderColor = 'border-blue-300';
          }

          return (
            <React.Fragment key={step.key}>
              <div 
                className="flex flex-col items-center relative cursor-pointer min-w-[64px]"
                onClick={() => setExpandedLog(expandedLog === step.key ? null : step.key)}
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${bgColor} ${borderColor} ${isRunning ? 'ring-4 ring-blue-100 shadow-lg shadow-blue-100' : ''} transition-all duration-300 z-10 bg-white`}>
                  <Icon className={`w-5 h-5 ${iconColor}`} />
                </div>
                <span className={`mt-3 text-[11px] font-bold ${isRunning ? 'text-blue-700' : isDone ? 'text-emerald-700' : 'text-slate-500'} uppercase tracking-wider`}>
                  {step.label}
                </span>
                
                {/* Time badge */}
                {isRunning && (
                  <span className="absolute -bottom-6 flex items-center gap-1 text-[10px] font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-100 whitespace-nowrap">
                    <Clock className="w-3 h-3" />
                    ~{Math.max(0, step.est - Math.floor(state?.elapsed || 0))}s
                  </span>
                )}
                {isDone && (
                  <span className="absolute -bottom-6 flex items-center gap-1 text-[10px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100 whitespace-nowrap">
                    {state?.elapsed?.toFixed(1)}s
                  </span>
                )}
              </div>
              
              {/* Connector line */}
              {index < steps.length - 1 && (
                <div className="flex-1 h-[2px] mx-1 -mt-6 bg-slate-100 relative min-w-[20px]">
                  <div 
                    className="absolute inset-0 bg-emerald-400 transition-all duration-700 ease-in-out" 
                    style={{ width: isDone ? '100%' : '0%' }}
                  />
                  {isRunning && (
                    <div className="absolute inset-0 bg-blue-400 opacity-50 animate-pulse w-full" />
                  )}
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Streaming Logs Panel */}
      {expandedLog && (
        <div className="mt-6 bg-slate-900 rounded-xl border border-slate-700 overflow-hidden animate-in slide-in-from-top-2 duration-200">
          <div className="flex items-center justify-between px-4 py-3 bg-slate-800 border-b border-slate-700">
            <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              {steps.find(s => s.key === expandedLog)?.label} LIVE LOGS
            </span>
            <button onClick={() => setExpandedLog(null)} className="text-slate-400 hover:text-white transition-colors">
              <ChevronUp className="w-4 h-4" />
            </button>
          </div>
          <div className="p-4 max-h-[200px] overflow-y-auto font-mono text-xs text-green-400 whitespace-pre-wrap leading-relaxed bg-[#0A0F1C]">
            {agents[expandedLog]?.status ? (
              <div className="flex flex-col gap-1.5 opacity-90">
                <span className="text-slate-500">[{new Date().toISOString().split('T')[1].slice(0,-1)}] [sys] initializing container...</span>
                <span>[{new Date().toISOString().split('T')[1].slice(0,-1)}] [exec] {agents[expandedLog].status}</span>
                {agents[expandedLog].done && <span className="text-emerald-400 mt-2">[{new Date().toISOString().split('T')[1].slice(0,-1)}] [ok] process finished successfully in {agents[expandedLog].elapsed?.toFixed(2)}s</span>}
                {agents[expandedLog].error && <span className="text-red-400 mt-2">[{new Date().toISOString().split('T')[1].slice(0,-1)}] [err] process failed with error code 1</span>}
              </div>
            ) : (
              <span className="text-slate-500">Waiting for process to start...</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
