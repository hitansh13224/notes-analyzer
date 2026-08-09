# Index — running Timetable + Chat locally

The Summary/Flashcards/Quiz tab works on its own (it calls Anthropic's API,
which is handled automatically). **Timetable** and **Chat** call Groq
instead, so they need the small backend in `app.py` running next to
`index.html` — this keeps your Groq key on the server instead of in the
page's source.

## Setup

1. Put `index.html`, `app.py`, and `requirements.txt` in the same folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Groq key as an environment variable (don't hardcode it in the
   file — rotate your old key in the Groq console since it was briefly
   exposed client-side):
   ```bash
   export GROQ_API_KEY="your-key-here"       # macOS/Linux
   set GROQ_API_KEY=your-key-here            # Windows (cmd)
   $env:GROQ_API_KEY="your-key-here"         # Windows (PowerShell)
   ```
4. Run it:
   ```bash
   python app.py
   ```
5. Open **http://localhost:5000** in your browser (not the raw HTML file —
   it needs to be served by Flask so `/api/groq` resolves).

Timetable and Chat will now work; the Groq key never appears in the page
you send to a browser, only in your server process.
