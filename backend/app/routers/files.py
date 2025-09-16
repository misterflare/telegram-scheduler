import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from ..deps import auth_required
from ..config import settings

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload")
async def upload(files: list[UploadFile] = File(...), user = Depends(auth_required)):
    saved = []
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    for f in files:
        dest = os.path.join(settings.UPLOAD_DIR, f.filename)
        # If exists, uniquify
        base, ext = os.path.splitext(dest)
        i = 1
        while os.path.exists(dest):
            dest = f"{base}_{i}{ext}"; i += 1
        with open(dest, "wb") as out:
            out.write(await f.read())
        saved.append({"filename": os.path.basename(dest), "path": dest})
    return {"files": saved}
