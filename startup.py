from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "JARVIS INDIA OS Running Successfully"}  