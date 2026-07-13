from flask import Flask, jsonify, request
import psycopg2
from prometheus_flask_exporter import PrometheusMetrics
import os


app = Flask(__name__)

metrics = PrometheusMetrics(app)


def get_db_connection():
    return psycopg2.connect(
        host="postgres",
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


@app.route("/")
def home():
    return "DevOps HomeLab API"


@app.route("/users", methods=["GET"])
def get_users():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name, email FROM users;"
    )

    users = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(users)


@app.route("/users", methods=["POST"])
def add_user():

    data = request.json

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users(name,email)
        VALUES(%s,%s)
        """,
        (
            data["name"],
            data["email"]
        )
    )

    conn.commit()

    cur.close()
    conn.close()

    return {
        "status": "created"
    }


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
