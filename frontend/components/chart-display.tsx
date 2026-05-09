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

        return (
          <div key={index} className="min-h-24 border border-brass/20 p-2">
            <div className="mb-1 flex items-center justify-between gap-1">
              <span className="text-[10px] font-semibold uppercase tracking-wide text-stone-500">
                {isLagna ? "Lagna" : RASHI_ABBR[sign] ?? sign.slice(0, 2)}
              </span>
            </div>
            <div className="space-y-1">
              {isLagna && (
                <div className="rounded-md bg-yellow-100 px-1.5 py-1 shadow-sm">
                  <span className="text-xs font-semibold text-yellow-800">Lagna</span>
                </div>
              )}
              {bodies.map((body) => (
                <div
                  key={`${body.name}-${body.rashi}-${body.degree_in_rashi}`}
                  className="rounded-md bg-white/80 px-1.5 py-1 shadow-sm"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate text-xs font-semibold text-ink">{body.name}</span>
                    {body.is_retrograde ? (
                      <span className="text-[10px] font-bold text-red-700">R</span>
                    ) : null}
                  </div>
                  <div className="truncate text-[10px] text-stone-600">
                    {body.rashi} {formatDegree(body)}
                  </div>
                </div>
              ))}
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
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-ink">Varga Charts</h2>
        <p className="text-sm text-stone-600">D1, D9, and D10 calculated from exact sidereal longitudes.</p>
      </div>
      <div className="grid gap-4 xl:grid-cols-3">
        {CHART_ORDER.map(([code, fallbackName]) => {
          const chart = vargas[code];
          if (!chart) {
            return null;
          }
          return <ChartPanel key={code} code={code} chart={{ ...chart, name: chart.name || fallbackName }} />;
        })}
      </div>
    </section>
  );
}
