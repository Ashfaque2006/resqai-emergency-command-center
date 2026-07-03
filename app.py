import os
import gradio as gr
from google import genai
from google.genai.errors import ClientError

# =========================================================
# Gemini API setup
# =========================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please add it in Hugging Face Space Secrets.")

client = genai.Client(api_key=GEMINI_API_KEY)

# =========================================================
# Input Validation
# =========================================================
def validate_inputs(location, disaster, people, injuries):
    if not location or str(location).strip() == "":
        return False, "Location is required."

    if not disaster or str(disaster).strip() == "":
        return False, "Disaster type is required."

    try:
        people = int(people)
        if people <= 0:
            return False, "People affected must be greater than 0."
    except:
        return False, "People affected must be a valid number."

    if not injuries or str(injuries).strip() == "":
        return False, "Medical situation is required."

    return True, "Valid input"

# =========================================================
# Risk Engine
# =========================================================
def calculate_risk(disaster, people, injuries):
    disaster = str(disaster).lower()
    injuries = str(injuries).lower()
    people = int(people)

    score = 0

    disaster_scores = {
        "earthquake": 5,
        "flood": 4,
        "cyclone": 4,
        "landslide": 4,
        "wildfire": 5,
        "tsunami": 5
    }
    score += disaster_scores.get(disaster, 3)

    if people >= 1000:
        score += 5
    elif people >= 500:
        score += 4
    elif people >= 200:
        score += 3
    elif people >= 50:
        score += 2
    else:
        score += 1

    severe_keywords = [
        "bleeding", "fracture", "bone fracture", "unconscious",
        "burn", "severe injury", "head injury", "multiple injuries",
        "critical", "trapped", "internal injury"
    ]

    medium_keywords = [
        "wound", "sprain", "cut", "fever", "dehydration", "pain"
    ]

    if any(word in injuries for word in severe_keywords):
        score += 5
    elif any(word in injuries for word in medium_keywords):
        score += 3
    else:
        score += 1

    if score >= 12:
        return "🔴 HIGH RISK"
    elif score >= 8:
        return "🟠 MEDIUM RISK"
    else:
        return "🟢 LOW RISK"

# =========================================================
# Resource Agent
# =========================================================
def resource_agent(people):
    people = int(people)

    doctors = max(2, round(people * 0.04))
    nurses = max(4, round(people * 0.10))
    ambulances = max(1, round(people * 0.03))
    tents = max(2, round(people * 0.20))
    water = people * 20
    food = people * 3

    return f"""
📦 RESOURCE ESTIMATION

👨‍⚕ Field Doctors Required: {doctors}
👩‍⚕ Field Nurses Required: {nurses}
🚑 Ambulances Required: {ambulances}
⛺ Relief Tents Required: {tents}
💧 Drinking Water: {water} Liters
🍱 Food Packets: {food}
"""

# =========================================================
# Hospital Capacity Agent
# =========================================================
def hospital_capacity_agent(people, injuries, risk):
    people = int(people)
    injuries_text = str(injuries).lower()
    risk = str(risk).upper()

    if "HIGH" in risk:
        critical_ratio = 0.18
        moderate_ratio = 0.32
        minor_ratio = 0.50
    elif "MEDIUM" in risk:
        critical_ratio = 0.10
        moderate_ratio = 0.30
        minor_ratio = 0.60
    else:
        critical_ratio = 0.05
        moderate_ratio = 0.20
        minor_ratio = 0.75

    severe_keywords = [
        "bleeding", "fracture", "burn", "head injury",
        "unconscious", "critical", "trapped", "multiple injuries"
    ]

    if any(word in injuries_text for word in severe_keywords):
        critical_ratio += 0.05
        moderate_ratio += 0.05
        minor_ratio -= 0.10

    if minor_ratio < 0:
        minor_ratio = 0

    critical_patients = max(1, round(people * critical_ratio))
    moderate_patients = max(1, round(people * moderate_ratio))
    minor_patients = max(1, people - critical_patients - moderate_patients)

    icu_beds_needed = critical_patients
    general_beds_needed = moderate_patients
    ambulances_needed = max(1, round((critical_patients + moderate_patients) / 8))
    trauma_doctors_needed = max(2, round(critical_patients / 10))
    nurses_needed = max(4, round((critical_patients + moderate_patients) / 4))

    total_beds_needed = icu_beds_needed + general_beds_needed

    if total_beds_needed > 150:
        overload_status = "🔴 Hospital capacity likely overloaded"
        field_hospital_needed = "YES"
    elif total_beds_needed > 70:
        overload_status = "🟠 Hospital capacity under heavy stress"
        field_hospital_needed = "POSSIBLY"
    else:
        overload_status = "🟢 Hospital capacity likely manageable"
        field_hospital_needed = "NO"

    return f"""
🏥 HOSPITAL CAPACITY & TRIAGE ESTIMATE

🚑 Critical Patients: {critical_patients}
🩺 Moderate Patients: {moderate_patients}
🩹 Minor Patients: {minor_patients}

🛏 ICU Beds Needed: {icu_beds_needed}
🛌 General Beds Needed: {general_beds_needed}
🏨 Total Beds Needed: {total_beds_needed}

🚑 Ambulances Needed: {ambulances_needed}
👨‍⚕ Trauma Doctors Needed in Hospital: {trauma_doctors_needed}
👩‍⚕ Hospital Nurses Needed: {nurses_needed}

🏥 Field Hospital Needed: {field_hospital_needed}
📊 Capacity Status: {overload_status}
"""

