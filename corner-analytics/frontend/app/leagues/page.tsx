import Link from "next/link";
import { api } from "@/lib/api";

export default async function LeaguesPage() {
  let leagues;
  try {
    leagues = await api.leagues();
  } catch {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 text-sm">
        Could not load leagues. Make sure the backend is running.
      </div>
    );
  }

  const flagMap: Record<string, string> = {
    England: "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    Spain: "🇪🇸",
    Germany: "🇩🇪",
    Italy: "🇮🇹",
  };

  return (
    <div>
      <h1 className="text-3xl font-extrabold text-gray-900 mb-2">Leagues</h1>
      <p className="text-gray-400 text-sm mb-8">
        Supported competitions for corner kick predictions.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {leagues.map((league) => (
          <Link
            key={league.id}
            href={`/?league_id=${league.id}`}
            className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 flex items-center gap-4 hover:shadow-md transition-shadow"
          >
            <span className="text-4xl">{flagMap[league.country] ?? "⚽"}</span>
            <div>
              <p className="font-bold text-gray-800">{league.name}</p>
              <p className="text-xs text-gray-400">{league.country}</p>
            </div>
            <span className="ml-auto text-xs font-bold text-brand-600 bg-brand-50 px-2.5 py-1 rounded-full">
              {league.short_name}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
