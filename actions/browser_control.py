import time
import webbrowser
import urllib.parse
import subprocess
import pyautogui
from PIL import ImageGrab


def browser_control(
    action: str,
    query: str = None,
    url: str = None,
    target: str = None,
    text: str = None
) -> str:
    """
    Brauzerni to'liq boshqarish:
    1-bosqich: Tezkor kodli/URL buyrug'i orqali saytni ochish yoki qidirish.
    2-bosqich: Agar sayt ichida tugmaga bosish yoki matn yozish kerak bo'lsa, avtomatik sichqoncha (Vision) orqali bajaradi.
    """
    act = (action or "open_url").lower().strip()
    try:
        if act in ["search_google", "search"] or (query and not url and act != "click_element"):
            search_text = query or text or ""
            q_enc = urllib.parse.quote(search_text)
            target_url = f"https://www.google.com/search?q={q_enc}"
            try:
                webbrowser.open(target_url)
            except Exception:
                subprocess.Popen(f'start "" "{target_url}"', shell=True)
            
            time.sleep(1.2)
            # Agar qidiruvdan so'ng biror elementga bosish kerak bo'lsa
            if target:
                from actions.screen_processor import screen_click
                return screen_click(target=target, click_type="click")
            return f"Google'da '{search_text}' qidirildi va ochildi."

        elif act in ["open_url", "open_site", "open"]:
            target_url = url or query or ""
            if target_url:
                if not target_url.startswith("http://") and not target_url.startswith("https://"):
                    if "." not in target_url:
                        target_url = f"https://www.google.com/search?q={urllib.parse.quote(target_url)}"
                    else:
                        target_url = "https://" + target_url
                try:
                    webbrowser.open(target_url)
                except Exception:
                    subprocess.Popen(f'start "" "{target_url}"', shell=True)
                
                time.sleep(1.2)
                # Agar sayt ochilgach biror tugma yoki maydonga bosish/yozish kerak bo'lsa
                if target and text:
                    from actions.screen_processor import screen_type
                    return screen_type(target=target, text=text)
                elif target:
                    from actions.screen_processor import screen_click
                    return screen_click(target=target, click_type="click")

                return f"'{target_url}' sayti ochildi."
            return "Ochish uchun sayt yoki URL manzili berilmadi."

        elif act == "click_element" or (target and not text):
            from actions.screen_processor import screen_click
            return screen_click(target=target or "element", click_type="click")

        elif act == "type_text" or (target and text):
            from actions.screen_processor import screen_type
            return screen_type(target=target or "qidiruv maydoni", text=text)

        elif act == "new_tab":
            pyautogui.hotkey("ctrl", "t")
            return "Yangi vkladka ochildi."

        elif act == "close_tab":
            pyautogui.hotkey("ctrl", "w")
            return "Vkladka yopildi."

        elif act == "next_tab":
            pyautogui.hotkey("ctrl", "tab")
            return "Keyingi vkladkaga o'tildi."

        elif act == "prev_tab":
            pyautogui.hotkey("ctrl", "shift", "tab")
            return "Oldingi vkladkaga o'tildi."

        elif act == "refresh":
            pyautogui.hotkey("ctrl", "r")
            return "Sahifa yangilandi."

        elif act in ["scroll_down", "scroll"]:
            pyautogui.scroll(-600)
            return "Sahifa pastga aylantirildi."

        elif act == "scroll_up":
            pyautogui.scroll(600)
            return "Sahifa yuqoriga aylantirildi."

        else:
            return f"Noma'lum brauzer amali: {act}"

    except Exception as e:
        return f"Brauzer amalida xatolik: {e}"