# =========================================================
# Unified AI Intelligence Agent
# =========================================================
def unified_intelligence_agent(location, disaster, people, injuries, risk):
    prompt = f"""
You are ResQAI, an expert disaster-response AI for emergency management.

Analyze this emergency incident and return a practical, field-ready response.

Emergency Details:
- Location: {location}
- Disaster Type: {disaster}
- People Affected: {people}
- Medical Situation: {injuries}
- Risk Level: {risk}

Your response MUST be in the following exact format:

## INCIDENT ASSESSMENT
Write a short but strong situation analysis of the disaster, danger level, affected population, and immediate concerns.

## WEATHER INTELLIGENCE
Give weather/environment-related caution, terrain or access concerns, likely field difficulties, and responder precautions.
If exact live weather is not available, give disaster-relevant operational weather guidance.

## MEDICAL OPERATIONS
Explain medical priorities, triage focus, emergency treatment concerns, transport needs, and public-health risks if relevant.

## STRATEGIC RESPONSE PLAN
Give a clear step-by-step emergency response plan in 5-8 points.
Keep it practical, concise, and useful for responders.

Rules:
- Be practical, not overly theoretical.
- Use clear emergency language.
- Keep each section readable.
- Do not include markdown tables.
- Do not add any extra sections outside the 4 sections above.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        return """## INCIDENT ASSESSMENT
AI response was empty.

## WEATHER INTELLIGENCE
Weather intelligence unavailable.

## MEDICAL OPERATIONS
Medical analysis unavailable.

## STRATEGIC RESPONSE PLAN
Please retry the request.
"""

    except ClientError as e:
        error_text = str(e)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            return f"""## INCIDENT ASSESSMENT
⚠ Gemini API quota/rate limit reached while analyzing the incident in {location}.

## WEATHER INTELLIGENCE
Live AI weather intelligence is temporarily unavailable.
Field teams should assume difficult conditions and proceed with caution.

## MEDICAL OPERATIONS
Reported medical condition: {injuries}.
Prioritize triage, first aid, stabilization, and ambulance support for severe cases.

## STRATEGIC RESPONSE PLAN
1. Secure the affected zone.
2. Deploy rescue and medical teams.
3. Set up temporary shelter and relief support.
4. Coordinate with district authorities and hospitals.
5. Retry AI intelligence after API quota resets.
"""

        return f"""## INCIDENT ASSESSMENT
API Error occurred while generating intelligence.

## WEATHER INTELLIGENCE
Unavailable due to API error.

## MEDICAL OPERATIONS
Unavailable due to API error.

## STRATEGIC RESPONSE PLAN
Error details: {error_text}
"""

    except Exception as e:
        return f"""## INCIDENT ASSESSMENT
Unexpected system error while generating incident intelligence.

## WEATHER INTELLIGENCE
Unavailable.

## MEDICAL OPERATIONS
Unavailable.

