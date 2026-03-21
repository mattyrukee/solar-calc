import Link from "next/link";
import Image from "next/image";
import { api } from "@/lib/api";
import TeamCornerHistory from "@/components/TeamCornerHistory";

interface Props {
  params: { id: string };
}

export default async function TeamPage({ params }: Props) {
  const teamId = parseInt(params.id);

  let team;
  let history;

  try {
    [team, history] = await Promise.all([
      api.team(teamId),
      api.cornerHistory(teamId, 20),
    ]);
  } catch {
    return (
      <div className="text-center py-20 text-gray-400">
        <p className="text-4xl mb-4">404</p>
        <p>Team not found.</p>
        <Link href="/" className="text-brand-600 underline text-sm mt-2 inline-block">
          Back to fixtures
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Link href="/" className="text-sm text-gray-400 hover:text-gray-600 mb-6 inline-flex items-center gap-1">
        ← All Fixtures
      </Link>

      {/* Team header */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6 flex items-center gap-5">
        {team.logo_url ? (
          <Image src={team.logo_url} alt={team.name} width={72} height={72} className="object-contain" />
        ) : (
          <div className="w-18 h-18 rounded-full bg-gray-200 flex items-center justify-center text-2xl font-bold text-gray-400">
            {(team.short_name ?? team.name).slice(0, 3).toUpperCase()}
          </div>
        )}
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900">{team.name}</h1>
          <p className="text-sm text-gray-400 mt-0.5">Corner kick history — last 20 matches</p>
        </div>
      </div>

      {/* Corner history chart + table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-5">Corner History</h2>
        <TeamCornerHistory history={history} teamName={team.name} />
      </div>
    </div>
  );
}
