"use client";

type VargaBody = {
  name: string;
  rashi: string;
  degree_in_rashi: number;
  degree_in_rashi_dms?: string;
  house: number;
  is_retrograde?: boolean;
};

type VargaChart = {
  name: string;
  lagna: VargaBody;
  planets: VargaBody[];
};

type ChartVargas = {
  D1?: VargaChart;
  D9?: VargaChart;
  D10?: VargaChart;
};

interface ChartDisplayProps {
  vargas: ChartVargas;
}

const RASHI_ABBR: Record<string, string> = {
  Mesha: "Me",
  Vrishabha: "Vr",
  Mithuna: "Mi",
  Karka: "Ka",
  Simha: "Si",
  Kanya: "Ky",
  Tula: "Tu",
  Vrischika: "Vs",
  Dhanu: "Dh",
  Makara: "Ma",
  Kumbha: "Ku",
  Meena: "Mn",
};

const RASHI_ORDER = [
  "Mesha",
  "Vrishabha",
  "Mithuna",
  "Karka",
  "Simha",
  "Kanya",
  "Tula",
  "Vrischika",
  "Dhanu",
  "Makara",
  "Kumbha",
  "Meena",
];

const PLANET_ABBR: Record<string, string> = {
  Sun: "Su", Moon: "Mo", Mars: "Ma", Mercury: "Me",
  Jupiter: "Ju", Venus: "Ve", Saturn: "Sa", Rahu: "Ra", Ketu: "Ke"
};

const CHART_ORDER = [
  ["D1", "Rashi"],
  ["D9", "Navamsha"],
  ["D10", "Dashamsha"],
] as const;

function formatDegree(body: VargaBody): string {
  if (body.degree_in_rashi_dms) {
    return body.degree_in_rashi_dms;
  }
  return `${body.degree_in_rashi.toFixed(2)} deg`;
}

function chartHouses(chart: VargaChart) {
  const houses: VargaBody[][] = Array.from({ length: 12 }, () => []);
  houses[0].push({ ...chart.lagna, name: "Lagna" });
  chart.planets.forEach((planet) => {
    const index = Math.min(11, Math.max(0, planet.house - 1));
    houses[index].push(planet);
  });
  return houses;
}

function chartHouseSigns(chart: VargaChart) {
  const lagnaIndex = Math.max(0, RASHI_ORDER.indexOf(chart.lagna.rashi));
  return Array.from({ length: 12 }, (_, houseIndex) => RASHI_ORDER[(lagnaIndex + houseIndex) % 12]);
}

function renderSouthIndianChart(chart: VargaChart) {
  const fixedSigns = [
    "Meena", "Mesha", "Vrishabha", "Mithuna",
    "Kumbha", null, null, "Karka",
    "Makara", null, null, "Simha",
    "Dhanu", "Vrischika", "Tula", "Kanya",
  ];

  return (
    <div className="grid aspect-square grid-cols-4 grid-rows-4 overflow-hidden rounded-lg border border-brass/30 bg-[#fffdfa]">
      {fixedSigns.map((sign, index) => {
        if (!sign) {
          return <div key={index} className="border-none"></div>; // Empty middle cells
        }

        const bodies = chart.planets.filter((planet) => planet.rashi === sign);
        const isLagna = chart.lagna.rashi === sign;

        // Map planet names to 2-letter abbreviations
        const bodyLabels = bodies.map((b) => PLANET_ABBR[b.name] || b.name.slice(0, 2));

        return (
          <div key={index} className="min-h-24 border border-brass/20 p-2 flex flex-col relative">
            {/* Small faded sign abbreviation in the top left corner */}
            <span className="absolute left-2 top-1 text-[10px] font-semibold uppercase tracking-wide text-stone-400">
              {RASHI_ABBR[sign] ?? sign.slice(0, 2)}
            </span>

            {/* Centered traditional text (e.g., "As, Su, Me") */}
            <div className="flex flex-1 items-center justify-center text-center">
              <div className="flex flex-wrap items-center justify-center text-sm font-semibold text-ink gap-1">
                {isLagna && <span className="font-bold text-red-700">As</span>}
                {isLagna && bodies.length > 0 && <span>,</span>}
                <span>{bodyLabels.join(", ")}</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function ChartPanel({ code, chart }: { code: string; chart: VargaChart }) {
  return (
    <article className="rounded-lg border border-stone-200 bg-white p-4 shadow-soft">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-ink">{code}</h3>
          <p className="text-xs font-medium uppercase tracking-wide text-stone-500">{chart.name}</p>
        </div>
        <div className="rounded-md bg-brass/10 px-2 py-1 text-xs font-semibold text-brass">
          Lagna {chart.lagna.rashi}
        </div>
      </div>
      {renderSouthIndianChart(chart)}
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-stone-200 bg-stone-50">
              <th className="px-2 py-2 text-left font-semibold text-stone-700">Body</th>
              <th className="px-2 py-2 text-left font-semibold text-stone-700">Rashi</th>
              <th className="px-2 py-2 text-right font-semibold text-stone-700">Degree</th>
              <th className="px-2 py-2 text-right font-semibold text-stone-700">House</th>
            </tr>
          </thead>
          <tbody>
            {[chart.lagna, ...chart.planets].map((body) => (
              <tr key={`${code}-${body.name}`} className="border-b border-stone-100">
                <td className="px-2 py-2 font-medium text-ink">{body.name}</td>
                <td className="px-2 py-2 text-stone-700">{body.rashi}</td>
                <td className="px-2 py-2 text-right text-stone-600">{formatDegree(body)}</td>
                <td className="px-2 py-2 text-right text-stone-600">{body.house}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}

export function ChartDisplay({ vargas }: ChartDisplayProps) {
  const d1Chart = vargas["D1"];
  const divisionalCharts = [
    ["D9", "Navamsha"],
    ["D10", "Dashamsha"],
  ] as const;

  return (
    <div className="space-y-10">
      {/* 1. Primary Natal Chart Section */}
      {d1Chart && (
        <section className="space-y-4">
          <div>
            <h2 className="text-2xl font-bold text-ink">Natal Chart</h2>
            <p className="text-sm text-stone-600">Primary D1 (Rashi) chart calculated from exact sidereal longitudes.</p>
          </div>
          <div className="max-w-xl">
            <ChartPanel code="D1" chart={{ ...d1Chart, name: "Natal Chart" }} />
          </div>
        </section>
      )}

      {/* 2. Divisional Charts Section */}
      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-ink">Divisional Charts (Vargas)</h2>
          <p className="text-sm text-stone-600">Detailed D9 and D10 charts for specific life areas.</p>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:max-w-4xl">
          {divisionalCharts.map(([code, fallbackName]) => {
            const chart = vargas[code as keyof ChartVargas];
            if (!chart) {
              return null;
            }
            return <ChartPanel key={code} code={code} chart={{ ...chart, name: chart.name || fallbackName }} />;
          })}
        </div>
      </section>
    </div>
  );
}