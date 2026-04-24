import os
import json
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

from pipeline import AgentPipeline
from chart_generator import generate_charts

# ✅ BASE + CHARTS DIR (ADDED HERE)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

app = Flask(__name__)

# Upload folder
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALLOWED_EXTENSIONS = {"csv"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# 🔥 JSON SAFE CONVERTER
def convert_numpy(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)


@app.route("/")
def index():
    return render_template("index.html")


# ✅ FIXED: using CHARTS_DIR
@app.route("/charts/<filename>")
def serve_chart(filename):
    return send_from_directory(CHARTS_DIR, filename)


@app.route("/analyze", methods=["POST"])
def analyze():

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only CSV files are supported"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    print(f"\n[Backend] Received file: {filename}")

    # Read CSV
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        return jsonify({"error": f"CSV read error: {str(e)}"}), 422

    # Run pipeline
    try:
        pipeline = AgentPipeline()
        result = pipeline.run(df)
    except Exception as e:
        return jsonify({"error": f"Pipeline error: {str(e)}"}), 500

    # Generate charts
    try:
        chart_files = generate_charts(result["data"], result["chart_suggestions"])
    except Exception as e:
        chart_files = []
        print(f"[Chart Error]: {e}")

    overview = result.get("overview", {})

    numeric_stats_list = []
    for col, stats in result.get("numeric_stats", {}).items():
        numeric_stats_list.append({
            "column": col,
            **stats
        })

    response = {
        "success": True,
        "filename": filename,
        "overview": {
            "rows": overview.get("total_rows", 0),
            "columns": overview.get("total_columns", 0),
            "numeric_columns": overview.get("numeric_cols", []),
            "categorical_columns": overview.get("categorical_cols", []),
        },
        "insights": result.get("insights", []),
        "numeric_stats": numeric_stats_list,
        "charts": chart_files,
        "agent_logs": {
            "cleaning": result.get("cleaning_log", []),
            "analysis": result.get("analysis_log", []),
            "insights": result.get("insight_log", []),
        }
    }

    # 🔥 FINAL SAFE JSON RESPONSE
    return app.response_class(
        response=json.dumps(response, default=convert_numpy),
        mimetype='application/json'
    )


if __name__ == "__main__":
    print("\n🚀 AI Data Analyst Agent is running!")
    print("   Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True, port=5000)