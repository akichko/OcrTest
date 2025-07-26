from PIL import Image
import io
import json

def get_image_size(img_bytes: bytes) -> str:
	try:
		img = Image.open(io.BytesIO(img_bytes))
		width, height = img.size
		file_size = len(img_bytes)
		result = {"width": width, "height": height, "file_size": file_size}
		ret = json.dumps(result)
		return ret

	except Exception as e:
		raise
		
if __name__ == "__main__":
	with open("./test/sample.gif", "rb") as f:
		img_bytes = f.read()
	ret = get_image_size(img_bytes)
	print(ret)