## STRATEGIC RESPONSE PLAN
System error details: {str(e)}
"""

# =========================================================
# Parse AI sections
# =========================================================
def parse_ai_sections(ai_text):
    sections = {
        "incident": "Incident assessment unavailable.",
        "weather": "Weather intelligence unavailable.",
        "medical": "Medical operations unavailable.",
        "strategy": "Strategic response plan unavailable."
    }

    if not ai_text or not isinstance(ai_text, str):
        return sections

    text = ai_text.strip()

    markers = {
        "incident": "## INCIDENT ASSESSMENT",
        "weather": "## WEATHER INTELLIGENCE",
        "medical": "## MEDICAL OPERATIONS",
        "strategy": "## STRATEGIC RESPONSE PLAN"
    }

    try:
        incident_start = text.find(markers["incident"])
        weather_start = text.find(markers["weather"])
        medical_start = text.find(markers["medical"])
        strategy_start = text.find(markers["strategy"])

        if incident_start != -1 and weather_start != -1:
            sections["incident"] = text[
                incident_start + len(markers["incident"]):weather_start
            ].strip()

        if weather_start != -1 and medical_start != -1:
            sections["weather"] = text[
                weather_start + len(markers["weather"]):medical_start
            ].strip()

        if medical_start != -1 and strategy_start != -1:
            sections["medical"] = text[
                medical_start + len(markers["medical"]):strategy_start
            ].strip()

        if strategy_start != -1:
            sections["strategy"] = text[
                strategy_start + len(markers["strategy"]):
            ].strip()

    except Exception:
        pass

    return sections

# =========================================================
# Coordinator Agent
# =========================================================
def coordinator_agent(location, disaster, people, injuries):
    valid, msg = validate_inputs(location, disaster, people, injuries)
    if not valid:
        raise ValueError(msg)

    risk = calculate_risk(disaster, people, injuries)
    resources = resource_agent(people)
    hospital_capacity = hospital_capacity_agent(people, injuries, risk)

    intelligence = unified_intelligence_agent(
        location,
        disaster,
        people,
        injuries,
        risk
    )

    ai_sections = parse_ai_sections(intelligence)

    final_report = f"""
==================================================
🚨 ResQAI Emergency Response Report
==================================================

📍 Location: {location}
🌪 Disaster: {disaster}
👥 People Affected: {people}
🏥 Medical Situation: {injuries}
🚨 Risk Level: {risk}

==================================================
📦 RESOURCE REQUIREMENTS
==================================================
{resources}

==================================================
🏥 HOSPITAL CAPACITY ANALYSIS
==================================================
{hospital_capacity}

==================================================
🤖 INCIDENT ASSESSMENT
==================================================
{ai_sections['incident']}

==================================================
🌦 WEATHER INTELLIGENCE
==================================================
{ai_sections['weather']}

==================================================
🏥 MEDICAL OPERATIONS
==================================================
{ai_sections['medical']}

