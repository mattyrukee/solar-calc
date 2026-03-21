const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ------------------------------------------------------------------ //
// Types                                                               //
// ------------------------------------------------------------------ //

export interface League {
  id: number;
  name: string;
  short_name: string;
  country: string;
  logo_url: string | null;
}

export interface Team {
  id: number;
  name: string;
  short_name: string | null;
  logo_url: string | null;
}

export interface Prediction {
  predicted_total: number;
  low_bound: number;
  high_bound: number;
  confidence_score: number;
  home_avg_corners_for: number | null;
  away_avg_corners_for: number | null;
  h2h_avg_corners: number | null;
  league_avg_corners: number | null;
  model_version: string;
  generated_at: string;
}

export interface Fixture {
  id: number;
  fixture_date: string;
  league: League;
  home_team: Team;
  away_team: Team;
  status: string;
  home_corners: number | null;
  away_corners: number | null;
  total_corners: number | null;
  prediction: Prediction | null;
}

export interface CornerHistoryEntry {
  match_id: number;
  fixture_date: string;
  opponent: string;
  is_home: boolean;
  corners_for: number | null;
  corners_against: number | null;
  total_corners: number | null;
}

export interface ModelStatus {
  status: "trained" | "not_trained";
  message?: string;
  metrics?: {
    mae_mean: number;
    rmse_mean: number;
    ci_coverage_mean: number;
    n_samples: number;
    model_version: string;
  };
}

// ------------------------------------------------------------------ //
// Fetch helper                                                        //
// ------------------------------------------------------------------ //

async function get<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(`${BASE}${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  }
  const res = await fetch(url.toString(), { next: { revalidate: 60 } });
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

// ------------------------------------------------------------------ //
// API functions                                                       //
// ------------------------------------------------------------------ //

export const api = {
  leagues(): Promise<League[]> {
    return get("/api/leagues/");
  },

  fixtures(params?: {
    league_id?: number;
    match_date?: string;
    days_ahead?: number;
  }): Promise<Fixture[]> {
    const p: Record<string, string> = {};
    if (params?.league_id) p.league_id = String(params.league_id);
    if (params?.match_date) p.match_date = params.match_date;
    if (params?.days_ahead) p.days_ahead = String(params.days_ahead);
    return get("/api/fixtures/", p);
  },

  prediction(fixtureId: number): Promise<Prediction> {
    return get(`/api/predictions/${fixtureId}`);
  },

  team(teamId: number): Promise<Team> {
    return get(`/api/teams/${teamId}`);
  },

  cornerHistory(teamId: number, last = 20): Promise<CornerHistoryEntry[]> {
    return get(`/api/teams/${teamId}/corner-history`, { last: String(last) });
  },

  modelStatus(): Promise<ModelStatus> {
    return get("/api/admin/model-status");
  },
};
