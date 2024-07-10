import importlib
from pathlib import Path
import sys


PAGES_DIR = Path(__file__).parent.joinpath("../pages")


def load_and_execute_module(module_name, package=None):
    try:
        if module_name in sys.modules:
            module = importlib.reload(sys.modules[module_name])
        else:
            module = importlib.import_module(module_name, package=package)
        print(f"Module {module_name} has been loaded and executed.")
        return module
    except ModuleNotFoundError as e:
        print(f"Module {module_name} not found: {e}")
        return None
    except Exception as e:
        print(f"Error loading module {module_name}: {e}")
        return None


def get_page_module_names():
    return [p.stem for p in PAGES_DIR.glob("*.py")]


def get_source_code(module_name: str):
    module_path = PAGES_DIR.joinpath(f"{module_name}.py")
    return module_path.read_text(encoding="utf-8")
