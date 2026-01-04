from fastapi import FastAPI


def lifespan(app: FastAPI):
    print('Started')
    yield
    print('Stopped')

app = FastAPI(lifespan=lifespan, title="CostFlow_FastApi", version="0.1.0")


@app.get("/", tags=["Health"])
def home():
    return {"message": "Project is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)