import os
import shutil
from pathlib import Path


def file_controller(action: str, path: str, content: str = None, destination: str = None, query: str = None) -> str:
    act = action.lower().strip()
    target_path = Path(os.path.expandvars(path))
    
    try:
        if act == "list_files":
            if not target_path.exists():
                return f"'{path}' yo'li mavjud emas."
            items = []
            for item in target_path.iterdir():
                t = "??" if item.is_dir() else "??"
                items.append(f"{t} {item.name}")
            return "\n".join(items[:50]) if items else "Papka bo'sh."

        elif act == "read_file":
            if not target_path.exists():
                return f"'{path}' fayli topilmadi."
            text = target_path.read_text(encoding="utf-8", errors="replace")
            return text[:3000] + ("\n...[qisqartirildi]" if len(text) > 3000 else "")

        elif act == "write_file":
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content or "", encoding="utf-8")
            return f"'{path}' fayliga ma'lumot muvaffaqiyatli yozildi."

        elif act == "append_file":
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "a", encoding="utf-8") as f:
                f.write(content or "")
            return f"'{path}' fayliga ma'lumot qo'shildi."

        elif act == "delete_file":
            if target_path.is_file():
                target_path.unlink()
                return f"'{path}' fayli o'chirildi."
            elif target_path.is_dir():
                shutil.rmtree(target_path)
                return f"'{path}' papkasi o'chirildi."
            return f"'{path}' topilmadi."

        elif act == "make_dir":
            target_path.mkdir(parents=True, exist_ok=True)
            return f"'{path}' papkasi yaratildi."

        elif act == "search_files":
            matches = []
            q = (query or "").lower()
            for root, dirs, files in os.walk(target_path):
                for f in files:
                    if q in f.lower():
                        matches.append(str(Path(root) / f))
                        if len(matches) >= 20:
                            break
                if len(matches) >= 20:
                    break
            return "\n".join(matches) if matches else "Fayl topilmadi."

        elif act in ("open_file", "open", "launch_file"):
            from actions.open_app import find_and_open_user_file
            res = find_and_open_user_file(path)
            if res:
                return res
            if target_path.exists():
                try:
                    os.startfile(str(target_path))
                    return f"✅ '{target_path.name}' fayli tizimda ochildi ({target_path})."
                except Exception as e:
                    return f"Faylni ochishda xatolik: {e}"
            return f"'{path}' fayli topilmadi."

        else:
            return f"Noma'lum fayl amali: {act}"

    except Exception as e:
        return f"Fayl amalida xatolik: {e}"
