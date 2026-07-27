import io
import time
import base64
from PIL import ImageGrab


def capture(delay: int = 3) -> str | None:
    try:
        time.sleep(delay)
        img = ImageGrab.grab(all_screens=True)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None
