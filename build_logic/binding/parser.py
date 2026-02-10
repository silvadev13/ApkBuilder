from build_logic.core import get_logger
try:
    import xml.etree.ElementTree as ET
except ImportError:
    get_logger().error("> xml.etree.ElementTree not available")

ANDROID_NS = "http://schemas.android.com/apk/res/android"

def parse_layout(path):
    try:
        tree = ET.parse(path)
        return tree.getroot()
    except ET.ParseError as e:
        get_logger().error(f"> XML parse error: {e}")
        raise