from flask import Flask, render_template, request
from services.ai_service import analyze_wellbeing

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        mood = request.form.get("mood")
        text = request.form.get("feeling")

        result = analyze_wellbeing(mood, text)
        return render_template("result.html", result=result)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

