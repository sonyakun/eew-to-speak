import requests
import json
import asyncio
import websockets
import datetime
import requests
import threading
from cleo.commands.command import Command
from cleo.helpers import option
import glob
import os,subprocess
import shutil
import urllib.request

class Color:
	BLACK          = '\033[30m'#(文字)黒
	RED            = '\033[31m'#(文字)赤
	GREEN          = '\033[32m'#(文字)緑
	YELLOW         = '\033[33m'#(文字)黄
	BLUE           = '\033[34m'#(文字)青
	MAGENTA        = '\033[35m'#(文字)マゼンタ
	CYAN           = '\033[36m'#(文字)シアン
	WHITE          = '\033[37m'#(文字)白
	COLOR_DEFAULT  = '\033[39m'#文字色をデフォルトに戻す
	BOLD           = '\033[1m'#太字
	UNDERLINE      = '\033[4m'#下線
	INVISIBLE      = '\033[08m'#不可視
	REVERCE        = '\033[07m'#文字色と背景色を反転
	BG_BLACK       = '\033[40m'#(背景)黒
	BG_RED         = '\033[41m'#(背景)赤
	BG_GREEN       = '\033[42m'#(背景)緑
	BG_YELLOW      = '\033[43m'#(背景)黄
	BG_BLUE        = '\033[44m'#(背景)青
	BG_MAGENTA     = '\033[45m'#(背景)マゼンタ
	BG_CYAN        = '\033[46m'#(背景)シアン
	BG_WHITE       = '\033[47m'#(背景)白
	BG_DEFAULT     = '\033[49m'#背景色をデフォルトに戻す
	RESET          = '\033[0m'#全てリセット

class GreetCommand(Command):
    name = "eew_tts"
    description = "棒読みちゃんまたはVOICEVOXで地震情報を受信したら読み上げます。"
    options = [
        option(
            "voicevox",
            "v",
            description="If set, the task will yell in uppercase letters",
            flag=True
        )
    ]

    def handle(self):
        global speaker
        option = self.argument("voicevox")
        if option:
            speaker = "VOICEVOX"
        else:
            speaker = "bouyomi"

speaker_dict={
    "VOICEVOX" : "VOICEVOX",
    "bouyomi" : "棒読みちゃん"
}

def speak_bouyomi(text='これはテストです。', voice=0, volume=-1, speed=-1, tone=-1):
    res = requests.get(
        'http://localhost:50080/Talk',
        params={
            'text': text,
            'voice': voice,
            'volume': volume,
            'speed': speed,
            'tone': tone})

async def connect():
    global text_list
    speaker = "bouyomi"
    async with websockets.connect("wss://api.p2pquake.net/v2/ws") as websocket:
        print(f"{Color.GREEN}[INFO]{Color.RESET}P2P地震速報 WebsocketAPIに接続しました！")
        print(f"{Color.GREEN}[INFO]{Color.RESET}システム情報")
        print(f"読み上げソフトウェア: {speaker_dict[speaker]}")
        print(f"接続先URL: wss://api.p2pquake.net/v2/ws")
        print(f"ソフトウェアバージョン: 0.1.0 - Beta1(最新バージョン:None)")
        for i in range(1,10,1):
            data = await websocket.recv()
            json_load = json.loads(data)
            if json_load["code"] == 551:
                depth = json_load[0]["earthquake"]["hypocenter"]["depth"]
                magnitude = json_load[0]["earthquake"]["hypocenter"]["magnitude"]
                time1 = datetime.datetime.strptime(json_load[0]["earthquake"]["hypocenter"]["time"], '%H時%M分')
                time = str(time1)
                hyposentername = json_load[0]["earthquake"]["hypocenter"]["name"]
                scale = json_load[0]["earthquake"]["hypocenter"]["maxScale"]
                domesticTsunami = json_load[0]["earthquake"]["domesticTsunami"]
                magnitude = json_load[0]["earthquake"]["hypocenter"]["magnitude"]
                latitude = json_load[0]["earthquake"]["hypocenter"]["latitude"]
                longitude = json_load[0]["earthquake"]["hypocenter"]["longitude"]
                maxScale ={
                    "10" : "1",
                    "20" : "2",
                    "30" : "3",
                    "40" : "4",
                    "50" : "5弱",
                    "55" : "5強",
                    "60" : "6弱",
                    "65" : "6強",
                    "70" : "7",
                }
                if domesticTsunami == "Warning":
                    tunami = "現在、津波警報が発表されています。"
                else:
                    tunami = "この地震による津波の心配はありません。"
                speak_bouyomi(f'{time}ごろ、{hyposentername}をしんげんとするさいだいしんど{maxScale[scale]}のじしんがはっせいしました。{tunami}')
                print(f"{Color.BLUE}[EEW]{Color.RESET}地震発生 {time}頃、{hyposentername}を震源とする最大震度{maxScale[scale]}の地震が発生しました。{tunami}")
            else:
                pass

def client():
    loop = asyncio.new_event_loop()
    loop.create_task(connect())
    loop.run_forever()

client()