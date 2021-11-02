
from flask import Flask, render_template, Response, request
from robot import Robot

app = Flask(__name__)
r = Robot()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/livestream')
def livestream():
    return Response(r.camera.gen_videostream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
