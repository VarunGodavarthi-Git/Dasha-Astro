"use client";

interface DashaData {
  current_maha_dasha: {
    planet: string;
    start_date: string;
    end_date: string;
    duration_years: number;
    remaining_days: number;
  };
  current_antara_dasha?: {
    planet: string;
    start_date: string;
    end_date: string;
    duration_days: number;
    remaining_days: number;
  } | null;
  next_maha_dasha: {
    planet: string;
    start_date: string;
    end_date: string;
    duration_years: number;
  } | null;
  antara_dashas: Array<{
    planet: string;
    start_date: string;
    end_date: string;
    duration_days: number;
    duration_months: number;
    is_current: boolean;
    remaining_days: number | null;
  }>;
  upcoming_maha_dashas: Array<{
    planet: string;
    start_date: string;
    end_date: string;
    duration_years: number;
  }>;
}

interface DashaTableProps {
  dasha: DashaData;
}

const PLANET_COLORS: { [key: string]: string } = {
  Sun: "#ff9500",
  Moon: "#9ca3af",
  Mars: "#dc2626",
  Mercury: "#06b6d4",
  Jupiter: "#f59e0b",
  Venus: "#2dd4bf",
  Saturn: "#64748b",
  Rahu: "#7c3aed",
  Ketu: "#0ea5e9",
};

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function getProgressPercentage(
  startDate: string,
  endDate: string,
  currentDate: Date = new Date()
): number {
  const start = new Date(startDate).getTime();
  const end = new Date(endDate).getTime();
  const current = currentDate.getTime();

  const total = end - start;
  const elapsed = current - start;
  return Math.min(100, Math.max(0, (elapsed / total) * 100));
}

export function DashaTable({ dasha }: DashaTableProps) {
  return (
    <div className="space-y-6 rounded-lg border border-stone-200 bg-white p-6 shadow-soft">
      <h3 className="text-lg font-semibold text-ink">Dasha & Antara Dasha</h3>

      {/* Current Maha Dasha */}
      <div className="space-y-4">
        <div className="rounded-md border border-brass/20 bg-brass/5 p-4">
          <div className="mb-2 flex items-center justify-between">
            <h4 className="font-semibold text-ink">Current Maha Dasha</h4>
            <span className="text-sm font-bold text-brass">{dasha.current_maha_dasha.planet}</span>
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-stone-600">Duration:</span>
              <span className="font-medium text-ink">{dasha.current_maha_dasha.duration_years} years</span>
            </div>
            <div className="flex justify-between">
              <span className="text-stone-600">Started:</span>
              <span className="font-medium text-ink">{formatDate(dasha.current_maha_dasha.start_date)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-stone-600">Ends:</span>
              <span className="font-medium text-ink">{formatDate(dasha.current_maha_dasha.end_date)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-stone-600">Remaining:</span>
              <span className="font-medium text-brass">{dasha.current_maha_dasha.remaining_days} days</span>
            </div>

            {/* Progress bar */}
            <div className="mt-3">
              <div className="h-2 overflow-hidden rounded-full bg-stone-200">
                <div
                  className="h-full bg-brass transition-all duration-500"
                  style={{
                    width: `${getProgressPercentage(
                      dasha.current_maha_dasha.start_date,
                      dasha.current_maha_dasha.end_date
                    )}%`,
                  }}
                />
              </div>
              <p className="mt-1 text-xs text-stone-500">
                {getProgressPercentage(
                  dasha.current_maha_dasha.start_date,
                  dasha.current_maha_dasha.end_date
                ).toFixed(1)}
                % complete
              </p>
            </div>
          </div>
        </div>

        {dasha.current_antara_dasha && (
          <div className="rounded-md border border-river/20 bg-river/5 p-4">
            <div className="mb-2 flex items-center justify-between">
              <h4 className="font-semibold text-ink">Current Antara Dasha</h4>
              <span className="text-sm font-bold text-river">{dasha.current_antara_dasha.planet}</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-stone-600">Started:</span>
                <span className="font-medium text-ink">{formatDate(dasha.current_antara_dasha.start_date)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-stone-600">Ends:</span>
                <span className="font-medium text-ink">{formatDate(dasha.current_antara_dasha.end_date)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-stone-600">Remaining:</span>
                <span className="font-medium text-river">{dasha.current_antara_dasha.remaining_days} days</span>
              </div>
            </div>
          </div>
        )}

        {/* Antara Dashas */}
        <div>
          <h5 className="mb-3 font-semibold text-ink">Antara Dashas (Sub-periods)</h5>
          <div className="grid gap-2">
            {dasha.antara_dashas.map((antara, index) => (
              <div
                key={index}
                className={`rounded-md border p-3 transition-colors ${
                  antara.is_current
                    ? "border-brass/40 bg-brass/10"
                    : "border-stone-200 bg-stone-50"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span
                        className="inline-block h-3 w-3 rounded-full"
                        style={{
                          backgroundColor: (PLANET_COLORS[antara.planet] as any) || "#d4af37",
                        }}
                      />
                      <span className="font-medium text-ink">{antara.planet}</span>
                      {antara.is_current && (
                        <span className="text-xs font-bold text-brass">CURRENT</span>
                      )}
                    </div>
                    <p className="mt-1 text-xs text-stone-600">
                      {formatDate(antara.start_date)} to {formatDate(antara.end_date)}
                    </p>
                    <p className="text-xs text-stone-500">
                      ~{antara.duration_months} months ({antara.duration_days} days)
                    </p>
                  </div>

                  {antara.is_current && antara.remaining_days !== null && (
                    <div className="text-right">
                      <p className="text-sm font-semibold text-brass">
                        {antara.remaining_days}d left
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Next Maha Dasha */}
      {dasha.next_maha_dasha && <div className="rounded-md border border-stone-200 bg-stone-50 p-4">
        <div className="mb-2 flex items-center justify-between">
          <h4 className="font-semibold text-ink">Next Maha Dasha</h4>
          <span className="text-sm font-bold text-stone-600">{dasha.next_maha_dasha.planet}</span>
        </div>

        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-stone-600">Duration:</span>
            <span className="font-medium text-ink">{dasha.next_maha_dasha.duration_years} years</span>
          </div>
          <div className="flex justify-between">
            <span className="text-stone-600">Starts:</span>
            <span className="font-medium text-ink">{formatDate(dasha.next_maha_dasha.start_date)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-stone-600">Ends:</span>
            <span className="font-medium text-ink">{formatDate(dasha.next_maha_dasha.end_date)}</span>
          </div>
        </div>
      </div>}

      {/* Upcoming Maha Dashas */}
      <div>
        <h4 className="mb-3 font-semibold text-ink">Upcoming Maha Dashas</h4>
        <div className="grid gap-2">
          {dasha.upcoming_maha_dashas.map((maha, index) => (
            <div key={index} className="flex items-center justify-between rounded-md border border-stone-200 bg-white p-3">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span
                    className="inline-block h-2.5 w-2.5 rounded-full"
                    style={{
                      backgroundColor: (PLANET_COLORS[maha.planet] as any) || "#d4af37",
                    }}
                  />
                  <span className="font-medium text-ink">{maha.planet}</span>
                </div>
                <p className="mt-1 text-xs text-stone-500">
                  {formatDate(maha.start_date)} to {formatDate(maha.end_date)}
                </p>
              </div>
              <span className="text-sm font-semibold text-stone-600">{maha.duration_years}y</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
