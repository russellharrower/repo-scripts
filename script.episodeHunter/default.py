import xbmcgui
import xbmcaddon

from helper import *
from sync import *

_settings = xbmcaddon.Addon("script.episodeHunter")
_language = _settings.getLocalizedString
_name = "EpisodeHunter"


def menu():

    if not isSettingsOkey():
        _settings.openSettings()
        return

    options = [_language(10024), _language(10026), _language(10023)]  # [Movie, TV, Settings]

    while True:
        select = xbmcgui.Dialog().select(_name, options)
        if select == -1:
            return
        else:
            if select == 0:  # Movie
                syncSeenMovies(True)
            elif select == 1:  # TV
                syncSeenTVShows(True)
            elif select == 2:  # Settings
                _settings.openSettings()

menu()