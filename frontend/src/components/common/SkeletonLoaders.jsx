import React from "react";

export const CardSkeleton = () => (
  <div className="glass-panel p-6 rounded-2xl animate-pulse space-y-4">
    <div className="flex items-center space-x-4">
      <div className="w-12 h-12 rounded-xl bg-slate-800"></div>
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-slate-800 rounded w-1/3"></div>
        <div className="h-3 bg-slate-800/60 rounded w-1/2"></div>
      </div>
    </div>
    <div className="h-20 bg-slate-800/40 rounded-xl"></div>
    <div className="flex space-x-2">
      <div className="h-6 bg-slate-800 rounded-full w-16"></div>
      <div className="h-6 bg-slate-800 rounded-full w-20"></div>
      <div className="h-6 bg-slate-800 rounded-full w-24"></div>
    </div>
  </div>
);

export const MeterSkeleton = () => (
  <div className="glass-panel p-8 rounded-2xl animate-pulse flex flex-col items-center justify-center space-y-4">
    <div className="w-40 h-40 rounded-full border-8 border-slate-800 bg-slate-900 flex items-center justify-center">
      <div className="h-8 w-16 bg-slate-800 rounded"></div>
    </div>
    <div className="h-5 bg-slate-800 rounded w-36"></div>
    <div className="h-3 bg-slate-800/60 rounded w-48"></div>
  </div>
);

export const TimelineSkeleton = () => (
  <div className="space-y-6 animate-pulse">
    {[1, 2, 3].map((idx) => (
      <div key={idx} className="glass-panel p-6 rounded-2xl flex space-x-4">
        <div className="w-10 h-10 rounded-full bg-slate-800 flex-shrink-0"></div>
        <div className="flex-1 space-y-3">
          <div className="h-4 bg-slate-800 rounded w-1/4"></div>
          <div className="h-3 bg-slate-800/60 rounded w-3/4"></div>
          <div className="h-16 bg-slate-800/30 rounded-xl"></div>
        </div>
      </div>
    ))}
  </div>
);

export const TableSkeleton = () => (
  <div className="glass-panel rounded-2xl p-4 animate-pulse space-y-3">
    <div className="h-8 bg-slate-800 rounded w-full"></div>
    <div className="h-12 bg-slate-800/50 rounded w-full"></div>
    <div className="h-12 bg-slate-800/50 rounded w-full"></div>
    <div className="h-12 bg-slate-800/50 rounded w-full"></div>
  </div>
);
