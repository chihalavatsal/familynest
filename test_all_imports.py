import sys
try:
    from backend.app.main import app
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
