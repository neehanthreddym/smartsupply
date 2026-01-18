import uuid
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import uvicorn
import time
from app.routers import catalog_router, inventory_router, movement_router, auth_router, user_router

app = FastAPI(
    title="SmartSupply API",
    description="Inventory Management System",
    version="1.0.0"
)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and attach a unique request_id to each request."""
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4()) # Generate a unique request ID
        request.state.request_id = request_id # Attach to request state

        start_time = time.time() # Capture start time
        response = await call_next(request) # Process the request
        response_time = (time.time() - start_time) * 1000 # Calculate response time in ms

        # Add metadata to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-URL"] = request.url.path
        response.headers["X-Response-Time"] = f"{response_time:.2f}ms"

        print(f"Request-id: {request_id}\nURL: {request.url.path}\nResponse-time: {response_time:.2f}ms")
        
        return response

# Add the middleware to the app
app.add_middleware(RequestIDMiddleware)

app.include_router(catalog_router.router)
app.include_router(inventory_router.router)
app.include_router(movement_router.router)
app.include_router(auth_router.router)
app.include_router(user_router.router)

@app.get("/")
def root():
    return {"message": "Welcome to SmartSupply API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)