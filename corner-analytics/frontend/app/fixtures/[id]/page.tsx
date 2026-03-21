import { format } from "date-fns";
import Link from "next/link";
import Image from "next/image";
import { api } from "@/lib/api";
import ConfidenceMeter from "@/components/ConfidenceMeter";
import CornerRangeChart from "@/components/CornerRangeChart";

interface Props {
  params: { id: string };
}

function TeamLogo({ team }: { team: { name: string; short_name: string | null; logo_url: string | null } }) {
  if (team.logo_url) {
    return (
      <Image src={team.logo_url} alt={team.name} width={64} height={64} className="object-contain" />
    );
  }
  return (
    <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center text-xl font-bold text-gray-400">
      {(team.short_name ?? team.name).slice(0, 3).toUpperCase()}
    </div>
  );
}

export default async function FixturePage({ params }: Props) {
  const fixtureId = parseInt(params.id);

  let fixture;
  try {
    // Fetch the fixture (includes prediction via the fixtures list endpoint if pre-loaded)
    const fixtures = await api.fixtures();
    fixture = fixtures.find((f) => f.id === fixtureId);
    if (!fixture) throw new Error("not found");
  } catch {
    return (
      <div className="text-center py-20 text-gray-400">
        <p className="text-4xl mb-4">404</p>
        <p>Fixture not found.</p>
        <Link href="/" className="text-brand-600 underline text-sm mt-2 inline-block">
          Back to fixtures
        </Link>
      </div>
    );
  }

  const { prediction } = fixture;

  return (
    <div className="max-w-2xl mx-auto">
      {/* Breadcrumb */}
      <Link href="/" className="text-sm text-gray-400 hover:text-gray-600 mb-6 inline-flex items-center gap-1">
        ← All Fixtures
      </Link>

      {/* Match header */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
            {fixture.league.name}
          </span>
          <span className="text-xs text-gray-400">
            {format(new Date(fixture.fixture_date), "EEEE d MMM yyyy · HH:mm")}
          </span>
        </div>

        <div className="flex items-center justify-around py-6">
          {/* Home */}
          <Link
            href={`/teams/${fixture.home_team.id}`}
            className="flex flex-col items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <TeamLogo team={fixture.home_team} />
            <span className="font-semibold text-gray-800 text-sm text-center">
              {fixture.home_team.name}
            </span>
            <span className="text-xs text-gray-400">Home</span>
          </Link>

          {/* Score / VS */}
          <div className="flex flex-col items-center">
            {fixture.status === "finished" ? (
              <span className="text-4xl font-black text-gray-800">
                {fixture.home_corners ?? "?"} – {fixture.away_corners ?? "?"}
                <span className="block text-xs text-gray-400 font-normal text-center mt-1">
                  Corners
                </span>
              </span>
            ) : (
              <span className="text-3xl font-light text-gray-300">VS</span>
            )}
          </div>

          {/* Away */}
          <Link
            href={`/teams/${fixture.away_team.id}`}
            className="flex flex-col items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <TeamLogo team={fixture.away_team} />
            <span className="font-semibold text-gray-800 text-sm text-center">
              {fixture.away_team.name}
            </span>
            <span className="text-xs text-gray-400">Away</span>
          </Link>
        </div>
      </div>

      {/* Prediction card */}
      {prediction ? (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-1">Corner Prediction</h2>
          <p className="text-sm text-gray-400 mb-5">
            Model: {prediction.model_version} · Generated{" "}
            {format(new Date(prediction.generated_at), "d MMM HH:mm")}
          </p>

          {/* Big number */}
          <div className="text-center mb-6">
            <p className="text-6xl font-black text-brand-600">
              {prediction.predicted_total % 1 === 0
                ? prediction.predicted_total
                : prediction.predicted_total.toFixed(1)}
            </p>
            <p className="text-sm text-gray-400 mt-1">predicted total corners</p>
          </div>

          <ConfidenceMeter score={prediction.confidence_score} size="lg" />

          <div className="mt-6">
            <CornerRangeChart
              prediction={prediction}
              homeName={fixture.home_team.name}
              awayName={fixture.away_team.name}
            />
          </div>
        </div>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-6 text-center text-yellow-700 text-sm mb-6">
          No prediction available for this fixture yet.
          <br />
          The model may not have enough historical data for these teams.
        </div>
      )}

      {/* Team corner history links */}
      <div className="grid grid-cols-2 gap-4">
        <Link
          href={`/teams/${fixture.home_team.id}`}
          className="bg-white rounded-2xl border border-gray-100 p-4 text-center hover:shadow-md transition-shadow"
        >
          <p className="text-xs text-gray-400 mb-1">View corner history</p>
          <p className="font-semibold text-gray-800">{fixture.home_team.name}</p>
        </Link>
        <Link
          href={`/teams/${fixture.away_team.id}`}
          className="bg-white rounded-2xl border border-gray-100 p-4 text-center hover:shadow-md transition-shadow"
        >
          <p className="text-xs text-gray-400 mb-1">View corner history</p>
          <p className="font-semibold text-gray-800">{fixture.away_team.name}</p>
        </Link>
      </div>
    </div>
  );
}
