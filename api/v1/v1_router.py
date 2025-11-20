from fastapi import APIRouter
from api.v1.endpoints.inference import inference_router
from api.v1.endpoints.files import files_router
from api.v1.endpoints.auth import auth_router


router = APIRouter(prefix='/v1')

router.include_router(inference_router,tags=['Inference'])
router.include_router(files_router,tags=['utils'])
router.include_router(auth_router,tags=["authentication"])