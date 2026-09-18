import time
from agent.planner import plan_task

# Tool dispatcher import
from actions.open_app import open_app, close_app
from actions.browser_control import browser_control
from actions.computer_control import computer_control
from actions.computer_settings import computer_settings
from actions.file_controller import file_controller
from actions.terminal_agent import terminal_execute
from actions.youtube_video import youtube_video
from actions.weather_report import weather_action


def execute_plan(task_goal: str) -> str:
    plan = plan_task(task_goal)
    results = []

    for item in plan:
        tool = item.get("tool")
        args = item.get("args", {})
        desc = item.get("description", "")

        try:
            if tool == "open_app":
                res = open_app(**args)
            elif tool == "browser_control":
                res = browser_control(**args)
            elif tool == "computer_control":
                res = computer_control(**args)
            elif tool == "computer_settings":
                res = computer_settings(**args)
            elif tool == "file_controller":
                res = file_controller(**args)
            elif tool == "terminal_execute":
                res = terminal_execute(**args)
            elif tool == "youtube_video":
                res = youtube_video(**args)
            elif tool == "weather_action":
                res = weather_action(**args)
            else:
                res = f"Bajarilmadi: {desc}"

            results.append(f"? {desc}: {res}")
            time.sleep(0.5)
        except Exception as e:
            results.append(f"? {desc} xatolik: {e}")

    return "\n".join(results)
