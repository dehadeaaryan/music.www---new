from time import sleep
from backend import *

import os

b = Backend()

b.createPlaylist("test")
b.insertInto("test", "Banana", "lemonMan2")
b.printAllFromTable("test")
# b.insertInto()
# b.playSong("lover")

# while True:
#     s = input()
#     if s == "d" or s == "D":
#         b.next()
#     if s == "a" or s == "A":
#         b.previous()
#     if s == " " or s == "p" or s == "P":
#         b.pauseOrPlay()
#     if s == "r" or s == "R":
#         b.repeat()
#     if s == "s" or s == "S":
#         b.shuffle()
#     if s == "w" or s == "W":
#         print(b.getCurrentSong(), b.getCurrentArtist())
#     if s == "t" or s == "T":
#         print(b.getCurrentTime())
#     if s == "q" or s == "Q":
#         break
b.quit()