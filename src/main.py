from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import logging
import json
import base64
import copy
import jsonpatch
import os


app = FastAPI()

logging.getLogger().setLevel("INFO")

# basic health endpoint for liveness
@app.get("/health")
def health():
    return "OK"

# mutating webhook for modifying pods
@app.post("/mutating")
async def mutating_webhook(request: Request):
    request_body = await request.json()
    # logging.info(f"request body:{request_body}")

    # 从环境变量里获取需要加入ingress里的注解
    env_annotations = json.loads(os.getenv('annotations','{"k8s.apisix.apache.org/use-regex": "true","kubernetes.io/ingress.class": "apisix"}'))

    json_response = await generate_response_body(request_body,env_annotations)
    # logging.info(f"response body:{json_response}")

    # return admissionreview json response
    return JSONResponse(content=jsonable_encoder(json_response))


async def generate_response_body(request_body,env_annotations):
    ingress_rule_name = request_body["request"]["name"]
    object_body = request_body["request"]["object"]
    new_object_body = copy.deepcopy(object_body)

    for key,value in env_annotations.items():
        new_object_body["metadata"]["annotations"][key] = value

    result_generate_response_body = {
            "response": {
                "allowed": True,
                "uid": request_body["request"]["uid"]
            }
        }

    patch_content = jsonpatch.JsonPatch.from_diff(object_body, new_object_body)
    # logging.info(f"patch content:{patch_content}")

    if patch_content:
        result_generate_response_body['response']['patchtype'] = "JSONPatch"
        result_generate_response_body['response']['patch'] = base64.b64encode(str(patch_content).encode()).decode()
        logging.info(f"ingress rule {ingress_rule_name} patch apisix annotations success")
    else:
        logging.info(f"ingress rule {ingress_rule_name} exists apisix annotations,skip")  

    return result_generate_response_body    