# main.py
# from operator import itemgetter
import os
import asyncio
from datetime import datetime
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from database import SessionLocal, Device, Session
from sqlalchemy import select

class DeviceData(BaseModel):
    device_id: int
    name: str
    field: str
    value: int|float = Field(ge=0, description="数值")
    status: str = Field(pattern = r"^正常|警告|停机$")
    update_time: str

app = FastAPI(title="工业数据展示面板",
    description = "提供产线设备数据的API接口库",
    version="1.0.0"
            )

app.mount("/static", StaticFiles(directory="static/", html=True), name="static")

# 模拟工业数据
factory_data = [
    {"device_id": 1, "name":"球磨机", "field":"power", "value": 4146, "status": "正常", "update_time":"2025-12-11 11:00:00"},
    {"device_id": 2, "name":"泵池", "field":"level", "value":50.1, "status": "正常", "update_time":"2025-12-10 10:00:00"},
    {"device_id": 3, "name":"给矿", "field":"pressure", "value": 0.501, "status": "警告", "update_time":"2025-11-10: 21:00:21"}
]

# 定义接口(get: 获取所有设备数据)
@app.get("/api/device/all",summary="获取所有设备数据")
def get_all_device_data():
    return {"code":200, "msg":"成功", "data":factory_data}

# 定义带参数的接口(get: 获取设备ID获取设备数据)
@app.get("/api/device/{device_id}", summary="根据ID获取设备数据")
def get_device_data(device_id: int):
    # iter_result = filter(lambda x: itemgetter('device_id')(x) == device_id, factory_data)
    # for data in iter_result:
    #     return {"code":200, "msg":"成功", "data": data}

    for device in factory_data:
        if device["device_id"] == device_id:
            return {"code":200, "msg":"成功", "data": device}

    return {"code":404, "msg":"设备不存在", "data": None}
    

@app.post("/api/device/add", summary="添加设备数据")
def add_device_data(data: DeviceData):
    factory_data.append(data.dict())
    return {"code":200,"msg":"添加成功", "data":None}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/device/all",summary="获取所有设备数据")
def get_all_device_data(db: SessionLocal=Depends(get_db)):
    devices = db.query(Device).all()
    data_list = []
    for d in devices:
        data_list.append({"device_id":d.device_id,"name":d.name,"field":d.field,"value":d.value,"status":d.status,"update":d.update_time})
    return {"code":200, "msg":"成功","data": data_list}

async def generate_realtime_data():
    while True:
        for device in factory_data:
            if device["field"] == "power":
                device["value"] += int(asyncio.random()*10) -5
                device["value"] = max(4000, min(4500, device["value"]))
            elif device["field"] == "level":
                device["value"] = round(device["value"]+(asyncio.random()*0.2-0.1),1)
                device["value"] = max(0, min(100, device["value"]))
            elif device["field"] == "pressure":
                device["value"] = round(device["value"] + (asyncio.random() * 0.002 - 0.001), 3)
                device["value"] = max(0, min(1, device["value"]))

            device["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if device["field"] == "pressure" and device["value"] > 0.8:
                device["status"] = "异常"
            elif device["field"] == "pressure" and device["value"] > 0.5:
                device["status"] = "警告"
            else:
                device["status"] = "正常"
            # SSE 格式:  data: 数据 
            import json
            yield f"data:{json.dumps(factory_data,ensure_ascii=False)}\n\n"
            await asyncio.sleep(1) # 异步休眠
# 定义SSE接口
@app.get("/api/device/realtime", summary="实时推送设备数据(SSE)")
async def get_realtime_data():
    return StreamingResponse(
        generate_realtime_data(), 
        media_type="text/event-stream"
        )

# 3. 从数据库获取设备数据（可选，演示用）
@app.get("/api/device/db/all", summary="从数据库获取所有设备数据")
def get_device_from_db(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    # 转换为字典返回
    data_list = []
    for d in devices:
        data_list.append({
            "device_id": d.device_id,
            "name": d.name,
            "field": d.field,
            "value": d.value,
            "status": d.status,
            "update_time": d.update_time
        })
    return {"code": 200, "msg": "成功", "data": data_list}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=8000)