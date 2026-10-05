from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/test', methods=['POST'])
def test_post():
    return jsonify({'success': True, 'message': 'POST请求成功'})

@app.route('/api/test', methods=['GET'])
def test_get():
    return jsonify({'success': True, 'message': 'GET请求成功'})

if __name__ == '__main__':
    app.run(port=8001, debug=True)
