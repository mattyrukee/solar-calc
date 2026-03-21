"use client";

import { useEffect, useState } from "react";
import { format } from "date-fns";
import { api, type Fixture, type League } from "@/lib/api";
import MatchCard from "@/components/MatchCard";
import LeagueFilter from "@/components/LeagueFilter";

export default function HomePage() {
  const [leagues, setLeagues] = useState<League[]>([]);
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [selectedLeague, setSelectedLeague] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.leagues().then(setLeagues).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api
      .fixtures({ league_id: selectedLeague ?? undefined, days_ahead: 7 })
      .then(setFixtures)
      .catch(() => setError("Could not load fixtures. Make sure the backend is running."))
      .finally(() => setLoading(false));
  }, [selectedLeague]);

  // Group by date
  const grouped = fixtures.reduce<Record<string, Fixture[]>>((acc, f) => {
    const day = format(new Date(f.fixture_date), "yyyy-MM-dd");
    if (!acc[day]) acc[day] = [];
    acc[day].push(f);
    return acc;
  }, {});

  const days = Object.keys(grouped).sort();

  return (
    <div>
      {/* Hero */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-1">
          Corner Kick Predictions
        </h1>
        <p className="text-gray-500 text-sm">
          AI-powered forecasts for upcoming matches across Europe's top leagues.
        </p>
      </div>

      {/* League filter */}
      <div className="mb-6">
        <LeagueFilter
          leagues={leagues}
          selected={selectedLeague}
          onChange={setSelectedLeague}
        />
      </div>

      {/* Content */}
      {loading && (
        <div className="flex justify-center items-center h-40">
          <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 text-sm">
          {error}
        </div>
      )}

      {!loading && !error && days.length === 0 && (
        <div className="text-center py-20 text-gray-400">
          <p className="text-5xl mb-4">⚽</p>
          <p className="font-medium text-gray-500">No upcoming fixtures found.</p>
          <p className="text-sm mt-1">
            Trigger a data refresh from the admin panel, or check back later.
          </p>
        </div>
      )}

      {!loading &&
        days.map((day) => (
          <section key={day} className="mb-10">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-4">
              {format(new Date(day), "EEEE, d MMMM yyyy")}
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {grouped[day].map((f) => (
                <MatchCard key={f.id} fixture={f} />
              ))}
            </div>
          </section>
        ))}
    </div>
  );
}