==================================================
🧭 STRATEGIC RESPONSE PLAN
==================================================
{ai_sections['strategy']}
"""

    return {
        "risk": risk,
        "resources": resources,
        "hospital_capacity": hospital_capacity,
        "mission": intelligence,
        "report": final_report,
        "incident": ai_sections["incident"],
        "weather": ai_sections["weather"],
        "medical": ai_sections["medical"],
        "strategy": ai_sections["strategy"]
    }

# =========================================================
# Helper UI formatters
# =========================================================
def format_resource_output(resource_text):
    if not resource_text or str(resource_text).strip() == "":
        return "📦 Resource estimation unavailable."
    return str(resource_text)

def format_report_output(report_text):
    if not report_text or str(report_text).strip() == "":
        return "📄 Emergency report unavailable."
    return str(report_text)

def get_risk_card(risk_text):
    risk_upper = str(risk_text).strip().upper()

    if "HIGH" in risk_upper:
        return """
        <div class="risk-card high-risk">
            <div class="risk-title">🔴 HIGH RISK</div>
            <div class="risk-subtitle">Immediate emergency response required</div>
        </div>
        """
    elif "MEDIUM" in risk_upper:
        return """
        <div class="risk-card medium-risk">
            <div class="risk-title">🟠 MEDIUM RISK</div>
            <div class="risk-subtitle">Situation serious — controlled response needed</div>
        </div>
        """
    elif "LOW" in risk_upper:
        return """
        <div class="risk-card low-risk">
            <div class="risk-title">🟢 LOW RISK</div>
            <div class="risk-subtitle">Situation currently manageable</div>
        </div>
        """
    else:
        return f"""
        <div class="risk-card medium-risk">
            <div class="risk-title">⚠ UNKNOWN RISK</div>
            <div class="risk-subtitle">{risk_text}</div>
        </div>
        """

# =========================================================
# Main launcher
# =========================================================
def launch_resqai(location, disaster, people, injuries):
    try:
        if not str(location).strip():
            raise ValueError("Location is required.")

        if people is None or str(people).strip() == "":
            raise ValueError("People affected is required.")

        people = int(people)

        if people <= 0:
            raise ValueError("People affected must be greater than 0.")

        if not str(disaster).strip():
            raise ValueError("Disaster type is required.")

        if not str(injuries).strip():
            raise ValueError("Medical situation is required.")

        result = coordinator_agent(
            location=location.strip(),
            disaster=str(disaster).strip(),
            people=people,
            injuries=injuries.strip()
        )

        risk = result.get("risk", "Unknown")
        resources = result.get("resources", "No resources generated.")
        hospital_capacity = result.get("hospital_capacity", "Hospital capacity analysis unavailable.")
        report = result.get("report", "No report generated.")
        incident = result.get("incident", "Incident assessment unavailable.")
        weather = result.get("weather", "Weather intelligence unavailable.")
        medical = result.get("medical", "Medical operations unavailable.")
        strategy = result.get("strategy", "Strategic response plan unavailable.")

        risk_html = get_risk_card(risk)
        resources_text = format_resource_output(resources)
        report_text = format_report_output(report)

        ai_combined = f"""{incident}\n{weather}\n{medical}\n{strategy}"""
        ai_engine_status = "🟢 AI Intelligence Engine: Active"

        mission_upper = ai_combined.upper()
        if "QUOTA" in mission_upper or "429" in mission_upper:
            ai_engine_status = "🟠 AI Intelligence Engine: Quota limited / fallback response used"
        elif "API ERROR" in mission_upper or "UNEXPECTED ERROR" in mission_upper:
            ai_engine_status = "🔴 AI Intelligence Engine: Error in Gemini response"

        system_status = f"""
🟢 Input Validation: Active
🟢 Risk Engine: Active
🟢 Resource Engine: Active
🟢 Coordinator Engine: Active
{ai_engine_status}
🟢 Report Generator: Active
"""

        return (
            risk_html,
            resources_text,
            hospital_capacity,
            incident,
            weather,
            medical,
            strategy,
            report_text,
            system_status
        )

    except Exception as e:
        error_html = """
<div class="risk-card medium-risk">
    <div class="risk-title">⚠ SYSTEM ERROR</div>
    <div class="risk-subtitle">Please check the input, backend function, or API quota</div>
