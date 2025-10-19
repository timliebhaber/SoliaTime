import sys
import subprocess

def _launch() -> None:
    # Run as a module so package imports (from src.…) work reliably
    subprocess.run([sys.executable, "-m", "src.app"])  # nosec - dev runner

if __name__ == "__main__":
    _launch()
