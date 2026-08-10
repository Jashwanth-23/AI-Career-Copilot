import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { useResume } from "../../context/ResumeContext";
import { UserIcon, LogoutIcon, DocumentIcon, SparklesIcon } from "./Icons";

const Topbar = ({ onToggleSidebar }) => {
  const { user, logout } = useAuth();
  const { activeResume } = useResume();

  return (
    <header className="sticky top-0 z-30 h-20 bg-surface-900/90 backdrop-blur-md border-b border-slate-800/80 px-4 sm:px-8 flex items-center justify-between">
      {/* Left: Mobile Toggle & Status */}
      <div className="flex items-center space-x-4">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        {/* Active Resume Status Badge */}
        {activeResume ? (
          <Link
            to="/resumes"
            className="hidden sm:flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-indigo-950/50 hover:bg-indigo-900/60 border border-indigo-500/30 text-xs text-indigo-300 transition-all hover:scale-[1.02]"
            title="Manage My Resumes"
          >
            <DocumentIcon className="w-3.5 h-3.5 text-indigo-400" />
            <span className="font-medium truncate max-w-[200px]">{activeResume.original_filename}</span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          </Link>
        ) : (
          <Link
            to="/resumes"
            className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-800/60 hover:bg-slate-800 border border-slate-700/50 text-xs text-slate-400 transition-all"
          >
            <span>No Active Resume</span>
          </Link>
        )}
      </div>

      {/* Right: User Profile & Actions */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-3 px-3.5 py-1.5 rounded-xl bg-slate-800/50 border border-slate-700/40">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs shadow-sm">
            {user?.name ? user.name.charAt(0).toUpperCase() : <UserIcon className="w-4 h-4" />}
          </div>
          <div className="hidden md:block text-left text-xs">
            <div className="font-semibold text-white leading-tight">{user?.name || "User"}</div>
            <div className="text-slate-400 leading-tight">{user?.email}</div>
          </div>
        </div>

        <button
          onClick={logout}
          title="Logout"
          className="p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/50 text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 hover:border-rose-500/30 transition-all duration-200"
        >
          <LogoutIcon className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};

export default Topbar;
