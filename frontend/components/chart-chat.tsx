"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { Bot, Loader2, MapPin, Search, Send, Sparkles } from "lucide-react";
import { useSession } from "next-auth/react";
import { ChartDisplay } from "./chart-display";
import { DashaTable } from "./dasha-table";

type Status = "idle" | "streaming" | "error" | "done";

type LocationResult = {
  query: string;
  display_name: string;
  latitude: number;
  longitude: number;
  timezone: string;
};

type Chart = {
  calculation: any;
  birth: any;
  lagna: any;
  planets: any[];
  houses: any[];
  vargas: any;
  dasha: any;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const MONTHS = [
  ["01", "Jan"],
  ["02", "Feb"],
  ["03", "Mar"],
  ["04", "Apr"],
  ["05", "May"],
  ["06", "Jun"],
  ["07", "Jul"],
  ["08", "Aug"],
  ["09", "Sep"],
  ["10", "Oct"],
  ["11", "Nov"],
  ["12", "Dec"],
];

function daysInMonth(year: string, month: string): number {
  const parsedYear = Number(year) || new Date().getFullYear();
  const parsedMonth = Number(month) || 1;
  return new Date(parsedYear, parsedMonth, 0).getDate();
}

function twoDigit(value: number): string {
  return value.toString().padStart(2, "0");
}

export function ChartChat() {
  const { data: session, status: authStatus } = useSession();
  const [birthYear, setBirthYear] = useState("");
  const [birthMonth, setBirthMonth] = useState("01");
  const [birthDay, setBirthDay] = useState("01");
  const [timeOfBirth, setTimeOfBirth] = useState("");
  const [cityName, setCityName] = useState("");
  const [selectedLocation, setSelectedLocation] = useState<LocationResult | null>(null);
  const [locationStatus, setLocationStatus] = useState<"idle" | "searching" | "error" | "done">("idle");
  const [locationMessage, setLocationMessage] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState("");
  const [chart, setChart] = useState<Chart | null>(null);

  const dateOfBirth = useMemo(() => {
    if (!birthYear || birthYear.length < 4) {
      return "";
    }
    return `${birthYear}-${birthMonth}-${birthDay}`;
  }, [birthDay, birthMonth, birthYear]);

  const dayCount = useMemo(() => daysInMonth(birthYear, birthMonth), [birthMonth, birthYear]);

  useEffect(() => {
    if (Number(birthDay) > dayCount) {
      setBirthDay(twoDigit(dayCount));
    }
  }, [birthDay, dayCount]);

  const canSubmit = useMemo(() => {
    return Boolean(session?.user?.email && dateOfBirth && timeOfBirth && cityName.trim() && status !== "streaming");
  }, [cityName, dateOfBirth, session?.user?.email, status, timeOfBirth]);

  function buildPayload(includeQuestion = true) {
    return {
      date_of_birth: dateOfBirth,
      time_of_birth: timeOfBirth,
      city_name: selectedLocation?.display_name ?? cityName,
      latitude: selectedLocation?.latitude,
      longitude: selectedLocation?.longitude,
      timezone: selectedLocation?.timezone,
      question: includeQuestion ? question : "",
      user_email: session?.user?.email,
      user_name: session?.user?.name,
    };
  }

  async function searchLocation() {
    const query = cityName.trim();
    if (query.length < 2) {
      return;
    }

    setLocationStatus("searching");
    setLocationMessage("");
    setSelectedLocation(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/location/search?query=${encodeURIComponent(query)}`);
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.detail ?? `Location search returned ${response.status}`);
      }
      setSelectedLocation(data);
      setLocationStatus("done");
      setLocationMessage(`${data.display_name} (${data.latitude.toFixed(5)}, ${data.longitude.toFixed(5)}, ${data.timezone})`);
    } catch (caught) {
      setLocationStatus("error");
      setLocationMessage(caught instanceof Error ? caught.message : "Could not resolve this place.");
    }
  }

  async function calculateChart() {
    const response = await fetch(`${apiBaseUrl}/api/chart`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(buildPayload(false)),
    });

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(data?.detail ?? `Backend returned ${response.status}`);
    }
    setChart(data.chart);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) {
      return;
    }

    setStatus("streaming");
    setAnswer("");
    setError("");
    setChart(null);

    try {
      await calculateChart();

      const response = await fetch(`${apiBaseUrl}/api/chart/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(buildPayload(true)),
      });

      if (!response.ok || !response.body) {
        const detail = await response.json().catch(() => null);
        throw new Error(detail?.detail ?? `Backend returned ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          break;
        }

        const decoded = decoder.decode(value, { stream: true });
        setAnswer((current) => current + decoded);
      }

      setStatus("done");
    } catch (caught) {
      setStatus("error");
      setError(caught instanceof Error ? caught.message : "Something went wrong.");
    }
  }

  if (authStatus === "loading") {
    return <div className="h-[520px] rounded-lg border border-stone-200 bg-white shadow-soft" />;
  }

  if (!session?.user) {
    return (
      <section className="grid min-h-[520px] place-items-center rounded-lg border border-stone-200 bg-white p-8 text-center shadow-soft">
        <div>
          <Sparkles className="mx-auto mb-4 text-brass" size={30} />
          <h1 className="text-2xl font-semibold text-ink">Dasha Astro</h1>
          <p className="mt-3 max-w-md text-sm leading-6 text-stone-600">
            Sign in to calculate Lahiri sidereal varga charts and stream a Gemini interpretation.
          </p>
        </div>
      </section>
    );
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[410px_minmax(0,1fr)]">
      <form className="h-fit rounded-lg border border-stone-200 bg-white p-4 shadow-soft" onSubmit={handleSubmit}>
        <div className="mb-4 flex items-center gap-2">
          <Sparkles className="text-brass" size={18} />
          <h1 className="text-base font-semibold text-ink">Chart Input</h1>
        </div>

        <div className="mb-4 grid grid-cols-[1fr_1fr_1.2fr] gap-2">
          <label className="block">
            <span className="mb-1 block text-xs font-medium text-stone-700">Month</span>
            <select
              className="h-9 w-full rounded-md border border-stone-300 bg-white px-2.5 text-sm text-ink focus:border-brass focus:outline-none focus:ring-1 focus:ring-brass"
              onChange={(event) => setBirthMonth(event.target.value)}
              value={birthMonth}
            >
              {MONTHS.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>

          <label className="block">
            <span className="mb-1 block text-xs font-medium text-stone-700">Day</span>
            <select
              className="h-9 w-full rounded-md border border-stone-300 bg-white px-2.5 text-sm text-ink focus:border-brass focus:outline-none focus:ring-1 focus:ring-brass"
              onChange={(event) => setBirthDay(event.target.value)}
              value={birthDay}
            >
              {Array.from({ length: dayCount }, (_, index) => twoDigit(index + 1)).map((day) => (
                <option key={day} value={day}>
                  {day}
                </option>
              ))}
            </select>
          </label>

          <label className="block">
            <span className="mb-1 block text-xs font-medium text-stone-700">Year</span>
            <input
              className="h-9 w-full rounded-md border border-stone-300 bg-white px-2.5 text-sm text-ink focus:border-brass focus:outline-none focus:ring-1 focus:ring-brass"
              max={new Date().getFullYear()}
              min={1800}
              onChange={(event) => setBirthYear(event.target.value)}
              placeholder="1994"
              required
              type="number"
              value={birthYear}
            />
          </label>
        </div>

        <label className="mb-4 block">
          <span className="mb-1 block text-xs font-medium text-stone-700">Time</span>
          <input
            className="h-9 w-full rounded-md border border-stone-300 bg-white px-2.5 text-sm text-ink focus:border-brass focus:outline-none focus:ring-1 focus:ring-brass"
            onChange={(event) => setTimeOfBirth(event.target.value)}
            required
            type="time"
            value={timeOfBirth}
          />
        </label>

        <label className="mb-2 block">
          <span className="mb-1 block text-xs font-medium text-stone-700">Birth Place</span>
          <div className="flex gap-2">
            <input
              className="h-9 min-w-0 flex-1 rounded-md border border-stone-300 bg-white px-2.5 text-sm text-ink focus:border-brass focus:outline-none focus:ring-1 focus:ring-brass"
              onChange={(event) => {
                setCityName(event.target.value);
                setSelectedLocation(null);
                setLocationStatus("idle");
                setLocationMessage("");
              }}
              placeholder="Tanuku, Andhra Pradesh"
              required
              type="text"
              value={cityName}
            />
            <button
              className="inline-flex h-9 w-10 items-center justify-center rounded-md border border-stone-300 bg-white text-ink shadow-sm hover:bg-stone-50 disabled:cursor-not-allowed disabled:bg-stone-100"
              disabled={locationStatus === "searching" || cityName.trim().length < 2}
              onClick={searchLocation}
              title="Resolve place"
              type="button"
            >
              {locationStatus === "searching" ? <Loader2 className="animate-spin" size={16} /> : <Search size={16} />}
            </button>
          </div>
        </label>

        {locationMessage ? (
          <div
            className={`mb-4 flex gap-2 rounded-md px-3 py-2 text-xs ${
              locationStatus === "error" ? "bg-red-50 text-red-700" : "bg-river/10 text-river"
            }`}
          >
            <MapPin aria-hidden="true" className="mt-0.5 shrink-0" size={14} />
            <span>{locationMessage}</span>
          </div>
        ) : (
          <div className="mb-4" />
        )}

        <label className="mb-4 block">
          <span className="mb-1 block text-xs font-medium text-stone-700">Question</span>
          <textarea
            className="min-h-24 w-full resize-none rounded-md border border-stone-300 bg-white px-2.5 py-2 text-sm leading-5 text-ink focus:border-brass focus:outline-none focus:ring-1 focus:ring-brass"
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask about this chart..."
            value={question}
          />
        </label>

        <button
          className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-leaf px-4 text-sm font-semibold text-white shadow-sm hover:bg-[#275d43] disabled:cursor-not-allowed disabled:bg-stone-300"
          disabled={!canSubmit}
          type="submit"
        >
          {status === "streaming" ? <Loader2 aria-hidden="true" className="animate-spin" size={17} /> : <Send aria-hidden="true" size={17} />}
          Generate reading
        </button>

        {error ? <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
      </form>

      <section className="space-y-5">
        {/* Gemini Response moved to the TOP */}
        <div className="flex min-h-[560px] flex-col rounded-lg border border-stone-200 bg-white shadow-soft">
          <div className="flex h-14 items-center gap-2 rounded-t-lg border-b border-stone-200 bg-stone-50 px-5">
            <Bot className="text-river" size={20} />
            <h2 className="text-sm font-semibold uppercase tracking-wide text-stone-600">AI Astrology Reading</h2>
          </div>
          
          <div className="flex-1 p-5">
            {/* Display the user's question like a chat message */}
            {question && status !== "idle" && (
              <div className="mb-6 rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-800">
                <span className="mb-1 block font-semibold text-stone-600">Your Question:</span>
                {question}
              </div>
            )}

            {/* Display the AI's streamed answer */}
            {answer ? (
              <div className="whitespace-pre-wrap text-sm leading-7 text-ink">{answer}</div>
            ) : (
              <div className="grid h-full min-h-[400px] place-items-center text-center text-sm text-stone-500">
                <span>
                  {status === "streaming" 
                    ? "Consulting the stars and analyzing your charts..." 
                    : "Submit your details and ask a question to generate a reading."}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Charts and Data Tables moved BELOW the reading */}
        {chart?.vargas ? <ChartDisplay vargas={chart.vargas} /> : null}

        {chart?.dasha ? <DashaTable dasha={chart.dasha} /> : null}
      </section>
    </div>
  );
}