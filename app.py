from flask import Flask

app = Flask(__name__)


@app.route('/api/v1/hello-world{29}')
def hello_world():
    return 'Hello World{29}'





if __name__ == '__main__':
    app.run(debug=True)
