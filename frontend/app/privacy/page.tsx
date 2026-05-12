import { Sparkles } from "lucide-react";

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8 flex items-center gap-3">
        <Sparkles className="text-brass" size={24} />
        <h1 className="text-3xl font-bold text-ink">Privacy Policy</h1>
      </div>

      <div className="prose prose-stone max-w-none rounded-lg border border-stone-200 bg-white p-8 shadow-soft">
        <p className="lead text-lg text-stone-600">
          At Dasha Astro, we take your privacy seriously. This policy outlines how we handle the information you provide when using our application.
        </p>

        <h2 className="mt-8 text-xl font-semibold text-ink">1. Information We Collect</h2>
        <p className="mt-4 text-stone-600">
          When you use our application to generate an astrological reading, we collect and temporarily store the following information:
        </p>
        <ul className="mt-4 list-disc pl-6 text-stone-600">
          <li>Your email address (if authenticated) and optional display name.</li>
          <li>Birth details you provide: Date, time, and location (city).</li>
          <li>The questions you submit for astrological interpretation.</li>
          <li>The calculated astrological chart and AI-generated responses.</li>
        </ul>

        <h2 className="mt-8 text-xl font-semibold text-ink">2. How We Use Your Information</h2>
        <p className="mt-4 text-stone-600">
          The information collected is used exclusively for:
        </p>
        <ul className="mt-4 list-disc pl-6 text-stone-600">
          <li>Calculating precise astronomical positions (charts, houses, vargas).</li>
          <li>Providing context to our AI models to generate personalized astrological readings.</li>
          <li>Maintaining a temporary log of your recent interactions to improve conversational continuity within your session.</li>
          <li>Enforcing usage limits (e.g., daily free reading limits).</li>
        </ul>

        <h2 className="mt-8 text-xl font-semibold text-ink">3. Data Sharing and Third Parties</h2>
        <p className="mt-4 text-stone-600">
          We do not sell your personal data. We share necessary data only with:
        </p>
        <ul className="mt-4 list-disc pl-6 text-stone-600">
          <li><strong>Location Providers:</strong> Your city query is sent to a geocoding service (Nominatim) to retrieve latitude and longitude.</li>
          <li><strong>AI Providers:</strong> Your chart data and questions are securely transmitted to Google (Gemini) or OpenAI APIs for the sole purpose of generating your reading. These providers do not use this data to train their base models according to their standard API terms.</li>
        </ul>

        <h2 className="mt-8 text-xl font-semibold text-ink">4. Data Retention</h2>
        <p className="mt-4 text-stone-600">
          Your interaction logs and generated charts are stored in our secure database. Site administrators may periodically clear these logs to minimize data footprint.
        </p>
      </div>
    </div>
  );
}
