from AssistantApi import Assistant_Api
import json

try:
    settings = json.load(open("settings.json", "r"))
except FileNotFoundError:
    with open("settings.json", "w") as f:
        f.write("""{
    "General":{
        "SD mount path":"",
        "SD card label":""
    },
    "Telegram":{
        "http proxy":"",
        "Token":"",
        "Chat id":""
    }
}""")
    print("Заполните settings.json!")
    exit()

assistant = Assistant_Api(settings)


if __name__ == "__main__":
    assistant.start()
