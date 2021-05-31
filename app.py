from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import ttk
import pygame
from mutagen.mp3 import MP3
import random
import os
import platform
import time
import sqlite3

# <--------------------------------------------------------------------------->

root = Tk()
root.title("Music Player")
if(platform.system() == "Windows"):
    root.iconbitmap("assets/appicon.ico")
elif(platform.system() == "Darwin"):
    root.iconbitmap("assets/appicon.icns")
else:
    root.iconbitmap("assets/appicon.xbm")
root.geometry("1000x600")
pygame.mixer.init()

# <--------------------------------------------------------------------------->

# Custom class for simpledialogbox
class StringDialog(simpledialog._QueryString):
    def body(self, master):
        super().body(master)
        if(platform.system() == "Windows"):
            self.iconbitmap("assets/appicon.ico")
        elif(platform.system() == "Darwin"):
            self.iconbitmap("assets/appicon.icns")
        else:
            self.iconbitmap("assets/appicon.xbm")

def ask_string(title, prompt, **kargs):
    d = StringDialog(title, prompt, **kargs)
    return d.result

# <--------------------------------------------------------------------------->

# Add a single song (Songs Menu function)
def addSong():
    global songDirectory
    global songCounter
    currentdir = os.getcwd()
    song = filedialog.askopenfilename(initialdir=currentdir, title="Choose songs", filetypes=(("mp3 Files", "*.mp3"), ))
    if song != "":
        currentsong = {}
        currentsong["name"] = os.path.basename(song).replace(".mp3", "")
        currentsong["path"] = song
        songPresent = False
        for k in songDirectory.keys():
            if songDirectory[k]["name"] == currentsong["name"] or songDirectory[k]["path"] == currentsong["path"]:
                songPresent = True
                break
        if not songPresent:
            songDirectory[songCounter] = currentsong
            songCounter = songCounter + 1
            songsList.insert(END, currentsong["name"])

#  Add multiple songs (Songs Menu function)
def addMultipleSongs():
    global songDirectory
    global songCounter
    currentdir = os.getcwd()
    songs = filedialog.askopenfilenames(initialdir=currentdir, title="Choose songs", filetypes=(("mp3 Files", "*.mp3"), ))
    if len(songs) != 0:
        for song in songs:
            currentsong = {}
            currentsong["name"] = os.path.basename(song).replace(".mp3", "")
            currentsong["path"] = song
            songPresent = False
            for k in songDirectory.keys():
                if songDirectory[k]["name"] == currentsong["name"] or songDirectory[k]["path"] == currentsong["path"]:
                    songPresent = True
                    break
            if not songPresent:
                songDirectory[songCounter] = currentsong
                songCounter = songCounter + 1
                songsList.insert(END, currentsong["name"])

# Find playtime of song
def songPlayTime():
    global songStopped
    global songPaused
    global songDirectory
    global songIsLooped
    global listIsLooped
    if songStopped:
        return
    currentTime = pygame.mixer.music.get_pos()/1000 # pygame returns time in milliseconds, divide by 1000 to get seconds
    formattedTime = time.strftime('%M:%S', time.gmtime(currentTime))
    currentSong = songsList.get(ACTIVE)
    currentSongPath = None
    for k in songDirectory.keys():
        if songDirectory[k]["name"] == currentSong:
            currentSongPath = songDirectory[k]["path"]
    songMeta = MP3(currentSongPath)
    songLength = songMeta.info.length
    formattedSongLength = time.strftime('%M:%S', time.gmtime(songLength))
    currentTime = currentTime + 1
    if int(progressBar.get()) == int(songLength):
        timeLabel.config(text=f"Time Elapsed : {formattedSongLength} | {formattedSongLength}")
        if songIsLooped:
            playSong()
        if listIsLooped:
            nextSong()
    elif songPaused:
        pass
    elif int(progressBar.get()) == int(currentTime):
        position = int(songLength)
        progressBar.config(to=position, value=int(currentTime))
    else:
        position = int(songLength)
        progressBar.config(to=position, value=int(progressBar.get()))
        formatTime = time.strftime('%M:%S', time.gmtime(int(progressBar.get())))
        timeLabel.config(text=f"Time Elapsed : {formatTime} | {formattedSongLength}")
        nextPos = int(progressBar.get())+1
        progressBar.config(value=nextPos)
    timeLabel.after(1000, songPlayTime)

