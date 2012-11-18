import os, sys
import xbmc, xbmcaddon

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__language__     = __addon__.getLocalizedString
__cwd__          = __addon__.getAddonInfo('path').decode("utf-8")

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
sys.path.append (BASE_RESOURCE_PATH)


if ( __name__ == "__main__" ):
    keyboard = xbmc.Keyboard( '', __language__(32101), False )
    keyboard.doModal()
    if ( keyboard.isConfirmed() ):
        searchstring = keyboard.getText()
        if searchstring:
            import gui
            ui = gui.GUI( "script-globalsearch-main.xml", __cwd__, "Default", searchstring=searchstring )
            ui.doModal()
            del ui
            sys.modules.clear()