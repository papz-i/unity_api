from fastapi import FastAPI, HTTPException, Body, Request
from pydantic import BaseModel
from redis import Redis
from rq import Queue
import uuid

app = FastAPI()

# create redis queue
redis_conn = Redis(host='redis', port=6379)
task_queue = Queue("task_queue", connection=redis_conn)

class InsertObject(BaseModel):
    reference_object: str
    prefab: str
    direction: str
    value: str

class SnapObject(BaseModel):
    snap_point: str
    prefab: str

class MoveObject(BaseModel):
    prefab: str
    direction: str
    value: str

class RemoveObject(BaseModel):
    prefab: str
    value: str

class ReplaceObject(BaseModel):
    prefab: str
    object_to_replace: str

class ScaleObject(BaseModel):
    prefab: str
    axis: str
    value: str

class RotateObject(BaseModel):
    prefab: str
    axis: str
    value: str

currentInstruction = {
    "action": "",
    "parameters": ""
}

responseFromUnity = {
    "message": ""
}

axisList = ['x', 'y', 'z', 'reset', 'default']
scaleList = ['x_up', 'y_up', 'z_up', 'x_down', 'y_down', 'z_down', 'multiply', 'increase', 'decrease', 'reset', 'default']
directionsList = ["left", "right", "front", "back", "top", "bottom", "default"]

@app.post("/set/insert")
async def set_insert(insert_obj: InsertObject):
    insert_params = insert_obj.model_dump()
    if insert_params['direction'].lower() not in directionsList:
        raise HTTPException(status_code=400, detail=f"Direction is invalid. {directionsList}")
    elif not insert_params['value'].isdigit():
        raise HTTPException(status_code=400, detail="Value should be a number.")
    else:
        currentInstruction['action'] = "insert"
        currentInstruction['parameters'] = insert_params
        

        try:
            task_queue.enqueue(insert_params)
            return {
                "success": True,
                "message": "Pushed to Redis Queue"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

@app.post("/set/snap")
async def set_snap(snap_obj: SnapObject):
    snap_params = snap_obj.model_dump()
    currentInstruction['action'] = "snap"
    currentInstruction['parameters'] = snap_params
    return snap_params

@app.post("/set/move")
async def set_move(move_obj: MoveObject):
    move_params = move_obj.model_dump()
    if move_params['direction'].lower() not in directionsList:
        raise HTTPException(status_code=400, detail=f"Direction is invalid. {directionsList}")
    elif not move_params['value'].isdigit():
        raise HTTPException(status_code=400, detail="Value should be a number.")
    else:
        currentInstruction['action'] = "move"
        currentInstruction['parameters'] = move_params
        return move_params

@app.post("/set/remove")
async def set_remove(remove_obj: RemoveObject):
    remove_params = remove_obj.model_dump()
    if not remove_params['value'].isdigit():
        raise HTTPException(status_code=400, detail="Value should be a number.")
    else:
        currentInstruction['action'] = "remove"
        currentInstruction['parameters'] = remove_params
        return remove_params

@app.post("/set/replace")
async def set_replace(replace_obj: ReplaceObject):
    replace_params = replace_obj.model_dump()
    currentInstruction['action'] = "replace"
    currentInstruction['parameters'] = replace_params
    return replace_params

@app.post("/set/scale")
async def set_scale(scale_obj: ScaleObject):
    scale_params = scale_obj.model_dump()
    if scale_params['axis'].lower() not in scaleList:
        raise HTTPException(status_code=400, detail=f"Axis is invalid. {scaleList}")
    elif not scale_params['value'].isdigit():
        raise HTTPException(status_code=400, detail="Value should be a number.")
    else:
        currentInstruction['action'] = "scale"
        currentInstruction['parameters'] = scale_params
        return scale_params

@app.post("/set/rotate")
async def set_rotate(rotate_obj: RotateObject):
    rotate_params = rotate_obj.model_dump()
    if rotate_params['axis'].lower() not in axisList:
        raise HTTPException(status_code=400, detail=f"Axis is invalid. {axisList}")
    elif not rotate_params['value'].isdigit():
        raise HTTPException(status_code=400, detail="Value should be a number.")
    else:
        currentInstruction['action'] = "rotate"
        currentInstruction['parameters'] = rotate_params
        return rotate_params

@app.get("/reset")
async def reset():
    currentInstruction['action'] = ""
    currentInstruction['parameters'] = ""
    return currentInstruction

@app.post("/set/response")
async def set_response(message: str = Body(...)):
    responseFromUnity['message'] = message
    return responseFromUnity

@app.get("/response")
async def get_response():
    return responseFromUnity

@app.get("/instruction")
async def get_instruction():
    return currentInstruction
