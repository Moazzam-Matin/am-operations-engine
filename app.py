import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, make_response
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from flask import send_file

load_dotenv()



# Setup the new client with your API key from the screenshot
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)


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
def get_ai_strategy(handle, followers):
    prompt = f"""
    You are the Lead Monetization Strategist at A&M Operations.

    Analyze Instagram creator {handle} with {followers} followers.

    Deliver:
    1. Three pain-to-identity transformations already visible in their content.
    2. The specific mechanism they demonstrate (not motivation, not mindset).
    3. One digital product per transformation with:
       - Product type
       - Outcome promise
       - Ideal price tier (low / mid / high)

    Be concise.
    No generic advice.
    No fluff.
    """

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text


# --- MAIN DASHBOARD ---
@app.route('/', methods=['GET', 'POST'])
def dashboard():
    stats = None
    handle = None
    ai_text = None  # Initialize this so the page doesn't crash

    if request.method == 'POST':
        handle = request.form.get('handle')
        followers = float(request.form.get('followers'))
        er = float(request.form.get('er'))
        stats = calculate_revenue_potential(followers, er)


        # 2. Run the AI Strategy (New Line)
        ai_text = get_ai_strategy(handle, followers)

    return render_template('index.html', stats=stats, handle=handle, ai_text=ai_text)


# --- STEP 4: THE PDF EXPORTER ---
@app.route("/download", methods=["POST"])
def download():
    handle = request.form.get("handle")
    revenue = request.form.get("revenue")
    ai_summary = request.form.get("ai_summary", "")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50

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