from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
import yaml

# 設定ファイルからエンドポイントとキーを読み込む
def load_settings(yaml_path="setting.yml"):
    with open(yaml_path, "r", encoding="utf-8") as f:
        settings = yaml.safe_load(f)
    return settings["face"]["endpoint"], settings["face"]["key"]

# endpoint, key をsetting.ymlから取得
endpoint, key = load_settings()

# FaceClientの初期化
face_client = FaceClient(endpoint, CognitiveServicesCredentials(key))

# 画像ファイル（ローカル画像パスまたは URL）
image_path1 = r"path/to/image1.jpg"
image_path2 = r"path/to/image2.jpg"

# 画像1の顔を検出
try:
    with open(image_path1, 'rb') as img1:
        detected_faces1 = face_client.face.detect_with_stream(
            img1
        )
        if not detected_faces1:
            raise Exception("No face detected in image 1")
        face_id1 = detected_faces1[0].face_id
except Exception as e:
    print(f"Error detecting face in image 1: {e}")
    raise

# 画像2の顔を検出
try:
    with open(image_path2, 'rb') as img2:
        detected_faces2 = face_client.face.detect_with_stream(
            img2,
            detection_model="detection_03",
            return_face_id=True
        )
        if not detected_faces2:
            raise Exception("No face detected in image 2")
        face_id2 = detected_faces2[0].face_id
except Exception as e:
    print(f"Error detecting face in image 2: {e}")
    raise

# 顔を比較（verify）
verify_result = face_client.face.verify_face_to_face(face_id1, face_id2)

# 結果出力
print(f"Is same person: {verify_result.is_identical}")
print(f"Confidence: {verify_result.confidence}")
