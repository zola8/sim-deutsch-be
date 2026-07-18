import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

app: FastAPI = FastAPI()


@app.get("/")
def home_page():
    return {"status": "OK"}


if __name__ == '__main__':
    print('http://localhost:8080')
    uvicorn.run(app, host="0.0.0.0", port=8080, forwarded_allow_ips="*")
