#######################################
#
# Name : video_stream_flask.py
#
# Author : Hakim CHERIF - M69710 <hakim.cherif@microchip.com>
#
# Description :
#   File that controls the webserver and the live video stream. And the displaying of the result
#######################################


# Copyright (C) 2022 Microchip Technology Inc.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
import time
from subprocess import PIPE
from flask import Flask, Response, render_template
import cv2

import logging



VERBOSE_DEBUG=0

if not VERBOSE_DEBUG:
  log = logging.getLogger('werkzeug')
  log.setLevel(logging.ERROR)

def get_current_ip():
  """
  Get current IP Address by testing IP route
  """
  process_get_ip = subprocess.Popen(["ip route get 1.2.3.4 | awk '{print $7}'"], shell=True, stdout=PIPE)
  output = process_get_ip.communicate()[0].decode("utf-8")
  return output


ip_address = get_current_ip()[:-2]
if VERBOSE_DEBUG:
  print("ip address=", repr(ip_address))
  print("type : ", type(ip_address))

app = Flask(__name__)

video = cv2.VideoCapture(cv2.CAP_V4L2)


@app.route('/')
def index():
  return render_template("index.html")


def gen(video):
  i = 10
  while True:
    success, image = video.read()
    ret, jpeg = cv2.imencode('.jpg', image)
    frame = jpeg.tobytes()
    if i == 10:
      cv2.imwrite("img.png", image)
      i = 0
    i = i + 1
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def result_read():
  with open("result.txt", "r") as f:
    content = f.read()
    yield content
    f.close()


@app.route('/video_feed')
def video_feed():
  global video
  return Response(gen(video),
                  mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/result_text')
def result_text():
  return Response(result_read(), mimetype='text')


print("\nCONNECT TO : " + repr(ip_address)[1:-1] + ":5000")
print("")


def main():
  app.run(host=ip_address, port=5000, threaded=True)


if __name__ == '__main__':
  main()
