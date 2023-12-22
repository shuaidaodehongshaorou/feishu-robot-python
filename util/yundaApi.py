import json
from typing import *

import requests
from lark_oapi import BaseRequest, HttpMethod, RawResponse, JSON, UTF_8, logger

from util.AES import AESCipher
from util.Httputil import Http
from util.yundaModel import HttpResponse, BarCodeMessage, EncryptedRequestBoy, ImageMessage, ExpressTrack

url = "https://qihang.yundasys.com/"  # 启航生产环境
partnerCode = "qihang"  # 启航生产环境
key = "YvIOPlG2lrJGJ5ar"  # 启航生产环境

enterpartnerCode = "qihangjingang"  # 进港专用
enterkey = "mRu7Jfxf35qZhfit"  # 进港专用


# 条码分配查询
def query_bar_code_record(waybill_no):
    # 构造加密数据
    encrypted_data = AESCipher().encrypt(json.dumps({"waybillNo": waybill_no}), key)
    # 构造请求内容
    RequestBoy: EncryptedRequestBoy = EncryptedRequestBoy.builder() \
        .partnerCode(partnerCode) \
        .logisticsInterface(encrypted_data) \
        .build()
    # 构造请求对象
    request: BaseRequest = BaseRequest.builder() \
        .uri(url + "manager/out/distribute") \
        .http_method(HttpMethod.POST) \
        .body(RequestBoy.to_dict()) \
        .headers({"Content-Type": "application/json"}) \
        .build()
    # 发起请求
    resp: RawResponse = Http.execute(request)
    res: HttpResponse = JSON.unmarshal(str(resp.content, UTF_8), HttpResponse)
    if res.success:
        res.result = BarCodeMessage(res.result)
    else:
        logger.error(f"{str(request.http_method.name)} {request.uri} , "
                     f"headers: {JSON.marshal(request.headers)}, "
                     f"params: {JSON.marshal(request.queries)}, "
                     f"body: {str(request.body, UTF_8) if isinstance(request.body, bytes) else request.body},"
                     f"code: {res.code}, "
                     f"success: {res.success}, "
                     f"message: {res.message}")
    return res


# 内网物流轨迹查询
def query_expressTrack(waybill_no):
    # 构造加密数据
    encrypted_data = AESCipher().encrypt(json.dumps({"waybillNo": waybill_no}), key)
    # 构造请求内容
    RequestBoy: EncryptedRequestBoy = EncryptedRequestBoy.builder() \
        .partnerCode(partnerCode) \
        .logisticsInterface(encrypted_data) \
        .build()
    # 构造请求对象
    request: BaseRequest = BaseRequest.builder() \
        .uri(url + "manager/out/getExpressTrackV2") \
        .http_method(HttpMethod.POST) \
        .body(RequestBoy.to_dict()) \
        .headers({"Content-Type": "application/json"}) \
        .build()
    # 发起请求
    resp: RawResponse = Http.execute(request)
    res: HttpResponse = JSON.unmarshal(str(resp.content, UTF_8), HttpResponse)
    if res.success:
        res.result = [ExpressTrack(item) for item in res.result]
    else:
        logger.error(f"{str(request.http_method.name)} {request.uri} , "
                     f"headers: {JSON.marshal(request.headers)}, "
                     f"params: {JSON.marshal(request.queries)}, "
                     f"body: {str(request.body, UTF_8) if isinstance(request.body, bytes) else request.body},"
                     f"code: {res.code}, "
                     f"success: {res.success}, "
                     f"message: {res.message}")
    return res, len(res.result)


# 发送进港留言
def send_incoming_message(content):
    # 构造加密数据
    encrypted_data = AESCipher().encrypt(json.dumps(content), enterkey)
    # 构造请求内容
    RequestBoy: EncryptedRequestBoy = EncryptedRequestBoy.builder() \
        .partnerCode(enterpartnerCode) \
        .logisticsInterface(encrypted_data) \
        .build()

    # 构造请求对象
    request: BaseRequest = BaseRequest.builder() \
        .uri(url + "manager/out/send/incomingMsg") \
        .http_method(HttpMethod.POST) \
        .body(RequestBoy.to_dict()) \
        .headers({"Content-Type": "application/json"}) \
        .build()
    # 发起请求
    resp: RawResponse = Http.execute(request)
    res: HttpResponse = JSON.unmarshal(str(resp.content, UTF_8), HttpResponse)
    if not res.success:
        logger.error(f"{str(request.http_method.name)} {request.uri} , "
                     f"params: {JSON.marshal(request.queries)}, "
                     f"body: {str(request.body, UTF_8) if isinstance(request.body, bytes) else request.body},"
                     f"code: {res.code}, "
                     f"success: {res.success}, "
                     f"message: {res.message}")

    return res


def upload_image(content, file: IO[Any]):
    # 图片文件路径
    files = {'file': file}
    encrypted_data = AESCipher().encrypt(json.dumps(content), key)
    # 构造请求内容
    RequestBoy: EncryptedRequestBoy = EncryptedRequestBoy.builder() \
        .logisticsInterface(encrypted_data) \
        .partnerCode(partnerCode) \
        .build()
    # 发送POST请求
    response = requests.post(url + "manager/out/uplod/img", files=files, data=RequestBoy.to_dict())
    res: HttpResponse = JSON.unmarshal(str(response.content, UTF_8), HttpResponse)
    if res.success:
        res.result = ImageMessage(res.result)
    else:
        logger.error(
            f"code: {res.code}, "
            f"success: {res.success}, "
            f"message: {res.message}")
    return res


if __name__ == "__main__":

    response, res = query_expressTrack("463292204930709")
    print(response.to_dict())
    print(res)
    if response.success:
        for datacontent in response.result:
            print(datacontent.to_dict())
