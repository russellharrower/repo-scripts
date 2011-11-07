import sys
import os
import xbmc
import xbmcaddon
import string
import time
import ConfigParser
import string
import re

###General vars
__scriptname__ = "trakt"
__author__ = "Sean Rudford"
__url__ = "http://trakt.tv/"
__version__ = "0.1.5"
__XBMC_Revision__ = ""

def addPadding(number):
    if len(number) == 1:
        number = '0' + number
    return number

def CheckAndSubmit(Manual=False):
    sType = ""
    if xbmc.Player().isPlayingVideo():
        Debug('Video found playing',False)
        bLibraryExcluded = False
        bRatingExcluded = False
        bPathExcluded = False
        bExcluded = False
        short = ""
        title = ""
        global VideoThreshold
        global lasttitle
        global lastUpdate
        global video_id
        global sleepTime
        global checkTitle
        
        iPercComp = CalcPercentageRemaining(xbmc.getInfoLabel("VideoPlayer.Time"), xbmc.getInfoLabel("VideoPlayer.Duration"))

        if iPercComp > (float(VideoThreshold) / 100) or lastUpdate == 0 or checkTitle != xbmc.getInfoLabel("VideoPlayer.Title"):
            # do nothing and let it continue to main script
            lastUpdate = 0
            Debug("continuing to send check")
        elif (time.time() - lastUpdate < 900):
            return
        
        pauseCheck = xbmc.Player().getTime()
        time.sleep(1)
        if xbmc.Player().isPlayingVideo():
            if (xbmc.Player().getTime() == pauseCheck):
                Debug('Video is currently paused', False)
                return
        else:
            Debug('Video ended during pause check', False)
            return
        
        if ((xbmc.getInfoLabel("VideoPlayer.mpaa") == "XXX")):
            Debug('Video is with XXX mpaa rating', False)
            bRatingExcluded = True
        currentPath = xbmc.Player().getPlayingFile()
        if (currentPath.find("http://") > -1):
            Debug("Video is playing via web source.  Excluded.", False)
            bPathExcluded = True
        if ((__settings__.getSetting( "ExcludePath" ) != "") and (__settings__.getSetting( "ExcludePathOption" ) == 'true')):
            if (currentPath.find(__settings__.getSetting( "ExcludePath" )) > -1):
                Debug('Video is located in excluded path', False)
                bPathExcluded = True
        if ((__settings__.getSetting( "ExcludePath2" ) != "") and (__settings__.getSetting( "ExcludePathOption2" ) == 'true')):
            currentPath = xbmc.Player().getPlayingFile()
            if (currentPath.find(__settings__.getSetting( "ExcludePath2" )) > -1):
                Debug('Video is located in excluded path 2', False)
                bPathExcluded = True
        if ((__settings__.getSetting( "ExcludePath3" ) != "") and (__settings__.getSetting( "ExcludePathOption3" ) == 'true')):
            currentPath = xbmc.Player().getPlayingFile()
            if (currentPath.find(__settings__.getSetting( "ExcludePath3" )) > -1):
                Debug('Video is located in excluded path 3', False)
                bPathExcluded = True                     
        
        if len(xbmc.getInfoLabel("VideoPlayer.TVshowtitle")) >= 1: # TvShow
            sType = "TVShow"
            Debug("Found TV Show", False)
            
            # format: title, year, season, episode, tvdbid
            showname = xbmc.getInfoLabel("VideoPlayer.TvShowTitle")
            showname = showname.replace(",", '')
            title = (showname +
                    ',' + xbmc.getInfoLabel("VideoPlayer.Year") +
                    ',' + addPadding(xbmc.getInfoLabel("VideoPlayer.Season")) +
                    ',' + addPadding(xbmc.getInfoLabel("VideoPlayer.Episode")))

        elif len(xbmc.getInfoLabel("VideoPlayer.Title")) >= 1: #Movie
            sType = "Movie"
            Debug("Found Movie", False)
            
            # format: title, year
            moviename = xbmc.getInfoLabel("VideoPlayer.Title")
            moviename = moviename.replace(",", '')
            
            title = (moviename + ',' + xbmc.getInfoLabel("VideoPlayer.Year"))

        if (bLibraryExcluded or bPathExcluded or bRatingExcluded):
            bExcluded = True
            Debug("Excluded", False)
        
        Debug("Title: " + title)
        
        if ((title != "" and lasttitle != title) and not bExcluded):
            
            if (iPercComp > (float(VideoThreshold) / 100)):
                Debug('Title: ' + title + ', sending watched status, current percentage: ' + str(iPercComp), True)
                SendUpdate(title, int(iPercComp*100), sType, "watched")
                lasttitle = title
                checkTitle = xbmc.getInfoLabel("VideoPlayer.Title")
                sleepTime = 15
            elif (time.time() - lastUpdate >= 900):
                Debug('Title: ' + title + ', sending watching status, current percentage: ' + str(iPercComp), True)
                SendUpdate(title, int(iPercComp*100), sType, "watching")
                lastUpdate = time.time();
                checkTitle = xbmc.getInfoLabel("VideoPlayer.Title")
                sleepTime = 168
    
    else:
        Debug('Resetting last update timestamp')
        lastUpdate = 0
        sleepTime = 15


