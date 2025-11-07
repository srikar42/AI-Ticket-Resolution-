import uvicorn

class UvicornServer:
    @staticmethod
    def run():
         uvicorn.run(
            "recommend_api:app",  # module_name:variable_name
            host="127.0.0.1",
            port=8000,
            reload=True   # enables auto-reload when you change code
        )

if __name__ == "__main__":
    server = UvicornServer()
    server.run()

