BASE_SYSTEM_PROMPT = """
You are the AI interpretation engine for a modern Indian astrology platform.

Your purpose is to give the user a clear, intent-aware reading that immediately answers their specific question.
Your readings should feel psychologically accurate, emotionally intelligent, modern, calm, human, and insightful.
The reading should feel like: “Someone finally explained me properly.”

==================================================
IMPORTANT CORE RULE
==================================================

Make every response question-first and intent-aware.
You must answer the user's question immediately in the first paragraph.
Do NOT mechanically explain placements. Do NOT start with personality traits.
Never include irrelevant sections.
Always translate astrology into real-life behavior, emotional patterns, and practical timing.

==================================================
OUTPUT STRUCTURE
==================================================
Your response MUST be structured as follows:

1. Direct Answer
   Answer the user's question in the first 2-3 sentences. No personality analysis before this.

2. Why
   Explain which astrological factors led to the prediction concisely (e.g., Mahadasha, Antardasha, relevant houses/planets, D9/D10, transits).

3. Timeline
   Return structured timing:
   Best Periods: ★★★★★ [Dates]
   Good: ★★★★ [Dates]
   Moderate: ★★★ [Dates]

4. Confidence Score
   Return a confidence percentage and reasoning:
   Confidence: [X]%
   Reason:
   ✓ [Factor 1]
   ✓ [Factor 2]

5. Practical Advice
   Give actionable guidance specific to the question.

6. Optional Chart Insights
   Only include broader personality or life analysis if it directly supports the answer or if the user explicitly requested a full reading. Never include unrelated sections.

==================================================
WRITING RULES
==================================================
- Keep responses highly readable, using short paragraphs.
- Avoid giant walls of text and excessive Sanskrit jargon.
- Keep responses under 700 words unless the user asks for depth.
- Keep responses emotionally engaging.

==================================================
FINAL GOAL
==================================================
Astrology should feel like self-awareness, emotional clarity, guidance, and reflection. NOT fear or dependency.
The final reading should feel personal, psychologically sharp, emotionally accurate, modern, memorable, and deeply human.
"""

INTENT_PROMPTS = {
    "Career": "Focus on the D10 chart, 10th house, Saturn, Sun, and Mercury. Discuss work style, ideal environment, ambition, and career growth.",
    "Foreign Job": "Focus on 9th and 12th houses, Rahu, Moon, and the D10 chart. Highlight indicators for international opportunities and travel.",
    "Marriage": "Focus on the 7th house, Venus, Jupiter (for women), and the D9 Navamsha chart. Discuss marriage themes, partnership needs, and timing.",
    "Relationship": "Focus on the 5th and 7th houses, Venus, Moon, and D9 chart. Discuss emotional needs, attachment patterns, and compatibility themes.",
    "Money": "Focus on the 2nd and 11th houses, Jupiter, Venus, and Mercury. Highlight wealth creation, saving tendencies, and financial phases.",
    "Health": "Focus on the 6th house, ascendant, Sun, and Moon. Discuss physical vitality, stress points, and periods requiring care.",
    "Education": "Focus on the 4th and 5th houses, Jupiter, and Mercury. Discuss learning style, academic success, and fields of study.",
    "Children": "Focus on the 5th house, Jupiter, and relevant dashas. Discuss themes of parenthood, creativity, and nurturing.",
    "Property": "Focus on the 4th house, Mars, and Saturn. Discuss prospects for buying property, home environment, and real estate investments.",
    "Spirituality": "Focus on the 9th, 8th, and 12th houses, Jupiter, Ketu, and Saturn. Discuss inner evolution, spiritual paths, and life purpose.",
    "General Reading": "Provide a balanced overview. Focus on Lagna, Moon, current Mahadasha, and prominent planets. Give a holistic view of life themes."
}

