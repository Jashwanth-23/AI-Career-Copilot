import React from "react";
import { Link } from "react-router-dom";
import PublicNavbar from "../components/common/PublicNavbar";
import {
  SparklesIcon,
  DocumentIcon,
  ChartIcon,
  TargetIcon,
  RoadmapIcon,
  BriefcaseIcon,
  CheckIcon,
  ChevronRightIcon,
} from "../components/common/Icons";

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-surface-950 text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      <PublicNavbar />

      {/* Hero Section */}
      <section className="relative pt-16 pb-24 lg:pt-24 lg:pb-32 overflow-hidden">
        {/* Glowing Background Radial Blobs */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-600/20 rounded-full blur-[140px] pointer-events-none"></div>
        <div className="absolute top-1/3 right-10 w-[400px] h-[400px] bg-purple-600/15 rounded-full blur-[120px] pointer-events-none"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full glass-panel border-indigo-500/30 text-indigo-300 text-xs font-semibold uppercase tracking-wider mb-8 shadow-glow">
            <SparklesIcon className="w-4 h-4 text-indigo-400" />
            <span>Next-Gen AI Career Acceleration Platform</span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight max-w-4xl mx-auto leading-tight text-white">
            Supercharge Your Tech Career with <span className="text-gradient">AI Career Copilot</span>
          </h1>

          {/* Subtitle */}
          <p className="mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto font-normal leading-relaxed">
            Upload your resume, unlock deep ATS score metrics, identify critical skill gaps, get personalized weekly learning roadmaps, and land top-paying tech roles.
          </p>

          {/* CTA Buttons */}
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-600 to-indigo-600 text-white font-bold text-base hover:shadow-glow-lg transition-all duration-300 transform hover:-translate-y-1 flex items-center justify-center space-x-2"
            >
              <span>Analyze Your Resume Now</span>
              <ChevronRightIcon className="w-5 h-5" />
            </Link>
            <Link
              to="/login"
              className="w-full sm:w-auto px-8 py-4 rounded-xl glass-panel text-slate-200 font-semibold text-base hover:bg-slate-800/80 transition-all border border-slate-700/60"
            >
              Sign In to Dashboard
            </Link>
          </div>

          {/* SaaS Preview Mockup */}
          <div className="mt-16 relative max-w-5xl mx-auto">
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-600 to-cyan-400 rounded-3xl blur-lg opacity-40 animate-pulse-slow"></div>
            <div className="relative glass-panel rounded-2xl p-6 sm:p-8 border border-slate-700/80 text-left shadow-2xl overflow-hidden">
              {/* Fake Window Header */}
              <div className="flex items-center justify-between pb-6 mb-6 border-b border-slate-800">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-amber-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80"></div>
                </div>
                <div className="text-xs text-slate-400 font-mono">dashboard.ai-career-copilot.app</div>
                <div className="w-12"></div>
              </div>

              {/* Grid Preview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-panel p-5 rounded-xl border border-indigo-500/20 bg-indigo-950/20">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-semibold text-slate-400">ATS Score</span>
                    <ChartIcon className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="text-3xl font-black text-emerald-400">88%</div>
                  <p className="text-xs text-slate-400 mt-1">High ATS compatibility for Senior Full Stack Role</p>
                </div>

                <div className="glass-panel p-5 rounded-xl border border-purple-500/20 bg-purple-950/20">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-semibold text-slate-400">Skill Gap</span>
                    <TargetIcon className="w-4 h-4 text-purple-400" />
                  </div>
                  <div className="text-3xl font-black text-purple-300">3 Missing</div>
                  <p className="text-xs text-slate-400 mt-1">Docker, GraphQL, System Architecture</p>
                </div>

                <div className="glass-panel p-5 rounded-xl border border-cyan-500/20 bg-cyan-950/20">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-semibold text-slate-400">Target Match</span>
                    <BriefcaseIcon className="w-4 h-4 text-cyan-400" />
                  </div>
                  <div className="text-3xl font-black text-cyan-300">92%</div>
                  <p className="text-xs text-slate-400 mt-1">10 tech roles analyzed & estimated</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid Section */}
      <section id="features" className="py-20 bg-surface-900/60 border-t border-b border-slate-800/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-indigo-400 mb-3">Powerful Capabilities</h2>
            <p className="text-3xl sm:text-4xl font-extrabold text-white">Everything You Need to Land Your Dream Tech Job</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="glass-panel p-8 rounded-2xl glass-panel-hover">
              <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mb-6 text-indigo-400">
                <DocumentIcon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">AI Resume Parsing</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Extract structured JSON fields (skills, experience, projects, education) from PDF and DOCX documents automatically using Gemini AI.
              </p>
            </div>

            <div className="glass-panel p-8 rounded-2xl glass-panel-hover">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center mb-6 text-purple-400">
                <ChartIcon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">ATS Score Engine</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Get an instant circular score meter breakdown, strengths, weaknesses, and concrete actionable suggestions to pass recruiter screening algorithms.
              </p>
            </div>

            <div className="glass-panel p-8 rounded-2xl glass-panel-hover">
              <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mb-6 text-cyan-400">
                <TargetIcon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Skill Gap Analysis</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Compare your current skills against industry standard job role taxonomies to uncover matched vs missing technologies.
              </p>
            </div>

            <div className="glass-panel p-8 rounded-2xl glass-panel-hover">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mb-6 text-emerald-400">
                <RoadmapIcon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Personalized Roadmap</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Follow step-by-step multi-week timeline modules with curated documentation links, mini-projects, and milestone achievements.
              </p>
            </div>

            <div className="glass-panel p-8 rounded-2xl glass-panel-hover">
              <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mb-6 text-amber-400">
                <BriefcaseIcon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Job Recommendations</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Discover matching job titles with calculated suitability match %, salary ranges, strengths alignment, and career advice.
              </p>
            </div>

            <div className="glass-panel p-8 rounded-2xl glass-panel-hover">
              <div className="w-12 h-12 rounded-xl bg-pink-500/10 border border-pink-500/30 flex items-center justify-center mb-6 text-pink-400">
                <SparklesIcon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Gemini Intelligence</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Powered by state-of-the-art LLM prompts tailored specifically for technical candidate resume optimization.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 relative overflow-hidden">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <div className="glass-panel p-10 sm:p-14 rounded-3xl border border-indigo-500/30 shadow-glow">
            <h2 className="text-3xl sm:text-5xl font-black text-white mb-4">Ready to Elevate Your Resume?</h2>
            <p className="text-slate-300 text-base sm:text-lg max-w-xl mx-auto mb-8">
              Join thousands of developers using AI Career Copilot to optimize their application materials.
            </p>
            <Link
              to="/register"
              className="inline-flex items-center space-x-2 px-8 py-4 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-base hover:shadow-glow-lg transition-all transform hover:-translate-y-1"
            >
              <span>Create Free Account</span>
              <ChevronRightIcon className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-8 border-t border-slate-800 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4">
          <p>© {new Date().getFullYear()} AI Career Copilot. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
