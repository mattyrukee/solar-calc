"use client";

import clsx from "clsx";
import type { League } from "@/lib/api";

interface Props {
  leagues: League[];
  selected: number | null;
  onChange: (id: number | null) => void;
}

export default function LeagueFilter({ leagues, selected, onChange }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      <button
        onClick={() => onChange(null)}
        className={clsx(
          "px-4 py-1.5 rounded-full text-sm font-medium transition-colors",
          selected === null
            ? "bg-brand-600 text-white"
            : "bg-gray-100 text-gray-600 hover:bg-gray-200"
        )}
      >
        All Leagues
      </button>

      {leagues.map((league) => (
        <button
          key={league.id}
          onClick={() => onChange(league.id)}
          className={clsx(
            "px-4 py-1.5 rounded-full text-sm font-medium transition-colors",
            selected === league.id
              ? "bg-brand-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          )}
        >
          {league.short_name}
        </button>
      ))}
    </div>
  );
}
