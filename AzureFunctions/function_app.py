import azure.functions as func
import logging
import json
from lib_image import get_image_size
from lib_ocr import analyze_read

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

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
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

@app.route(route="ImageSize", methods=["POST"])
def ImageSizeFunc(req: func.HttpRequest) -> func.HttpResponse:
    try:
        img_bytes = req.get_body()
        result = get_image_size(img_bytes)
        return func.HttpResponse(
            result,
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=400
        )
        
@app.route(route="ocr_read", methods=["POST"])
def ocr_read(req: func.HttpRequest) -> func.HttpResponse:
    try:
        img_bytes = req.get_body()
        result = analyze_read(img_bytes)
  
        result = {"content": result.content}
        res_body = json.dumps(result, ensure_ascii=False, indent=2)
  
        return func.HttpResponse(
            res_body,
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=400
        )
        