from watchfiles import run_process, PythonFilter
import sys
import subprocess

def _launch() -> None:
    # Run as a module so package imports (from src.…) work reliably
    subprocess.run([sys.executable, "-m", "src.app"])  # nosec - dev runner

if __name__ == "__main__":
    run_process('src', target=_launch, watch_filter=PythonFilter(), debounce=500)
