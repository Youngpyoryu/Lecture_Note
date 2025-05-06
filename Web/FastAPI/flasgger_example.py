from flask import Flask, request, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)  # Swagger UI 자동 활성화

@app.route('/add', methods=['GET'])
def add():
    """
    덧셈 API
    ---
    parameters:
      - name: a
        in: query
        type: number
        required: true
        description: 첫 번째 숫자
      - name: b
        in: query
        type: number
        required: true
        description: 두 번째 숫자
    responses:
      200:
        description: 두 숫자의 합 결과
        examples:
          application/json: {"result": 15}
    """
    a = float(request.args.get("a"))
    b = float(request.args.get("b"))
    return jsonify({"result": a + b})

if __name__ == '__main__':
    app.run(debug=True)

