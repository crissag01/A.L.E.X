from Tools.files import read_file, list_directory, write_file, delete_file
from Tools.time_tool import get_time
from Tools.memory_tool import remember, forget
from Tools.system_tool import open_program, get_system_info
from Tools.web_search import web_search
from Tools.shell_tool import execute_command
from Tools.reminder_tool import set_reminder, list_reminders, cancel_reminder
from Tools.weather_tool import get_weather
from Tools.calc_tool import calculate

TOOLS = {
    "get_time": get_time,
    "remember": remember,
    "forget": forget,
    "open_program": open_program,
    "list_directory": list_directory,
    "web_search": web_search,
    "read_file": read_file,
    "write_file": write_file,
    "delete_file": delete_file,
    "execute_command": execute_command,
    "set_reminder": set_reminder,
    "list_reminders": list_reminders,
    "cancel_reminder": cancel_reminder,
    "get_weather": get_weather,
    "get_system_info": get_system_info,
    "calculate": calculate,
}
