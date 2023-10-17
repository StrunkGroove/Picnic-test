from fastapi import FastAPI

from api.endpoints.v1.users import router as users_router
from api.endpoints.v1.picnic import router as picnic_router
from api.endpoints.v1.city import router as city_router


app = FastAPI()

app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(picnic_router, prefix="/api/v1/picnic", tags=["Picnic"])
app.include_router(city_router, prefix="/api/v1/city", tags=["City"])