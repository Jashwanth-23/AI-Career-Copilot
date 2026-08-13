import React from "react";
import { NavLink } from "react-router-dom";
import {
  DashboardIcon,
  UploadIcon,
  DocumentIcon,
  ChartIcon,
  TargetIcon,
  RoadmapIcon,
  BriefcaseIcon,
  SparklesIcon,
  MicrophoneIcon,
} from "./Icons";

const navItems = [
  { name: "Dashboard", path: "/dashboard", icon: DashboardIcon },
  { name: "My Resumes", path: "/resumes", icon: DocumentIcon },
  { name: "Upload Resume", path: "/upload", icon: UploadIcon },
  { name: "Resume Analysis", path: "/analysis", icon: DocumentIcon },
  { name: "ATS Score", path: "/ats", icon: ChartIcon },
  { name: "Skill Gap", path: "/skill-gap", icon: TargetIcon },
  { name: "Learning Roadmap", path: "/roadmap", icon: RoadmapIcon },
  { name: "Job Recommendations", path: "/jobs", icon: BriefcaseIcon },
  { name: "🎤 AI Mock Interview", path: "/mock-interview", icon: MicrophoneIcon },
];

const Sidebar = ({ isOpen, onClose }) => {
  return (
    <>
      {/* Mobile Drawer Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-surface-950/80 backdrop-blur-sm z-40 lg:hidden"
        ></div>
      )}

      <aside
        className={`fixed top-0 left-0 bottom-0 w-64 bg-surface-900 border-r border-slate-800/80 z-50 flex flex-col transition-transform duration-300 transform lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Sidebar Header Logo */}
        <div className="h-20 flex items-center px-6 border-b border-slate-800/80">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 p-0.5 shadow-glow flex items-center justify-center">
              <SparklesIcon className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-white tracking-tight">
              AI Copilot
            </span>
          </div>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 py-6 px-4 space-y-1.5 overflow-y-auto">
          <div className="px-3 mb-2 text-[11px] font-bold uppercase tracking-wider text-slate-500">
            Platform Menu
          </div>
          {navItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3.5 py-3 rounded-xl text-sm font-semibold transition-all duration-200 ${
                    isActive
                      ? "bg-gradient-to-r from-indigo-600/90 to-purple-600/90 text-white shadow-glow"
                      : "text-slate-400 hover:text-white hover:bg-slate-800/60"
                  }`
                }
              >
                <IconComponent className="w-5 h-5 flex-shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </div>

        {/* Sidebar Footer Badge */}
        <div className="p-4 border-t border-slate-800/80">
          <div className="glass-panel p-3.5 rounded-xl text-xs space-y-1 bg-indigo-950/20 border-indigo-500/20">
            <div className="flex items-center space-x-2 text-indigo-300 font-bold">
              <SparklesIcon className="w-4 h-4 text-indigo-400" />
              <span>Gemini AI Active</span>
            </div>
            <p className="text-slate-400 text-[11px]">
              Instant resume parsing, ATS scoring & roadmaps enabled.
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
