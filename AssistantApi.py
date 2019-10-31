from time import sleep
import os
import telebot
from telebot import apihelper
from multiprocessing import Process
from datetime import datetime
import json
from PIL import Image


class Assistant_Api(object):
    def __init__(self, settings):
        self.settings = settings

        apihelper.proxy = {'http': settings["Telegram"]["http proxy"]}
        self.tgBot = telebot.TeleBot(self.settings["Telegram"]["Token"])
        self.chatID = self.settings["Telegram"]["Chat id"]

        self.cardsPath = self.settings["General"]["SD mount path"]
        self.SDCardLabel = self.settings["General"]["SD card label"]

    def __processImage(self, path, size=(2000, 1250), outpath=None):
        print("Processing image %s" % (path))
        img = Image.open(path).resize(size)
        filename = path.split('.')
        savePath = os.getcwd() + "/tmp/" + filename[0].split("/")[-1] + "." + filename[1]
        img.save(savePath)

        print("Processing ok!")

        return savePath

    def __findPath(self, dir, name):
        dirPaths = []
        paths = os.listdir(dir)
        for path in paths:
            if path.count('.') == 0:
                if path.count(name) > 0:
                    dirPaths.append(dir + "/" + path)
        return dirPaths

    def __checkPath(self, path):
        photoList = []
        for file in os.listdir(path):
            fullpath = path + "/" + file
            if file.count(".JPG") == 1:
                if file.count("IMG_") == 1:
                    fileInfo = os.stat(fullpath)
                    date = datetime.fromtimestamp(fileInfo.st_ctime - 10800)
                    photoList.append({"path": fullpath, "file": file, "timestamp": fileInfo.st_ctime, "datetime": "%s:%s:%s" % (date.hour, date.minute, date.second)})
        return {"status": "ok", "photos": photoList}

    def __loop(self):
        while True:
            self.DCIMPaths = self.__findPath(dir=self.cardsPath,
                                             name=self.SDCardLabel)

            if len(self.DCIMPaths) == 0:
                # self.tgBot.send_message(chat_id=self.chatID,
                #                        text="DCIM path '%s' is not found!" %
                #                        (self.settings["General"]["SD card label"]))
                sleep(5)
                continue

            self.DCIMPath = self.DCIMPaths[0] + "/DCIM"

            self.MEDIAPaths = self.__findPath(dir=self.DCIMPath, name="CANON")

            if len(self.MEDIAPaths) == 0:
                self.tgBot.send_message(chat_id=self.chatID,
                                        text="MEDIA path in '%s' is not found!" %
                                        (self.DCIMPath))
                sleep(5)
                continue

            images = []

            for path in self.MEDIAPaths:
                for image in self.__checkPath(path)["photos"]:
                    images.append(image)

            images = sorted(images, key=lambda image: image["timestamp"])

            with open("lastPhotoTimestamp.txt", "r") as f:
                lastTimestamp = json.load(f)

            for image in images:
                if image["timestamp"] > lastTimestamp[0]:
                    self.tgBot.send_photo(self.chatID, open(self.__processImage(image["path"]), "rb"), caption="%s\n%s" % (image["path"].split('/')[-1], image["datetime"]))
                with open("lastPhotoTimestamp.txt", "w") as f:
                    json.dump([int(image["timestamp"])], f)

    def start(self):

        self.tgBot.send_message(chat_id=self.chatID,
                                text="Started")
        self.__loop()
        '''
        except Exception as e:
            print(e)
            self.start()
            '''


if __name__ == "__main__":
    print("Run main.py!")
