import Link from "next/link";
import Image from "next/image";
import { format } from "date-fns";
import clsx from "clsx";
import type { Fixture } from "@/lib/api";
import ConfidenceMeter from "./ConfidenceMeter";

interface Props {
  fixture: Fixture;
}

function CornerBadge({ low, high, total }: { low: number; high: number; total: number }) {
  return (
    <div className="flex flex-col items-center">
      <span className="text-xs text-gray-500 uppercase tracking-wide mb-0.5">
        Predicted Corners
      </span>
      <span className="text-2xl font-bold text-brand-600">
        {total % 1 === 0 ? total : total.toFixed(1)}
      </span>
      <span className="text-xs text-gray-400 mt-0.5">
        range {low}–{high}
      </span>
    </div>
  );
}

function TeamLogo({ team }: { team: Fixture["home_team"] }) {
  if (team.logo_url) {
    return (
      <Image
        src={team.logo_url}
        alt={team.name}
        width={36}
        height={36}
        className="object-contain"
      />
    );
  }
  return (
    <div className="w-9 h-9 rounded-full bg-gray-200 flex items-center justify-center text-xs font-bold text-gray-500">
      {(team.short_name ?? team.name).slice(0, 3).toUpperCase()}
    </div>
  );
}

export default function MatchCard({ fixture }: Props) {
  const { prediction } = fixture;
  const kickoff = format(new Date(fixture.fixture_date), "HH:mm");

  return (
    <Link href={`/fixtures/${fixture.id}`} className="block">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow cursor-pointer">
        {/* League + time header */}
        <div className="flex justify-between items-center mb-4">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
            {fixture.league.short_name}
          </span>
          <span className="text-xs text-gray-400">{kickoff}</span>
        </div>

        {/* Teams row */}
        <div className="flex items-center justify-between gap-3">
          {/* Home team */}
          <div className="flex flex-col items-center gap-1.5 flex-1 min-w-0">
            <TeamLogo team={fixture.home_team} />
            <span className="text-xs font-medium text-gray-700 text-center truncate w-full">
              {fixture.home_team.short_name ?? fixture.home_team.name}
            </span>
          </div>

          {/* Centre: prediction or VS */}
          <div className="flex flex-col items-center shrink-0 px-3">
            {prediction ? (
              <CornerBadge
                low={prediction.low_bound}
                high={prediction.high_bound}
                total={prediction.predicted_total}
              />
            ) : (
              <span className="text-gray-300 text-xl font-light">VS</span>
            )}
          </div>

          {/* Away team */}
          <div className="flex flex-col items-center gap-1.5 flex-1 min-w-0">
            <TeamLogo team={fixture.away_team} />
            <span className="text-xs font-medium text-gray-700 text-center truncate w-full">
              {fixture.away_team.short_name ?? fixture.away_team.name}
            </span>
          </div>
        </div>

        {/* Confidence bar */}
        {prediction && (
          <div className="mt-4 pt-4 border-t border-gray-50">
            <ConfidenceMeter score={prediction.confidence_score} size="sm" />
          </div>
        )}

        {!prediction && (
          <p className="mt-3 text-center text-xs text-gray-400">
            Prediction not yet available
          </p>
        )}
      </div>
    </Link>
  );
}
