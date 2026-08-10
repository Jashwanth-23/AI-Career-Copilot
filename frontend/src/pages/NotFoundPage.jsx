import React from "react";
import { Link } from "react-router-dom";

const NotFoundPage = () => {
  return (
    <div className="min-h-screen bg-surface-950 flex flex-col items-center justify-center p-6 text-center">
      <div className="glass-panel p-10 rounded-3xl max-w-md w-full border border-slate-800 space-y-4 shadow-2xl">
        <span className="text-6xl font-black text-gradient">404</span>
        <h1 className="text-2xl font-bold text-white">Page Not Found</h1>
        <p className="text-slate-400 text-sm">
          The route you requested does not exist or has been moved.
        </p>
        <Link
          to="/dashboard"
          className="inline-block px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-sm hover:shadow-glow transition-all"
        >
          Return to Dashboard
        </Link>
      </div>
    </div>
  );
};

export default NotFoundPage;
