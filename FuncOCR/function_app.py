import azure.functions as func
import logging
from openai_llm import extract_order_info
from PIL import Image
import io
#from app_settings import key, endpoint

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="OcrFunc")
def OcrFunc(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    user_content = "株式会社テストの佐藤様より、注文番号 #X123 のご注文がありました。納期は7月25日とのことです。"

    res = extract_order_info(user_content)
    
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             res,
             status_code=200
        )

@app.route(route="ImageSize", methods=["POST"])
def ImageSizeFunc(req: func.HttpRequest) -> func.HttpResponse:
    try:
        img_bytes = req.get_body()
        img = Image.open(io.BytesIO(img_bytes))
        width, height = img.size
        result = {"width": width, "height": height}
        return func.HttpResponse(
            func.json.dumps(result),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            func.json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=400
        )