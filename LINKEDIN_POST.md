🌟 Excited to share a passion project I’ve been building: **Dasha Astro**! 🌟

I wanted to bridge ancient wisdom with modern technology, so I developed a full-stack Vedic astrology workspace that calculates your birth chart and allows you to chat with an AI astrologer about your unique planetary placements.

**What does it do?**
Dasha Astro provides a complete Vedic astrology experience. You enter your birth details, and it computes your D1 Rashi, D9 Navamsha, and D10 Dashamsha charts, along with Vimshottari dasha timings. What makes it special is the AI integration—you can chat with an interactive AI astrologer directly about your calculated charts, asking specific questions about your life, career, or relationships based on your planetary positions!

**What I built:**
I built this from the ground up as a full-stack developer:
💻 **Frontend:** Built a responsive, interactive UI using Next.js, React, Tailwind CSS, and NextAuth for a smooth user experience.
⚙️ **Backend:** Developed a robust FastAPI and SQLAlchemy backend in Python.
🔧 **Core Features:** Integrated the `pyswisseph` (Swiss Ephemeris) library for high-precision astrological calculations (implementing the True Chitra Paksha Lahiri ayanamsha and Parashari rules) and created an Indian location lookup feature.
🔐 **Admin & Security:** Implemented a secure local administrator login system, role-based access control, and an admin dashboard to view interaction logs.
🗄️ **Database:** Used SQLite and Prisma to manage users, sessions, and chat logs.

**How AI is being used:**
The app uses **Google Gemini AI** (or local Ollama models) to interpret the complex astrological data. Instead of just giving you a static reading, I implemented a real-time streaming endpoint that pipes your exact planetary degrees, house placements, and dashas into the LLM. This allows the AI to act as a personalized astrologer, giving you tailored, interactive answers in real-time about your specific chart!

It was a challenging and incredibly rewarding journey combining astronomical precision with the power of modern LLMs.

I’d love to hear your thoughts or connect with others building at the intersection of traditional domains and AI! Let me know what you think! 🚀

#FullStackDevelopment #AI #Nextjs #FastAPI #Python #Astrology #VedicAstrology #GeminiAI #WebDevelopment #SoftwareEngineering #TechInnovation
