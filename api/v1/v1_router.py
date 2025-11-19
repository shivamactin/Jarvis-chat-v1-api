from fastapi import APIRouter
from api.v1.endpoints.inference import inference_router
from api.v1.endpoints.files import files_router


router = APIRouter(prefix='/v1')

router.include_router(inference_router,tags=['Inference'])
router.include_router(files_router,tags=['utils'])
