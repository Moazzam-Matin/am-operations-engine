-# am-operations-engine
-Creator monetization &amp; revenue audit system
+# A&M Operations Engine
+
+A Flask-based monetization audit tool for Instagram creators. The app combines a deterministic revenue model with an AI-generated strategy report, and lets users export a branded PDF audit.
+
+## Features
+
+- **Revenue potential calculator** based on followers and engagement rate.
+- **AI monetization strategy generation** using Google Gemini (`gemini-2.5-flash`).
+- **Section parsing** for structured AI output blocks.
+- **Web dashboard** for entering creator metrics and viewing results.
+- **PDF export** of the monetization audit with branding.
+
+## Tech Stack
+
+- **Backend:** Python, Flask
+- **AI:** `google-generativeai`
+- **PDF Generation:** ReportLab
+- **Frontend:** Jinja2 templates, embedded CSS
+- **Config:** `python-dotenv`
+
+## Project Structure
+
+```text
+.
+├── app.py
+├── requirements.txt
+├── README.md
+├── static/
+│   ├── logo.png
+│   └── images/
+│       └── logo.png
+└── templates/
+    └── index.html
+```
+
+## Prerequisites
+
+- Python 3.10+
+- A Google Gemini API key
+
+## Setup
+
+1. **Clone and enter the repository**
+   ```bash
+   git clone <your-repo-url>
+   cd am-operations-engine
+   ```
+
+2. **Create and activate a virtual environment**
+   ```bash
+   python -m venv .venv
+   source .venv/bin/activate
+   ```
+
+3. **Install dependencies**
+   ```bash
+   pip install -r requirements.txt
+   ```
+
+4. **Configure environment variables**
+
+   Create a `.env` file in the project root:
+
+   ```env
+   GEMINI_API_KEY=your_api_key_here
+   PORT=5000
+   ```
+
+## Running the App
+
+Start the Flask server:
+
+```bash
+python app.py
+```
+
+Then open your browser at:
+
+- `http://localhost:5000`
+
+## How It Works
+
+1. User submits:
+   - Instagram handle
+   - Follower count
+   - Engagement rate (%)
+2. The app computes expected revenue across low, mid, and high ticket offer tiers.
+3. The app requests a structured monetization audit from Gemini.
+4. The UI displays total revenue and AI strategy output.
+5. User can download a PDF report of the audit.
+
+## Revenue Model Assumptions
+
+The calculator uses these default tiers:
+
+- **Low ticket:** `$49` @ `4%` conversion
+- **Mid ticket:** `$299` @ `0.8%` conversion
+- **High ticket:** `$2500` @ `0.1%` conversion
+
+`active_engagers = followers * (engagement_rate / 100)`
+
+Each tier estimates buyers from active engagers and sums tier revenues into a total projected value.
+
+## API / Routes
+
+- `GET /` - Render dashboard.
+- `POST /` - Run revenue calculation + AI strategy generation.
+- `POST /download` - Generate and return the PDF audit.
+
+## Notes & Limitations
+
+- The AI strategy quality depends on prompt adherence and API output consistency.
+- API errors are not yet surfaced with user-friendly error states.
+- Input validation is minimal (form-level); robust server-side validation can be added.
+- This project currently targets Instagram-based creator assumptions in the prompt.
+
+## Future Improvements
+
+- Add validation and graceful error handling for API/PDF failures.
+- Format AI section output as rich cards instead of raw text.
+- Add automated tests for calculator and parser logic.
+- Add authentication and persistent audit history.
+
+## License
+
+No license is currently specified. Add a `LICENSE` file if you plan to distribute this project.

