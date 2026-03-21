"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { Prediction } from "@/lib/api";

interface Props {
  prediction: Prediction;
  homeName: string;
  awayName: string;
}

export default function CornerRangeChart({ prediction, homeName, awayName }: Props) {
  const { predicted_total, low_bound, high_bound } = prediction;

  // Build a bar representing the CI range (low → high) and the point estimate
  const data = [
    {
      label: "Corner Prediction",
      low: low_bound,
      range: high_bound - low_bound,
      predicted: predicted_total,
    },
  ];

  return (
    <div className="w-full">
      <p className="text-sm text-gray-500 mb-3">
        90% confidence interval: <strong>{low_bound}</strong> – <strong>{high_bound}</strong> total corners
      </p>

      {/* Horizontal range visual */}
      <div className="relative h-14 bg-gray-100 rounded-xl overflow-hidden">
        {/* CI band */}
        <div
          className="absolute top-0 h-full bg-brand-100 border-l-2 border-r-2 border-brand-400"
          style={{
            left: `${(low_bound / (high_bound + 4)) * 100}%`,
            width: `${((high_bound - low_bound) / (high_bound + 4)) * 100}%`,
          }}
        />
        {/* Point estimate marker */}
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-4 h-4 bg-brand-600 rounded-full border-2 border-white shadow"
          style={{
            left: `${(predicted_total / (high_bound + 4)) * 100}%`,
          }}
        />
        {/* Labels */}
        <div
          className="absolute bottom-1 text-[10px] text-brand-700 font-medium -translate-x-1/2"
          style={{ left: `${(low_bound / (high_bound + 4)) * 100}%` }}
        >
          {low_bound}
        </div>
        <div
          className="absolute bottom-1 text-[10px] text-brand-700 font-medium -translate-x-1/2"
          style={{ left: `${(high_bound / (high_bound + 4)) * 100}%` }}
        >
          {high_bound}
        </div>
        <div
          className="absolute top-1 text-[10px] text-brand-700 font-bold -translate-x-1/2"
          style={{ left: `${(predicted_total / (high_bound + 4)) * 100}%` }}
        >
          {predicted_total % 1 === 0 ? predicted_total : predicted_total.toFixed(1)}
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3 mt-5">
        <StatBox label="Home avg corners" value={prediction.home_avg_corners_for?.toFixed(1) ?? "—"} />
        <StatBox label="League avg total" value={prediction.league_avg_corners?.toFixed(1) ?? "—"} />
        <StatBox label="Away avg corners" value={prediction.away_avg_corners_for?.toFixed(1) ?? "—"} />
        <StatBox label="H2H avg total" value={prediction.h2h_avg_corners?.toFixed(1) ?? "—"} />
        <StatBox label="CI width" value={`${high_bound - low_bound} corners`} />
        <StatBox label="Model" value={prediction.model_version} />
      </div>
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-xl p-3 text-center">
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className="text-sm font-bold text-gray-700">{value}</p>
    </div>
  );
}
