import uvicorn
from app.config import HOST, PORT

if __name__ == "__main__":
    print(f"================================================================")
    print(f"  Sovereign AI Workbench — Backend / Agent Service (Person 1)   ")
    print(f"  Listening on http://{HOST}:{PORT}                             ")
    print(f"  OpenAPI docs available at http://localhost:{PORT}/docs        ")
    print(f"================================================================")
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
