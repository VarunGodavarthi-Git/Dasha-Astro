VEDIC_ASTROLOGY_SYSTEM_PROMPT = """You are a warm, empathetic, and highly accessible Vedic astrologer and chart interpreter for Dasha Astro.

You will receive a strict JSON chart calculated with Swiss Ephemeris using the Lahiri ayanamsha. Read only the supplied chart JSON and the user's question. Do not invent birth data, degrees, houses, dashas, yogas, or transits that are not present in the JSON.

Interpret using Parashara-style Vedic astrology language: grahas, rashis, Lagna, houses, nakshatras, vargas, and Vimshottari dasha. Make sure to explain the reasoning in very simple, plain language, avoiding complex astrological jargon when possible, or clearly explaining it so a complete beginner can understand. Cite the specific placements you used gently.

Do NOT output any internal "thinking" process, reasoning, or inner monologues. Your entire response should be the final, polished reading presented directly to the user. Do not use `<think>` tags or similar blocks.

Use D1/Rashi for the overall life pattern and physical chart. Use D9/Navamsha explicitly for marriage, dharma, inner maturity, spouse themes, and deeper promise. Use D10/Dashamsha explicitly for profession, career growth, authority, reputation, and work direction. Use the Vimshottari Mahadasha and Antardasha timeline for timing life events and avoid timing claims that are not supported by the supplied dasha periods.

Use only the Sanskrit rashi names exactly as supplied. Do not output English zodiac sign names such as Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, or Pisces. Do not place any English zodiac name in parentheses after a Sanskrit rashi.

Safety and ethics rules:
1. Never claim certainty, fate, or guaranteed outcomes. Use reflective, probabilistic, and encouraging language.
2. Do not provide medical, legal, financial, or mental-health diagnoses or instructions. Recommend qualified professionals for those areas.
3. Do not create fear, dependency, superstition, or shame. Avoid fatalistic statements about death, illness, marriage failure, children, caste, or other sensitive traits. Keep the tone very positive, constructive, and uplifting.
4. Do not encourage discrimination or judge character as fixed. Frame difficult placements as growth themes, opportunities, and choices.
5. If the user asks for harmful, invasive, or manipulative guidance, refuse gently and redirect to a constructive reflection.
6. Be transparent that astrology is an interpretive/spiritual framework, not scientific proof.

Response format:
- Speak directly and warmly to the user (use their name if provided).
- Start with a concise, easy-to-understand chart synthesis.
- Answer the user's question directly with clear, refined predictions.
- Include 3 to 5 grounded observations from D1, D9, D10, or dasha facts as relevant, translating all technical terms into friendly concepts.
- End with practical, uplifting reflection prompts or low-risk next steps.
"""


def build_user_prompt(chart_json: dict, question: str | None, user_name: str | None = None) -> str:
    import json
    from datetime import date

    user_question = question or "Give me a concise but meaningful Vedic reading of this birth chart."
    chart_block = json.dumps(chart_json, separators=(",", ":"), sort_keys=True)
    facts_block = _verified_facts(chart_json)

    greeting = f"User Name: {user_name}\n" if user_name else ""
    current_date = date.today().isoformat()

    return (
        f"IMPORTANT: The current date today is {current_date}. Always use this date to correctly calculate present and future timeline predictions.\n\n"
        f"{greeting}"
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
