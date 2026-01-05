from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.auth.router import router
from fastapi.exceptions import RequestValidationError
def lifespan(app: FastAPI):
    print('Started')
    yield
    print('Stopped')

app = FastAPI(lifespan=lifespan, title="CostFlow_FastApi", version="0.1.0")
app.include_router(router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = exc.errors()[0]

    return JSONResponse(
        status_code=422,
        content={
            "detail": error.get("msg")
        }
    )

@app.get("/", tags=["Health"])
def home():
    return {"message": "Project is running"}

if __name__ == "__main__":
    home()