# Play Button Function
def playSong():
    global songStopped
    global songDirectory
    global songCounter
    global songPaused
    checkSelection = songsList.curselection()
    if len(checkSelection)!=0:
        songStopped = False
        songPaused = False
        song = songsList.get(ACTIVE)
        songPath = None
        for i in songDirectory.keys():
            if songDirectory[i]["name"]==song:
                songPath = songDirectory[i]["path"]
                break
        timeLabel.config(text="")
        progressBar.config(value=0)
        songPlayTime()
        songInfo.config(text=f"Currently Playing : {song}")
        pygame.mixer.music.load(songPath)
        pygame.mixer.music.play(loops=0)

# Pause Button Function
def pauseSong(isPaused):
    global songPaused
    songPaused = isPaused
    if songPaused:
        pygame.mixer.music.unpause()
        songPaused = False
    else:
        pygame.mixer.music.pause()
        songPaused = True

# Stop Song Button Function
def stopSong():
    global songStopped
    timeLabel.config(text="")
    progressBar.config(value=0)
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    songInfo.config(text="No Song Selected")
    songsList.selection_clear(ACTIVE)
    songStopped = True

# Next Song Button Function
def nextSong():
    global songDirectory
    global songCounter
    global songPaused
    if len(songDirectory.keys()) > 1:
        timeLabel.config(text="")
        progressBar.config(value=0)
        currentSong = songsList.curselection()
        next = currentSong[0]+1
        if next>=songCounter:
            next = 0
        requiredSong = songsList.get(next)
        reqSongPath = None
        for k in songDirectory.keys():
            if songDirectory[k]["name"] == requiredSong:
                reqSongPath = songDirectory[k]["path"]
                break
        pygame.mixer.music.load(reqSongPath)
        pygame.mixer.music.play(loops=0)
        songInfo.config(text=f"Currently Playing : {requiredSong}")
        songsList.selection_clear(0, END)
        songsList.activate(next)
        songsList.selection_set(next, last=None)
        songPaused = False

# Previous Song Button Function
def previousSong():
    global songDirectory
    global songCounter
    global songPaused
    if len(songDirectory.keys()) > 1:
        timeLabel.config(text="")
        progressBar.config(value=0)
        currentSong = songsList.curselection()
        prev = currentSong[0]-1
        if prev<0:
            prev = songCounter-1
        requiredSong = songsList.get(prev)
        reqSongPath = None
        for k in songDirectory.keys():
            if songDirectory[k]["name"] == requiredSong:
                reqSongPath = songDirectory[k]["path"]
                break
        pygame.mixer.music.load(reqSongPath)
        pygame.mixer.music.play(loops=0)
        songInfo.config(text=f"Currently Playing : {requiredSong}")
        songsList.selection_clear(0, END)
        songsList.activate(prev)
        songsList.selection_set(prev, last=None)
        songPaused = False

# Remove current Song (Songs Menu function)
def removeCurrentSong():
    global songDirectory
    global songCounter
    checkSelect = songsList.curselection()
    if len(checkSelect)!=0:
        currentSong = songsList.get(ACTIVE)
        stopSong()
        songsList.delete(ANCHOR)
        pygame.mixer.music.stop()
        currentSongIndex = None
        for k in songDirectory.keys():
            if songDirectory[k]["name"]==currentSong:
                currentSongIndex = k
                break
        songDirectory.pop(currentSongIndex, None)
        songCounter = songCounter - 1
        songInfo.config(text="No Song Selected")

# Remove all songs (Songs Menu Function)
def removeAllSongs():
    global songDirectory
    global songCounter
    stopSong()
    songsList.delete(0, END)
    pygame.mixer.music.stop()
    songInfo.config(text="No Song Selected")
    songDirectory = {}
    songCounter = 0

