import webbrowser
import urllib.parse


def youtube_video(action: str = "search_play", query: str = "") -> str:
    try:
        q_enc = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={q_enc}"
        webbrowser.open(url)
        return f"YouTube'da '{query}' qidirildi va ochildi."
    except Exception as e:
        return f"YouTube ochishda xatolik: {e}"
