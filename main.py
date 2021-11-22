from flask import Flask

main = Flask(__name__)


@main.route('/api/v1/hello-world{29}')
def hello_world():
    return 'Hello World{29}'



if __name__ == '__main__':
    main.run(debug=True)