</div>
"""
        error_message = str(e)
        error_report = f"❌ Error in report generation:\n{error_message}"

        return (
            error_html,
            f"❌ Error in resource generation:\n{error_message}",
            f"❌ Hospital capacity analysis error:\n{error_message}",
            f"❌ Incident assessment error:\n{error_message}",
            f"❌ Weather intelligence error:\n{error_message}",
            f"❌ Medical operations error:\n{error_message}",
            f"❌ Strategic response error:\n{error_message}",
            error_report,
            f"🔴 System Status: Error\n\n{error_message}"
        )

# =========================================================
# CSS
# =========================================================
custom_css = """
body {
    background: linear-gradient(180deg, #07111f 0%, #0b1220 100%);
}

.gradio-container {
    max-width: 1450px !important;
    margin: auto;
    background: transparent !important;
}

.main-wrap {
    padding: 10px 8px 20px 8px;
}

.hero-box {
    text-align: center;
    background: linear-gradient(135deg, #0f172a, #111827);
    border: 1px solid #24334d;
    border-radius: 22px;
    padding: 24px 18px 20px 18px;
    box-shadow: 0 0 25px rgba(0, 229, 255, 0.10);
    margin-bottom: 18px;
}

.hero-logo {
    font-size: 46px;
    margin-bottom: 8px;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    color: #00E5FF;
    margin-bottom: 6px;
}

.hero-subtitle {
    font-size: 20px;
    color: #dbeafe;
    font-weight: 600;
    margin-bottom: 4px;
}

.hero-tagline {
    font-size: 16px;
    color: #a5b4fc;
}

.section-heading {
    font-size: 26px;
    font-weight: 800;
    color: #ffffff;
    margin: 6px 0 10px 0;
}

.risk-card {
    border-radius: 18px;
    padding: 20px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 0 22px rgba(0,0,0,0.22);
    margin-bottom: 8px;
}

.high-risk {
    background: linear-gradient(135deg, #3b0a0a, #7f1d1d);
    border: 1px solid #ef4444;
    color: #fff;
}

.medium-risk {
    background: linear-gradient(135deg, #3a2605, #7c2d12);
    border: 1px solid #f59e0b;
    color: #fff;
}

.low-risk {
    background: linear-gradient(135deg, #052e16, #14532d);
    border: 1px solid #22c55e;
    color: #fff;
}

.risk-title {
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 8px;
}

.risk-subtitle {
    font-size: 15px;
    color: #f8fafc;
}

.footer-box {
    text-align: center;
    color: #cbd5e1;
    font-size: 15px;
    padding: 18px;
    margin-top: 10px;
}

.footer-box b {
    color: #ffffff;
}

textarea {
    font-size: 15px !important;
}

@media (max-width: 768px) {
    .hero-title {
        font-size: 34px;
    }
    .hero-subtitle {
        font-size: 18px;
    }
    .section-heading {
        font-size: 22px;
    }
    .risk-title {
        font-size: 24px;
    }
}
"""

# =========================================================
# UI
# =========================================================
with gr.Blocks(
    title="🚨 ResQAI - AI Emergency Command Center",
    theme=gr.themes.Soft(primary_hue="blue", secondary_hue="indigo"),
    css=custom_css
) as demo:

    gr.HTML("""
    <div class="main-wrap">
        <div class="hero-box">
            <div class="hero-logo">🚨</div>
            <div class="hero-title">ResQAI</div>
            <div class="hero-subtitle">AI Emergency Command Center</div>
            <div class="hero-tagline">Google × Kaggle Capstone Project</div>
        </div>
    </div>
    """)

    with gr.Row(equal_height=True):
        with gr.Column(scale=4):
            gr.HTML('<div class="section-heading">📍 Incident Information</div>')

            with gr.Group():
                location = gr.Textbox(label="📍 Location", placeholder="Example: Kolkata")

                disaster = gr.Dropdown(
                    choices=["Earthquake", "Flood", "Cyclone", "Landslide", "Wildfire", "Tsunami", "Eruption"],
                    label="🌪 Disaster Type",
                    value="Earthquake"
                )

                people = gr.Number(label="👥 People Affected", value=100, precision=0)

                injuries = gr.Textbox(
                    label="🏥 Medical Situation",
                    placeholder="Example: fractures, bleeding, trapped civilians, burnt, dehydration...",
                    lines=5
                )

            analyze_btn = gr.Button("🚀 Analyze Emergency", variant="primary", size="lg")

            gr.HTML("<br>")
            gr.HTML('<div class="section-heading">🟢 System Status</div>')

            system_status = gr.Textbox(label="🛠 Engine Health", lines=7, interactive=False)

        with gr.Column(scale=5):
            gr.HTML('<div class="section-heading">🚨 Live Emergency Status</div>')

            risk_html = gr.HTML()

            resources = gr.Textbox(label="📦 Resource Command Center", lines=12, interactive=False)

            hospital_box = gr.Textbox(label="🏥 Hospital Capacity & Triage", lines=14, interactive=False)

    gr.HTML("<br>")

    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            incident_box = gr.Textbox(label="📍 Incident Assessment", lines=8, interactive=False)
            weather_box = gr.Textbox(label="🌦 Weather Intelligence", lines=8, interactive=False)

        with gr.Column(scale=1):
            medical_box = gr.Textbox(label="🏥 Medical Operations", lines=8, interactive=False)
            strategy_box = gr.Textbox(label="🧭 Strategic Response Plan", lines=8, interactive=False)

    gr.HTML("<br>")

    report = gr.Textbox(label="📄 Complete Emergency Report", lines=18, interactive=False)

    analyze_btn.click(
        fn=launch_resqai,
        inputs=[location, disaster, people, injuries],
        outputs=[
            risk_html,
            resources,
            hospital_box,
            incident_box,
            weather_box,
            medical_box,
            strategy_box,
            report,
            system_status
        ]
    )

    gr.HTML("""
    <div class="footer-box">
        🚨 Built with ❤️ using Google Gemini AI • Gradio • Python
        <br><br>
        Developed by <b>Ashfaque Ahamed Khan</b>
    </div>
    """)

demo.launch()