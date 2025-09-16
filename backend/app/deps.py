from fastapi import Depends, HTTPException
from .auth import get_current_user

async def auth_required(user = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user