# Volume Bar Function. The x is passed as a variable since ttk.Scale will keep sending current value which we need to take.
def volumeBar(x):
    pygame.mixer.music.set_volume(volumeScale.get())
    if pygame.mixer.music.get_volume() == 0:
        volumeLabel.config(image=muteLabelImage)
    else:
        volumeLabel.config(image=volumeLabelImage)

# Song Progress Bar Function
def songProgress(x):
    global songDirectory
    currentSong = songsList.get(ACTIVE)
    currentSongPath = None
    for k in songDirectory.keys():
        if songDirectory[k]["name"] == currentSong:
            currentSongPath = songDirectory[k]["path"]
    pygame.mixer.music.load(currentSongPath)
    pygame.mixer.music.play(loops=0, start=int(progressBar.get()))

# Loop Current Song
def loopCurrentSong():
    global songIsLooped
    global listIsLooped
    if songIsLooped == False:
        songIsLooped = True
        loopSongButton.config(text="Loop Song : ON")
        if listIsLooped == True:
            listIsLooped = False
            loopPlaylistButton.config(text="Loop Playlist : OFF")
    else:
        songIsLooped = False
        loopSongButton.config(text="Loop Song : OFF")

# Loop the playlist
def loopPlaylist():
    global listIsLooped
    global songIsLooped
    if listIsLooped == False:
        listIsLooped = True
        loopPlaylistButton.config(text="Loop Playlist : ON")
        if songIsLooped == True:
            songIsLooped = False
            loopSongButton.config(text="Loop Song : OFF")
    else:
        listIsLooped = False
        loopPlaylistButton.config(text="Loop Playlist : OFF")

# Shuffle the playlist
def shufflePlaylist():
    global songDirectory
    global songCounter
    stopSong()
    dirKeys = list(songDirectory.keys())
    songIndex = 0
    tempSongDirectory = {}
    while len(dirKeys) != 0:
        k = random.choice(dirKeys)
        kSong = songDirectory[k]
        tempSongDirectory[songIndex] = kSong
        songIndex = songIndex + 1
        dirKeys.remove(k)
    removeAllSongs()
    songDirectory = tempSongDirectory
    for k in songDirectory.keys():
        songsList.insert(END, songDirectory[k]["name"])

