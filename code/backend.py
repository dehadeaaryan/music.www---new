"""
Music.www backend
"""

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Other imports
import os
import pyttsx3
import random
import time
import threading
import sqlite3

# Global variables
HOME_URL = "https://www.youtube.com/"
RUNNING = True
TIME = "0:00 / 0:00 ~ LOADING"
CAN_PROCEED = False
DB_INITIALIZED = False
FAV, LIKED, DISLIKED, RECENT = "fav", "liked", "disliked", "recent"

class Backend:
    def __init__(self) -> None:
        global DB_INITIALIZED
        self.options = webdriver.firefox.options.Options()
        self.options.headless = True
        self.driver = webdriver.Firefox(executable_path = f"{os.getcwd()}/geckodriver", options = self.options)

        self.timeGetterThread = threading.Thread(target = self.getTime)
        self.timeGetterThread.start()

        self.functionsAvailableThread = threading.Thread(target = self.canProceed)

        self.dbConnection = sqlite3.connect("db/musicwww.db")
        self.dbCursor = self.dbConnection.cursor()

        self.createTables()
    


    def search(self, query: str) -> None:
        self.driver.get(f"https://music.youtube.com/search?q={query}")
    
    def filterSongs(self) -> None:
        self.clickElementByXpath("/html/body/ytmusic-app/ytmusic-app-layout/div[3]/ytmusic-search-page/ytmusic-tabbed-search-results-renderer/div[2]/ytmusic-section-list-renderer/div[1]/ytmusic-chip-cloud-renderer/div/ytmusic-chip-cloud-chip-renderer[1]/a")
    
    def clickFirstResult(self) -> None:
        time.sleep(1)
        self.clickElementByXpath("/html/body/ytmusic-app/ytmusic-app-layout/div[3]/ytmusic-search-page/ytmusic-tabbed-search-results-renderer/div[2]/ytmusic-section-list-renderer/div[2]/ytmusic-shelf-renderer/div[2]/ytmusic-responsive-list-item-renderer[1]/div[2]/div[1]/yt-formatted-string/a")
    
    def playSong(self, songName: str) -> None:
        self.search(songName)
        time.sleep(1)
        self.filterSongs()
        self.clickFirstResult()
        self.functionsAvailableThread.start()
    
    def pauseOrPlay(self) -> None:
        self.clickElementByXpath("/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-player-bar/div[1]/div/tp-yt-paper-icon-button[3]")
    
    def next(self) -> None:
        self.clickElementByXpath("/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-player-bar/div[1]/div/tp-yt-paper-icon-button[5]") if CAN_PROCEED else None
    
    def previous(self) -> None:
        self.clickElementByXpath("/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-player-bar/div[1]/div/tp-yt-paper-icon-button[1]") if CAN_PROCEED else None
    
    def repeat(self) -> None:
        self.clickElementByXpath("/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-player-bar/div[3]/div/tp-yt-paper-icon-button[2]") if CAN_PROCEED else None
    
    def shuffle(self) -> None:
        self.clickElementByXpath("/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-player-bar/div[3]/div/tp-yt-paper-icon-button[3]") if CAN_PROCEED else None
    
    def getCurrentTime(self) -> str:
        global TIME
        try:
            TIME = self.getElementByXpath("/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-player-bar/div[1]/span").text
        except:
            TIME = "0:00 / 0:00 ~ LOADING"
        return TIME
    
    def getTime(self) -> None:
        while RUNNING:
            self.getCurrentTime()
            time.sleep(1)
    
    def canProceed(self) -> None:
        time.sleep(5)
        global CAN_PROCEED
        while not CAN_PROCEED:
            time.sleep(0.5)
            if not self.advertisementExists():
                CAN_PROCEED = True
                print("Functions available now!")
                break
    
    def getCurrentSong(self) -> str:
        return self.getElementByXpath("/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-player-bar/div[2]/div[2]/yt-formatted-string").text if CAN_PROCEED else None

    def getCurrentArtist(self) -> str:
        return self.getElementByXpath("/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-player-bar/div[2]/div[2]/span/span[2]/yt-formatted-string/a[1]").text if CAN_PROCEED else None
    
    def favouriteCurrentSong(self) -> None:
        self.insertInto(FAV, self.getCurrentSong(), self.getCurrentArtist())
    
    def likeCurrentSong(self) -> None:
        self.insertInto(LIKED, self.getCurrentSong(), self.getCurrentArtist())
    
    def dislikeCurrentSong(self) -> None:
        self.insertInto(DISLIKED, self.getCurrentSong(), self.getCurrentArtist())
    
    def addCurrentSongToRecent(self) -> None:
        self.insertInto(RECENT, self.getCurrentSong(), self.getCurrentArtist())

    def quit(self) -> None:
        global RUNNING
        RUNNING = False
        self.driver.quit()
        self.dbConnection.commit()
        self.dbConnection.close()
    
    

    # Selenium methods
    
    def getElementByXpath(self, xpath: str) -> webdriver.remote.webelement.WebElement:
        return self.driver.find_element(By.XPATH, xpath)
    
    def clickElementByXpath(self, xpath: str) -> None:
        self.driver.implicitly_wait(2)
        self.getElementByXpath(xpath).click()
    
    def sendKeysToElementByXpath(self, xpath: str, keys: str) -> None:
        self.driver.implicitly_wait(2)
        self.getElementByXpath(xpath).send_keys(keys)
    
    def checkIfPresent(self, xpath: str) -> bool:
        try:
            self.getElementByXpath(xpath)
            return True
        except:
            return False
    
    def advertisementExists(self) -> bool:
        return self.checkIfPresent("/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-player-page/div/div[1]/ytmusic-player/div[2]/div/div/div[13]/div/div[3]/div/span")

    

    # Database methods
    
    def createTables(self) -> None:
        tableNames = ["_fav", "_liked", "_disliked", "_recent"]
        for tableName in tableNames:
            self.dbCursor.execute(f"CREATE TABLE IF NOT EXISTS {tableName} (song TEXT, artist TEXT)")
        self.dbConnection.commit()
    
    def createPlaylist(self, playlistName: str) -> None:
        self.dbCursor.execute(f"CREATE TABLE IF NOT EXISTS {playlistName} (song TEXT, artist TEXT)")
        self.dbConnection.commit()
    
    def getAllTables(self) -> list:
        self.dbCursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [table[0] for table in self.dbCursor.fetchall()]
    
    def getPlaylists(self) -> list:
        self.dbCursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '\_%' ESCAPE '\\'" )
        return [table[0] for table in self.dbCursor.fetchall()]
    
    def insertInto(self, table: str, song: str, artist: str) -> None:
        self.dbCursor.execute(f"SELECT * FROM {table} WHERE song = ? AND artist = ?", (song, artist))
        if not self.dbCursor.fetchone():
            self.dbCursor.execute(f"INSERT INTO {table} (song, artist) VALUES (?, ?)", (song, artist))
            self.dbConnection.commit()
    
    def removeFrom(self, table: str, song: str, artist: str) -> None:
        self.dbCursor.execute(f"DELETE FROM {table} WHERE song = ? AND artist = ?", (song, artist))
        self.dbConnection.commit()
    
    def printAllFromTable(self, table: str) -> None:
        self.dbCursor.execute(f"SELECT * FROM {table}")
        print(self.dbCursor.fetchall())