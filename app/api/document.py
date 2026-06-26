from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.schemas.response import UnifiedResponse
from app.services.document import upload_documents
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/upload", summary="上传单个文件", description="支持 .txt, .docx, .pdf, .md 格式，自动去重、分割、向量化存储")
async def document_upload(file: UploadFile = File(..., description="待上传的文件"), current_user: dict = Depends(get_current_user)) -> UnifiedResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="文件内容为空")

    result = await upload_documents(content, file.filename, current_user)

    if hasattr(result, "model_dump"):
        result_data = result.model_dump()
    else:
        result_data = result

    return UnifiedResponse.success(
        code=200,
        data=result_data,
        message=f"[Success] {file.filename} 上传成功"
    )