###Settings related parsing
__settings__ = xbmcaddon.Addon(id='script.trakt')
__language__ = __settings__.getLocalizedString
_ = sys.modules[ "__main__" ].__language__
__cwd__ = __settings__.getAddonInfo('path')

###Path handling
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
LANGUAGE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'language' ) )
MEDIA_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'skins' ) )
sys.path.append (BASE_RESOURCE_PATH)
sys.path.append (LANGUAGE_RESOURCE_PATH)

from utilities import *
    
Debug('----------- ' + __scriptname__ + ' by ' + __author__ + ', version ' + __version__ + ' -----------', False)

###Vars and initial load
bRun = True #Enter idle state waiting to submit
bStartup = False
bShortcut = False
bUsername = False
bPassword = False
lasttitle = ""
lastUpdate = 0
video_id = ""
sleepTime = 168
checkTitle = ''

bAutoStart = False
bNotify = False
bRunBackground = False
bAutoSubmitVideo = False
VideoThreshold = 0

if (__settings__.getSetting( "AutoStart" ) == 'true'): bAutoStart = True
if (__settings__.getSetting( "NotifyOnSubmit" ) == 'true'): bNotify = True
if (__settings__.getSetting( "RunBackground" ) == 'true'): bRunBackground = True
if (__settings__.getSetting( "AutoSubmitVideo" ) == 'true'): bAutoSubmitVideo = True

bUsername = __settings__.getSetting( "Username" )
bPassword = __settings__.getSetting( "Password" )

VideoThreshold = int(__settings__.getSetting( "VideoThreshold" ))
if (VideoThreshold == 0): VideoThreshold = 70
elif (VideoThreshold == 1): VideoThreshold = 85

try:
    count = len(sys.argv) - 1
    if (sys.argv[1] == '-startup'):
        bStartup = True			
except:
    pass

Debug( '::Settings::', True)
Debug( 'AutoStart: ' + str(bAutoStart), True)
Debug( 'RunBackground: ' + str(bRunBackground), True)
Debug( 'Username: ' + bUsername, True)
Debug( 'Password: ' + bPassword, True)
Debug( 'AutoSubmitVideo:' + str(bAutoSubmitVideo), True)
Debug( 'VideoThreshold: ' + str(VideoThreshold), True)
Debug( 'Startup: ' + str(bStartup), True)
Debug( '::Settings::', True)

###Main logic
if (not xbmc.getCondVisibility('videoplayer.isfullscreen') and not bShortcut and not bStartup):
    Debug(  'Pressed in scripts menu', False)        
    SetAutoStart(bAutoStart)

#Startup Execution 
if ((bStartup and bAutoStart) or bRun):
    Debug(  'Entering idle state, waiting for media playing...', False)
    
    if (bNotify):
        notification("Trakt", __language__(45050).encode( "utf-8", "ignore" ), 3000, __settings__.getAddonInfo("icon"))

    while (not xbmc.abortRequested):
        #If Set To AutoSubmit
        if (bAutoSubmitVideo):
            CheckAndSubmit()
            
        time.sleep(sleepTime)

Debug( 'Exiting...', False)