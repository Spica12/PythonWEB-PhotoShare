

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from cloudinary_functions import upload_photo, get_asset_info, create_photo_tag

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, this is your FastAPI Cloudinary integration!"}

@app.post("/upload-photo")
async def upload_photo_route():
    try:
        result = upload_photo()
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/get-asset-info")
async def get_asset_info_route():
    try:
        result = get_asset_info()
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/create-photo-tag")
async def create_photo_tag_route():
    try:
        result = create_photo_tag()
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

