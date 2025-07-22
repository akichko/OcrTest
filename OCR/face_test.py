# !/usr/bin/python
# coding: UTF-8

from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
import sys

# キーとエンドポイントを設定する
KEY = "api_key_here"
ENDPOINT = "https://xxxxx.cognitiveservices.azure.com/"
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

if len(sys.argv) < 2:
    print("Usage: python face_test.py <image_path>")
    sys.exit(1)

image_path = sys.argv[1]

# 画像を分析する
with open(image_path, 'rb') as img:
    detected_faces = face_client.face.detect_with_stream(
        img,
        detection_model="detection_01",  # 必須
        return_face_id=True
    )

# 分析結果を表示する
for idx, face in enumerate(detected_faces):
    print(f"----- Detection result: #{idx+1} -----")
    print(face.as_dict())