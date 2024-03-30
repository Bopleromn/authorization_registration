import uvicorn
from fastapi import FastAPI
import routers.user_routes as user_routes


class Server:
    def __init__(self, ip: str, port: int) -> None:
        self.__ip = ip
        self.__port = port
        self.app = FastAPI(debug=True, title="SPARKS")

    def init_routes(self):
        self.app.include_router(user_routes.router)

    def run(self):
        uvicorn.run(
            self.app, host=self.__ip, port=self.__port
        )
