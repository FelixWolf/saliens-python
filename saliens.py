#!/usr/bin/env python3
#Copyright 2018 Félix
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import argparse
import json
import urllib.request
import urllib.parse
import urllib.error
import webbrowser
import random
import time

def main(token, planet=None):
    serverCtx = CServerInterface(token)
    pinfo = serverCtx.GetPlayerInfo()
    print("Current score = {}/{}; Current Level = {}".format(
        pinfo["response"]["score"],
        pinfo["response"]["next_level_score"],
        pinfo["response"]["level"]
    ))
    if not planet:
        planet = pinfo['response']["active_planet"]
        #planets = serverCtx.GetPlanets()
        #planet = random.choice(planets["response"]["planets"])["id"]
    
    serverCtx.JoinPlanet(planet)
    print("Joined planet {}".format(planet))
    while True:
        planetInfo = serverCtx.GetPlanet(planet)
        zone = None
        for i in range(3,0,-1):
            for zone in planetInfo["response"]["planets"][0]["zones"]:
                if zone["captured"] == False and zone["difficulty"] == i:
                    zone = zone
                    break
            if zone != None:
                break
        
        if zone != None:
            print("Attacking zone {0} diff = {1}".format(zone["zone_position"], zone["difficulty"]))
        else:
            print("Out of zones? Finding a new planet!")
            planets = serverCtx.GetPlanets()
            for Planet in planets["response"]["planets"]:
                if Planet["state"]["capture_progress"] < 1:
                    print("Planet #{} - {} ({}%) seems nice, joining there!".format(
                        Planet["id"],
                        Planet["state"]["name"],
                        int(Planet["state"]["capture_progress"]*100)
                    ))
                    planet = Planet["id"]
                    break
        
        #Sleep before joining zone
        time.sleep(random.randint(5,10))
        
        serverCtx.JoinZone(zone["zone_position"])
        
        time.sleep(120) #Sleep for 2 minutes
        
        #Fix for difficulty score difference thing possibly?
        score = 120
        if zone["difficulty"] == 1:
            score = 595
        elif zone["difficulty"] == 2:
            score = 1190
        elif zone["difficulty"] == 3:
            score = 2380
        else:
            print("PANIC! THEY UPDATED THE MAX DIFFICULTY!")
        
        try:
            scoreStats = serverCtx.ReportScore(score) #
            print("Current score = {}/{}; Current Level = {}".format(
                scoreStats["response"]["new_score"],
                scoreStats["response"]["next_level_score"],
                scoreStats["response"]["new_level"]
            ))
        except KeyError:
            print("It tossed our request(Too early?), maybe next time. :(")
    

class CServerInterface:
    #Universal headers
    headers = {
        "Accept": "*/*",
        "Origin": "https://steamcommunity.com",
        "Referer": "https://steamcommunity.com/saliengame/play",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36"
    }
    gLanguage = "english"
    
    def __init__(self, token=None):
        self.token = token
    
    #Base networking
    m_strHost = "https://community.steam-api.com/"
    def BuildURL(self, strInterface, strMethod, strVersion="v0001"):
        return "{}{}/{}/{}/".format(self.m_strHost, strInterface, strMethod, strVersion)
    
    def get(self, path):
        while True:
            try:
                req = urllib.request.Request(path, headers=self.headers)
                with urllib.request.urlopen(req) as res:
                    return json.loads(res.read().decode())
            except urllib.error.HTTPError as e:
                print("HTTP {} - {}\nRetrying in 1 second...".format(e.code, e.reason))
            
            time.sleep(1)
    
    def post(self, path, data):
        while True:
            try:
                req = urllib.request.Request(path, headers={
                    **self.headers,
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                })
                with urllib.request.urlopen(req, data=data.encode()) as res:
                    return json.loads(res.read().decode())
            except urllib.error.HTTPError as e:
                print("HTTP {} - {}\nRetrying in 1 second...".format(e.code, e.reason))
            
            time.sleep(1)
    
    #network.js implementation
    def GetPlanet(self, planetid):
        return self.get("{}?{}".format(
            self.BuildURL('ITerritoryControlMinigameService', 'GetPlanet'),
            urllib.parse.urlencode({
                "id": planetid,
                "language": self.gLanguage
            })
        ))
    
    def GetPlanets(self):
        return self.get("{}?{}".format(
            self.BuildURL('ITerritoryControlMinigameService', 'GetPlanets'),
            urllib.parse.urlencode({
                "active_only": 1,
                "language": self.gLanguage
            })
        ))
    
    def GetPlayerInfo(self):
        return self.post(
            self.BuildURL('ITerritoryControlMinigameService', 'GetPlayerInfo'),
            urllib.parse.urlencode({
                "access_token": self.token
            })
        )
    
    def JoinPlanet(self, planetid):
        return self.post(
            self.BuildURL('ITerritoryControlMinigameService', 'JoinPlanet'),
            urllib.parse.urlencode({
                "id": planetid,
                "access_token": self.token
            })
        )
    
    def JoinZone(self, zoneid):
        return self.post(
            self.BuildURL('ITerritoryControlMinigameService', 'JoinZone'),
            urllib.parse.urlencode({
                "zone_position": zoneid,
                "access_token": self.token
            })
        )
    
    def RepresentClan(self, ulClanid):
        return self.post(
            self.BuildURL('ITerritoryControlMinigameService', 'RepresentClan'),
            urllib.parse.urlencode({
                "access_token": self.token,
                "clanid": ulClanid
            })
        )
    
    def ReportScore(self, nScore):
        return self.post(
            self.BuildURL('ITerritoryControlMinigameService', 'ReportScore'),
            urllib.parse.urlencode({
                "score": nScore,
                "access_token": self.token,
                "language": self.gLanguage
            })
        )
    
    def LeaveGameInstance(self, instanceid):
        return self.post(
            self.BuildURL('ITerritoryControlMinigameService', 'LeaveGame'),
            urllib.parse.urlencode({
                "gameid": instanceid,
                "access_token": self.token
            })
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--token", help="Token value from https://steamcommunity.com/saliengame/gettoken")
    parser.add_argument("-p", "--planet", help="Planet ID")
    parser.add_argument("-l", "--list-planets", action='store_true', help="List planets")
    args = parser.parse_args()
    if args.list_planets:
        serverCtx = CServerInterface()
        planets = serverCtx.GetPlanets()
        for planet in planets["response"]["planets"]:
            print("{}: {} ({}%)".format(planet["id"], planet["state"]["name"], int(planet["state"]["capture_progress"]*100)))
        exit()
    
    if not args.token:
        print(
            "A browser page will open, please copy and paste the value of \"token\"\n"
            "This will look like: 00112233445566778899aabbccddeeff"
        )
        webbrowser.open("https://steamcommunity.com/saliengame/gettoken")
        args.token = input("Token: ")
    
    if len(args.token) != 32:
        print("Token is invalid, it should look like 00112233445566778899aabbccddeeff and be 32 characters long!");
        exit()
    
    main(args.token, args.planet)
        
    
    
