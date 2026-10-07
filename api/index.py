import os
import sys
import traceback

root_dir = os.path.dirname(os.path.dirname(__file__))
backend_dir = os.path.join(root_dir, 'backend')
sys.path.insert(0, root_dir)
sys.path.insert(0, backend_dir)

try:
    from backend.app.main import app
except Exception as e:
    err_msg = traceback.format_exc()
    
    # Create a dummy ASGI app that returns the error
    async def app(scope, receive, send):
        assert scope['type'] == 'http'
        await send({
            'type': 'http.response.start',
            'status': 500,
            'headers': [
                (b'content-type', b'text/plain'),
            ]
        })
        await send({
            'type': 'http.response.body',
            'body': err_msg.encode('utf-8'),
        })
