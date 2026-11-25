
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class API(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/api/consultar":
            self.send_error(404)
            return

        respuesta = {
            "status": 200,
            "totalRegistros": 150,
            "data": [
                {"id": i, "resultado": "POSITIVO"}
                for i in range(1, 121)
            ]
        }

        contenido = json.dumps(respuesta).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(contenido)))
        self.end_headers()
        self.wfile.write(contenido)

HTTPServer(("127.0.0.1", 8080), API).serve_forever()
