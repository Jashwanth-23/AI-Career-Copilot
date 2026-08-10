import React from "react";

const CircularMeter = ({
  score = 0,
  size = 180,
  strokeWidth = 14,
  label = "ATS Score",
  sublabel = "",
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clampedScore = Math.min(100, Math.max(0, score));
  const strokeDashoffset = circumference - (clampedScore / 100) * circumference;

  // Determine color based on score tier
  let gradientId = "scoreGradientIndigo";
  let strokeColor = "url(#scoreGradientIndigo)";
  let textColor = "text-indigo-400";

  if (clampedScore >= 80) {
    gradientId = "scoreGradientGreen";
    strokeColor = "url(#scoreGradientGreen)";
    textColor = "text-emerald-400";
  } else if (clampedScore >= 60) {
    gradientId = "scoreGradientAmber";
    strokeColor = "url(#scoreGradientAmber)";
    textColor = "text-amber-400";
  } else if (clampedScore < 50 && clampedScore > 0) {
    gradientId = "scoreGradientRose";
    strokeColor = "url(#scoreGradientRose)";
    textColor = "text-rose-400";
  }

  return (
    <div className="flex flex-col items-center justify-center relative">
      <svg width={size} height={size} className="transform -rotate-90">
        <defs>
          <linearGradient id="scoreGradientIndigo" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="100%" stopColor="#8b5cf6" />
          </linearGradient>
          <linearGradient id="scoreGradientGreen" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="100%" stopColor="#059669" />
          </linearGradient>
          <linearGradient id="scoreGradientAmber" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#f59e0b" />
            <stop offset="100%" stopColor="#d97706" />
          </linearGradient>
          <linearGradient id="scoreGradientRose" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#f43f5e" />
            <stop offset="100%" stopColor="#e11d48" />
          </linearGradient>
        </defs>

        {/* Background Track Circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#1e293b"
          strokeWidth={strokeWidth}
          fill="transparent"
        />

        {/* Progress Arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>

      {/* Inner Label Container */}
      <div className="absolute flex flex-col items-center justify-center text-center">
        <span className={`text-4xl font-extrabold tracking-tight ${textColor}`}>
          {clampedScore}
          <span className="text-xl text-slate-400 font-normal">%</span>
        </span>
        {label && <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mt-0.5">{label}</span>}
        {sublabel && <span className="text-[11px] text-slate-500">{sublabel}</span>}
      </div>
    </div>
  );
};

export default CircularMeter;
