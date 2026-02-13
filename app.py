import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, make_response
import pdfkit
import google.generativeai as genai

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

    model = genai.GenerativeModel("gemini-1.5-flash")
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
@app.route('/download', methods=['POST'])
def download():
    handle = request.form.get('handle')
    revenue = request.form.get('revenue')
    ai_summary = request.form.get('ai_summary')

    # Path to your installed wkhtmltopdf engine
    path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    # The Document Template
    html_content = f"""
    <html>
        <body style="font-family: Arial; padding: 50px; border: 5px solid black;">
            <h1 style="text-align: center;">A&M OPERATIONS</h1>
            <hr>

            <h2>REVENUE AUDIT FOR: {handle}</h2>
            <p>Based on our proprietary analysis of your ecosystem's engagement metrics.</p>

            <h1 style="color: green; font-size: 40px;">
                Potential: {revenue}
            </h1>

            <p>This floor represents uncaptured value ready for systemization.</p>

            <hr style="margin:40px 0;">

            <h3>Monetization Strategy Overview</h3>
            <div style="
                background:#f4f4f4;
                padding:20px;
                border-left:5px solid #00aa88;
                white-space: pre-wrap;
                font-size:14px;
            ">
                {ai_summary}
            </div>

            <footer style="margin-top: 80px; font-size:12px;">
                Confidential Document – 2026
            </footer>
        </body>
    </html>
    """

    pdf = pdfkit.from_string(html_content, False, configuration=config)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Audit_{handle}.pdf'
    return response


if __name__ == '__main__':
    app.run(debug=True, port=5000)