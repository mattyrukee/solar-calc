import clsx from "clsx";

interface Props {
  score: number; // 0.0 – 1.0
  size?: "sm" | "md" | "lg";
}

function confidenceLabel(score: number): string {
  if (score >= 0.90) return "Very High";
  if (score >= 0.80) return "High";
  if (score >= 0.70) return "Moderate";
  return "Low";
}

function confidenceColor(score: number): string {
  if (score >= 0.90) return "bg-brand-500";
  if (score >= 0.80) return "bg-blue-500";
  if (score >= 0.70) return "bg-yellow-400";
  return "bg-red-400";
}

export default function ConfidenceMeter({ score, size = "md" }: Props) {
  const pct = Math.round(score * 100);
  const label = confidenceLabel(score);
  const color = confidenceColor(score);

  const barHeight = size === "sm" ? "h-1.5" : size === "lg" ? "h-3" : "h-2";
  const textSize = size === "sm" ? "text-xs" : size === "lg" ? "text-base" : "text-sm";

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-1">
        <span className={clsx("font-medium text-gray-600", textSize)}>
          Confidence
        </span>
        <span className={clsx("font-bold", textSize, score >= 0.90 ? "text-brand-600" : "text-gray-700")}>
          {pct}% — {label}
        </span>
      </div>
      <div className={clsx("w-full bg-gray-200 rounded-full", barHeight)}>
        <div
          className={clsx("rounded-full transition-all duration-500", barHeight, color)}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
