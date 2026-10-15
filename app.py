from flask import Flask, render_template, request, redirect, Response
import csv
import io
import os

app = Flask(__name__)

# Sample prices only; these are not live market prices.
stocks = {
    "AAPL": 180,
    "TSLA": 250,
    "GOOGL": 150,
    "MSFT": 420
}

portfolio = []
next_id = 1


@app.route("/", methods=["GET", "POST"])
def home():
    global next_id

    if request.method == "POST":
        stock = request.form.get("stock", "")
        quantity_text = request.form.get("quantity", "")

        try:
            quantity = int(quantity_text)
        except (TypeError, ValueError):
            quantity = 0

        if stock in stocks and quantity > 0:
            portfolio.append({
                "id": next_id,
                "name": stock,
                "price": stocks[stock],
                "quantity": quantity,
                "investment": stocks[stock] * quantity
            })
            next_id += 1

        return redirect("/")

    total = sum(item["investment"] for item in portfolio)
    return render_template(
        "index.html",
        stocks=stocks,
        portfolio=portfolio,
        total=total
    )


@app.route("/remove/<int:stock_id>", methods=["POST"])
def remove_stock(stock_id):
    global portfolio
    portfolio = [item for item in portfolio if item["id"] != stock_id]
    return redirect("/")


@app.route("/export")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Stock", "Price", "Quantity", "Investment"])

    for item in portfolio:
        writer.writerow([
            item["name"],
            item["price"],
            item["quantity"],
            item["investment"]
        ])

    writer.writerow(["Total", "", "", sum(item["investment"] for item in portfolio)])
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=stock_portfolio.csv"
    return response


if __name__ == "__main__":
    # Uses the hosting provider's port when deployed, or 5000 locally.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
