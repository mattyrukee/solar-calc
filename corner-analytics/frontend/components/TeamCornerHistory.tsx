"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { format } from "date-fns";
import type { CornerHistoryEntry } from "@/lib/api";

interface Props {
  history: CornerHistoryEntry[];
  teamName: string;
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ value: number; name: string }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-lg p-3 text-sm">
      <p className="font-semibold text-gray-700 mb-1">{label}</p>
      {payload.map((p) => (
        <p key={p.name} className="text-gray-600">
          {p.name}: <span className="font-bold text-brand-600">{p.value}</span>
        </p>
      ))}
    </div>
  );
}

export default function TeamCornerHistory({ history, teamName }: Props) {
  if (!history.length) {
    return (
      <p className="text-gray-400 text-sm text-center py-8">
        No corner history available yet.
      </p>
    );
  }

  // Reverse so oldest is on the left
  const data = [...history].reverse().map((entry) => ({
    date: format(new Date(entry.fixture_date), "d MMM"),
    opponent: entry.opponent,
    venue: entry.is_home ? "H" : "A",
    cornersFor: entry.corners_for ?? 0,
    cornersAgainst: entry.corners_against ?? 0,
    total: entry.total_corners ?? 0,
  }));

  const avgFor = data.reduce((s, d) => s + d.cornersFor, 0) / data.length;

  return (
    <div className="w-full">
      {/* Summary chips */}
      <div className="flex gap-3 mb-5 flex-wrap">
        <Chip label="Avg corners for" value={avgFor.toFixed(1)} color="brand" />
        <Chip
          label="Home avg"
          value={(
            data.filter((d) => d.venue === "H").reduce((s, d) => s + d.cornersFor, 0) /
              (data.filter((d) => d.venue === "H").length || 1)
          ).toFixed(1)}
          color="blue"
        />
        <Chip
          label="Away avg"
          value={(
            data.filter((d) => d.venue === "A").reduce((s, d) => s + d.cornersFor, 0) /
              (data.filter((d) => d.venue === "A").length || 1)
          ).toFixed(1)}
          color="purple"
        />
      </div>

      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data} margin={{ top: 5, right: 10, bottom: 5, left: -10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#9ca3af" }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "#9ca3af" }}
            tickLine={false}
            axisLine={false}
            domain={[0, "dataMax + 2"]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: 12, color: "#6b7280" }}
            formatter={(value) =>
              value === "cornersFor" ? "Corners Won" : "Corners Conceded"
            }
          />
          <ReferenceLine
            y={avgFor}
            stroke="#22c55e"
            strokeDasharray="4 4"
            strokeWidth={1.5}
            label={{ value: `Avg ${avgFor.toFixed(1)}`, fontSize: 10, fill: "#16a34a" }}
          />
          <Line
            type="monotone"
            dataKey="cornersFor"
            name="cornersFor"
            stroke="#22c55e"
            strokeWidth={2.5}
            dot={{ r: 4, fill: "#22c55e", strokeWidth: 0 }}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            dataKey="cornersAgainst"
            name="cornersAgainst"
            stroke="#94a3b8"
            strokeWidth={1.5}
            strokeDasharray="4 4"
            dot={{ r: 3, fill: "#94a3b8", strokeWidth: 0 }}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Recent matches table */}
      <div className="mt-5 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-400 text-xs uppercase tracking-wide border-b border-gray-100">
              <th className="text-left py-2 pr-3">Date</th>
              <th className="text-left py-2 pr-3">Opponent</th>
              <th className="text-center py-2 pr-3">H/A</th>
              <th className="text-center py-2 pr-3">Won</th>
              <th className="text-center py-2">Conceded</th>
            </tr>
          </thead>
          <tbody>
            {[...data].reverse().slice(0, 10).map((row, i) => (
              <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                <td className="py-2 pr-3 text-gray-500">{row.date}</td>
                <td className="py-2 pr-3 text-gray-700 font-medium">{row.opponent}</td>
                <td className="py-2 pr-3 text-center">
                  <span
                    className={`text-xs font-bold px-1.5 py-0.5 rounded ${
                      row.venue === "H"
                        ? "bg-brand-100 text-brand-700"
                        : "bg-gray-100 text-gray-500"
                    }`}
                  >
                    {row.venue}
                  </span>
                </td>
                <td className="py-2 pr-3 text-center font-bold text-brand-600">
                  {row.cornersFor}
                </td>
                <td className="py-2 text-center text-gray-400">{row.cornersAgainst}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Chip({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: "brand" | "blue" | "purple";
}) {
  const styles = {
    brand: "bg-brand-50 text-brand-700 border-brand-200",
    blue: "bg-blue-50 text-blue-700 border-blue-200",
    purple: "bg-purple-50 text-purple-700 border-purple-200",
  };
  return (
    <div className={`border rounded-xl px-3 py-2 text-center ${styles[color]}`}>
      <p className="text-xs opacity-70">{label}</p>
      <p className="text-lg font-bold">{value}</p>
    </div>
  );
}