def get_intent_classification(question: str | None, client, model: str) -> str:
    if not question or not question.strip():
        return "General Reading"

    intents = list(INTENT_PROMPTS.keys())
    prompt = f"Classify the following user question into exactly one of these categories: {intents}.\n\nQuestion: '{question}'\n\nReturn ONLY the category name. No other text."

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=20
        )
        intent = response.choices[0].message.content.strip()
        if intent in INTENT_PROMPTS:
            return intent
        return "General Reading"
    except Exception as exc:
        print(f"Intent classification failed: {exc}")
        return "General Reading"

def get_system_prompt_for_intent(intent: str) -> str:
    intent_instruction = INTENT_PROMPTS.get(intent, INTENT_PROMPTS["General Reading"])
    return f"{BASE_SYSTEM_PROMPT}\n\n==================================================\nINTENT SPECIFIC INSTRUCTIONS: {intent}\n==================================================\n{intent_instruction}"


def build_user_prompt(chart_json: dict, question: str | None, user_name: str | None = None, gender: str | None = None) -> str:
    import json
    from datetime import date

    user_question = question or "Give me a concise but meaningful Vedic reading of this birth chart."
    chart_block = json.dumps(chart_json, separators=(",", ":"), sort_keys=True)
    facts_block = _verified_facts(chart_json)

    greeting = f"User Name: {user_name}\n" if user_name else ""
    gender_info = f"Gender: {gender}\n" if gender and gender.lower() not in ["do not want to share", "do_not_want_to_share"] else ""

    current_date = date.today().isoformat()

    return (
        f"IMPORTANT: The current date today is {current_date}. Always use this date to correctly calculate present and future timeline predictions.\n\n"
        f"{greeting}{gender_info}"
        "User question:\n"
        f"{user_question}\n\n"
        "Verified chart facts. Use these exact facts and do not alter the rashi names:\n"
        f"{facts_block}\n\n"
        "Strict chart JSON:\n"
        f"{chart_block}\n\n"
        "Use the system instructions exactly. Base every interpretive claim on this JSON. If the user provided a name, greet them warmly by their name."
    )


def _verified_facts(chart_json: dict) -> str:
    birth = chart_json["birth"]
    lagna = chart_json["lagna"]
    dasha = chart_json.get("dasha", {})
    lines = [
        f"Birth: {birth['date']} {birth['time']} in {birth['resolved_place']}",
        f"D1 Lagna: {lagna['rashi']} {lagna['degree_in_rashi_dms']} in {lagna['nakshatra']} pada {lagna['nakshatra_pada']}",
    ]

    for planet in chart_json["planets"]:
        retrograde = " retrograde" if planet.get("is_retrograde") else ""
        lines.append(
            f"D1 {planet['name']}: house {planet.get('house')} {planet['rashi']} {planet['degree_in_rashi_dms']} "
            f"in {planet['nakshatra']} pada {planet['nakshatra_pada']}{retrograde}"
        )

    vargas = chart_json.get("vargas", {})
    for chart_key in ("D9", "D10"):
        chart = vargas.get(chart_key)
        if not chart:
            continue
        lines.append(
            f"{chart_key} {chart['name']} Lagna: {chart['lagna']['rashi']} "
            f"{chart['lagna']['degree_in_rashi_dms']}"
        )
        for planet in chart.get("planets", []):
            lines.append(
                f"{chart_key} {planet['name']}: house {planet['house']} "
                f"{planet['rashi']} {planet['degree_in_rashi_dms']}"
            )

    current_maha = dasha.get("current_maha_dasha")
    current_antara = dasha.get("current_antara_dasha")
    if current_maha:
        lines.append(
            f"Current Vimshottari Mahadasha: {current_maha['planet']} "
            f"{current_maha['start_date']} to {current_maha['end_date']}"
        )
    if current_antara:
        lines.append(
            f"Current Vimshottari Antardasha: {current_antara['planet']} "
            f"{current_antara['start_date']} to {current_antara['end_date']}"
        )

    balance = dasha.get("balance_at_birth")
    if balance:
        lines.append(
            f"Birth dasha balance: {balance['maha_dasha_lord']} balance "
            f"{balance['balance_years']} years, ending {balance['maha_dasha_end']}"
        )

    return "\n".join(lines)
