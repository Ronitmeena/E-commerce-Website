from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

def init_db():
    if not os.path.exists("database.db"):
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
        c.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER)")
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('test', '123'))
        c.executemany("INSERT INTO products (name, price) VALUES (?, ?)", [
            ('Nike Shoes', 3499),
            ('Puma Hoodie', 2599),
            ('Apple Watch', 18999),
            ('Gaming Mouse', 1499),
            ('Laptop Stand', 799),
            ('Leather Wallet', 1199),
        ])
        conn.commit()
        conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                  (request.form["username"], request.form["password"]))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", 
                  (request.form["username"], request.form["password"]))
        user = c.fetchone()
        conn.close()
        if user:
            session["user"] = user[1]
            return redirect("/products")
        else:
            return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/products")
def products():
    if "user" not in session:
        return redirect("/login")
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    items = c.fetchall()
    conn.close()
    return render_template("products.html", items=items)

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(product_id)
    return redirect("/products")

@app.route("/cart")
def cart():
    if "cart" not in session or not session["cart"]:
        return render_template("cart.html", items=[], total=0)
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    placeholders = ','.join(['?'] * len(session["cart"]))
    c.execute(f"SELECT * FROM products WHERE id IN ({placeholders})", tuple(session["cart"]))
    items = c.fetchall()
    total = sum(item[2] for item in items)
    conn.close()
    return render_template("cart.html", items=items, total=total)

@app.route("/checkout")
def checkout():
    session.pop("cart", None)
    return render_template("checkout.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
