import subprocess
import threading
import logging

logger = logging.getLogger("claude_installer")


def run_stream(cmd: str, log_callback, cwd=None, timeout=300) -> int:
    logger.debug(f"Running: {cmd}")
    try:
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            text=True,
            bufsize=1,
        )

        def _read_lines():
            for line in proc.stdout:
                line = line.rstrip()
                if line:
                    logger.debug(line)
                    if log_callback:
                        log_callback(line)

        reader = threading.Thread(target=_read_lines, daemon=True)
        reader.start()
        reader.join(timeout=timeout)

        if reader.is_alive():
            proc.kill()
            reader.join(timeout=5)
            if log_callback:
                log_callback(f"ERROR: Command timed out after {timeout}s")
            logger.warning(f"Command timed out: {cmd}")
            return -1

        proc.wait()  # Ensure returncode is set
        return proc.returncode or 0

    except Exception as e:
        logger.error(f"Command failed: {cmd} — {e}")
        if log_callback:
            log_callback(f"ERROR: {e}")
        return -1


def run_quiet(cmd: str, cwd=None, timeout=300) -> tuple[int, str]:
    logger.debug(f"Running (quiet): {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return result.returncode, output.strip()
    except subprocess.TimeoutExpired:
        logger.warning(f"Command timed out: {cmd}")
        return -1, "Command timed out"
    except Exception as e:
        logger.error(f"Command failed: {cmd} — {e}")
        return -1, str(e)
