"""
This code sample shows Prebuilt Read operations with the Azure AI Document Intelligence client library.
The async versions of the samples require Python 3.8 or later.

To learn more, please visit the documentation - Quickstart: Document Intelligence (formerly Form Recognizer) SDKs
https://learn.microsoft.com/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api?pivots=programming-language-python
"""

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
import numpy as np
import sys
import os
import yaml
import json
import io
from lib_common import load_settings

"""
Remember to remove the key from your code when you're done, and never post it publicly. For production, use
secure methods to store and access your credentials. For more information, see 
https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-security?tabs=command-line%2Ccsharp#environment-variables-and-application-configuration
"""

# 設定ファイルからエンドポイントとキーを読み込む
# def load_settings(yaml_path="app_setting.yml"):
#     with open(yaml_path, "r", encoding="utf-8") as f:
#         settings = yaml.safe_load(f)
#     return settings["ocr"]["endpoint"], settings["ocr"]["key"]

# endpoint, key をsetting.ymlから取得
endpoint, key = load_settings("ocr", "app_setting.yml")

def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    reshaped_bounding_box = np.array(bounding_box).reshape(-1, 2)
    return ", ".join(["[{}, {}]".format(x, y) for x, y in reshaped_bounding_box])

def analyze_read(img_bytes: bytes) -> object:
	try:
		document_intelligence_client  = DocumentIntelligenceClient(
			endpoint=endpoint, credential=AzureKeyCredential(key)
		)

		file_input = "./test/sample1.jpg"
		if not os.path.exists(file_input):
			print(f"File not found: {file_input}")
			return
		with open(file_input, "rb") as f:
			poller = document_intelligence_client.begin_analyze_document(
				"prebuilt-read", io.BytesIO(img_bytes), content_type="application/pdf"
			)
	
		result = poller.result()

		# resultをJSON形式で保存
		# try:
		# 	# resultにはto_dict()がある場合が多いが、なければ__dict__を使う
		# 	if hasattr(result, 'to_dict'):
		# 		result_json = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
		# 	else:
		# 		result_json = json.dumps(result.__dict__, ensure_ascii=False, indent=2, default=str)
		# 	with open("./test/ocrresult.json", "w", encoding="utf-8") as f:
		# 		f.write(result_json)
		# except Exception as save_e:
		# 	print(f"Failed to save result as JSON: {save_e}")

		return result

	except Exception as e:
		print(f"An error occurred: {e}")
		return None

def print_result(result):
	print ("Document contains content: ", result.content)

	# for idx, style in enumerate(result.styles):
	# 	print(
	# 		"Document contains {} content".format(
	# 			"handwritten" if style.is_handwritten else "no handwritten"
	# 		)
	# 	)

	for idx, paragraph in enumerate(result.paragraphs):
		print(
			"...Paragraph # {} : '{}'".format(
				idx,
				paragraph.content
			)
		)
   
	for page in result.pages:
		print("----Analyzing Read from page #{}----".format(page.page_number))
		print(
			"Page has width: {} and height: {}, measured with unit: {}".format(
				page.width, page.height, page.unit
			)
		)

		# for line_idx, line in enumerate(page.lines):
		# 	print(
		# 		"...Line # {} has text content '{}' within bounding box '{}'".format(
		# 			line_idx,
		# 			line.content,
		# 			format_bounding_box(line.polygon),
		# 		)
		# 	)

		# for word in page.words:
		# 	print(
		# 		"...Word '{}' has a confidence of {}".format(
		# 			word.content, word.confidence
		# 		)
		# 	)

	print("----------------------------------------")


if __name__ == "__main__":
	with open("./test/sample1.jpg", "rb") as f:
		img_bytes = f.read()
	result = analyze_read(img_bytes)
	print_result(result)
 