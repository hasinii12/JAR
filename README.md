# Jar — Growth Intern Assignment Dashboard

An interactive Streamlit dashboard covering all three assignment questions:
- **Part 1–3 (Q1):** Category profitability, Furniture target trends, regional performance
- **Q2:** Jar app exploration (what works / what to improve)
- **Q3:** New business opportunity recommendations

## Files needed (all in the same folder)
- `app.py`
- `List_of_Orders.xlsx`
- `Order_Details.xlsx`
- `Sales_target.xlsx`
- `requirements.txt`

## How to run

1. Open a terminal in this folder.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Launch the dashboard:
   ```
   streamlit run app.py
   ```
4. It will automatically open in your browser at `http://localhost:8501`.
   If it doesn't open automatically, copy that URL into your browser manually.

To stop the app, go back to the terminal and press `Ctrl + C`.

## Also included
- `jar_sales_analysis.py` — the plain Python/pandas script behind the numbers (no dashboard, just printed output — useful to show the raw analysis logic).
- `Jar_Growth_Intern_Assignment_Hasini.docx` — the written report version, if a document is preferred/required for submission instead of (or alongside) the dashboard.
