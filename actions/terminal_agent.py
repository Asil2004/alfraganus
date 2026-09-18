import subprocess


def terminal_execute(command: str, timeout: int = 30) -> str:
    try:
        res = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        out = res.stdout.strip()
        err = res.stderr.strip()
        
        result = []
        if out:
            result.append(f"[Output]:\n{out}")
        if err:
            result.append(f"[Error]:\n{err}")
            
        return "\n".join(result) if result else "Buyruq muvaffaqiyatli bajarildi (hech qanday xabar qaytmadi)."

    except subprocess.TimeoutExpired:
        return f"Buyruq bajarilishi {timeout} soniyadan oshib ketdi va to'xtatildi."
    except Exception as e:
        return f"Terminal buyrug'ini bajarishda xatolik: {e}"