def createPlaylist():

    global songDirectory
    global songCounter
    if songCounter == 0:
        messagebox.showerror(title="Error", message="Please add songs in the playlist before creating it")
        return

    con = sqlite3.connect("musicPlayerPlaylists.db")
    c = con.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS PLAYLISTS
             (
                 playlistID INTEGER PRIMARY KEY,
                 playlistName TEXT NOT NULL UNIQUE
             )''')
    c.execute('''CREATE TABLE IF NOT EXISTS SONGS
             (
                 songID INTEGER PRIMARY KEY,
                 songName TEXT NOT NULL UNIQUE,
                 songPath TEXT NOT NULL UNIQUE
             )''')
    c.execute('''CREATE TABLE IF NOT EXISTS PLAYLIST_SONGS
             (
                 mapID INTEGER PRIMARY KEY,
                 playlistID INTEGER,
                 songID INTEGER,
                 songPosition INTEGER,
                 FOREIGN KEY (playlistID) REFERENCES PLAYLISTS (playlistID),
                 FOREIGN KEY (songID) REFERENCES SONGS (songID)
             )''')

    enteredPlayListName = None
    enteredPlayListName = ask_string(title="Playlist Name", prompt="Enter a name for the playlist : ")
    enteredPlayListName = enteredPlayListName.strip() # remove leading and trailing whitespaces to avoid empty playlist names
    c.execute('''SELECT playlistName FROM PLAYLISTS''')
    checkIfPlaylistExists = c.fetchall()
    checkIfPlaylistExists = [i[0] for i in checkIfPlaylistExists]

    if enteredPlayListName == "":
        messagebox.showerror(title="Error", message="Playlist name cannot be empty")

    elif enteredPlayListName == None:
        messagebox.showinfo(title="Cancelled", message="Playlist creation cancelled")

    elif enteredPlayListName in checkIfPlaylistExists:
        messagebox.showerror(title="Error", message="The entered playlist name already exists. Please use another name.")

    else:
        confirmation = messagebox.askyesno(title="Confirmation", message="Confirm playlist creation")
        if confirmation:
            c.execute('''INSERT INTO PLAYLISTS VALUES (NULL,?)''',(enteredPlayListName,))
            c.execute('''SELECT playlistID FROM PLAYLISTS WHERE playlistName=:pLN''',{"pLN":enteredPlayListName})
            currentPlaylistID = c.fetchall()
            currentPlaylistID = currentPlaylistID[0][0]
            currentSongPos = 0
            for k in songDirectory.keys():
                currentSongName = songDirectory[k]["name"]
                currentSongPath = songDirectory[k]["path"]
                # check and see if song is already present in the songs table
                c.execute('''SELECT songID FROM SONGS WHERE songName=:sNG AND songPath=:sGP''',{"sNG":currentSongName,"sGP":currentSongPath})
                checkSongExists = c.fetchall()
                # song already exists, so we dont add
                if len(checkSongExists) != 0:
                    c.execute('''SELECT songID FROM SONGS WHERE songName=:sNG AND songPath=:sGP''',{"sNG":currentSongName,"sGP":currentSongPath})
                    currentSongID = c.fetchall()
                    currentSongID = currentSongID[0][0]
                    c.execute('''INSERT INTO PLAYLIST_SONGS VALUES (NULL,?,?,?)''',(currentPlaylistID,currentSongID,currentSongPos))
                # song doesn't exist yet, so we add it
                else: 
                    c.execute('''INSERT INTO SONGS VALUES (NULL,?,?)''',(currentSongName,currentSongPath))
                    c.execute('''SELECT songID FROM SONGS WHERE songName=:sNG AND songPath=:sGP''',{"sNG":currentSongName,"sGP":currentSongPath})
                    currentSongID = c.fetchall()
                    currentSongID = currentSongID[0][0]
                    c.execute('''INSERT INTO PLAYLIST_SONGS VALUES (NULL,?,?,?)''',(currentPlaylistID,currentSongID,currentSongPos))
                currentSongPos = currentSongPos + 1
        messagebox.showinfo(title="Playlist Created", message=f"The playlist : {enteredPlayListName} has been created.")

    con.commit()
    con.close()

def undoDisableState(event):

    playlistMenu.entryconfigure(1, state=ACTIVE)
    playlistMenu.entryconfigure(2, state=ACTIVE)

def loadSelectedPlaylist(selectedPlaylist, loadPlaylistWindow):

    global songDirectory
    global songCounter

    removeAllSongs()

    con = sqlite3.connect("musicPlayerPlaylists.db")
    c = con.cursor()

    c.execute('''SELECT playlistID FROM PLAYLISTS WHERE playlistName=:pLN''',{"pLN":selectedPlaylist})
    selectedPlaylistID = c.fetchall()
    selectedPlaylistID = selectedPlaylistID[0][0]

    c.execute('''SELECT * FROM PLAYLIST_SONGS WHERE playlistID=:pLID''',{"pLID":selectedPlaylistID})
    songsOfPlaylist = c.fetchall()
    
    songIDsOfPlaylist = [i[2] for i in songsOfPlaylist]
    songPosOfPlaylist = [i[3] for i in songsOfPlaylist]
    songExistsFlag = True
    tempSongDirectory = {}
    tempCounter = 0
    for id in songIDsOfPlaylist:
        c.execute('''SELECT * FROM SONGS WHERE songID=:sID''',{"sID":id})
        dets = c.fetchall()
        dets = dets[0]
        currentSong = {}
        currentSong["name"] = dets[1]
        currentSong["path"] = dets[2]
        if os.path.exists(currentSong["path"]):
            tempSongDirectory[songPosOfPlaylist[tempCounter]] = currentSong
            tempCounter = tempCounter + 1
        else:
            songExistsFlag = False
            songName=currentSong["name"]
            con.commit()
            con.close()
            loadPlaylistWindow.destroy()
            messagebox.showerror(title="Error",message=f"The file {songName}  present in the playist - {selectedPlaylist} no longer exists. The file has been moved to a new location or has been deleted. Please DELETE THIS PLAYLIST to avoid any further errors.")
            break

    if songExistsFlag:
        songDirectory = tempSongDirectory
        songCounter = len(songIDsOfPlaylist)
        for k in songDirectory.keys():
            songsList.insert(END, songDirectory[k]["name"])

        con.commit()
        con.close()
        loadPlaylistWindow.destroy()

def loadPlaylist():

    playlistMenu.entryconfigure(1, state=DISABLED)
    playlistMenu.entryconfigure(2, state=DISABLED)
    loadPlaylistWindow = Toplevel(root)
    loadPlaylistWindow.title("Load a Playlist")
    if(platform.system() == "Windows"):
        loadPlaylistWindow.iconbitmap("assets/appicon.ico")
    elif(platform.system() == "Darwin"):
        loadPlaylistWindow.iconbitmap("assets/appicon.icns")
    else:
        loadPlaylistWindow.iconbitmap("assets/appicon.xbm")
    loadPlaylistWindow.geometry("500x650")
    loadPlaylistWindow.resizable(width=0,height=0)
    loadPlaylistWindow.bind("<Destroy>", undoDisableState)

    loadFrame = ttk.Frame(loadPlaylistWindow)
    loadFrame.grid(row=0, column=0, sticky=(N, S, E, W))
    uploadInfoLabel = ttk.Label(loadFrame, text="Select the playlist to be loaded and click on the Load Playlist button", anchor=CENTER)
    uploadInfoLabel.pack(side=TOP, pady=30)
    playlistsListBox = Listbox(loadFrame, activestyle="none", font=(font.nametofont("TkDefaultFont"),14), height=20)
    playlistsListBox.pack(fill=BOTH, padx=20)
    confirmButton = ttk.Button(loadFrame, text="Load Playlist", command=lambda : loadSelectedPlaylist(playlistsListBox.get(ACTIVE), loadPlaylistWindow))
    confirmButton.pack(side=TOP, pady=30)
    loadPlaylistWindow.rowconfigure(0, weight=1)
    loadPlaylistWindow.columnconfigure(0, weight=1)

    con = sqlite3.connect("musicPlayerPlaylists.db")
    c = con.cursor()

    try: 

        c.execute('''SELECT * FROM PLAYLISTS''')
        listOfPlaylists = c.fetchall()
        listOfPlaylists = [i[1] for i in listOfPlaylists]

        if len(listOfPlaylists) != 0:
            for k in listOfPlaylists:
                playlistsListBox.insert(END, k)

            con.commit()
            con.close()
        
        else:
            con.commit()
            con.close()
            loadPlaylistWindow.destroy()
            messagebox.showerror(title="Error",message="No playlists have been created yet.")

    except:

        con.commit()
        con.close()
        loadPlaylistWindow.destroy()
        messagebox.showerror(title="Error",message="No playlists have been created yet.")

def deleteSelectedPlaylist(selectedPlaylist, deletePlaylistWindow):
    
    con = sqlite3.connect("musicPlayerPlaylists.db")
    c = con.cursor()

    c.execute('''SELECT playlistID FROM PLAYLISTS WHERE playlistName=:pLN''',{"pLN":selectedPlaylist})
    selectedPlaylistID = c.fetchall()
    selectedPlaylistID = selectedPlaylistID[0][0]

    c.execute('''DELETE FROM PLAYLIST_SONGS WHERE playlistID=:pLID''',{"pLID":selectedPlaylistID})
    c.execute('''DELETE FROM PLAYLISTS WHERE playlistName=:pLN''',{"pLN":selectedPlaylist})

    con.commit()
    con.close()
    deletePlaylistWindow.destroy()

def deletePlaylist():

    playlistMenu.entryconfigure(1, state=DISABLED)
    playlistMenu.entryconfigure(2, state=DISABLED)
    deletePlaylistWindow = Toplevel(root)
    deletePlaylistWindow.title("Delete a Playlist")
    if(platform.system() == "Windows"):
        deletePlaylistWindow.iconbitmap("assets/appicon.ico")
    elif(platform.system() == "Darwin"):
        deletePlaylistWindow.iconbitmap("assets/appicon.icns")
    else:
        deletePlaylistWindow.iconbitmap("assets/appicon.xbm")
    deletePlaylistWindow.geometry("500x650")
    deletePlaylistWindow.resizable(width=0, height=0)
    deletePlaylistWindow.bind("<Destroy>", undoDisableState)

    deleteFrame = ttk.Frame(deletePlaylistWindow)
    deleteFrame.grid(row=0, column=0, sticky=(N, S, E, W))
    deleteInfoLabel = ttk.Label(deleteFrame, text="Select the playlist to be deleted and click on the Delete Playlist button", anchor=CENTER)
    deleteInfoLabel.pack(side=TOP, pady=30)
    playlistsListBox = Listbox(deleteFrame, activestyle="none", font=(font.nametofont("TkDefaultFont"),14), height=20)
    playlistsListBox.pack(fill=BOTH, padx=20)
    confirmButton = ttk.Button(deleteFrame, text="Delete Playlist", command=lambda : deleteSelectedPlaylist(playlistsListBox.get(ACTIVE), deletePlaylistWindow))
    confirmButton.pack(side=TOP, pady=30)
    deletePlaylistWindow.rowconfigure(0, weight=1)
    deletePlaylistWindow.columnconfigure(0, weight=1)

    con = sqlite3.connect("musicPlayerPlaylists.db")
    c = con.cursor()

    try:

        c.execute('''SELECT * FROM PLAYLISTS''')
        listOfPlaylists = c.fetchall()
        listOfPlaylists = [i[1] for i in listOfPlaylists]

        if len(listOfPlaylists) != 0:
            for k in listOfPlaylists:
                playlistsListBox.insert(END, k)

            con.commit()
            con.close()

        else:
            con.commit()
            con.close()
            deletePlaylistWindow.destroy()
            messagebox.showerror(title="Error",message="No playlists have been created yet.")

    except:

        con.commit()
        con.close()
        deletePlaylistWindow.destroy()
        messagebox.showerror(title="Error",message="No playlists have been created yet.")

# <--------------------------------------------------------------------------->

# Global Variables
global songPaused
songPaused = False
global songStopped
songStopped = False
global songDirectory
songDirectory = {}
global songCounter
songCounter = 0
global songIsLooped
songIsLooped = False
global listIsLooped
listIsLooped = False

# Assets
playButtonImage = PhotoImage(file="assets/play-button.png")
pauseButtonIimage = PhotoImage(file="assets/pause-button.png")
nextButtonImage = PhotoImage(file="assets/next-button.png")
prevButtonImage = PhotoImage(file="assets/previous-button.png")
stopButtonImage = PhotoImage(file="assets/stop-button.png")
loopSongButtonImage = PhotoImage(file="assets/loopsong.png")
loopPlaylistButtonImage = PhotoImage(file="assets/loop.png")
shuffleButtonImage = PhotoImage(file="assets/shuffle.png")
volumeLabelImage = PhotoImage(file="assets/speaker.png")
muteLabelImage = PhotoImage(file="assets/speaker-off.png")

# <--------------------------------------------------------------------------->

# Appearance
styleconfig = ttk.Style()
styleconfig.configure("TLabel", font=(font.nametofont("TkDefaultFont"),12), anchor="center")
# Light Mode
# styleconfig.configure("TFrame", background="#f7fbfc")
# styleconfig.configure("Dark.TFrame", background="#d6e6f2")
# styleconfig.configure("Darker.TFrame", background="#b9d7ea")
# styleconfig.configure("TLabel", background="#b9d7ea")

# <--------------------------------------------------------------------------->

# Structure
# Main Window
mainframe = ttk.Frame(root, padding="10")
mainframe.grid(row=0, column=0, sticky=(N, E, S, W))

# Control Panel
subframe1 = ttk.Frame(mainframe, padding="5", borderwidth=2, relief="solid")
subframe1.grid(row=0, column=0, sticky=(N, E, S, W), padx=10, pady=10)

# Song Information Label
songInfo = ttk.Label(subframe1, text="No Song Selected")
songInfo.grid(row=0, column=0, sticky=(N, E, S, W))

# Button Set 1 
buttonSet1Frame = ttk.Frame(subframe1, borderwidth=2, padding="2", relief="solid")
buttonSet1Frame.grid(row=1, column=0, pady=30, sticky=(N, E, S, W))
prevButton = ttk.Button(buttonSet1Frame, image=prevButtonImage, command=previousSong, text="Previous", compound="top")
prevButton.grid(row=0, column=0, padx=10)
playButton = ttk.Button(buttonSet1Frame, image=playButtonImage, command=playSong, text="Play", compound="top")
playButton.grid(row=0, column=1, padx=10)
pauseButton = ttk.Button(buttonSet1Frame, image=pauseButtonIimage, command=lambda: pauseSong(songPaused), text="Pause", compound="top")
pauseButton.grid(row=0, column=2, padx=10)
stopButton = ttk.Button(buttonSet1Frame, image=stopButtonImage, command=stopSong, text="Stop", compound="top")
stopButton.grid(row=0, column=3, padx=10)
nextButton = ttk.Button(buttonSet1Frame, image=nextButtonImage, command=nextSong, text="Next", compound="top")
nextButton.grid(row=0, column=4, padx=10)

#  Button Set 2 
buttonSet2Frame = ttk.Frame(subframe1, borderwidth=2, padding="2", relief="solid")
buttonSet2Frame.grid(row=2, column=0, pady=30, sticky=(N, E, S, W))
loopSongButton = ttk.Button(buttonSet2Frame, image=loopSongButtonImage, text="Loop Song : OFF", compound="top", command=loopCurrentSong, width=16)
loopSongButton.grid(row=0, column=0, padx=10)
loopPlaylistButton = ttk.Button(buttonSet2Frame, image=loopPlaylistButtonImage, text="Loop Playlist : OFF", compound="top", command=loopPlaylist, width=20)
loopPlaylistButton.grid(row=0, column=1, padx=10)
shuffleButton = ttk.Button(buttonSet2Frame, image=shuffleButtonImage, text="Shuffle Playlist", compound="top", command=shufflePlaylist, width=17)
shuffleButton.grid(row=0, column=2, padx=10)
# playlistInfoLabel = ttk.Label(buttonSet2Frame, text="No Playlist Selected", borderwidth=2, relief="solid", padding="5 10 5 10")
# playlistInfoLabel.grid(row=0, column=3, columnspan=2, padx=10, sticky=(N, S, E, W), pady=10)

# Volume Control
volumeControlFrame = ttk.Frame(subframe1, borderwidth=2, relief="solid", padding="2")
volumeControlFrame.grid(row=3, column=0, pady=30, sticky=(N, E, S, W))
volumeLabel = ttk.Label(volumeControlFrame, text="Volume Control    " , image=volumeLabelImage, compound="right")
volumeLabel.grid(row=0, column=0, sticky=(N, S, E), padx=10)
volumeScale = ttk.Scale(volumeControlFrame, orient=HORIZONTAL, value=1, from_=0.0, to=1.0, command=volumeBar)
volumeScale.grid(row=0, column=1, columnspan=2, sticky=(N, S, E, W), padx=10)

# Song Progressbar
progressBarFrame = ttk.Frame(subframe1, borderwidth=2, relief="solid", padding="2")
progressBarFrame.grid(row=4, column=0, pady=30, sticky=(N, E, S, W))
timeLabel = ttk.Label(progressBarFrame, text="", borderwidth=2, relief="solid", padding="2 4 2 4")
timeLabel.grid(row=0, column=0, sticky=(N, S, E, W), padx=10, pady=10)
progressBar = ttk.Scale(progressBarFrame, orient=HORIZONTAL, from_=0, to=100, value=0, command=songProgress)
progressBar.grid(row=0, column=1, columnspan=2, sticky=(N, S, E, W))

# Playlist
labelForPlaylistFrame = ttk.Label(text="Playlist")
subframe2 = ttk.Labelframe(mainframe, labelwidget=labelForPlaylistFrame, borderwidth=2, relief="solid", padding="5")
subframe2.grid(row=0, column=1, sticky=(N, E, S, W), padx=10, pady=10)
songsList = Listbox(subframe2, activestyle="none", font=(font.nametofont("TkDefaultFont"),14))
songsList.grid(row=0, column=0, sticky=(N, S, E, W))

# Menu
menubar = Menu(root, tearoff=False)
root.config(menu=menubar)

songsMenu = Menu(menubar, tearoff=False)
menubar.add_cascade(label="Songs", menu=songsMenu)
songsMenu.add_command(label="Add Song", command=addSong)
songsMenu.add_command(label="Add Multiple Songs", command=addMultipleSongs)
songsMenu.add_separator()
songsMenu.add_command(label="Remove Current Song", command=removeCurrentSong)
songsMenu.add_command(label="Remove All Songs", command=removeAllSongs)

playlistMenu = Menu(menubar, tearoff=False)
menubar.add_cascade(label="Playlists", menu=playlistMenu)
playlistMenu.add_command(label="Create Playlist from songs present in Playlist Box", command=createPlaylist)
playlistMenu.add_command(label="Delete a Playlist", command=deletePlaylist)
playlistMenu.add_command(label="Load a Playlist", command=loadPlaylist)

appearanceMenu = Menu(menubar, tearoff=False)
menubar.add_cascade(label="Appearance", menu=appearanceMenu)
appearanceMenu.add_command(label="Dark Mode")
appearanceMenu.add_command(label="Light Mode")

# Handling Resizing
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe.columnconfigure(0, weight=2)
mainframe.columnconfigure(1, weight=2)
mainframe.rowconfigure(0, weight=1)
subframe1.columnconfigure(0, weight=1)
subframe1.rowconfigure(0, weight=1)
subframe1.rowconfigure(1, weight=1)
subframe1.rowconfigure(2, weight=1)
subframe1.rowconfigure(3, weight=1)
subframe1.rowconfigure(4, weight=1)
subframe2.rowconfigure(0, weight=1)
subframe2.columnconfigure(0, weight=1)
buttonSet1Frame.columnconfigure(0, weight=1)
buttonSet1Frame.columnconfigure(1, weight=1)
buttonSet1Frame.columnconfigure(2, weight=1)
buttonSet1Frame.columnconfigure(3, weight=1)
buttonSet1Frame.columnconfigure(4, weight=1)
buttonSet1Frame.rowconfigure(0, weight=1)
buttonSet2Frame.columnconfigure(0, weight=1)
buttonSet2Frame.columnconfigure(1, weight=1)
buttonSet2Frame.columnconfigure(2, weight=1)
# buttonSet2Frame.columnconfigure(3, weight=1)
# buttonSet2Frame.columnconfigure(4, weight=1)
buttonSet2Frame.rowconfigure(0, weight=1)
volumeControlFrame.columnconfigure(0, weight=1)
volumeControlFrame.columnconfigure(1, weight=1)
volumeControlFrame.columnconfigure(2, weight=1)
volumeControlFrame.rowconfigure(0, weight=1)
progressBarFrame.columnconfigure(0, weight=1)
progressBarFrame.columnconfigure(1, weight=1)
progressBarFrame.columnconfigure(2, weight=1)
progressBarFrame.rowconfigure(0, weight=1)

root.mainloop()