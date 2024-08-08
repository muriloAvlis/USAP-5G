from flask import Flask, jsonify

app = Flask("usap-enc-dec-api")


@app.route("/usap/api/v1/health", methods=["GET"])
def root():
    return jsonify({
        "status": "healthy",
        "message": "API is up and running"
    }), 200


def run():
    app.run(debug=True, port=8081)


if __name__ == '__main__':
    run()
