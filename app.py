import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, make_response
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from flask import send_file
from reportlab.lib.utils import ImageReader

load_dotenv()



# Setup the new client with your API key from the screenshot
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
"""
# ------Helper function for AI-------#
def parse_ai_sections(text):
    sections = {}
    current_section = None

    for line in text.splitlines():
        line = line.strip()

        if line.startswith("===") and line.endswith("==="):
            current_section = line.replace("=", "").strip()
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line)

    # Join lines back into clean text
    for key in sections:
        sections[key] = "\n".join(sections[key]).strip()

    return sections
    """

# --- STEP 2 LOGIC: THE CALCULATOR ---
def calculate_revenue_potential(followers, engagement_rate):
    active_engagers = followers * (engagement_rate / 100)

    tiers = {
        "low_ticket": {
            "price": 49,
            "conversion": 0.04
        },
        "mid_ticket": {
            "price": 299,
            "conversion": 0.008
        },
        "high_ticket": {
            "price": 2500,
            "conversion": 0.001
        }
    }

    results = {}
    total_revenue = 0

    for tier, data in tiers.items():
        buyers = active_engagers * data["conversion"]
        revenue = buyers * data["price"]
        total_revenue += revenue

        results[tier] = {
            "buyers": int(buyers),
            "revenue": f"${revenue:,.2f}"
        }

    results["total"] = f"${total_revenue:,.2f}"
    return results


# ----The Strategy funtion uses genai ---
def get_ai_strategy(handle, followers, engagement):
    prompt = f"""
    You are a monetisation strategist who builds revenue systems for content creators.

    Create a structured Monetisation Audit.
    Write clearly, confidently, and like a consultant.
    Avoid generic advice.

    CREATOR DETAILS
    - Platform: Instagram
    - Handle: {handle}
    - Followers: {followers}
    - Engagement Rate: {engagement}%

    OUTPUT FORMAT (FOLLOW EXACTLY):

    === CREATOR_OVERVIEW ===
    Identified Niche:
    Hidden Transformation:

    === DEMAND_ANALYSIS ===
    Theme 1:
    Observed Engagement:
    Sales Potential:

    Theme 2:
    Observed Engagement:
    Sales Potential:

    Theme 3:
    Observed Engagement:
    Sales Potential:

    Verdict:

    === NUMBERS ===
    Follower Base:
    Assumed Product Price:
    Engagement Rate:
    Conversion Rate:
    Revenue Potential:
    Explanation:

    === PRODUCT_SUGGESTIONS ===
    Option 1 (The Big Bet):
    What it is:
    Who it is for:
    Why it works:

    Option 2:
    What it is:
    Who it is for:
    Why it works:

    Option 3:
    What it is:
    Who it is for:
    Why it works:

    === IMPLEMENTATION_PLAN ===
    Phase 1 (Days 1–3):
    Phase 2 (Days 4–9):
    Phase 3 (Days 10–14):

    === VALIDATION_CAROUSEL ===
    Slide 1 (Hook):
    Slide 2 (Agitation):
    Slide 3 (Call to Action):
    """

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    ai_text = response.text
    print("===== AI TEXT START =====")
    print(ai_text)
    print("===== AI TEXT END =====")

    #sections = parse_ai_sections(ai_text)

    return sections


# --- MAIN DASHBOARD ---
@app.route('/', methods=['GET', 'POST'])
def dashboard():
    stats = None
    handle = None
    ai_sections = None  # Initialize this so the page doesn't crash

    if request.method == 'POST':
        handle = request.form.get('handle')
        followers = float(request.form.get('followers'))
        er = float(request.form.get('er'))
        stats = calculate_revenue_potential(followers, er)


        # 2. Run the AI Strategy (New Line)
        ai_text = get_ai_strategy(handle, followers, er)
        ai_sections = ai_text

    return render_template(
        'index.html',
        stats=stats,
        handle=handle,
        ai_sections=ai_sections
    )


# --- STEP 4: THE PDF EXPORTER ---
@app.route("/download", methods=["POST"])
def download():
    handle = request.form.get("handle")
    revenue = request.form.get("revenue")
    ai_summary = request.form.get("ai_summary", "")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 100

    # ---- ADD LOGO ----
    logo_path = os.path.join("static", "logo.png")

    logo_width = 80  # adjust if needed
    logo_height = 40  # adjust if needed

    c.drawImage(
        logo_path,
        40,  # X position (left margin)
        height - 50,  # Y position (top)
        width=logo_width,
        height=logo_height,
        mask='auto'  # THIS keeps transparency
    )

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "A&M OPERATIONS")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Revenue Audit for: {handle}")
    y -= 30

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Potential Revenue: {revenue}")
    y -= 40

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Monetization Strategy")
    y -= 20

    c.setFont("Helvetica", 10)
    for line in ai_summary.split("\n"):
        c.drawString(50, y, line)
        y -= 14
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 50

    c.showPage()
    c.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Audit_{handle}.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)