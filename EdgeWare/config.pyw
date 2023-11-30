import json
import os
import shutil
import subprocess
import webbrowser
import zipfile
import pathlib
import ast
import urllib.request
import hashlib
import ctypes
import sys
import logging
import time
import textwrap
import random as rand
from tkinter import Tk, ttk, simpledialog, messagebox, filedialog, IntVar, BooleanVar, StringVar, Frame, Checkbutton, Button, Scale, Label, Toplevel, Entry, OptionMenu, Listbox, SINGLE, DISABLED, GROOVE, RAISED, Text, END, Scrollbar, VERTICAL
from tk_ToolTip_class101 import CreateToolTip

PATH = f'{str(pathlib.Path(__file__).parent.absolute())}\\'
os.chdir(PATH)

#starting logging
if not os.path.exists(os.path.join(PATH, 'logs')):
    os.mkdir(os.path.join(PATH, 'logs'))
LOG_TIME = time.asctime().replace(' ', '_').replace(':', '-')
logging.basicConfig(filename=os.path.join(PATH, 'logs', LOG_TIME + '-dbg.txt'), format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.info('Started config logging successfully.')

def pip_install(packageName:str):
    try:
        logging.info(f'attempting to install {packageName}')
        subprocess.call(f'py -m pip install {packageName}')
    except:
        logging.warning(f'failed to install {packageName} using py -m pip, trying raw pip request')
        subprocess.call(f'pip install {packageName}')
        logging.warning(f'{packageName} should be installed, fatal errors will occur if install failed.')

try:
    import requests
except:
    pip_install('requests')
    import requests

try:
    import PIL
    from PIL import Image, ImageTk
except:
    logging.warning('failed to import pillow module')
    pip_install('pillow')
    from PIL import Image, ImageTk

try:
    import ttkwidgets as tw
except:
    pip_install('ttkwidgets')
    import ttkwidgets as ttkw

#if you are working on this i'm just letting you know there's like almost no documentation for ttkwidgets
#source code is here https://github.com/TkinterEP/ttkwidgets/blob/master/ttkwidgets/checkboxtreeview.py
class CheckboxTreeview(tw.CheckboxTreeview):

    def __init__(self, master=None, **kw):
        tw.CheckboxTreeview.__init__(self, master, **kw)
        # disabled tag to mar disabled items
        self.tag_configure("disabled", foreground='grey')
        if kw['name']:
            self.name = kw['name']

    def _box_click(self, event):
        """Check or uncheck box when clicked."""
        x, y, widget = event.x, event.y, event.widget
        elem = widget.identify("element", x, y)
        if "image" in elem:
            # a box was clicked
            item = self.identify_row(y)
            if self.tag_has("disabled", item):
                return  # do nothing when disabled
            if self.tag_has("unchecked", item) or self.tag_has("tristate", item):
                self.change_state(item, "checked")
                updateMoods(self.name, item, True)
                #self._check_ancestor(item)
                #self._check_descendant(item)
            elif self.tag_has("checked"):
                self.change_state(item, "unchecked")
                updateMoods(self.name, item, False)
                #self._uncheck_descendant(item)
                #self._uncheck_ancestor(item)


SYS_ARGS = sys.argv.copy()
SYS_ARGS.pop(0)
logging.info(f'args: {SYS_ARGS}')

pil_logger = logging.getLogger('PIL')
pil_logger.setLevel(logging.INFO)

#text for the about tab
ANNOYANCE_TEXT          = 'The "Annoyance" section consists of the 5 main configurable settings of Edgeware:\nDelay\nPopup Frequency\nWebsite Frequency\nAudio Frequency\nPromptFrequency\n\nEach is fairly self explanatory, but will still be expounded upon in this section. Delay is the forced time delay between each tick of the "clock" for Edgeware. The longer it is, the slower things will happen. Popup frequency is the percent chance that a randomly selected popup will appear on any given tick of the clock, and similarly for the rest, website being the probability of opening a website or video from /resource/vid/, audio for playing a file from /resource/aud/, and prompt for a typing prompt to pop up.\n\nThese values can be set by adjusting the bars, or by clicking the button beneath each respective slider, which will allow you to type in an explicit number instead of searching for it on the scrollbar.\n\nIn order to disable any feature, lower its probability to 0, to ensure that you\'ll be getting as much of any feature as possible, turn it up to 100.\nThe popup setting "Mitosis mode" changes how popups are displayed. Instead of popping up based on the timer, the program create a single popup when it starts. When the submit button on ANY popup is clicked to close it, a number of popups will open up in its place, as given by the "Mitosis Strength" setting.\n\nPopup timeout will result in popups timing out and closing after a certain number of seconds.'
DRIVE_TEXT              = 'The "Drive" portion of Edgeware has three features: fill drive, replace images, and Booru downloader.\n\n"Fill Drive" does exactly what it says: it attempts to fill your hard drive with as much porn from /resource/img/ as possible. It does, however, have some restrictions. It will (should) not place ANY images into folders that start with a "." or have their names listed in the folder name blacklist.\nIt will also ONLY place images into the User folder and its subfolders.\nFill drive has one modifier, which is its own forced delay. Because it runs with between 1 and 8 threads at any given time, when unchecked it can fill your drive VERY quickly. To ensure that you get that nice slow fill, you can adjust the delay between each folder sweep it performs and the max number of threads.\n\n"Replace Images" is more complicated. Its searching is the exact same as fill drive, but instead of throwing images everywhere, it will seek out folders with large numbers of images (more than the threshold value) and when it finds one, it will replace ALL of the images with porn from /resource/img/. REMEMBER THAT IF YOU CARE ABOUT YOUR PHOTOS, AND THEY\'RE IN A FOLDER WITH MORE IMAGES THAN YOUR CHOSEN THRESHOLD VALUE, EITHER BACK THEM UP IN A ZIP OR SOMETHING OR DO. NOT. USE. THIS SETTING. I AM NOT RESPONSIBLE FOR YOUR OWN DECISION TO RUIN YOUR PHOTOS.\n\nBooru downloader allows you to download new items from a Booru of your choice. For the booru name, ONLY the literal name is used, like "censored" or "blacked" instead of the full url. This is not case sensitive. Use the "Validate" button to ensure that downloading will be successful before running. For tagging, if you want to have mutliple tags, they can be combined using "tag1+tag2+tag3" or if you want to add blacklist tags, type your tag and append a "+-blacklist_tag" after the desired tag.'
STARTUP_TEXT            = 'Start on launch does exactly what it says it does and nothing more: it allows Edgeware to start itself whenever you start up and log into your PC.\n\nPlease note that the method used does NOT edit registry or schedule any tasks. The "lazy startup" method was used for both convenience of implementation and convenience of cleaning.\n\nIf you forget to turn off the "start on logon" setting before uninstalling, you will need to manually go to your Startup folder and remove "edgeware.bat".'
WALLPAPER_TEXT          = 'The Wallpaper section allows you to set up rotating wallpapers of your choice from any location, or auto import all images from the /resource/ folder (NOT /resource/img/ folder) to use as wallpapers.\n\nThe rotate timer is the amount of time the program will wait before rotating to another randomly selected wallpaper, and the rotate variation is the amount above or below that set value that can randomly be selected as the actual wait time.'
HIBERNATE_TEXT          = 'The Hibernate feature is an entirely different mode for Edgeware to operate in.\nInstead of constantly shoving popups, lewd websites, audio, and prompts in your face, hibernate starts quiet and waits for a random amount of time between its provided min and max before exploding with a rapid assortment of your chosen payloads. Once it finishes its barrage, it settles back down again for another random amount of time, ready to strike again when the time is right.\n\n\nThis feature is intend to be a much "calmer" way to use Edgeware; instead of explicitly using it to edge yourself or get off, it\'s supposed to lie in wait for you and perform bursts of self-sabotage to keep drawing you back to porn.\n\n In EdgeWare++, the hibernate function has been expanded with two key features: fix wallpaper and hibernate types. Fix wallpaper is fairly straightforward, it changes your wallpaper back to your panic wallpaper after hibernate is finished. Hibernate types are a bit more complicated, as each one changes the the way hibernate handles payloads. There is a short-form description next to the dropdown menu for quick reference, but you can check the about tab labelled \"Hibernate Types\" for a more detailed description of each type. Also, if you wish to trial out any of these types and don\'t want to wait, you can enable the \"Toggle Tray Hibernate Skip\" option in the troubleshooting tab to immediately skip to hibernate starting, on command.'
HIBERNATE_TYPE_TEXT     = 'Check the \"Hibernate\" about tab for more information on what this is and how it works.\n\nOriginal: The original hibernate type that came with base EdgeWare. Spawns a barrage of popups instantly, the max possible amount is based on your awaken activity.\n\nSpaced: Essentially runs EdgeWare normally, but over a brief period of time before ceasing generation of new popups. Because of this awaken activity isn\'t used, instead popup delay is looked at for frequency of popups.\n\nGlitch: Creates popups at random-ish intervals over a period of time. The total amount of popups spawned is based on the awaken activity. Perfect for those who want a \'virus-like\' experience, or just something different every time.\n\nRamp: Similar to spaced, only the popup frequency gets faster and faster over the hibernate length. After reaching the max duration, it will spawn a number of popups equal to the awaken activity at a speed slightly faster than your popup delay. Best used with long hibernate length values and fairly short popup delay. (keep in mind that if the popup delay is too short though, popups can potentially not appear or lag behind)\n\nPump-Scare: Do you like haunted houses or scary movies? Don\'t you wish that instead of screamers and jumpscares, they had porn pop out at you instead? This is kind of like that. When hibernate is triggered a popup with audio will appear for around a second or two, then immediately disappear. This works best on packs with short, immediate audio files: old EdgeWare packs that contain half-hour long hypno files will likely not reach meaningful audio in time. Large audio files can also hamper effectiveness of the audio and lead to desync with the popup.\n\nChaos: Every time hibernate activates, it randomly selects any of the other hibernate modes.'
CORRUPTION_TEXT         = 'This is a feature not currently implemented in the release version of EdgeWare. But it will be soon! Feel free to slide the sliders around and press some buttons. It currently won\'t do anything but sometimes just feels good to do.'
ADVANCED_TEXT           = 'The Advanced section is also something previously only accessible by directly editing the config.cfg file. It offers full and complete customization of all setting values without any limitations outside of variable typing.\n\n\nPlease use this feature with discretion, as any erroneous values will result in a complete deletion and regeneration of the config file from the default, and certain value ranges are likely to result in crashes or unexpected glitches in the program.'
THANK_AND_ABOUT_TEXT    = '[NOTE: this is the thanks page from the original EdgeWare. I didn\'t want to replace/remove it and erase credit to the original creator! Sorry if this caused confusion!]\n\nThank you so much to all the fantastic artists who create and freely distribute the art that allows programs like this to exist, to all the people who helped me work through the various installation problems as we set the software up (especially early on), and honestly thank you to ALL of the people who are happily using Edgeware. \n\nIt truly makes me happy to know that my work is actually being put to good use by people who enjoy it. After all, at the end of the day that\'s really all I\'ve ever really wanted, but figured was beyond reach of a stupid degreeless neet.\nI love you all <3\n\n\n\nIf you like my work, please feel free to help support my neet lifestyle by donating to $PetitTournesol on Cashapp; by no means are you obligated or expected to, but any and all donations are greatly appreciated!'

PLUSPLUS_TEXT           = 'Thanks for taking the time to check out this extension on EdgeWare! However you found it, I appreciate that it interested you enough to give it a download.\n\nI am not an expert programmer by any means, so apologies if there are any bugs or errors in this version. My goal is to not do anything crazy ambitious like rewrite the entire program or fix up the backend, but rather just add on functionality that I thought could improve the base version. Because of this, i\'m hoping that compatability between those who use normal EdgeWare and those who use this version stays relatively stable.\n\nCurrent changes:\n\n•Added a option under "misc" to enable/disable desktop icon generation.\n•Added options to cap the number of audio popups and video popups.\n•Added a chance slider for subliminals, and a max subliminals slider.\n•Added feature to change Startup Graphic and Icon per pack. (name the file(s) \"loading_splash.png\" and/or \"icon.ico\" in the resource folder)\n•Added feature to enable warnings for \"Dangerous Settings\".\n•Added hover tooltips on some things to make the program easier to understand.\n•Added troubleshooting tab under \"advanced\" with some settings to fix things for certain users.\n•Added feature to click anywhere on popup to close.\n•Made the EdgewareSetup.bat more clear with easier to read text. Hopefully if you\'re seeing this it all worked out!\n•Moved the import/export resources button to be visible on every page, because honestly they\'re pretty important\n•Added the \"Pack Info\" tab with lots of fun goodies and stats so you know what you\'re getting into with each pack.\n•Added a simplified error console in the \"advanced\" tab.\n•Overhauled Hibernate with a bunch of new modes and features\n•Added file tab with multiple file management settings\n•Added feature to enable or disable moods (feature in regular edgeware that went unused afaik)\n•Added corruption. What is it? Dont worry about it.'
PACKINFO_TEXT          = 'The pack info section contains an overview for whatever pack is currently loaded.\n\nThe \"Stats\" tab allows you to see what features are included in the current pack (or if a pack is even loaded at all), but keep in mind all of these features have default fallbacks if they aren\'t included. It also lets you see a lot of fun stats relating to the pack, including almost everything you\'ll encounter while using EdgeWare. Keep in mind that certain things having \"0\" as a stat doesn\'t mean you can\'t use it, for example, having 0 subliminals uses the default spiral and having 0 images displays a very un-sexy circle.\n\nThe \"Information\" tab gets info on the pack from //resource//info.json, which is a new addition to EdgeWare++. This feature was added to allow pack creators to give the pack a formal name and description without having to worry about details being lost if transferred from person to person. Think of it like a readme. Also included in this section is the discord status info, which gives what your discord status will be set to if that setting is turned on, along with the image. As of time of writing (or if I forget to update this later), the image cannot be previewed as it is \"hard coded\" into EdgeWare\'s discord application and accessed through the API. As I am not the original creator of EdgeWare, and am not sure how to contact them, the best I could do is low-res screenshots or the name of each image. I chose the latter. Because of this hard-coding, the only person i\'ve run into so far who use these images is PetitTournesol themselves, but it should be noted that anyone can use them as long as they know what to add to the discord.dat file. This is partially the reason I left this information in.\n\nThe \"Moods\" tab is where you can access mood settings and previews for the current pack. The left table shows information for media (linking moods to images, videos, etc), captions, and prompts, while the \"Corruption Path\" area shows how these moods correlate to corruption levels.'
FILE_TEXT              = 'The file tab is for all your file management needs, whether it be saving things, loading things, deleting things, or looking around in config folders. The Preset window has also been moved here to make more room for general options.\n\nThere are only two things that aren\'t very self explanatory: deleting logs and unique IDs.\n\nWhile deleting logs is fairly straightforward, it should be noted that it will not delete the log currently being written during the session, so the \"total logs in folder\" stat will always display as \"1\".\n\nUnique IDs are a feature to help assist with saving moods. In short, they are a generated identifier that is used when saving to a \"moods json file\", which is tapped into when selecting what moods you want to see in the \"Pack Info\" tab. Unique IDs are only used if the pack does not have a \'info.json\' file, otherwise the pack name is just used instead. If you are rapidly editing a pack without info.json and want EdgeWare++ to stop generating new mood files, there is an option to disable it in the troubleshooting tab.\n\n When manually editing mood config jsons, you don\'t need to worry about how the unique ID is generated- the file tab will tell you what to look for. If you are curious though, here is the exact formula:\n\nnum_images + num_audio + num_video + wallpaper(y/n) + loading_splash(y/n) + discord_status(y/n) + icon(y/n) + corruption(y/n)\n\nFor example:\nA pack with 268 images, 7 audio, 6 videos, has a wallpaper, doesn\'t have a custom loading splash, has a discord status, doesn\'t have a custom icon, and doesn\'t have a corruption file, would generate \"26876wxdxx.json\" in //moods//unnamed (mood files go in unnamed when using unique IDs)'


errors_list = []

#all booru consts
BOORU_FLAG = '<BOORU_INSERT>'                                                      #flag to replace w/ booru name
BOORU_URL  = f'https://{BOORU_FLAG}.booru.org/index.php?page=post&s=list&tags='    #basic url
BOORU_VIEW = f'https://{BOORU_FLAG}.booru.org/index.php?page=post&s=view&id='      #post view url
BOORU_PTAG = '&pid='                                                               #page id tag

#info defaults & vars
INFO_NAME_DEFAULT = 'N/A'
INFO_DESCRIPTION_DEFAULT = 'No pack loaded, or the pack does not have an \'info.json\' file.'
INFO_CREATOR_DEFAULT = 'Anonymous'
INFO_VERSION_DEFAULT = '0'
INFO_DISCORD_DEFAULT = ['[No pack loaded, or the pack does not have a \'discord.dat\' file.]', 'default']

if os.path.isfile(PATH + '\\resource\\info.json'):
    try:
        info_dict = ''
        with open(f'{PATH}\\resource\\info.json') as r:
            info_dict = json.loads(r.read())
        info_name = info_dict['name'] if info_dict['name'] else 'Unnamed Pack'
        info_description = info_dict['description'] if info_dict['description'] else 'No description set.'
        info_creator = info_dict['creator'] if info_dict['creator'] else 'Anonymous'
        info_version = info_dict['version'] if info_dict['version'] else '1.0'
    except Exception as e:
        logging.warning(f'error copying info.json data to pack info page. {e}')
        errors_list.append('Could not use the info.json file for pack info!\n')
        info_name = INFO_NAME_DEFAULT
        info_description = INFO_DESCRIPTION_DEFAULT
        info_creator = INFO_CREATOR_DEFAULT
        info_version = INFO_VERSION_DEFAULT
else:
    info_name = INFO_NAME_DEFAULT
    info_description = INFO_DESCRIPTION_DEFAULT
    info_creator = INFO_CREATOR_DEFAULT
    info_version = INFO_VERSION_DEFAULT

UNIQUE_ID = '0'

#creating a semi-parseable unique ID for the pack to make mood saving work, if the pack doesn't have an info.json file.
#probably could have made it so the user manually has to save/load and not worried about this, but here we are
if (info_name == INFO_NAME_DEFAULT) and os.path.exists(PATH + '\\resource\\'):
    try:
        #already done the brunt of the work for getting these values in the pack info page, so i'm just using those again here. If this needs to be replaced, look there too
        im = str(len(os.listdir(PATH + '\\resource\\img\\'))) if os.path.exists(PATH + '\\resource\\img\\') else '0'
        au = str(len(os.listdir(PATH + '\\resource\\aud\\'))) if os.path.exists(PATH + '\\resource\\aud\\') else '0'
        vi = str(len(os.listdir(PATH + '\\resource\\vid\\'))) if os.path.exists(PATH + '\\resource\\vid\\') else '0'
        wa = 'w' if os.path.isfile(PATH + '\\resource\\wallpaper.png') else 'x'
        sp = 's' if os.path.isfile(PATH + '\\resource\\loading_splash.png') else 'x'
        di = 'd' if os.path.isfile(PATH + '\\resource\\discord.dat') else 'x'
        ic = 'i' if os.path.isfile(PATH + '\\resource\\icon.ico') else 'x'
        co = 'c' if os.path.isfile(PATH + '\\resource\\corruption.json') else 'x'
        UNIQUE_ID = im + au + vi + wa + sp + di + ic + co
        logging.info(f'generated unique ID. {UNIQUE_ID}')
    except Exception as e:
        logging.warning(f'failed to create unique id. {e}')
        errors_list.append('Could not create the pack unique ID! Mood settings might not save!\n')



#url to check online version
UPDCHECK_URL = 'http://raw.githubusercontent.com/PetitTournesol/Edgeware/main/EdgeWare/configDefault.dat'
local_version = '0.0.0_NOCONNECT'

UPDCHECK_PP_URL = 'http://raw.githubusercontent.com/araten10/EdgewarePlusPlus/main/EdgeWare/configDefault.dat'
local_pp_version = '0.0.0_NOCONNECT'

logging.info('opening configDefault')
with open(f'{PATH}configDefault.dat') as r:
    defaultSettingLines = r.readlines()
    varNames = defaultSettingLines[0].split(',')
    varNames[-1] = varNames[-1].replace('\n', '')
    defaultVars = defaultSettingLines[1].split(',')
logging.info(f'done with configDefault\n\tdefault={defaultVars}')

local_version = defaultVars[0]
local_pp_version = defaultVars[1]

settings = {}
for var in varNames:
    settings[var] = defaultVars[varNames.index(var)]

defaultSettings = settings.copy()

if not os.path.exists(f'{PATH}config.cfg'):
    logging.warning('no "config.cfg" file found, creating new "config.cfg".')
    with open(f'{PATH}config.cfg', 'w') as f:
        f.write(json.dumps(settings))
    logging.info('created new config file.')

with open(f'{PATH}config.cfg', 'r') as f:
    logging.info('json loading settings')
    try:
        settings = json.loads(f.readline())
    except Exception as e:
        logging.fatal(f'could not load settings.\n\nReason: {e}')
        exit()


#inserts new settings if versions are literally different
# or if the count of settings between actual and default is different
if settings['version'] != defaultVars[0] or len(settings) != len(defaultSettings):
    logging.warning('version difference/settingJson len mismatch, regenerating new settings with missing keys...')
    tempSettingDict = {}
    for name in varNames:
        try:
            tempSettingDict[name] = settings[name]
        except:
            tempSettingDict[name] = defaultVars[varNames.index(name)]
            logging.info(f'added missing key: {name}')
    tempSettingDict['version'] = defaultVars[0]
    settings = tempSettingDict.copy()
    with open(f'{PATH}config.cfg', 'w') as f:
        #bugfix for the config crash issue
        tempSettingDict['wallpaperDat'] = str(tempSettingDict['wallpaperDat']).replace("'", '%^%')
        tempSettingString = str(tempSettingDict).replace("'", '"')
        f.write(tempSettingString.replace("%^%", "'"))
        logging.info('wrote regenerated settings.')

logging.info('converting wallpaper dict string.')
DEFAULT_WALLPAPERDAT = {'default': 'wallpaper.png'}
try:
    if settings['wallpaperDat'] == 'WPAPER_DEF':
        logging.info('default wallpaper dict inserted.')
        settings['wallpaperDat'] = DEFAULT_WALLPAPERDAT
    else:
        #print(settings['wallpaperDat'])
        if type(settings['wallpaperDat']) == dict:
            logging.info('wallpaper object already dict?')
        else:
            settings['wallpaperDat'] = ast.literal_eval(settings['wallpaperDat'].replace('\\', '/'))
            logging.info('evaluated settings wallpaper str to dict.')
except Exception as e:
    settings['wallpaperDat'] = DEFAULT_WALLPAPERDAT
    logging.warning(f'failed to process wallpaper dict.\n\tReason: {e}\nused default wallpaper dict instead.')

pass_ = ''

#creating the mood file if it doesn't exist
if settings['toggleMoodSet'] != True:
    if UNIQUE_ID != '0' and os.path.exists(PATH + '\\resource\\'):
        if not os.path.isfile(PATH + '\\moods\\unnamed\\' + UNIQUE_ID + '.json'):
            logging.info(f'moods file does not exist, creating one using unique id {UNIQUE_ID}')
            try:
                with open(f'{PATH}\\moods\\unnamed\\{UNIQUE_ID}.json', 'w+') as mood:
                    mood_dict = {"media": [], "captions": [], "prompts": []}

                    if os.path.isfile(PATH + '\\resource\\media.json'):
                        media_dict = ''
                        with open(f'{PATH}\\resource\\media.json') as media:
                            media_dict = json.loads(media.read())
                            mood_dict["media"] += media_dict

                    if os.path.isfile(PATH + '\\resource\\captions.json'):
                        captions_dict = ''
                        with open(f'{PATH}\\resource\\captions.json') as captions:
                            captions_dict = json.loads(captions.read())
                            if 'prefix' in captions_dict: del captions_dict['prefix']
                            if 'subtext' in captions_dict: del captions_dict['subtext']
                            mood_dict["captions"] += captions_dict

                    if os.path.isfile(PATH + '\\resource\\prompt.json'):
                        prompt_dict = ''
                        with open(f'{PATH}\\resource\\prompt.json') as prompt:
                            prompt_dict = json.loads(prompt.read())
                            mood_dict["prompts"] += prompt_dict["moods"]

                    content = json.dumps(mood_dict)
                    mood.write(content)
            except Exception as e:
                logging.warning(f'error creating/populating mood json. {e}')
                errors_list.append('Could not create the mood json file!\n')
    elif UNIQUE_ID == '0' and os.path.exists(PATH + '\\resource\\'):
        if not os.path.isfile(PATH + '\\moods\\' + info_name + '.json'):
            logging.info(f'moods file does not exist, creating one using infoname id {info_name}')
            try:
                with open(f'{PATH}\\moods\\{info_name}.json', 'w+') as mood:
                    mood_dict = {"media": [], "captions": [], "prompts": []}

                    if os.path.isfile(PATH + '\\resource\\media.json'):
                        media_dict = ''
                        with open(f'{PATH}\\resource\\media.json') as media:
                            media_dict = json.loads(media.read())
                            mood_dict["media"] += media_dict

                    if os.path.isfile(PATH + '\\resource\\captions.json'):
                        captions_dict = ''
                        with open(f'{PATH}\\resource\\captions.json') as captions:
                            captions_dict = json.loads(captions.read())
                            if 'prefix' in captions_dict: del captions_dict['prefix']
                            if 'subtext' in captions_dict: del captions_dict['subtext']
                            mood_dict["captions"] += captions_dict

                    if os.path.isfile(PATH + '\\resource\\prompt.json'):
                        prompt_dict = ''
                        with open(f'{PATH}\\resource\\prompt.json') as prompt:
                            prompt_dict = json.loads(prompt.read())
                            mood_dict["prompts"] += prompt_dict["moods"]

                    mood.write(json.dumps(mood_dict))
            except Exception as e:
                logging.warning(f'error creating/populating mood json. {e}')
                errors_list.append('Could not create the mood json file!\n')

def show_window():
    global settings, defaultSettings


    #window things
    root = Tk()
    root.title('Edgeware++ Config')
    root.geometry('740x680')
    try:
        root.iconbitmap(f'{PATH}default_assets\\config_icon.ico')
        logging.info('set iconbitmap.')
    except:
        logging.warning('failed to set iconbitmap.')
    fail_loop = 0

    #painful control variables ._.
    while(fail_loop < 2):
        try:
            delayVar            = IntVar(root, value=int(settings['delay']))
            popupVar            = IntVar(root, value=int(settings['popupMod']))
            webVar              = IntVar(root, value=int(settings['webMod']))
            audioVar            = IntVar(root, value=int(settings['audioMod']))
            promptVar           = IntVar(root, value=int(settings['promptMod']))
            fillVar             = BooleanVar(root, value=(settings['fill']==1))

            fillDelayVar        = IntVar(root, value=int(settings['fill_delay']))
            replaceVar          = BooleanVar(root, value=(settings['replace'] == 1))
            replaceThreshVar    = IntVar(root, value=int(settings['replaceThresh']))
            startLoginVar       = BooleanVar(root, value=(settings['start_on_logon'] == 1))

            hibernateVar        = BooleanVar(root, value=(settings['hibernateMode']==1))
            hibernateMinVar     = IntVar(root, value=int(settings['hibernateMin']))
            hibernateMaxVar     = IntVar(root, value=(settings['hibernateMax']))
            hibernateTypeVar    = StringVar(root, value=(settings['hibernateType'].strip()))
            wakeupActivityVar   = IntVar(root, value=(settings['wakeupActivity']))
            hibernateLengthVar  = IntVar(root, value=(settings['hibernateLength']))
            fixWallpaperVar     = BooleanVar(root, value=(settings['fixWallpaper']==1))

            discordVar          = BooleanVar(root, value=(int(settings['showDiscord'])==1))
            startFlairVar       = BooleanVar(root, value=(int(settings['showLoadingFlair'])==1))
            captionVar          = BooleanVar(root, value=(int(settings['showCaptions'])==1))
            panicButtonVar      = StringVar(root, value=settings['panicButton'])
            panicVar            = BooleanVar(root, value=(int(settings['panicDisabled'])==1))

            promptMistakeVar    = IntVar(root, value=int(settings['promptMistakes']))
            mitosisVar          = BooleanVar(root, value=(int(settings['mitosisMode'])==1))
            onlyVidVar          = BooleanVar(root, value=(int(settings['onlyVid'])==1))
            popupWebVar         = BooleanVar(root, value=(int(settings['webPopup'])==1))

            rotateWallpaperVar  = BooleanVar(root, value=(int(settings['rotateWallpaper'])==1))
            wallpaperDelayVar   = IntVar(root, value=int(settings['wallpaperTimer']))
            wpVarianceVar       = IntVar(root, value=int(settings['wallpaperVariance']))

            timeoutPopupsVar    = BooleanVar(root, value=(int(settings['timeoutPopups'])==1))
            popupTimeoutVar     = IntVar(root, value=(int(settings['popupTimeout'])))
            mitosisStrenVar     = IntVar(root, value=(int(settings['mitosisStrength'])))
            booruNameVar        = StringVar(root, value=settings['booruName'])

            downloadEnabledVar  = BooleanVar(root, value=(int(settings['downloadEnabled']) == 1))
            downloadModeVar     = StringVar(root, value=settings['downloadMode'])
            useWebResourceVar   = BooleanVar(root, value=(int(settings['useWebResource'])==1))
            fillPathVar         = StringVar(root, value=settings['drivePath'])
            rosVar              = BooleanVar(root, value=(int(settings['runOnSaveQuit'])==1))

            timerVar            = BooleanVar(root, value=(int(settings['timerMode'])==1))
            timerTimeVar        = IntVar(root, value=int(settings['timerSetupTime']))
            lkCorner            = IntVar(root, value=int(settings['lkCorner']))
            popopOpacity        = IntVar(root, value=int(settings['lkScaling']))
            lkToggle            = BooleanVar(root, value=(int(settings['lkToggle'])==1))

            safewordVar         = StringVar(root, value='password')

            videoVolume         = IntVar(root, value=int(settings['videoVolume']))
            vidVar              = IntVar(root, value=int(settings['vidMod']))
            denialMode          = BooleanVar(root, value=(int(settings['denialMode']) == 1))
            denialChance        = IntVar(root, value=int(settings['denialChance']))
            popupSublim         = IntVar(root, value=(int(settings['popupSubliminals']) == 1))

            booruMin            = IntVar(root, value=int(settings['booruMinScore']))

            deskIconVar         = BooleanVar(root, value=(int(settings['desktopIcons'])==1))

            maxAToggleVar       = BooleanVar(root, value=(int(settings['maxAudioBool'])==1))
            maxAudioVar         = IntVar(root, value=(int(settings['maxAudio'])))
            maxVToggleVar       = BooleanVar(root, value=(int(settings['maxVideoBool'])==1))
            maxVideoVar         = IntVar(root, value=(int(settings['maxVideos'])))

            subliminalsChanceVar        = IntVar(root, value=int(settings['subliminalsChance']))
            maxSubliminalsVar           = IntVar(root, value=int(settings['maxSubliminals']))

            safeModeVar         = BooleanVar(root, value=(int(settings['safeMode'])==1))

            antiOrLanczosVar    = BooleanVar(root, value=(int(settings['antiOrLanczos'])==1))
            toggleInternetVar   = BooleanVar(root, value=(int(settings['toggleInternet'])==1))
            toggleHibSkipVar    = BooleanVar(root, value=(int(settings['toggleHibSkip'])==1))
            toggleMoodSetVar    = BooleanVar(root, value=(int(settings['toggleMoodSet'])==1))

            buttonlessVar       = BooleanVar(root, value=(int(settings['buttonless'])==1))

            corruptionModeVar         = BooleanVar(root, value=(int(settings['corruptionMode'])==1))
            corruptionTimeVar         = IntVar(root, value=int(settings['corruptionTime']))
            corruptionFadeTypeVar     = StringVar(root, value=(settings['corruptionFadeType'].strip()))

            pumpScareOffsetVar        = IntVar(root, value=int(settings['pumpScareOffset']))

            vlcModeVar                = BooleanVar(root, value=(int(settings['vlcMode'])==1))
            mulitClickVar             = BooleanVar(root, value=(int(settings['multiClick'])==1))

            #grouping for sanity's sake later
            in_var_group = [delayVar, popupVar, webVar, audioVar, promptVar, fillVar,
                            fillDelayVar, replaceVar, replaceThreshVar, startLoginVar,
                            hibernateVar, hibernateMinVar, hibernateMaxVar, wakeupActivityVar,
                            discordVar, startFlairVar, captionVar, panicButtonVar, panicVar,
                            promptMistakeVar, mitosisVar, onlyVidVar, popupWebVar,
                            rotateWallpaperVar, wallpaperDelayVar, wpVarianceVar,
                            timeoutPopupsVar, popupTimeoutVar, mitosisStrenVar, booruNameVar,
                            downloadEnabledVar, downloadModeVar, useWebResourceVar, fillPathVar, rosVar,
                            timerVar, timerTimeVar, lkCorner, popopOpacity, lkToggle,
                            videoVolume, vidVar, denialMode, denialChance, popupSublim,
                            booruMin, deskIconVar, maxAToggleVar, maxAudioVar, maxVToggleVar,
                            maxVideoVar, subliminalsChanceVar, maxSubliminalsVar, safeModeVar,
                            antiOrLanczosVar, toggleInternetVar, buttonlessVar, hibernateTypeVar,
                            hibernateLengthVar, fixWallpaperVar, toggleHibSkipVar, toggleMoodSetVar,
                            corruptionModeVar, corruptionTimeVar, pumpScareOffsetVar, corruptionFadeTypeVar,
                            vlcModeVar, mulitClickVar]

            in_var_names = ['delay', 'popupMod', 'webMod', 'audioMod', 'promptMod', 'fill',
                            'fill_delay', 'replace', 'replaceThresh', 'start_on_logon',
                            'hibernateMode', 'hibernateMin', 'hibernateMax', 'wakeupActivity',
                            'showDiscord', 'showLoadingFlair', 'showCaptions', 'panicButton', 'panicDisabled',
                            'promptMistakes', 'mitosisMode', 'onlyVid', 'webPopup',
                            'rotateWallpaper', 'wallpaperTimer', 'wallpaperVariance',
                            'timeoutPopups', 'popupTimeout', 'mitosisStrength', 'booruName',
                            'downloadEnabled', 'downloadMode', 'useWebResource', 'drivePath', 'runOnSaveQuit',
                            'timerMode', 'timerSetupTime', 'lkCorner', 'lkScaling', 'lkToggle',
                            'videoVolume', 'vidMod', 'denialMode', 'denialChance', 'popupSubliminals',
                            'booruMinScore', 'desktopIcons', 'maxAudioBool', 'maxAudio', 'maxVideoBool',
                            'maxVideos', 'subliminalsChance', 'maxSubliminals', 'safeMode', 'antiOrLanczos',
                            'toggleInternet', 'buttonless', 'hibernateType', 'hibernateLength', 'fixWallpaper',
                            'toggleHibSkip', 'toggleMoodSet', 'corruptionMode', 'corruptionTime', 'pumpScareOffset',
                            'corruptionFadeType', 'vlcMode', 'multiClick']
            break
        except Exception as e:
            messagebox.showwarning(
                        'Settings Warning',
                        f'File "config.cfg" appears corrupted.\nFile will be restored to default.\n[{e}]'
                        )
            logging.warning(f'failed config var loading.\n\tReason: {e}')
            emergencySettings = {}
            for var in varNames:
                emergencySettings[var] = defaultVars[varNames.index(var)]
            with open(f'{PATH}config.cfg', 'w') as f:
                f.write(json.dumps(emergencySettings))
            with open(f'{PATH}config.cfg', 'r') as f:
                settings = json.loads(f.readline())
            fail_loop += 1

    hasWebResourceVar = BooleanVar(root, os.path.exists(os.path.join(PATH, 'resource', 'webResource.json')))

    #done painful control variables

    if getPresets() is None:
        write_save(in_var_group, in_var_names, '', False)
        savePreset('Default')

    #grouping for enable/disable
    hibernate_group = []
    hlength_group   = []
    hactivity_group = []
    fill_group      = []
    replace_group   = []
    mitosis_group   = []
    mitosis_cGroup  = []
    wallpaper_group = []
    timeout_group   = []
    download_group  = []
    timer_group     = []
    lowkey_group    = []
    denial_group    = []
    maxAudio_group  = []
    maxVideo_group  = []
    subliminals_group = []
    info_group     = []
    discord_group  = []

    webv = getLiveVersion(UPDCHECK_URL, 0)
    webvpp = getLiveVersion(UPDCHECK_PP_URL, 1)

    #tab display code start
    tabMaster    = ttk.Notebook(root)       #tab manager
    tabGeneral   = ttk.Frame(None)          #general tab, will have current settings
    tabWallpaper = ttk.Frame(None)          #tab for wallpaper rotation settings
    tabAnnoyance = ttk.Frame(None)          #tab for popup settings
    tabDrive     = ttk.Frame(None)          #tab for drive settings
    tabJSON      = ttk.Frame(None)          #tab for JSON editor (unused)
    tabAdvanced  = ttk.Frame(None)          #advanced tab, will have settings pertaining to startup, hibernation mode settings
    tabInfo      = ttk.Frame(None)          #info, github, version, about, etc.
    tabPackInfo  = ttk.Frame(None)          #pack information
    tabFile      = ttk.Frame(None)          #file management tab

    style = ttk.Style(root)                 #style setting for left aligned tabs
    style.configure('lefttab.TNotebook', tabposition='wn')
    tabInfoExpound = ttk.Notebook(tabInfo, style='lefttab.TNotebook')  #additional subtabs for info on features

    tab_annoyance = ttk.Frame(None)
    tab_drive = ttk.Frame(None)
    tab_wallpaper = ttk.Frame(None)
    tab_launch = ttk.Frame(None)
    tab_hibernate = ttk.Frame(None)
    tab_hibernateType = ttk.Frame(None)
    tab_corruption = ttk.Frame(None)
    tab_advanced = ttk.Frame(None)
    tab_thanksAndAbout = ttk.Frame(None)
    tab_plusPlus = ttk.Frame(None)
    tab_packInfo = ttk.Frame(None)
    tab_file = ttk.Frame(None)

    tabMaster.add(tabGeneral, text='General')
    #==========={IN HERE IS GENERAL TAB ITEM INITS}===========#
    #init
    hibernate_types = ['Original', 'Spaced', 'Glitch', 'Ramp', 'Pump-Scare', 'Chaos']

    hibernateHostFrame = Frame(tabGeneral, borderwidth=5, relief=RAISED)
    hibernateTypeFrame = Frame(hibernateHostFrame)
    hibernateTypeDescriptionFrame = Frame(hibernateHostFrame, borderwidth=2, relief=GROOVE)
    hibernateFrame = Frame(hibernateHostFrame)
    hibernateMinFrame = Frame(hibernateHostFrame)
    hibernateMaxFrame = Frame(hibernateHostFrame)
    hibernateActivityFrame = Frame(hibernateHostFrame)
    hibernateLengthFrame = Frame(hibernateHostFrame)

    toggleHibernateButton = Checkbutton(hibernateTypeFrame, text='Hibernate Mode', variable=hibernateVar, command=lambda: hibernateHelper(hibernateTypeVar.get()), cursor='question_arrow')
    fixWallpaperButton = Checkbutton(hibernateTypeFrame, text='Fix Wallpaper', variable=fixWallpaperVar, cursor='question_arrow')
    hibernateTypeDropdown = OptionMenu(hibernateTypeFrame, hibernateTypeVar, *hibernate_types, command=lambda key: hibernateHelper(key))
    hibernateTypeDescription = Label(hibernateTypeDescriptionFrame, text='Error loading Hibernate Description!', wraplength=175)
    def hibernateHelper(key:str):
        if key == 'Original':
            hibernateTypeDescription.configure(text='Creates an immediate quantity of popups on wakeup based on the awaken activity.\n\n')
            if hibernateVar.get():
                toggleAssociateSettings(False, hlength_group)
                toggleAssociateSettings(True, hactivity_group)
                toggleAssociateSettings(True, hibernate_group)
        if key == 'Spaced':
            hibernateTypeDescription.configure(text='Creates popups consistently over the hibernate length, based on popup delay.\n\n')
            if hibernateVar.get():
                toggleAssociateSettings(False, hactivity_group)
                toggleAssociateSettings(True, hlength_group)
                toggleAssociateSettings(True, hibernate_group)
        if key == 'Glitch':
            hibernateTypeDescription.configure(text='Creates popups at random times over the hibernate length, with the max amount spawned based on awaken activity.\n')
            if hibernateVar.get():
                toggleAssociateSettings(True, hlength_group)
                toggleAssociateSettings(True, hactivity_group)
                toggleAssociateSettings(True, hibernate_group)
        if key == 'Ramp':
            hibernateTypeDescription.configure(text='Creates a ramping amount of popups over the hibernate length, popups at fastest speed based on awaken activity, fastest speed based on popup delay.')
            if hibernateVar.get():
                toggleAssociateSettings(True, hlength_group)
                toggleAssociateSettings(True, hactivity_group)
                toggleAssociateSettings(True, hibernate_group)
        if key == 'Pump-Scare':
            hibernateTypeDescription.configure(text='Spawns a popup, usually accompanied by audio, then quickly deletes it. Best used on packs with short audio files. Like a horror game, but horny?')
            if hibernateVar.get():
                toggleAssociateSettings(False, hlength_group)
                toggleAssociateSettings(False, hactivity_group)
                toggleAssociateSettings(True, hibernate_group)
        if key == 'Chaos':
            hibernateTypeDescription.configure(text='Every time hibernate activates, a random type (other than chaos) is selected.\n\n')
            if hibernateVar.get():
                toggleAssociateSettings(True, hlength_group)
                toggleAssociateSettings(True, hactivity_group)
                toggleAssociateSettings(True, hibernate_group)
        if not hibernateVar.get():
            toggleAssociateSettings(False, hlength_group)
            toggleAssociateSettings(False, hactivity_group)
            toggleAssociateSettings(False, hibernate_group)

    hibernateHelper(hibernateTypeVar.get())

    hibernateMinButton = Button(hibernateMinFrame, text='Manual min...', command=lambda: assign(hibernateMinVar, simpledialog.askinteger('Manual Minimum Sleep (sec)', prompt='[1-7200]: ')))
    hibernateMinScale = Scale(hibernateMinFrame, label='Min Sleep (sec)', variable=hibernateMinVar, orient='horizontal', from_=1, to=7200)
    hibernateMaxButton = Button(hibernateMaxFrame, text='Manual max...', command=lambda: assign(hibernateMaxVar, simpledialog.askinteger('Manual Maximum Sleep (sec)', prompt='[2-14400]: ')))
    hibernateMaxScale = Scale(hibernateMaxFrame, label='Max Sleep (sec)', variable=hibernateMaxVar, orient='horizontal', from_=2, to=14400)
    h_activityScale = Scale(hibernateActivityFrame, label='Awaken Activity', orient='horizontal', from_=1, to=50, variable=wakeupActivityVar)
    h_activityButton = Button(hibernateActivityFrame, text='Manual act...', command=lambda: assign(wakeupActivityVar, simpledialog.askinteger('Manual Wakeup Activity', prompt='[1-50]: ')))
    hibernateLengthScale = Scale(hibernateLengthFrame, label='Max Length (sec)', variable=hibernateLengthVar, orient='horizontal', from_=5, to=300)
    hibernateLengthButton = Button(hibernateLengthFrame, text='Manual length...', command=lambda: assign(hibernateLengthVar, simpledialog.askinteger('Manual Hibernate Length', prompt='[5-300]: ')))

    hibernatettp = CreateToolTip(toggleHibernateButton, 'Runs EdgeWare silently without any popups.\n\n'
                                    'After a random time in the specified range, EdgeWare activates and barrages the user with popups '
                                    'based on the \"Awaken Activity\" value (depending on the hibernate type), then goes back to \"sleep\".\n\n'
                                    'Check the \"About\" tab for more detailed information on each hibernate type.')
    fixwallpaperttp = CreateToolTip(fixWallpaperButton, '\"fixes\" your wallpaper after hibernate is finished by changing it to'
                                        ' your panic wallpaper. If left off, it will keep the pack\'s wallpaper on until you panic'
                                        ' or change it back yourself.')

    hibernate_group.append(hibernateMinButton)
    hibernate_group.append(hibernateMinScale)
    hibernate_group.append(hibernateMaxButton)
    hibernate_group.append(hibernateMaxScale)

    hlength_group.append(hibernateLengthButton)
    hlength_group.append(hibernateLengthScale)

    hactivity_group.append(h_activityScale)
    hactivity_group.append(h_activityButton)

    Label(tabGeneral, text='Hibernate Settings', font='Default 13', relief=GROOVE).pack(pady=2)
    hibernateHostFrame.pack(fill='x')
    hibernateFrame.pack(fill='y', side='left')
    hibernateTypeFrame.pack(fill='x', side='left')
    toggleHibernateButton.pack(fill='x', side='top')
    fixWallpaperButton.pack(fill='x', side='top')
    hibernateTypeDropdown.pack(fill='x', side='top')
    hibernateTypeDescriptionFrame.pack(fill='both', side='left', expand=1, padx=2, pady=2)
    hibernateTypeDescription.pack(fill='y', pady=2)
    hibernateMinScale.pack(fill='y')
    hibernateMinButton.pack(fill='y')
    hibernateMinFrame.pack(fill='x', side='left')
    hibernateMaxScale.pack(fill='y')
    hibernateMaxButton.pack(fill='y')
    hibernateMaxFrame.pack(fill='x', side='left')
    h_activityScale.pack(fill='y')
    h_activityButton.pack(fill='y')
    hibernateActivityFrame.pack(fill='x', side='left')
    hibernateLengthScale.pack(fill='y')
    hibernateLengthButton.pack(fill='y')
    hibernateLengthFrame.pack(fill='x', side='left')

    #timer settings
    Label(tabGeneral, text='Timer Settings', font='Default 13', relief=GROOVE).pack(pady=2)
    timerFrame = Frame(tabGeneral, borderwidth=5, relief=RAISED)

    timerToggle = Checkbutton(timerFrame, text='Timer Mode', variable=timerVar, command=lambda: toggleAssociateSettings(timerVar.get(), timer_group), cursor='question_arrow')
    timerSlider = Scale(timerFrame, label='Timer Time (mins)', from_=1, to=1440, orient='horizontal', variable=timerTimeVar)
    safewordFrame = Frame(timerFrame)

    timerttp = CreateToolTip(timerToggle, 'Enables \"Run on Startup\" and disables the Panic function until the time limit is reached.\n\n'
                                '\"Safeword\" allows you to set a password to re-enable Panic, if need be.')

    Label(safewordFrame, text='Emergency Safeword').pack()
    timerSafeword = Entry(safewordFrame, show='*', textvariable=safewordVar)
    timerSafeword.pack(expand=1, fill='both')

    timer_group.append(timerSafeword)
    timer_group.append(timerSlider)

    timerToggle.pack(side='left', fill='x', padx=5)
    timerSlider.pack(side='left', fill='x', expand=1, padx=10)
    safewordFrame.pack(side='right', fill='x', padx=5)

    timerFrame.pack(fill='x')

    #other
    Label(tabGeneral, text='Other', font='Default 13', relief=GROOVE).pack(pady=2)
    otherHostFrame = Frame(tabGeneral, borderwidth=5, relief=RAISED)
    toggleFrame1 = Frame(otherHostFrame)
    toggleFrame2 = Frame(otherHostFrame)
    toggleFrame3 = Frame(otherHostFrame)

    toggleStartupButton = Checkbutton(toggleFrame1, text='Launch on Startup', variable=startLoginVar)
    toggleDiscordButton = Checkbutton(toggleFrame1, text='Show on Discord', variable=discordVar, cursor='question_arrow')
    toggleFlairButton = Checkbutton(toggleFrame2, text='Show Loading Flair', variable=startFlairVar, cursor='question_arrow')
    toggleROSButton = Checkbutton(toggleFrame2, text='Run Edgeware on Save & Exit', variable=rosVar)
    toggleDesktopButton = Checkbutton(toggleFrame3, text='Create Desktop Icons', variable=deskIconVar)
    toggleSafeMode = Checkbutton(toggleFrame3, text='Warn if \"Dangerous\" Settings Active', variable=safeModeVar, cursor='question_arrow')

    otherHostFrame.pack(fill='x')
    toggleFrame1.pack(fill='both', side='left', expand=1)
    toggleStartupButton.pack(fill='x')
    toggleDiscordButton.pack(fill='x')
    toggleFrame2.pack(fill='both', side='left', expand=1)
    toggleFlairButton.pack(fill='x')
    toggleROSButton.pack(fill='x')
    toggleFrame3.pack(fill='both', side='left', expand=1)
    toggleDesktopButton.pack(fill='x')
    toggleSafeMode.pack(fill='x')

    discordttp = CreateToolTip(toggleDiscordButton, 'Displays a lewd status on discord (if your discord is open), which can be set per-pack by the pack creator.')
    loadingFlairttp = CreateToolTip(toggleFlairButton, 'Displays a brief \"loading\" image before EdgeWare startup, which can be set per-pack by the pack creator.')
    safeModettp = CreateToolTip(toggleSafeMode, 'Asks you to confirm before saving if certain settings are enabled.\n'
                    'Things defined as Dangerous Settings:\n\n'
                    'Extreme (code red! code red! read the documentation in \"about\"!):\n'
                    'Replace Images\n\n'
                    'Major (very dangerous, can affect your computer):\n'
                    'Launch on Startup, Fill Drive\n\n'
                    'Medium (can lead to embarassment or reduced control over EdgeWare):\n'
                    'Timer Mode, Show on Discord, short hibernate cooldown\n\n'
                    'Minor (low risk but could lead to unwanted interactions):\n'
                    'Disable Panic Hotkey, Run on Save & Exit')

    Label(tabGeneral, text='Information', font='Default 13', relief=GROOVE).pack(pady=2)
    infoHostFrame = Frame(tabGeneral, borderwidth=5, relief=RAISED)
    zipGitFrame = Frame(infoHostFrame)
    verFrame = Frame(infoHostFrame)
    #zipDropdown = OptionMenu(tabGeneral, zipDropVar, *DOWNLOAD_STRINGS)
    #zipDownloadButton = Button(tabGeneral, text='Download Zip', command=lambda: downloadZip(zipDropVar.get(), zipLabel))
    #zipLabel = Label(zipGitFrame, text=f'Current Zip:\n{pickZip()}', background='lightgray', wraplength=100)
    local_verLabel = Label(verFrame, text=f'EdgeWare Local Version:\n{defaultVars[0]}')
    web_verLabel = Label(verFrame, text=f'EdgeWare GitHub Version:\n{webv}', bg=('SystemButtonFace' if (defaultVars[0] == webv) else 'red'))
    openGitButton = Button(zipGitFrame, text='Open Github (EdgeWare Base)', command=lambda: webbrowser.open('https://github.com/PetitTournesol/Edgeware'))

    verPlusFrame = Frame(infoHostFrame)
    local_verPlusLabel = Label(verPlusFrame, text=f'EdgeWare++ Local Version:\n{defaultVars[1]}')
    web_verPlusLabel = Label(verPlusFrame, text=f'EdgeWare++ GitHub Version:\n{webvpp}', bg=('SystemButtonFace' if (defaultVars[1] == webvpp) else 'red'))
    openGitPlusButton = Button(zipGitFrame, text='Open Github (EdgeWare++)', command=lambda: webbrowser.open('https://github.com/araten10/EdgewarePlusPlus'))

    infoHostFrame.pack(fill='x')
    zipGitFrame.pack(fill='both', side='left', expand=1)
    #zipLabel.pack(fill='x')
    openGitButton.pack(fill='both', expand=1)
    verFrame.pack(fill='both', side='left', expand=1)
    local_verLabel.pack(fill='x')
    web_verLabel.pack(fill='x')

    verPlusFrame.pack(fill='both', side='left', expand=1)
    local_verPlusLabel.pack(fill='x')
    web_verPlusLabel.pack(fill='x')
    openGitPlusButton.pack(fill='both', expand=1)

    forceReload = Button(infoHostFrame, text='Force Reload', command=refresh)
    optButton   = Button(infoHostFrame, text='Test Func', command=lambda: getDescriptText('default'))

    resourceFrame = Frame(root)
    exportResourcesButton = Button(resourceFrame, text='Export Resource Pack', command=exportResource)
    importResourcesButton = Button(resourceFrame, text='Import Resource Pack', command=lambda: importResource(root))
    saveExitButton = Button(root, height=5, text='Save & Exit', command=lambda: write_save(in_var_group, in_var_names, safewordVar, True))

    #force reload button for debugging, only appears on DEV versions
    if local_version.endswith('DEV'):
        forceReload.pack(fill='y', expand=1)
        optButton.pack(fill='y', expand=1)

    #zipDownloadButton.grid(column=0, row=10) #not using for now until can find consistent direct download
    #zipDropdown.grid(column=0, row=9)
    #==========={HERE ENDS  GENERAL TAB ITEM INITS}===========#
    tabMaster.add(tabAnnoyance, text='Annoyance')

    Label(tabAnnoyance).pack()

    delayModeFrame = Frame(tabAnnoyance, borderwidth=5, relief=RAISED)
    delayFrame = Frame(delayModeFrame)
    lowkeyFrame = Frame(delayModeFrame)

    delayScale = Scale(delayFrame, label='Popup Timer Delay (ms)', from_=10, to=60000, orient='horizontal', variable=delayVar)
    delayManual = Button(delayFrame, text='Manual delay...', command=lambda: assign(delayVar, simpledialog.askinteger('Manual Delay', prompt='[10-60000]: ')))
    opacityScale = Scale(tabAnnoyance, label='Popup Opacity (%)', from_=5, to=100, orient='horizontal', variable=popopOpacity)

    posList = ['Top Right', 'Top Left', 'Bottom Left', 'Bottom Right', 'Random']
    lkItemVar = StringVar(root, posList[lkCorner.get()])
    lowkeyDropdown = OptionMenu(lowkeyFrame, lkItemVar, *posList, command=lambda x: (lkCorner.set(posList.index(x))))
    lowkeyToggle = Checkbutton(lowkeyFrame, text='Lowkey Mode', variable=lkToggle, command=lambda: toggleAssociateSettings(lkToggle.get(), lowkey_group), cursor='question_arrow')

    lowkeyttp = CreateToolTip(lowkeyToggle, 'Makes popups appear in a corner of the screen instead of the middle.\n\n'
                                'Best used with Popup Timeout or high delay as popups will stack.')

    lowkey_group.append(lowkeyDropdown)

    delayModeFrame.pack(fill='x')

    delayScale.pack(fill='x', expand=1)
    delayManual.pack(fill='x', expand=1)

    delayFrame.pack(side='left', fill='x', expand=1)

    lowkeyFrame.pack(fill='y', side='left')
    lowkeyDropdown.pack(fill='x', padx=2, pady = 5)
    lowkeyToggle.pack(fill='both', expand=1)

    opacityScale.pack(fill='x')

    #popup frame handling
    popupHostFrame = Frame(tabAnnoyance, borderwidth=5, relief=RAISED)
    popupFrame = Frame(popupHostFrame)
    timeoutFrame = Frame(popupHostFrame)
    mitosisFrame = Frame(popupHostFrame)
    panicFrame = Frame(popupHostFrame)
    denialFrame = Frame(popupHostFrame)

    popupScale = Scale(popupFrame, label='Popup Freq (%)', from_=0, to=100, orient='horizontal', variable=popupVar)
    popupManual = Button(popupFrame, text='Manual popup...', command=lambda: assign(popupVar, simpledialog.askinteger('Manual Popup', prompt='[0-100]: ')), cursor='question_arrow')

    popupManualttp = CreateToolTip(popupManual, 'Whenever the timer is reached to spawn a new popup, this value is rolled to see if it spawns or not.\n\n'
                                    'Leave at 100 for a more consistent experience, and make it less for a more random one.')

    toggleMultiClickButton = Checkbutton(popupFrame, text='Multi-Click popups', variable=mulitClickVar, cursor='question_arrow')

    mitosis_group.append(popupScale)
    mitosis_group.append(popupManual)

    def toggleMitosis():
        toggleAssociateSettings(not mitosisVar.get(), mitosis_group)
        toggleAssociateSettings(mitosisVar.get(), mitosis_cGroup)

    mitosisToggle = Checkbutton(mitosisFrame, text='Mitosis Mode', variable=mitosisVar, command=toggleMitosis, cursor='question_arrow')
    mitosisStren  = Scale(mitosisFrame, label='Mitosis Strength', orient='horizontal', from_=2, to=10, variable=mitosisStrenVar)

    mitosisttp = CreateToolTip(mitosisToggle, 'When a popup is closed, more popups will spawn in it\'s place based on the mitosis strength.')

    mitosis_cGroup.append(mitosisStren)

    setPanicButtonButton = Button(panicFrame, text=f'Set Panic Button\n<{panicButtonVar.get()}>', command=lambda:getKeyboardInput(setPanicButtonButton, panicButtonVar), cursor='question_arrow')
    doPanicButton = Button(panicFrame, text='Perform Panic', command=lambda: os.startfile('panic.pyw'))
    panicDisableButton = Checkbutton(popupHostFrame, text='Disable Panic Hotkey', variable=panicVar, cursor='question_arrow')

    setpanicttp = CreateToolTip(setPanicButtonButton, 'NOTE: To use this hotkey you must be \"focused\" on a EdgeWare popup. Click on a popup before using.')
    disablePanicttp = CreateToolTip(panicDisableButton, 'This not only disables the panic hotkey, but also the panic function in the system tray as well.\n\n'
                        'If you want to use Panic after this, you can still:\n'
                        '•Directly run \"panic.pyw\"\n'
                        '•Keep the config window open and press \"Perform Panic\"\n'
                        '•Use the panic desktop icon (if you kept those enabled)')

    popupWebToggle= Checkbutton(popupHostFrame, text='Popup close opens web page', variable=popupWebVar)
    toggleCaptionsButton = Checkbutton(popupHostFrame, text='Popup Captions', variable=captionVar)
    toggleEasierButton = Checkbutton(popupHostFrame, text='Buttonless Closing Popups', variable=buttonlessVar, cursor='question_arrow')

    buttonlessttp = CreateToolTip(toggleEasierButton, 'Disables the \"close button\" on popups and allows you to click anywhere on the popup to close it.\n\n'
                                    'IMPORTANT: The panic keyboard hotkey will only work in this mode if you use it while *holding down* the mouse button over a popup!')


    timeoutToggle = Checkbutton(timeoutFrame, text='Popup Timeout', variable=timeoutPopupsVar, command=lambda: toggleAssociateSettings(timeoutPopupsVar.get(), timeout_group))
    timeoutSlider = Scale(timeoutFrame, label='Time (sec)', from_=1, to=120, orient='horizontal', variable=popupTimeoutVar)

    timeout_group.append(timeoutSlider)

    denialSlider = Scale(denialFrame, label='Denial Chance', orient='horizontal', variable=denialChance)
    denialToggle = Checkbutton(denialFrame, text='Denial Mode', variable=denialMode, command=lambda: toggleAssociateSettings(denialMode.get(), denial_group), cursor='question_arrow')

    denialttp = CreateToolTip(denialToggle, 'Adds a percentage chance to \"censor\" an image.')
    denial_group.append(denialSlider)

    popupHostFrame.pack(fill='x')
    popupScale.pack(fill='x')
    popupManual.pack(fill='x')
    toggleMultiClickButton.pack(fill='x')
    popupFrame.pack(fill='y', side='left')    
    timeoutSlider.pack(fill='x')
    timeoutToggle.pack(fill='x')
    timeoutFrame.pack(fill='y', side='left')
    mitosisFrame.pack(fill='y', side='left')
    mitosisStren.pack(fill='x')
    mitosisToggle.pack(fill='x')
    denialFrame.pack(fill='y', side='left')
    denialSlider.pack(fill='x')
    denialToggle.pack(fill='x')
    panicFrame.pack(fill='y', side='left')
    setPanicButtonButton.pack(fill='x')
    doPanicButton.pack(fill='x')
    panicDisableButton.pack(fill='x')
    popupWebToggle.pack(fill='x')
    toggleCaptionsButton.pack(fill='x')
    toggleEasierButton.pack(fill='x')
    #popup frame handle end

    #other start
    otherHostFrame = Frame(tabAnnoyance, borderwidth=5, relief=RAISED)

    audioFrame = Frame(otherHostFrame)
    webFrame = Frame(otherHostFrame)
    vidFrameL = Frame(otherHostFrame)
    vidFrameR = Frame(otherHostFrame)
    promptFrame = Frame(otherHostFrame)
    mistakeFrame = Frame(otherHostFrame)

    audioScale = Scale(audioFrame, label='Audio Freq (%)', from_=0, to=100, orient='horizontal', variable=audioVar)
    audioManual = Button(audioFrame, text='Manual audio...', command=lambda: assign(audioVar, simpledialog.askinteger('Manual Audio', prompt='[0-100]: ')))

    webScale = Scale(webFrame, label='Website Freq (%)', from_=0, to=100, orient='horizontal', variable=webVar)
    webManual = Button(webFrame, text='Manual web...', command=lambda: assign(webVar, simpledialog.askinteger('Web Chance', prompt='[0-100]: ')))

    vidScale = Scale(vidFrameL, label='Video Chance (%)', from_=0, to=100, orient='horizontal', variable=vidVar)
    vidManual = Button(vidFrameL, text='Manual vid...', command=lambda: assign(vidVar, simpledialog.askinteger('Video Chance', prompt='[0-100]: ')))
    vidVolumeScale = Scale(vidFrameR, label='Video Volume', from_=0, to=100, orient='horizontal', variable=videoVolume)
    vidVolumeManual = Button(vidFrameR, text='Manual volume...', command=lambda: assign(videoVolume, simpledialog.askinteger('Video Volume', prompt='[0-100]: ')))

    promptScale = Scale(promptFrame, label='Prompt Freq (%)', from_=0, to=100, orient='horizontal', variable=promptVar)
    promptManual = Button(promptFrame, text='Manual prompt...', command=lambda: assign(promptVar, simpledialog.askinteger('Manual Prompt', prompt='[0-100]: ')))

    mistakeScale = Scale(mistakeFrame, label='Prompt Mistakes', from_=0, to=150, orient='horizontal', variable=promptMistakeVar)
    mistakeManual = Button(mistakeFrame, text='Manual mistakes...', command=lambda: assign(promptMistakeVar, simpledialog.askinteger('Max Mistakes', prompt='Max mistakes allowed in prompt text\n[0-150]: ')), cursor='question_arrow')

    mistakettp = CreateToolTip(mistakeManual, 'The number of allowed mistakes when filling out a prompt.\n\n'
                                'Good for when you can\'t think straight, or typing with one hand...')

    otherHostFrame.pack(fill='x')

    audioScale.pack(fill='x', padx=3, expand=1)
    audioManual.pack(fill='x')
    audioFrame.pack(side='left')

    webFrame.pack(fill='y', side='left', padx=3, expand=1)
    webScale.pack(fill='x')
    webManual.pack(fill='x')

    vidFrameL.pack(fill='x', side='left', padx=(3, 0), expand=1)
    vidScale.pack(fill='x')
    vidManual.pack(fill='x')
    vidFrameR.pack(fill='x', side='left', padx=(0, 3), expand=1)
    vidVolumeScale.pack(fill='x')
    vidVolumeManual.pack(fill='x')

    promptFrame.pack(fill='y', side='left', padx=(3,0), expand=1)
    promptScale.pack(fill='x')
    promptManual.pack(fill='x')
    mistakeFrame.pack(fill='y', side='left', padx=(0, 3), expand=1)
    mistakeScale.pack(fill='x')
    mistakeManual.pack(fill='x')
    #end web

    #max start
    maxPopupFrame = Frame(tabAnnoyance, borderwidth=5, relief=RAISED)

    maxAudioFrame = Frame(maxPopupFrame)
    maxVideoFrame = Frame(maxPopupFrame)
    subliminalsFrame = Frame(maxPopupFrame)

    subliminalsChanceFrame = Frame(subliminalsFrame)
    maxSubliminalsFrame = Frame(subliminalsFrame)
    #extra space for one more?

    maxAudioToggle = Checkbutton(maxAudioFrame, text='Cap Audio', variable=maxAToggleVar, command=lambda: toggleAssociateSettings(maxAToggleVar.get(), maxAudio_group))
    maxAudioScale = Scale(maxAudioFrame, label='Max Audio Popups', from_=1, to=50, orient='horizontal', variable=maxAudioVar)
    maxAudioManual = Button(maxAudioFrame, text='Manual Max Audio...', command=lambda: assign(maxAudioVar, simpledialog.askinteger('Manual Max Audio', prompt='[1-50]: ')))

    maxAudio_group.append(maxAudioScale)
    maxAudio_group.append(maxAudioManual)

    maxVideoToggle = Checkbutton(maxVideoFrame, text='Cap Videos', variable=maxVToggleVar, command=lambda: toggleAssociateSettings(maxVToggleVar.get(), maxVideo_group))
    maxVideoScale = Scale(maxVideoFrame, label='Max Video Popups', from_=1, to=50, orient='horizontal', variable=maxVideoVar)
    maxVideoManual = Button(maxVideoFrame, text='Manual Max Videos...', command=lambda: assign(maxVideoVar, simpledialog.askinteger('Manual Max Videos', prompt='[1-50]: ')))

    maxVideo_group.append(maxVideoScale)
    maxVideo_group.append(maxVideoManual)

    toggleSubliminalButton = Checkbutton(subliminalsFrame, text='Popup Subliminals', variable=popupSublim, command=lambda: toggleAssociateSettings(popupSublim.get(), subliminals_group), cursor='question_arrow')

    subliminalttp = CreateToolTip(toggleSubliminalButton, 'Overlays transparent gifs on popups.\n\nThis feature can be CPU intensive, try a low max limit to start!')

    subliminalsChanceScale = Scale(subliminalsChanceFrame, label='Sublim. Chance (%)', from_=1, to=100, orient='horizontal', variable=subliminalsChanceVar)
    subliminalsChanceManual = Button(subliminalsChanceFrame, text='Manual Sub Chance...', command=lambda: assign(subliminalsChanceVar, simpledialog.askinteger('Manual Subliminal Chance', prompt='[1-100]: ')))

    subliminals_group.append(subliminalsChanceScale)
    subliminals_group.append(subliminalsChanceManual)

    maxSubliminalsScale = Scale(maxSubliminalsFrame, label='Max Subliminals', from_=1, to=200, orient='horizontal', variable=maxSubliminalsVar)
    maxSubliminalsManual = Button(maxSubliminalsFrame, text='Manual Max Sub...', command=lambda: assign(maxSubliminalsVar, simpledialog.askinteger('Manual Max Subliminals', prompt='[1-200]: ')))

    subliminals_group.append(maxSubliminalsScale)
    subliminals_group.append(maxSubliminalsManual)

    maxPopupFrame.pack(fill='x')

    maxAudioFrame.pack(side='left')
    maxAudioToggle.pack(fill='x')
    maxAudioScale.pack(fill='x', padx=1, expand=1)
    maxAudioManual.pack(fill='x')

    maxVideoFrame.pack(fill='y', side='left', padx=3, expand=1)
    maxVideoToggle.pack(fill='x')
    maxVideoScale.pack(fill='x', padx=1, expand=1)
    maxVideoManual.pack(fill='x')

    subliminalsFrame.pack(side='left')
    toggleSubliminalButton.pack(fill='x')

    subliminalsChanceFrame.pack(fill='y', side='left', padx=3, expand=1)
    subliminalsChanceScale.pack(fill='x', padx=1, expand=1)
    subliminalsChanceManual.pack(fill='x')

    maxSubliminalsFrame.pack(fill='y', side='left', padx=3, expand=1)
    maxSubliminalsScale.pack(fill='x', padx=1, expand=1)
    maxSubliminalsManual.pack(fill='x')

    #corruption start
    corruptionFrame = Frame(tabAnnoyance, borderwidth=5, relief=RAISED)

    corruptionSettingsFrame = Frame(corruptionFrame)
    corruptionTypeFrame = Frame(corruptionFrame)
    corruptionTimeFrame = Frame(corruptionFrame)

    corruptionToggle = Checkbutton(corruptionSettingsFrame, text='Turn on Corruption', variable=corruptionModeVar, cursor='question_arrow')
    corruptionRecommendedToggle = Button(corruptionSettingsFrame, text='Recommended Settings', cursor='question_arrow')

    corruptionFrame.pack(fill='x')

    corruptionSettingsFrame.pack(side='left')
    corruptionTypeFrame.pack(side='left')
    corruptionTimeFrame.pack(side='left')

    corruptionToggle.pack(fill='x')
    corruptionRecommendedToggle.pack(fill='x')

    corruptionmodettp = CreateToolTip(corruptionToggle, 'Corruption Mode gradually makes the pack more depraved, by slowly toggling on previously hidden'
                                        ' content. Or at least that\'s the idea, pack creators can do whatever they want with it.\n\n'
                                        'Corruption uses the \'mood\' feature, which must be supported with a corruption.json file in the resource'
                                        ' folder. Over time moods will \"unlock\", leading to new things you haven\'t seen before the longer you use'
                                        ' EdgeWare.\n\nFor more information, check out the \"About\" tab. \n\nNOTE: currently not implemented! Holy god I hope I remember to remove this notice later!')
    corruptionsettingsttp = CreateToolTip(corruptionRecommendedToggle, 'Pack creators can set \"default corruption settings\" for their pack, to give'
                                        ' users a more designed and consistent experience. This setting turns those on (if they exist).')

    corruptionTimerButton = Button(corruptionTimeFrame, text='Manual time...', command=lambda: assign(corruptionTimeVar, simpledialog.askinteger('Manual Level Time (sec)', prompt='[5-1800]: ')))
    corruptionTimerScale = Scale(corruptionTimeFrame, label='Level Time', variable=corruptionTimeVar, orient='horizontal', from_=5, to=1800)

    corruptionTimerScale.pack(fill='y')
    corruptionTimerButton.pack(fill='y')
    #===================={DRIVE}==============================#
    tabMaster.add(tabDrive, text='Drive')

    hardDriveFrame = Frame(tabDrive, borderwidth=5, relief=RAISED)

    pathFrame = Frame(hardDriveFrame)
    fillFrame = Frame(hardDriveFrame)
    replaceFrame = Frame(hardDriveFrame)

    def local_assignPath():
        nonlocal fillPathVar
        path_ = str(filedialog.askdirectory(initialdir='/', title='Select Parent Folder'))
        if path_ != '':
            settings['drivePath'] = path_
            pathBox.configure(state='normal')
            pathBox.delete(0, 9999)
            pathBox.insert(1, path_)
            pathBox.configure(state='disabled')
            fillPathVar.set(str(pathBox.get()))
    pathBox = Entry(pathFrame)
    pathButton = Button(pathFrame, text='Select', command=local_assignPath)

    pathBox.insert(1, settings['drivePath'])
    pathBox.configure(state='disabled')

    fillBox = Checkbutton(fillFrame, text='Fill Drive', variable=fillVar, command=lambda: toggleAssociateSettings(fillVar.get(), fill_group), cursor='question_arrow')
    fillDelay = Scale(fillFrame, label='Fill Delay (10ms)', from_=0, to=250, orient='horizontal', variable=fillDelayVar)

    fillttp = CreateToolTip(fillBox, 'Fills folders on your harddrive with images from the resource folder.\n\n'
                'This can cause space issues, potential embarassment, navigation difficulties... Please read the full documentation in the About tab!!!')

    fill_group.append(fillDelay)

    replaceBox = Checkbutton(fillFrame, text='Replace Images', variable=replaceVar, command=lambda: toggleAssociateSettings(replaceVar.get(), replace_group), cursor='question_arrow')
    replaceThreshScale = Scale(fillFrame, label='Image Threshold', from_=1, to=1000, orient='horizontal', variable=replaceThreshVar)

    replacettp = CreateToolTip(replaceBox, 'Seeks out folders with more images than the threshold value, then replaces all of them. No, there is no automated backup!\n\n'
                                'I am begging you to read the full documentation in the \"About\" tab before even thinking about enabling this feature!\n\n'
                                'We are not responsible for any pain, suffering, miserere, or despondence caused by your files being deleted! '
                                'At the very least, back them up and use the blacklist!')

    replace_group.append(replaceThreshScale)

    avoidHostFrame = Frame(hardDriveFrame)

    avoidListBox = Listbox(avoidHostFrame, selectmode=SINGLE)
    for name in settings['avoidList'].split('>'):
        avoidListBox.insert(2, name)
    addName = Button(avoidHostFrame, text='Add Name', command=lambda: addList(avoidListBox, 'avoidList', 'Folder Name', 'Fill/replace will skip any folder with given name.'))
    removeName = Button(avoidHostFrame, text='Remove Name', command=lambda: removeList(avoidListBox, 'avoidList', 'Remove EdgeWare', 'You cannot remove the EdgeWare folder exception.'))
    resetName  = Button(avoidHostFrame, text='Reset', command=lambda: resetList(avoidListBox, 'avoidList', 'EdgeWare>AppData'))

    avoidHostFrame.pack(fill='y', side='left')
    Label(avoidHostFrame, text='Folder Name Blacklist').pack(fill='x')
    avoidListBox.pack(fill='x')
    addName.pack(fill='x')
    removeName.pack(fill='x')
    resetName.pack(fill='x')

    Label(tabDrive, text='Hard Drive Settings').pack(fill='both')
    hardDriveFrame.pack(fill='x')
    fillFrame.pack(fill='y', side='left')
    fillBox.pack()
    fillDelay.pack()
    replaceFrame.pack(fill='y', side='left')
    replaceBox.pack()
    replaceThreshScale.pack()
    pathFrame.pack(fill='x')
    Label(pathFrame, text='Fill/Replace Start Folder').pack(fill='x')
    pathBox.pack(fill='x')
    pathButton.pack(fill='x')

    downloadHostFrame = Frame(tabDrive, borderwidth=5, relief=RAISED)
    otherFrame = Frame(downloadHostFrame)
    tagFrame   = Frame(downloadHostFrame)
    booruFrame = Frame(downloadHostFrame)
    booruNameEntry = Entry(booruFrame, textvariable=booruNameVar)
    downloadEnabled = Checkbutton(otherFrame, text='Download from Booru', variable=downloadEnabledVar, command=lambda: (
        toggleAssociateSettings_manual(downloadEnabledVar.get(), download_group, 'white', 'gray25')))
    downloadResourceEnabled = Checkbutton(otherFrame, text='Download from webResource', variable=useWebResourceVar)
    toggleAssociateSettings(hasWebResourceVar.get(), [downloadResourceEnabled])
    downloadMode    = OptionMenu(booruFrame, downloadModeVar, *['All', 'First Page', 'Random Page'])
    downloadMode.configure(width=15)
    minScoreSlider = Scale(booruFrame, from_=-50, to=100, orient='horizontal', variable=booruMin, label='Minimum Score')

    booruValidate  = Button(booruFrame, text='Validate', command=lambda: (
        messagebox.showinfo('Success!', 'Booru is valid.')
        if validateBooru(booruNameVar.get()) else
        messagebox.showerror('Failed', 'Booru is invalid.')
    ))

    tagListBox = Listbox(tagFrame, selectmode=SINGLE)
    for tag in settings['tagList'].split('>'):
        tagListBox.insert(1, tag)
    addTag = Button(tagFrame, text='Add Tag', command=lambda: addList(tagListBox, 'tagList', 'New Tag', 'Enter Tag(s)'))
    removeTag = Button(tagFrame, text='Remove Tag', command=lambda: removeList_(tagListBox, 'tagList', 'Remove Failed', 'Cannot remove all tags. To download without a tag, use "all" as the tag.'))
    resetTag  = Button(tagFrame, text='Reset Tags', command=lambda: resetList(tagListBox, 'tagList', 'all'))

    download_group.append(booruNameEntry)
    download_group.append(booruValidate)
    download_group.append(tagListBox)
    download_group.append(addTag)
    download_group.append(removeTag)
    download_group.append(resetTag)
    download_group.append(downloadMode)
    download_group.append(minScoreSlider)

    Label(tabDrive, text='Image Download Settings').pack(fill='x')
    Label(downloadHostFrame, text='THE BOORU DOWNLOADER IS OUTDATED AND BROKEN. IT WILL LIKELY BARELY FUNCTION, IF AT ALL.\nNo I will not fix it, this shit is a pain in the ass and I\'m stupid.', foreground='red').pack(fill='x')
    tagFrame.pack(fill='y', side='left')
    booruFrame.pack(fill='y', side='left')
    otherFrame.pack(fill='both',side='right')

    downloadEnabled.pack()
    downloadHostFrame.pack(fill='both')
    tagListBox.pack(fill='x')
    addTag.pack(fill='x')
    removeTag.pack(fill='x')
    resetTag.pack(fill='x')
    Label(booruFrame, text='Booru Name').pack(fill='x')
    booruNameEntry.pack(fill='x')
    booruValidate.pack(fill='x')
    Label(booruFrame, text='Download Mode').pack(fill='x')
    downloadMode.pack(fill='x')
    minScoreSlider.pack(fill='x')
    downloadResourceEnabled.pack(fill='x')

    tabMaster.add(tabWallpaper, text='Wallpaper')
    #==========={WALLPAPER TAB ITEMS} ========================#
    rotateCheckbox = Checkbutton(tabWallpaper, text='Rotate Wallpapers', variable=rotateWallpaperVar,
                                 command=lambda: toggleAssociateSettings(rotateWallpaperVar.get(), wallpaper_group))
    wpList = Listbox(tabWallpaper, selectmode=SINGLE)
    for key in settings['wallpaperDat']:
        wpList.insert(1, key)
    addWPButton = Button(tabWallpaper, text='Add/Edit Wallpaper', command=lambda: addWallpaper(wpList))
    remWPButton = Button(tabWallpaper, text='Remove Wallpaper', command=lambda: removeWallpaper(wpList))
    autoImport  = Button(tabWallpaper, text='Auto Import', command=lambda: autoImportWallpapers(wpList))
    varSlider     = Scale(tabWallpaper, orient='horizontal', label='Rotate Variation (sec)', from_=0,
                          to=(wallpaperDelayVar.get()-1), variable=wpVarianceVar)
    wpDelaySlider = Scale(tabWallpaper, orient='horizontal', label='Rotate Timer (sec)', from_=5, to=300,
                          variable=wallpaperDelayVar, command=lambda val: updateMax(varSlider, int(val)-1))

    pHoldImageR = Image.open(os.path.join(PATH, 'default_assets', 'default_win10.jpg')).resize((int(root.winfo_screenwidth()*0.13), int(root.winfo_screenheight()*0.13)), Image.NEAREST)

    def updatePanicPaper():
        nonlocal pHoldImageR
        selectedFile = filedialog.askopenfile('rb', filetypes=[
            ('image file', '.jpg .jpeg .png')
        ])
        if not isinstance(selectedFile, type(None)):
            try:
                img = Image.open(selectedFile.name).convert('RGB')
                img.save(os.path.join(PATH, 'default_assets', 'default_win10.jpg'))
                pHoldImageR = ImageTk.PhotoImage(img.resize((int(root.winfo_screenwidth()*0.13), int(root.winfo_screenheight()*0.13)), Image.NEAREST))
                panicWallpaperLabel.config(image=pHoldImageR)
                panicWallpaperLabel.update_idletasks()
            except Exception as e:
                logging.warning(f'failed to open/change default wallpaper\n{e}')

    panicWPFrame = Frame(tabWallpaper)
    panicWPFrameL = Frame(panicWPFrame)
    panicWPFrameR = Frame(panicWPFrame)
    panicWallpaperImage = ImageTk.PhotoImage(pHoldImageR)
    panicWallpaperButton = Button(panicWPFrameL, text='Change Panic Wallpaper', command=updatePanicPaper, cursor='question_arrow')
    panicWallpaperLabel = Label(panicWPFrameR, text='Current Panic Wallpaper', image=panicWallpaperImage)

    panicWallpaperttp = CreateToolTip(panicWallpaperButton, 'When you use panic, the wallpaper will be set to this image.\n\n'
                                        'This is useful since most packs have a custom wallpaper, which is usually porn...!\n\n'
                                        'It is recommended to find your preferred/original desktop wallpaper and set it to that.')

    wallpaper_group.append(wpList)
    wallpaper_group.append(addWPButton)
    wallpaper_group.append(remWPButton)
    wallpaper_group.append(wpDelaySlider)
    wallpaper_group.append(autoImport)
    wallpaper_group.append(varSlider)

    rotateCheckbox.pack(fill='x')
    wpList.pack(fill='x')
    addWPButton.pack(fill='x')
    remWPButton.pack(fill='x')
    autoImport.pack(fill='x')
    wpDelaySlider.pack(fill='x')
    varSlider.pack(fill='x')
    panicWPFrame.pack(fill='x', expand=1)
    panicWPFrameL.pack(side='left', fill='y')
    panicWPFrameR.pack(side='right', fill='x', expand=1)
    panicWallpaperButton.pack(fill='x', padx=5, pady=5, expand=1)
    Label(panicWPFrameR, text='Current Panic Wallpaper').pack(fill='x')
    panicWallpaperLabel.pack()
    #==========={EDGEWARE++ "PACK INFO" TAB STARTS HERE}===========#
    tabMaster.add(tabPackInfo, text='Pack Info')

    #Stats
    Label(tabPackInfo, text='Stats', font='Default 13', relief=GROOVE).pack(pady=2)
    infoStatusFrame = Frame(tabPackInfo, borderwidth=5, relief=RAISED)
    statusPackFrame = Frame(infoStatusFrame)
    statusAboutFrame = Frame(infoStatusFrame)
    statusWallpaperFrame = Frame(infoStatusFrame)
    statusStartupFrame = Frame(infoStatusFrame)
    statusDiscordFrame = Frame(infoStatusFrame)
    statusIconFrame = Frame(infoStatusFrame)
    statusCorruptionFrame = Frame(infoStatusFrame)

    if os.path.exists(PATH + '\\resource\\'):
        statusPack = True
        statusAbout = True if os.path.isfile(PATH + '\\resource\\info.json') else False
        statusWallpaper = True if os.path.isfile(PATH + '\\resource\\wallpaper.png') else False
        statusStartup = True if os.path.isfile(PATH + '\\resource\\loading_splash.png') else False
        statusDiscord = True if os.path.isfile(PATH + '\\resource\\discord.dat') else False
        statusIcon = True if os.path.isfile(PATH + '\\resource\\icon.ico') else False
        statusCorruption = True if os.path.isfile(PATH + '\\resource\\corruption.json') else False
    else:
        statusPack = False
        statusAbout = False
        statusWallpaper = False
        statusStartup = False
        statusDiscord = False
        statusIcon = False
        statusCorruption = False

    statusPackFrameVarLabel = Label(statusPackFrame, text=('✓' if statusPack else '✗'), font='Default 14', fg=('green' if statusPack else 'red'))
    statusAboutFrameVarLabel = Label(statusAboutFrame, text=('✓' if statusAbout else '✗'), font='Default 14', fg=('green' if statusAbout else 'red'))
    statusWallpaperFrameVarLabel = Label(statusWallpaperFrame, text=('✓' if statusWallpaper else '✗'), font='Default 14', fg=('green' if statusWallpaper else 'red'))
    statusStartupFrameVarLabel = Label(statusStartupFrame, text=('✓' if statusStartup else '✗'), font='Default 14', fg=('green' if statusStartup else 'red'), cursor='question_arrow')
    statusDiscordFrameVarLabel = Label(statusDiscordFrame, text=('✓' if statusDiscord else '✗'), font='Default 14', fg=('green' if statusDiscord else 'red'))
    statusIconFrameVarLabel = Label(statusIconFrame, text=('✓' if statusIcon else '✗'), font='Default 14', fg=('green' if statusIcon else 'red'), cursor='question_arrow')
    statusCorruptionFrameVarLabel = Label(statusCorruptionFrame, text=('✓' if statusCorruption else '✗'), font='Default 14', fg=('green' if statusCorruption else 'red'), cursor='question_arrow')

    infoStatusFrame.pack(fill='x', padx=3)
    statusPackFrame.pack(fill='x', side='left', expand=1)
    Label(statusPackFrame, text='Pack Loaded', font='Default 10').pack(padx=2, pady=2, side='top')
    statusPackFrameVarLabel.pack(padx=2, pady=2, side='top')
    statusAboutFrame.pack(fill='x', side='left', expand=1)
    Label(statusAboutFrame, text='Info File', font='Default 10').pack(padx=2, pady=2, side='top')
    statusAboutFrameVarLabel.pack(padx=2, pady=2, side='top')
    statusWallpaperFrame.pack(fill='x', side='left', expand=1)
    Label(statusWallpaperFrame, text='Pack has Wallpaper', font='Default 10').pack(padx=2, pady=2, side='top')
    statusWallpaperFrameVarLabel.pack(padx=2, pady=2, side='top')
    statusStartupFrame.pack(fill='x', side='left', expand=1)
    Label(statusStartupFrame, text='Custom Startup', font='Default 10').pack(padx=2, pady=2, side='top')
    statusStartupFrameVarLabel.pack(padx=2, pady=2, side='top')
    statusDiscordFrame.pack(fill='x', side='left', expand=1)
    Label(statusDiscordFrame, text='Custom Discord Status', font='Default 10').pack(padx=2, pady=2, side='top')
    statusDiscordFrameVarLabel.pack(padx=2, pady=2, side='top')
    statusIconFrame.pack(fill='x', side='left', expand=1)
    Label(statusIconFrame, text='Custom Icon', font='Default 10').pack(padx=2, pady=2, side='top')
    statusIconFrameVarLabel.pack(padx=2, pady=2, side='top')
    statusCorruptionFrame.pack(fill='x', side='left', expand=1)
    Label(statusCorruptionFrame, text='Corruption', font='Default 10').pack(padx=2, pady=2, side='top')
    statusCorruptionFrameVarLabel.pack(padx=2, pady=2, side='top')

    statusStartupttp = CreateToolTip(statusStartupFrameVarLabel, 'If you are looking to add this to packs made before EdgeWare++,'
                                        ' put the desired file in /resource/ and name it \"loading_splash.png\".')
    statusIconttp = CreateToolTip(statusIconFrameVarLabel, 'If you are looking to add this to packs made before EdgeWare++,'
                                        ' put the desired file in /resource/ and name it \"icon.ico\". (the file must be'
                                        ' a .ico file! make sure you convert properly!)')
    corruptionttp = CreateToolTip(statusCorruptionFrameVarLabel, 'An EdgeWare++ feature that is kind of hard to describe in a single tooltip.\n\n'
                                        'For more information, check the \"About\" tab for a detailed writeup.')

    statsFrame = Frame(tabPackInfo, borderwidth=5, relief=RAISED)
    statsFrame1 = Frame(statsFrame)
    statsFrame2 = Frame(statsFrame)
    imageStatsFrame = Frame(statsFrame1)
    audioStatsFrame = Frame(statsFrame1)
    videoStatsFrame = Frame(statsFrame1)
    webStatsFrame = Frame(statsFrame1)
    promptStatsFrame = Frame(statsFrame2)
    captionsStatsFrame = Frame(statsFrame2)
    subliminalsStatsFrame = Frame(statsFrame2)

    imageStat = len(os.listdir(PATH + '\\resource\\img\\')) if os.path.exists(PATH + '\\resource\\img\\') else 0
    audioStat = len(os.listdir(PATH + '\\resource\\aud\\')) if os.path.exists(PATH + '\\resource\\aud\\') else 0
    videoStat = len(os.listdir(PATH + '\\resource\\vid\\')) if os.path.exists(PATH + '\\resource\\vid\\') else 0

    if os.path.exists(PATH + '\\resource\\web.json'):
        try:
            with open(PATH + '\\resource\\web.json', 'r') as f:
                webStat = len(json.loads(f.read())['urls'])
        except Exception as e:
            logging.warning(f'error in web.json. Aborting preview load. {e}')
            errors_list.append('Something is wrong with the currently loaded web.json file!\n')
            webStat = 0
    else:
        webStat = 0

    if os.path.exists(PATH + '\\resource\\prompt.json'):
        #frankly really ugly but the easiest way I found to do it
        try:
            with open(PATH + '\\resource\\prompt.json', 'r') as f:
                l = json.loads(f.read())
                i = 0
                if 'moods' in l: del l['moods']
                if 'minLen' in l: del l['minLen']
                if 'maxLen' in l: del l['maxLen']
                if 'freqList' in l: del l['freqList']
                if 'subtext' in l: del l['subtext']
                if 'commandtext' in l: del l['commandtext']
                for x in l:
                    i += len(l[x])
                promptStat = i
        except Exception as e:
            logging.warning(f'error in prompt.json. Aborting preview load. {e}')
            errors_list.append('Something is wrong with the currently loaded prompt.json file!\n')
            promptStat = 0
    else:
        promptStat = 0

    if os.path.exists(PATH + '\\resource\\captions.json'):
        #don't think these have moods currently but will implement this just in case
        try:
            with open(PATH + '\\resource\\captions.json', 'r') as f:
                l = json.loads(f.read())
                i = 0
                if 'prefix' in l: del l['prefix']
                if 'subtext' in l: del l['subtext']
                for x in l:
                    i += len(l[x])
                captionStat = i
        except Exception as e:
            logging.warning(f'error in captions.json. Aborting preview load. {e}')
            errors_list.append('Something is wrong with the currently loaded captions.json file!\n')
            captionStat = 0
    else:
        captionStat = 0

    subliminalStat = len(os.listdir(PATH + '\\resource\\subliminals\\')) if os.path.exists(PATH + '\\resource\\subliminals\\') else 0

    statsFrame.pack(fill='x', padx=3, pady=1)
    statsFrame1.pack(fill='x', side='top')
    imageStatsFrame.pack(fill='x', side='left', expand=1)
    Label(imageStatsFrame, text='Images', font='Default 10').pack(pady=2, side='top')
    ttk.Separator(imageStatsFrame, orient='horizontal').pack(fill='x', side='top', padx=10)
    Label(imageStatsFrame, text=f'{imageStat}').pack(pady=2, side='top')
    audioStatsFrame.pack(fill='x', side='left', expand=1)
    Label(audioStatsFrame, text='Audio Files', font='Default 10').pack(pady=2, side='top')
    ttk.Separator(audioStatsFrame, orient='horizontal').pack(fill='x', side='top', padx=10)
    Label(audioStatsFrame, text=f'{audioStat}').pack(pady=2, side='top')
    videoStatsFrame.pack(fill='x', side='left', expand=1)
    Label(videoStatsFrame, text='Videos', font='Default 10').pack(pady=2, side='top')
    ttk.Separator(videoStatsFrame, orient='horizontal').pack(fill='x', side='top', padx=10)
    Label(videoStatsFrame, text=f'{videoStat}').pack(pady=2, side='top')
    webStatsFrame.pack(fill='x', side='left', expand=1)
    Label(webStatsFrame, text='Web Links', font='Default 10').pack(pady=2, side='top')
    ttk.Separator(webStatsFrame, orient='horizontal').pack(fill='x', side='top', padx=10)
    Label(webStatsFrame, text=f'{webStat}').pack(pady=2, side='top')

    statsFrame2.pack(fill='x', side='top', pady=1)
    promptStatsFrame.pack(fill='x', side='left', expand=1)
    Label(promptStatsFrame, text='Prompts', font='Default 10').pack(pady=2, side='top')
    ttk.Separator(promptStatsFrame, orient='horizontal').pack(fill='x', side='top', padx=20)
    Label(promptStatsFrame, text=f'{promptStat}').pack(pady=2, side='top')
    captionsStatsFrame.pack(fill='x', side='left', expand=1)
    Label(captionsStatsFrame, text='Captions', font='Default 10').pack(pady=2, side='top')
    ttk.Separator(captionsStatsFrame, orient='horizontal').pack(fill='x', side='top', padx=20)
    Label(captionsStatsFrame, text=f'{captionStat}').pack(pady=2, side='top')
    subliminalsStatsFrame.pack(fill='x', side='left', expand=1)
    Label(subliminalsStatsFrame, text='Subliminals', font='Default 10').pack(pady=2, side='top')
    ttk.Separator(subliminalsStatsFrame, orient='horizontal').pack(fill='x', side='top', padx=20)
    Label(subliminalsStatsFrame, text=f'{subliminalStat}').pack(pady=2, side='top')

    #Information
    Label(tabPackInfo, text='Information', font='Default 13', relief=GROOVE).pack(pady=2)
    infoDescFrame = Frame(tabPackInfo, borderwidth=5, relief=RAISED)
    subInfoFrame = Frame(infoDescFrame, borderwidth=2, relief=GROOVE)
    descriptionFrame = Frame(infoDescFrame, borderwidth=2, relief=GROOVE)

    nameFrame = Frame(subInfoFrame)
    nameLabel = Label(nameFrame, text='Pack Name:', font='Default 10')
    nameVarLabel = Label(nameFrame, text=f'{info_name}')
    creatorFrame = Frame(subInfoFrame)
    creatorLabel = Label(creatorFrame, text='Author Name:', font='Default 10')
    creatorVarLabel = Label(creatorFrame, text=f'{info_creator}')
    versionFrame = Frame(subInfoFrame)
    versionLabel = Label(versionFrame, text='Version:', font='Default 10')
    versionVarLabel = Label(versionFrame, text=f'{info_version}')
    descriptionLabel = Label(descriptionFrame, text='Description', font='Default 10')
    infoDescriptionWrap = textwrap.TextWrapper(width=80, max_lines=5)
    descriptionVarLabel = Label(descriptionFrame, text=infoDescriptionWrap.fill(text=f'{info_description}'))

    infoDescFrame.pack(fill='x', padx=3)
    subInfoFrame.pack(fill='x', side='left', expand=1)

    nameFrame.pack(fill='x')
    nameLabel.pack(padx=6, pady=2, side='left')
    ttk.Separator(nameFrame, orient='vertical').pack(fill='y', side='left')
    nameVarLabel.pack(padx=2, pady=2, side='left')
    ttk.Separator(subInfoFrame, orient='horizontal').pack(fill='x')

    creatorFrame.pack(fill='x')
    creatorLabel.pack(padx=2, pady=2, side='left')
    ttk.Separator(creatorFrame, orient='vertical').pack(fill='y', side='left')
    creatorVarLabel.pack(padx=2, pady=2, side='left')
    ttk.Separator(subInfoFrame, orient='horizontal').pack(fill='x')

    versionFrame.pack(fill='x')
    versionLabel.pack(padx=18, pady=2, side='left')
    ttk.Separator(versionFrame, orient='vertical').pack(fill='y', side='left')
    versionVarLabel.pack(padx=2, pady=2, side='left')

    descriptionFrame.pack(fill='both', side='right')
    descriptionLabel.pack(padx=2, pady=2, side='top')
    ttk.Separator(descriptionFrame, orient='horizontal').pack(fill='x', side='top')
    descriptionVarLabel.pack(padx=2, pady=2, side='top')

    info_group.append(infoDescFrame)
    info_group.append(nameFrame)
    info_group.append(nameLabel)
    info_group.append(nameVarLabel)
    info_group.append(creatorFrame)
    info_group.append(creatorLabel)
    info_group.append(creatorVarLabel)
    info_group.append(descriptionFrame)
    info_group.append(descriptionLabel)
    info_group.append(descriptionVarLabel)
    info_group.append(versionFrame)
    info_group.append(versionLabel)
    info_group.append(versionVarLabel)
    toggleAssociateSettings(statusAbout, info_group)

    discordStatusFrame = Frame(tabPackInfo, borderwidth=5, relief=RAISED)
    discordStatusLabel = Label(discordStatusFrame, text='Custom Discord Status:', font='Default 10')
    discordStatusImageLabel = Label(discordStatusFrame, text='Discord Status Image:', font='Default 10')
    if statusDiscord:
        try:
            with open((PATH + '\\resource\\discord.dat'), 'r') as f:
                datfile = f.read()
                if not datfile == '':
                    info_discord = datfile.split('\n')
                    if len(info_discord) < 2:
                        info_discord.append(INFO_DISCORD_DEFAULT[1])
        except Exception as e:
            logging.warning(f'error in discord.dat. Aborting preview load. {e}')
            errors_list.append('Something is wrong with the currently loaded discord.dat file!\n')
            info_discord = INFO_DISCORD_DEFAULT.copy()
    else:
        info_discord = INFO_DISCORD_DEFAULT.copy()

    discordStatusVarLabel = Label(discordStatusFrame, text=f'{info_discord[0]}')
    discordStatusImageVarLabel = Label(discordStatusFrame, text=f'{info_discord[1]}', cursor='question_arrow')

    discordStatusFrame.pack(fill='x', padx=3)
    discordStatusLabel.pack(padx=2, pady=2, side='left')
    ttk.Separator(discordStatusFrame, orient='vertical').pack(fill='y', side='left')
    discordStatusVarLabel.pack(padx=2, pady=2, side='left', expand=1)
    ttk.Separator(discordStatusFrame, orient='vertical').pack(fill='y', side='left')
    discordStatusImageLabel.pack(padx=2, pady=2, side='left')
    ttk.Separator(discordStatusFrame, orient='vertical').pack(fill='y', side='left')
    discordStatusImageVarLabel.pack(padx=2, pady=2, side='left')

    discord_group.append(discordStatusFrame)
    discord_group.append(discordStatusLabel)
    discord_group.append(discordStatusImageLabel)
    discord_group.append(discordStatusVarLabel)
    discord_group.append(discordStatusImageVarLabel)
    toggleAssociateSettings(statusDiscord, discord_group)

    discordimagettp = CreateToolTip(discordStatusImageVarLabel, 'As much as I would like to show you this image, it\'s fetched from the discord '
                                    'application API- which I cannot access without permissions, as far as i\'m aware.\n\n'
                                    'Because of this, only packs created by the original EdgeWare creator, PetitTournesol, have custom status images.\n\n'
                                    'Nevertheless, I have decided to put this here not only for those packs, but also for other '
                                    'packs that tap in to the same image IDs.')
    #Moods
    Label(tabPackInfo, text='Moods', font='Default 13', relief=GROOVE).pack(pady=2)

    moodsFrame = Frame(tabPackInfo, borderwidth=5, relief=RAISED)
    moodsListFrame = Frame(moodsFrame)
    tabMoodsMaster = ttk.Notebook(moodsListFrame)
    moodsMediaFrame = Frame(tabMoodsMaster)
    moodsCaptionsFrame = Frame(tabMoodsMaster)
    moodsPromptsFrame = Frame(tabMoodsMaster)

    moodsFrame.pack(fill='x')
    moodsListFrame.grid(row=0, column=0, sticky="nsew")
    tabMoodsMaster.pack(fill='x')
    moodsMediaFrame.pack(fill='both')
    moodsCaptionsFrame.pack(fill='both')
    moodsPromptsFrame.pack(fill='both')

    tabMoodsMaster.add(moodsMediaFrame, text='Media')
    tabMoodsMaster.add(moodsCaptionsFrame, text='Captions')
    tabMoodsMaster.add(moodsPromptsFrame, text='Prompts')

        #Media frame
    mediaTree = CheckboxTreeview(moodsMediaFrame, height=7, show='tree', name='captionsTree')
    mediaScrollbar = ttk.Scrollbar(moodsMediaFrame, orient=VERTICAL, command=mediaTree.yview)
    mediaTree.configure(yscroll=mediaScrollbar.set)

    if os.path.exists(PATH + '\\resource\\media.json'):
        try:
            with open(PATH + '\\resource\\media.json', 'r') as f:
                l = json.loads(f.read())
                for m in l:
                    if m == 'default':
                        continue
                    parent = mediaTree.insert('', 'end', iid=str(m), values=str(m), text=str(m))
                    mediaTree.insert(parent, 'end', iid=(f'{m}desc'), text=(f'{len(l[m])} media related to this mood.'))
                    mediaTree.change_state((f'{m}desc'), 'disabled')

        except Exception as e:
            logging.warning(f'error in media.json. Aborting treeview load. {e}')
            errors_list.append('The media.json treeview couldn\'t load properly!\n')
            mediaTree.insert('', 'end', id='NAer', text='Pack doesn\'t support media moods, or they\'re improperly configured!')
            mediaTree.change_state('NAer', 'disabled')
    if len(mediaTree.get_children()) == 0:
        mediaTree.insert('', '0', iid='NAmi', text='No media moods found in pack!')
        mediaTree.change_state('NAmi', 'disabled')

    if settings['toggleMoodSet'] != True:
        if len(mediaTree.get_children()) != 0:
            if UNIQUE_ID != '0' and os.path.exists(PATH + '\\resource\\'):
                try:
                    with open(f'{PATH}\\moods\\unnamed\\{UNIQUE_ID}.json', 'r') as mood:
                        mood_dict = json.loads(mood.read())
                        for c in mediaTree.get_children():
                            value = mediaTree.item(c, 'values')
                            if value[0] in mood_dict["media"]:
                                mediaTree.change_state(value[0], 'checked')
                except Exception as e:
                    logging.warning(f'error checking media treeview nodes. {e}')
                    errors_list.append('The media treeview nodes couldn\'t finish their checking setup!\n')


    mediaTree.pack(side='left', fill='both', expand=1)
    mediaScrollbar.pack(side='left', fill='y')

        #Captions frame
    captionsTree = CheckboxTreeview(moodsCaptionsFrame, height=7, show='tree', name='captionsTree')
    captionsScrollbar = ttk.Scrollbar(moodsCaptionsFrame, orient=VERTICAL, command=captionsTree.yview)
    captionsTree.configure(yscroll=captionsScrollbar.set)

    if os.path.exists(PATH + '\\resource\\captions.json'):
        try:
            with open(PATH + '\\resource\\captions.json', 'r') as f:
                l = json.loads(f.read())
                if 'prefix' in l: del l['prefix']
                if 'subtext' in l: del l['subtext']
                for m in l:
                    if m == 'default':
                        continue
                    parent = captionsTree.insert('', 'end', iid=str(m), values=str(m), text=str(m))
                    captionsTree.insert(parent, 'end', iid=(f'{m}desc'), text=(f'{len(l[m])} captions related to this mood.'))
                    captionsTree.change_state((f'{m}desc'), 'disabled')

        except Exception as e:
            logging.warning(f'error in captions.json. Aborting treeview load. {e}')
            errors_list.append('The captions.json treeview couldn\'t load properly!\n')
            captionsTree.insert('', 'end', iid='NAer', text='Pack doesn\'t support caption moods, or they\'re improperly configured!')
            captionsTree.change_state('NAer', 'disabled')
    if len(captionsTree.get_children()) == 0:
        captionsTree.insert('', '0', iid='NAmi', text='No caption moods found in pack!')
        captionsTree.change_state('NAmi', 'disabled')

    if settings['toggleMoodSet'] != True:
        if len(captionsTree.get_children()) != 0:
            if UNIQUE_ID != '0' and os.path.exists(PATH + '\\resource\\'):
                try:
                    with open(f'{PATH}\\moods\\unnamed\\{UNIQUE_ID}.json', 'r') as mood:
                        mood_dict = json.loads(mood.read())
                        for c in captionsTree.get_children():
                            value = captionsTree.item(c, 'values')
                            if value[0] in mood_dict["captions"]:
                                captionsTree.change_state(value[0], 'checked')
                except Exception as e:
                    logging.warning(f'error checking caption treeview nodes. {e}')
                    errors_list.append('The captions treeview nodes couldn\'t finish their checking setup!\n')

    captionsTree.pack(side='left', fill='both', expand=1)
    captionsScrollbar.pack(side='left', fill='y')

        #Prompts frame
    promptsTree = CheckboxTreeview(moodsPromptsFrame, height=7, show='tree', name='promptsTree')
    promptsScrollbar = ttk.Scrollbar(moodsPromptsFrame, orient=VERTICAL, command=promptsTree.yview)
    promptsTree.configure(yscroll=promptsScrollbar.set)

    if os.path.exists(PATH + '\\resource\\prompt.json'):
        try:
            with open(PATH + '\\resource\\prompt.json', 'r') as f:
                l = json.loads(f.read())
                for m in l['moods']:
                    if m == 'default':
                        continue
                    parent = promptsTree.insert('', 'end', iid=str(m), values=str(m), text=str(m))
                    promptsTree.insert(parent, 'end', iid=(f'{m}desc'), text=(f'{len(l[m])} prompts related to this mood.'))
                    promptsTree.change_state((f'{m}desc'), 'disabled')

        except Exception as e:
            logging.warning(f'error in prompt.json. Aborting treeview load. {e}')
            errors_list.append('The prompt.json treeview couldn\'t load properly!\n')
            promptsTree.insert('', 'end', iid='NAer', text='Pack doesn\'t support prompt moods, or they\'re improperly configured!')
            promptsTree.change_state('NAer', 'disabled')

    if len(promptsTree.get_children()) == 0:
        promptsTree.insert('', '0', iid='NAmi', text='No prompt moods found in pack!')
        promptsTree.change_state('NAmi', 'disabled')

    if settings['toggleMoodSet'] != True:
        if len(promptsTree.get_children()) != 0:
            if UNIQUE_ID != '0' and os.path.exists(PATH + '\\resource\\'):
                try:
                    with open(f'{PATH}\\moods\\unnamed\\{UNIQUE_ID}.json', 'r') as mood:
                        mood_dict = json.loads(mood.read())
                        for c in promptsTree.get_children():
                            value = promptsTree.item(c, 'values')
                            if value[0] in mood_dict["prompts"]:
                                promptsTree.change_state(value[0], 'checked')
                except Exception as e:
                    logging.warning(f'error checking prompt treeview nodes. {e}')
                    errors_list.append('The prompt treeview nodes couldn\'t finish their checking setup!\n')


    promptsTree.pack(side='left', fill='both', expand=1)
    promptsScrollbar.pack(side='left', fill='y')


    #corruption

    moodsPathFrame = Frame(moodsFrame)

    moodsPathFrame.grid(row=0, column=1, sticky="nsew")

    corruptionLabel = '--CORRUPTION PATH--'
    moodsPathLabel = Label(moodsPathFrame, text=corruptionLabel)

    #putting too much work into a really minor display feature when the rest of the app is more functional than fancy... thats a classic
    def animateCorruption(text):
        trueLabel = '--CORRUPTION PATH--'
        try:
            err = 0
            n = 0
            for i in range(len(text)):
                if trueLabel[i] is not text[i]:
                    err += 1
                    #logging.info(f'err {err}')
            if err >= 1:
                for i in range(len(text)):
                    if trueLabel[i] is not text[i]:
                        n += i
                        break
            else:
                n += rand.randint(0, len(text)-1)
                #logging.info(f'n {n}')
            finaltext = ''
            if trueLabel[n] == text[n]:
                for i, txt in enumerate(text):
                    if i == n:
                        finaltext = finaltext + rand.choice(['!','@','#','%','^','&','*','x','X','-','_'])
                    else:
                        finaltext = finaltext + txt
                if rand.randint(1,5) == 5:
                    moodsPathLabel.configure(fg='red')
                corruptionLabel = finaltext
                moodsPathLabel.after(500, animateCorruption, corruptionLabel)
            else:
                for i, txt in enumerate(text):
                    if i == n:
                        finaltext = finaltext + trueLabel[n]
                    else:
                        finaltext = finaltext + txt
                if moodsPathLabel.cget('fg') == 'red':
                    moodsPathLabel.configure(fg='black')
                corruptionLabel = finaltext
                moodsPathLabel.after(rand.randint(5000, 10000), animateCorruption, corruptionLabel)
            moodsPathLabel.configure(text=corruptionLabel)
        except Exception as e:
            logging.warning(f'Error in the corruption text animation. Not doing the animation, since it\'s not necessary! {e}')
            errors_list.append('Something went wrong with the corruption text animation! But don\'t worry, it\'s not necessary at all... I just tried to be fancy and really fucked up!!!\n')

    pathInnerFrame = Frame(moodsPathFrame)
    pathTree = ttk.Treeview(pathInnerFrame, height=6, show='headings', columns=('level', 'moods'))
    pathScrollbar = ttk.Scrollbar(pathInnerFrame, orient=VERTICAL, command=pathTree.yview)
    pathTree.configure(yscroll=pathScrollbar.set)

    pathTree.heading('level', text='LEVEL')
    pathTree.column('level', width=40, stretch=False, anchor='center')
    pathTree.heading('moods', text='MOODS')

    corruptionList = []
    if statusCorruption:
        try:
            with open((PATH + '\\resource\\corruption.json'), 'r') as f:
                l = json.loads(f.read())
                for key in l:
                    corruptionList.append((f'{key}', str(l[key]).strip('[]')))

        except Exception as e:
            logging.warning(f'error in corruption.json. Aborting preview load. {e}')
            errors_list.append('Something is wrong with the currently loaded corruption.json file!\n')
        try:
            for level in corruptionList:
                pathTree.insert('', 'end', values=level)
        except Exception as e:
            logging.warning(f'error in loading corruption treeview. {e}')
            errors_list.append('The corruption treeview could not load properly!\n')

    moodsPathLabel.pack(pady=1, fill='x', side='top')
    pathInnerFrame.pack(fill='both', side='top')
    pathTree.pack(side='left', fill='both', expand=1)
    pathScrollbar.pack(side='left', fill='y')

    moodsFrame.grid_columnconfigure(0, weight=1, uniform='group1')
    moodsFrame.grid_columnconfigure(1, weight=1, uniform='group1')
    moodsFrame.grid_rowconfigure(0, weight=1)

    #==========={EDGEWARE++ FILE TAB STARTS HERE}==============#
    tabMaster.add(tabFile, text='File')

    #save/load
    Label(tabFile, text='Save/Load', font='Default 13', relief=GROOVE).pack(pady=2)
    importExportFrame = Frame(tabFile, borderwidth=5, relief=RAISED)
    fileTabImportButton = Button(importExportFrame, height=2, text='Import Resource Pack', command=lambda: importResource(root))
    fileTabExportButton = Button(importExportFrame, height=2, text='Export Resource Pack', command=exportResource)
    fileSaveButton = Button(tabFile, text='Save Config Settings', command=lambda: write_save(in_var_group, in_var_names, safewordVar, False))

    fileSaveButton.pack(fill='x', pady=2)
    importExportFrame.pack(fill='x', pady=2)
    fileTabImportButton.pack(padx=5, pady=5, fill='x', side='left', expand=1)
    fileTabExportButton.pack(padx=5, pady=5, fill='x', side='left', expand=1)

    #directories
    Label(tabFile, text='Directories', font='Default 13', relief=GROOVE).pack(pady=2)

    logNum = len(os.listdir(PATH + '\\logs\\')) if os.path.exists(PATH + '\\logs\\') else 0
    logsFrame = Frame(tabFile, borderwidth=5, relief=RAISED)
    lSubFrame1 = Frame(logsFrame)
    lSubFrame2 = Frame(logsFrame)
    openLogsButton = Button(lSubFrame2, text='Open Logs Folder', command=lambda: explorerView(os.path.join(PATH, 'logs')))
    clearLogsButton = Button(lSubFrame2, text='Delete All Logs', command=lambda: cleanLogs(), cursor='question_arrow')
    logStat = Label(lSubFrame1, text=f'Total Logs: {logNum}')

    clearlogsttp = CreateToolTip(clearLogsButton, 'This will delete every log (except the log currently being written).')

    def cleanLogs():
        try:
            logNum = len(os.listdir(PATH + '\\logs\\')) if os.path.exists(PATH + '\\logs\\') else 0
            if messagebox.askyesno('Confirm Delete', f'Are you sure you want to delete all logs? There are currently {logNum}.', icon='warning') == True:
                    if os.path.exists(PATH + '\\logs\\') and os.listdir(PATH + '\\logs\\'):
                        logs = os.listdir(PATH + '\\logs\\')
                        for f in logs:
                            if os.path.splitext(f)[0] == os.path.join(LOG_TIME + '-dbg'):
                                continue
                            e = os.path.splitext(f)[1].lower()
                            if e == '.txt':
                                os.remove(PATH + '\\logs\\' + f)
                        logNum = len(os.listdir(PATH + '\\logs\\')) if os.path.exists(PATH + '\\logs\\') else 0
                        logStat.configure(text=f'Total Logs: {logNum}')
        except Exception as e:
            logging.warning(f'could not clear logs. this might be an issue with attempting to delete the log currently in use. if so, ignore this prompt. {e}')

    logsFrame.pack(fill='x', pady=2)
    lSubFrame1.pack(fill='both', side='left', expand=1)
    lSubFrame2.pack(fill='both', side='left', expand=1)
    logStat.pack(fill='both', expand=1)
    openLogsButton.pack(fill='x', expand=1)
    clearLogsButton.pack(fill='x', expand=1)

    moodsFileFrame = Frame(tabFile, borderwidth=5, relief=RAISED)
    mfSubFrame1 = Frame(moodsFileFrame)
    mfSubFrame2 = Frame(moodsFileFrame)
    uniqueIDCheck = Label(mfSubFrame1, text=('Using Unique ID?: ' + ('✓' if (info_name == INFO_NAME_DEFAULT) else '✗')), fg=('green' if (info_name == INFO_NAME_DEFAULT) else 'red'))
    uniqueIDLabel = Label(mfSubFrame1, text=('Your Unique ID is: ' + (UNIQUE_ID if (info_name == INFO_NAME_DEFAULT) else info_name)))
    openMoodsButton = Button(mfSubFrame2, height=2, text='Open Moods Folder', command=lambda: explorerView(os.path.join(PATH, 'moods')), cursor='question_arrow')

    openmoodsttp = CreateToolTip(openMoodsButton, 'If your currently loaded pack has a \"info.json\" file, it can be found under the pack name in this folder.\n\n'
                                    'If it does not have this file however, EdgeWare++ will generate a Unique ID for it, so you can still save your mood settings '
                                    'without it. When using a Unique ID, your mood config file will be put into a subfolder called \"unnamed\".')

    moodsFileFrame.pack(fill='x', pady=2)
    mfSubFrame1.pack(fill='both', side='left', expand=1)
    mfSubFrame2.pack(fill='both', side='left', expand=1)
    uniqueIDCheck.pack(fill='both', expand=1)
    uniqueIDLabel.pack(fill='both', expand=1)
    openMoodsButton.pack(fill='x', expand=1)

    openResourcesButton = Button(tabFile, height=2, text='Open Resources Folder', command=lambda: explorerView(os.path.join(PATH, 'resource')))
    openResourcesButton.pack(fill='x', pady=2)

    #mode presets
    Label(tabFile, text='Mode Presets', font='Default 13', relief=GROOVE).pack(pady=2)
    presetFrame = Frame(tabFile, borderwidth=5, relief=RAISED)
    dropdownSelectFrame = Frame(presetFrame)

    style_list = [_.split('.')[0].capitalize() for _ in getPresets() if _.endswith('.cfg')]
    logging.info(f'pulled style_list={style_list}')
    styleStr = StringVar(root, style_list.pop(0))

    styleDropDown = OptionMenu(dropdownSelectFrame, styleStr, styleStr.get(),
                                *style_list, command=lambda key: changeDescriptText(key))
    def changeDescriptText(key:str):
        descriptNameLabel.configure(text=f'{key} Description')
        descriptLabel.configure(text=presetDescriptionWrap.fill(text=getDescriptText(key)))

    def updateHelperFunc(key:str):
        styleStr.set(key)
        changeDescriptText(key)

    def doSave() -> bool:
        name_ = simpledialog.askstring('Save Preset', 'Preset name')
        existed = os.path.exists(os.path.join(PATH, 'presets', f'{name_.lower()}.cfg'))
        if name_ != None and name != '':
            write_save(in_var_group, in_var_names, safewordVar, False)
            if existed:
                if messagebox.askquestion('Overwrite', 'A preset with this name already exists. Overwrite it?') == 'no':
                    return False
        if savePreset(name_) and not existed:
            style_list.insert(0, 'Default')
            style_list.append(name_.capitalize())
            styleStr.set('Default')
            styleDropDown['menu'].delete(0, 'end')
            for item in style_list:
                styleDropDown['menu'].add_command(label=item, command=lambda x=item: updateHelperFunc(x))
            styleStr.set(style_list[0])
        return True

    confirmStyleButton = Button(dropdownSelectFrame, text='Load Preset', command=lambda: applyPreset(styleStr.get()))
    saveStyleButton = Button(dropdownSelectFrame, text='Save Preset', command=doSave)

    presetDescriptFrame = Frame(presetFrame, borderwidth=2, relief=GROOVE)

    descriptNameLabel = Label(presetDescriptFrame, text='Default Description', font='Default 15')
    presetDescriptionWrap = textwrap.TextWrapper(width=100, max_lines=5)
    descriptLabel = Label(presetDescriptFrame, text=presetDescriptionWrap.fill(text=f'Default Text Here'), relief=GROOVE)
    changeDescriptText('Default')

    dropdownSelectFrame.pack(side='left', fill='x', padx=6)
    styleDropDown.pack(fill='x', expand=1)
    confirmStyleButton.pack(fill='both', expand=1)
    Label(dropdownSelectFrame).pack(fill='both', expand=1)
    Label(dropdownSelectFrame).pack(fill='both', expand=1)
    saveStyleButton.pack(fill='both', expand=1)

    presetDescriptFrame.pack(side='right', fill='both', expand=1)
    descriptNameLabel.pack(fill='y', pady=4)
    descriptLabel.pack(fill='both', expand=1)

    presetFrame.pack(fill='both', pady=2)

    #==========={IN HERE IS ADVANCED TAB ITEM INITS}===========#
    tabMaster.add(tabAdvanced, text='Advanced/Troubleshooting')
    itemList = []
    for settingName in settings:
        itemList.append(settingName)
    dropdownObj = StringVar(root, itemList[0])
    textObj = StringVar(root, settings[dropdownObj.get()])
    advPanel = Frame(tabAdvanced)
    textInput = Entry(advPanel)
    textInput.insert(1, textObj.get())
    expectedLabel = Label(tabAdvanced, text=f'Expected value: {defaultSettings[dropdownObj.get()]}')
    dropdownMenu = OptionMenu(advPanel, dropdownObj, *itemList, command=lambda a: updateText([textInput, expectedLabel], settings[a], a))
    dropdownMenu.configure(width=10)
    applyButton = Button(advPanel, text='Apply', command= lambda: assignJSON(dropdownObj.get(), textInput.get()))
    Label(tabAdvanced, text='Debug Config Edit', font='Default 13', relief=GROOVE).pack(pady=2)
    Label(tabAdvanced, text='Be careful messing with some of these; improper configuring can cause\nproblems when running, or potentially cause unintended damage to files.').pack()
    advPanel.pack(fill='x', padx=2)
    dropdownMenu.pack(padx=2, side='left')
    textInput.pack(padx=2, fill='x', expand=1, side='left')
    applyButton.pack(padx=2, fill='x', side='right')
    expectedLabel.pack()
    #==========={HERE ENDS  ADVANCED TAB ITEM INITS}===========#
    Label(tabAdvanced, text='Troubleshooting', font='Default 13', relief=GROOVE).pack(pady=2)
    troubleshootingHostFrame = Frame(tabAdvanced, borderwidth=5, relief=RAISED)
    troubleshootingFrame1 = Frame(troubleshootingHostFrame)
    troubleshootingFrame2 = Frame(troubleshootingHostFrame)

    toggleLanczos = Checkbutton(troubleshootingFrame1, text='Use Lanczos instead of Antialias', variable=antiOrLanczosVar, cursor='question_arrow')
    toggleInternetSetting = Checkbutton(troubleshootingFrame2, text='Disable Connection to Github', variable=toggleInternetVar, cursor='question_arrow')
    toggleHibernateSkip = Checkbutton(troubleshootingFrame1, text='Toggle Tray Hibernate Skip', variable=toggleHibSkipVar, cursor='question_arrow')
    toggleMoodSettings = Checkbutton(troubleshootingFrame2, text='Toggle Mood Settings', variable=toggleMoodSetVar, cursor='question_arrow')

    troubleshootingHostFrame.pack(fill='x')
    troubleshootingFrame1.pack(fill='both', side='left', expand=1)
    troubleshootingFrame2.pack(fill='both', side='left', expand=1)
    toggleLanczos.pack(fill='x', side='top')
    toggleInternetSetting.pack(fill='x', side='top')
    toggleHibernateSkip.pack(fill='x', side='top')
    toggleMoodSettings.pack(fill='x', side='top')

    Label(tabAdvanced, text='Playback Options', font='Default 13', relief=GROOVE).pack(pady=2)

    troubleshootingHostFrame2 = Frame(tabAdvanced, borderwidth=5, relief=RAISED)
    troubleshootingFrame3 = Frame(troubleshootingHostFrame2)
    troubleshootingFrame4 = Frame(troubleshootingHostFrame2)

    offsetSlider = Scale(troubleshootingFrame3, label='Pump-Scare Offset', orient='horizontal', variable=pumpScareOffsetVar, to=50, width=10)
    scareOffsetButton = Button(troubleshootingFrame3, text='Manual offset...', command=lambda: assign(pumpScareOffsetVar, simpledialog.askinteger('Offset for Pump-Scare Audio (seconds)', prompt='[0-50]: ')), cursor='question_arrow')

    toggleVLC = Checkbutton(troubleshootingFrame4, text='Use VLC to play videos', variable=vlcModeVar, cursor='question_arrow')
    VLCNotice = Label(troubleshootingFrame4, text='NOTE: Installing VLC is required for this option!', width=10)
    installVLCButton = Button(troubleshootingFrame4, text='Go to VLC\'s website', command=lambda: webbrowser.open('https://www.videolan.org/vlc/'))

    troubleshootingHostFrame2.pack(fill='x')
    troubleshootingFrame3.pack(fill='both', side='left', expand=1)
    offsetSlider.pack(fill='x', side='top', padx=2)
    scareOffsetButton.pack(fill='x', side='top', padx=2)
    troubleshootingFrame4.pack(fill='both', side='left', expand=1)
    toggleVLC.pack(fill='both', side='top', expand=1, padx=2)
    VLCNotice.pack(fill='both', side='top', expand=1, padx=2)
    installVLCButton.pack(fill='both', side='top', padx=2)

    lanczosttp = CreateToolTip(toggleLanczos, 'Are popups and the startup image inexplicably not showing up for you? Try this setting.\n\n'
                                'I am not entirely sure why, but the Lanczos image resizing algorithm sometimes works for people when the antialiasing one does not.\n\n'
                                'This is not something changed in EdgeWare++, so if normal EdgeWare also didn\'t work for you, this might fix it?\n\n'
                                'Enabled by default as i\'ve encountered way more people where antialiasing doesn\'t work than people who have it work fine.')
    internetttp = CreateToolTip(toggleInternetSetting, 'In some cases, having a slow internet connection can cause the config window to delay opening for a long time.\n\n'
                                    'EdgeWare connects to Github just to check if there\'s a new update, but sometimes even this can take a while.\n\n'
                                    'If you have noticed this, try enabling this setting- it will disable all connections to Github on future launches.')
    hibernateskipttp = CreateToolTip(toggleHibernateSkip, 'Want to test out how hibernate mode works with your current settings, and hate waiting for the minimum time? Me too!\n\n'
                                    'This adds a feature in the tray that allows you to skip to the start of hibernate.')
    moodtogglettp = CreateToolTip(toggleMoodSettings, 'If your pack does not have a \'info.json\' file with a valid pack name, it will generate a mood setting file based on a unique identifier.\n\n'
                                    'This unique identifier is created by taking a bunch of values from your pack and putting them all together, including the amount of images,'
                                    ' audio, videos, and whether or not the pack has certain features.\n\n'
                                    'Because of this, if you are rapidly editing your pack and entering the config window, you could potentially create a bunch of mood settings'
                                    ' files in //moods//unnamed, all pointing to what is essentially the same pack. This will reset your mood settings every time, too.\n\n'
                                    'In situations like this, I recommend creating a info file with a pack name, but if you\'re unsure how to do that or just don\'t want to'
                                    ' deal with all this mood business, you can disable the mood saving feature here.')
    psoffsetttp = CreateToolTip(scareOffsetButton, 'Pump-Scare is a hibernate mode type where an image \"jump-scares\" you by appearing suddenly then disappears seconds later. However, '
                                    'sometimes audio files are large enough that the audio won\'t even have a chance to load in before the image disappears.\n\nThis setting allows you to let the audio '
                                    'start playing earlier so it has time to load properly. Maybe you also have an audio file that builds up to a horny crecendo and want the image to appear at that point? '
                                    'You could get creative with this!')
    vlcttp = CreateToolTip(toggleVLC, 'Going to get a bit technical here:\n\nBy default, EdgeWare loads videos by taking the source file, turning every frame into an image, and then playing the images in '
                                    'sequence at the specified framerate. The upside to this is it requires no additional dependencies, but it has multiple downsides. Firstly, it\'s very slow: you may have '
                                    'noticed that videos take a while to load and also cause excessive memory usage. Secondly, there is a bug that can cause certain users to not have audio while playing videos.'
                                    '\n\nSo here\'s an alternative: by installing VLC to your computer and using this option, you can make videos play much faster and use less memory by using libvlc. '
                                    'If videos were silent for you this will hopefully fix that as well.\n\nPlease note that this feature has the potential to break in the future as VLC is a program independent '
                                    'from EdgeWare. For posterity\'s sake, the current version of VLC as of writing this tooltip is 3.0.20.')

    Label(tabAdvanced, text='Errors', font='Default 13', relief=GROOVE).pack(pady=2)
    errorsFrame = Frame(tabAdvanced, borderwidth=5, relief=GROOVE)
    errorsFrame.pack(fill='x')
    Label(errorsFrame, text='These errors have been found while starting up EdgeWare Config, but might also affect running '
            'EdgeWare itself.\n Likewise, there might be bugs that don\'t show up here but prevent EdgeWare itself from running '
            'properly.\n Check the logs subfolder for more details.').pack()
    if errors_list:
        errorsText = Text(errorsFrame, height=10, fg='red')
        errorsText.pack(pady=2, padx=2, fill='x')
        for i in errors_list:
            errorsText.insert(END, i)
    else:
        errorsText = Text(errorsFrame, height=10, fg='green')
        errorsText.pack(pady=2, padx=2, fill='x')
        errorsText.insert(END, 'No errors detected! (´◡`)')

    tabMaster.add(tabInfo, text='About')
    #==========={IN HERE IS ABOUT TAB ITEM INITS}===========#
    tabInfoExpound.add(tab_annoyance, text='Annoyance')
    Label(tab_annoyance, text=ANNOYANCE_TEXT, anchor='nw', wraplength=460).pack()
    tabInfoExpound.add(tab_drive, text='Hard Drive')
    Label(tab_drive, text=DRIVE_TEXT, anchor='nw', wraplength=460).pack()
    #tabInfoExpound.add(tab_export, text='Exporting')
    tabInfoExpound.add(tab_wallpaper, text='Wallpaper')
    Label(tab_wallpaper, text=WALLPAPER_TEXT, anchor='nw', wraplength=460).pack()
    tabInfoExpound.add(tab_launch, text='Startup')
    Label(tab_launch, text=STARTUP_TEXT, anchor='nw', wraplength=460).pack()
    tabInfoExpound.add(tab_hibernate, text='Hibernate')
    Label(tab_hibernate, text=HIBERNATE_TEXT, anchor='nw', wraplength=460).pack()
    tabInfoExpound.add(tab_hibernateType, text='Hibernate Types')
    Label(tab_hibernateType, text=HIBERNATE_TYPE_TEXT, anchor='nw', wraplength=460).pack()
    tabInfoExpound.add(tab_corruption, text='Corruption')
    Label(tab_corruption, text=CORRUPTION_TEXT, anchor='nw', wraplength=460).pack()
    tabInfoExpound.add(tab_advanced, text='Advanced')
    Label(tab_advanced, text=ADVANCED_TEXT, anchor='nw', wraplength=460).pack()
    tabInfoExpound.add(tab_thanksAndAbout, text='Thanks & About')
    Label(tab_thanksAndAbout, text=THANK_AND_ABOUT_TEXT, anchor='nw', wraplength=460).pack()
    tabInfoExpound.add(tab_plusPlus, text='EdgeWare++')
    Label(tab_plusPlus, text=PLUSPLUS_TEXT, anchor='nw', wraplength=460).pack()
    tabInfoExpound.add(tab_packInfo, text='Pack Info')
    Label(tab_packInfo, text=PACKINFO_TEXT, anchor='nw', wraplength=460).pack()
    tabInfoExpound.add(tab_file, text='File')
    Label(tab_file, text=FILE_TEXT, anchor='nw', wraplength=460).pack()
    #==========={HERE ENDS  ABOUT TAB ITEM INITS}===========#

    toggleAssociateSettings(fillVar.get(), fill_group)
    toggleAssociateSettings(replaceVar.get(), replace_group)
    toggleAssociateSettings(rotateWallpaperVar.get(), wallpaper_group)
    toggleAssociateSettings(timeoutPopupsVar.get(), timeout_group)
    toggleAssociateSettings(mitosisVar.get(), mitosis_cGroup)
    toggleAssociateSettings(not mitosisVar.get(), mitosis_group)
    toggleAssociateSettings_manual(downloadEnabledVar.get(), download_group, 'white', 'gray25')
    toggleAssociateSettings(timerVar.get(), timer_group)
    toggleAssociateSettings(lkToggle.get(), lowkey_group)
    toggleAssociateSettings(denialMode.get(), denial_group)
    toggleAssociateSettings(maxAToggleVar.get(), maxAudio_group)
    toggleAssociateSettings(maxVToggleVar.get(), maxVideo_group)
    toggleAssociateSettings(popupSublim.get(), subliminals_group)
    hibernateHelper(hibernateTypeVar.get())

    tabMaster.pack(expand=1, fill='both')
    tabInfoExpound.pack(expand=1, fill='both')
    resourceFrame.pack(fill='x')
    importResourcesButton.pack(fill='x', side='left', expand=1)
    exportResourcesButton.pack(fill='x', side='left', expand=1)
    saveExitButton.pack(fill='both',expand=1)


    timeObjPath = os.path.join(PATH, 'hid_time.dat')
    HIDDEN_ATTR = 0x02
    SHOWN_ATTR  = 0x08
    ctypes.windll.kernel32.SetFileAttributesW(timeObjPath, SHOWN_ATTR)
    if os.path.exists(timeObjPath):
        with open(timeObjPath, 'r') as file:
            time_ = int(file.readline()) / 60
            if not time_ == int(settings['timerSetupTime']):
                timerToggle.configure(state=DISABLED)
                for item in timer_group:
                    item.configure(state=DISABLED)
    ctypes.windll.kernel32.SetFileAttributesW(timeObjPath, HIDDEN_ATTR)


    #first time alert popup
    #if not settings['is_configed'] == 1:
    #    messagebox.showinfo('First Config', 'Config has not been run before. All settings are defaulted to frequency of 0 except for popups.\n[This alert will only appear on the first run of config]')
    #version alert, if core web version (0.0.0) is different from the github configdefault, alerts user that update is available
    #   if user is a bugfix patch behind, the _X at the end of the 0.0.0, they will not be alerted
    #   the version will still be red to draw attention to it
    if local_version.split('_')[0] != webv.split('_')[0] and not (local_version.endswith('DEV') or settings['toggleInternet']):
        messagebox.showwarning('Update Available', 'Main local version and web version are not the same.\nPlease visit the Github and download the newer files.')
    root.after(10000, animateCorruption, corruptionLabel)
    root.mainloop()

def explorerView(url):
    try:
        subprocess.Popen(f'explorer "{url}"')
    except Exception as e:
        logging.warning(f'failed to open explorer view\n\tReason: {e}')
        messagebox.showerror('Explorer Error', 'Failed to open explorer view.')


def pickZip() -> str:
    #selecting zip
    for dirListObject in os.listdir(f'{PATH}\\'):
        try:
            if dirListObject.split('.')[-1].lower() == 'zip':
                return dirListObject.split('.')[0]
        except:
            print('{} is not a zip file.'.format(dirListObject))
    return '[No Zip Found]'

def exportResource() -> bool:
    try:
        logging.info('starting zip export...')
        saveLocation = filedialog.asksaveasfile('w', defaultextension ='.zip')
        with zipfile.ZipFile(saveLocation.name, 'w', compression=zipfile.ZIP_DEFLATED) as zip:
            beyondRoot = False
            for root, dirs, files in os.walk(os.path.join(PATH, 'resource')):
                for file in files:
                    logging.info(f'write {file}')
                    if beyondRoot:
                        zip.write(os.path.join(root, file), root.split('\\')[-1] + f'\\{file}')
                    else:
                        zip.write(os.path.join(root, file), f'\\{file}')
                for dir in dirs:
                    logging.info(f'make dir {dir}')
                    zip.write(os.path.join(root, dir), f'\\{dir}\\')
                beyondRoot = True
        return True
    except Exception as e:
        logging.fatal(f'failed to export zip\n\tReason: {e}')
        messagebox.showerror('Write Error', 'Failed to export resource to zip file.')
        return False

def importResource(parent:Tk) -> bool:
    try:
        openLocation = filedialog.askopenfile('r', defaultextension ='.zip')
        if openLocation == None:
            return False
        if os.path.exists(f'{PATH}resource\\'):
            resp = confirmBox(parent, 'Confirm', 'Current resource folder will be deleted and overwritten. Is this okay?'
                                '\nNOTE: This might take a while when importing larger packs, please be patient!')
            if not resp:
                logging.info('exited import resource overwrite')
                return False
            shutil.rmtree(f'{PATH}resource\\')
            logging.info('removed old resource folder')
        with zipfile.ZipFile(openLocation.name, 'r') as zip:
            zip.extractall(f'{PATH}resource\\')
            logging.info('extracted all from zip')
        messagebox.showinfo('Done', 'Resource importing completed.')
        refresh()
        return True
    except Exception as e:
        messagebox.showerror('Read Error', f'Failed to import resources from file.\n[{e}]')
        return False

def confirmBox(parent:Tk, btitle:str, message:str) -> bool:
    allow = False
    root = Toplevel(parent)
    def complete(state:bool) -> bool:
        nonlocal allow
        allow=state
        root.quit()
    root.geometry('300x150')
    root.resizable(False, False)
    root.wm_attributes('-toolwindow', 1)
    root.focus_force()
    root.title(btitle)
    Label(root, text=message, wraplength=292).pack(fill='x')
    #Label(root).pack()
    Button(root, text='Continue', command=lambda: complete(True)).pack()
    Button(root, text='Cancel', command=lambda: complete(False)).pack()
    root.mainloop()
    try:
        root.destroy()
    except:
        False
    return allow

#helper funcs for lambdas =======================================================
#def checkInfo():

def write_save(varList:list[StringVar | IntVar | BooleanVar], nameList:list[str], passVar:str, exitAtEnd:bool):
    if int(varList[nameList.index('safeMode')].get()) == 1 and exitAtEnd:
        if safeCheck(varList, nameList) == False:
            return
    logging.info('starting config save write...')
    temp = json.loads('{}')
    settings['wallpaperDat'] = str(settings['wallpaperDat'])
    settings['wallpaperDat'] = f'{settings["wallpaperDat"]}'
    settings['is_configed'] = 1

    toggleStartupBat(varList[nameList.index('start_on_logon')].get())

    SHOWN_ATTR = 0x08
    HIDDEN_ATTR = 0x02
    hashObjPath = os.path.join(PATH, 'pass.hash')
    timeObjPath = os.path.join(PATH, 'hid_time.dat')

    if int(varList[nameList.index('timerMode')].get()) == 1:
        toggleStartupBat(True)

        #revealing hidden files
        ctypes.windll.kernel32.SetFileAttributesW(hashObjPath, SHOWN_ATTR)
        ctypes.windll.kernel32.SetFileAttributesW(timeObjPath, SHOWN_ATTR)
        logging.info('revealed hashed pass and time files')

        with open(hashObjPath, 'w') as passFile, open(timeObjPath, 'w') as timeFile:
            logging.info('attempting file writes...')
            passFile.write(hashlib.sha256(passVar.get().encode(encoding='ascii',errors='ignore')).hexdigest())
            timeFile.write(str(varList[nameList.index('timerSetupTime')].get()*60))
            logging.info('wrote files.')

        #hiding hash file with saved password hash for panic and time data
        ctypes.windll.kernel32.SetFileAttributesW(hashObjPath, HIDDEN_ATTR)
        ctypes.windll.kernel32.SetFileAttributesW(timeObjPath, HIDDEN_ATTR)
        logging.info('hid hashed pass and time files')
    else:
        try:
            if not varList[nameList.index('start_on_logon')].get():
                toggleStartupBat(False)
            ctypes.windll.kernel32.SetFileAttributesW(hashObjPath, SHOWN_ATTR)
            ctypes.windll.kernel32.SetFileAttributesW(timeObjPath, SHOWN_ATTR)
            os.remove(hashObjPath)
            os.remove(timeObjPath)
            logging.info('removed pass/time files.')
        except Exception as e:
            errText = str(e).lower().replace(os.environ['USERPROFILE'].lower().replace('\\', '\\\\'), '[USERNAME_REDACTED]')
            logging.warning(f'failed timer file modifying\n\tReason: {errText}')
            pass

    for name in varNames:
        try:
            p = varList[nameList.index(name)].get()
            #standard named variables
            temp[name] = p if type(p) is int or type(p) is str else (1 if type(p) is bool and p else 0)
        except:
            #nonstandard named variables
            try:
                temp[name] = int(settings[name])
            except:
                temp[name] = settings[name]

    with open(f'{PATH}config.cfg', 'w') as file:
        file.write(json.dumps(temp))
        logging.info(f'wrote config file: {json.dumps(temp)}')

    if int(varList[nameList.index('runOnSaveQuit')].get()) == 1 and exitAtEnd:
        os.startfile('start.pyw')

    if exitAtEnd:
        logging.info('exiting config')
        os.kill(os.getpid(), 9)
    else:
        messagebox.showinfo('Success!', 'Settings saved successfully!')

#i'm sure there's a better way to do this but I also have a habit of taking the easy way out
def safeCheck(varList:list[StringVar | IntVar | BooleanVar], nameList:list[str]) -> bool:
    dangersList = []
    numDangers = 0
    logging.info('running through danger list...')
    if int(varList[nameList.index('replace')].get()) == 1:
        logging.info('extreme dangers found.')
        dangersList.append('\n\nExtreme:')
        if int(varList[nameList.index('replace')].get()) == 1:
            numDangers += 1
            dangersList.append('\n•Replace Images is enabled! THIS WILL DELETE FILES ON YOUR COMPUTER! Only enable this willingly and cautiously! Read the documentation in the \"About\" tab!')
    if int(varList[nameList.index('start_on_logon')].get()) == 1 or int(varList[nameList.index('fill')].get()) == 1:
        logging.info('major dangers found.')
        dangersList.append('\n\nMajor:')
        if int(varList[nameList.index('start_on_logon')].get()) == 1:
            numDangers += 1
            dangersList.append('\n•Launch on Startup is enabled! This will run EdgeWare when you start your computer!')
        if int(varList[nameList.index('fill')].get()) == 1:
            numDangers += 1
            dangersList.append('\n•Fill Drive is enabled! Edgeware will place images all over your computer! Even if you want this, make sure the protected directories are right!')
    if int(varList[nameList.index('timerMode')].get()) == 1 or int(varList[nameList.index('showDiscord')].get()) == 1 or (int(varList[nameList.index('hibernateMode')].get()) == 1 and (int(varList[nameList.index('hibernateMin')].get()) < 30 or int(varList[nameList.index('hibernateMax')].get()) < 30)):
        logging.info('medium dangers found.')
        dangersList.append('\n\nMedium:')
        if int(varList[nameList.index('timerMode')].get()) == 1:
            numDangers += 1
            dangersList.append('\n•Timer mode is enabled! Panic cannot be used until a specific time! Make sure you know your Safeword!')
        if int(varList[nameList.index('hibernateMode')].get()) == 1 and (int(varList[nameList.index('hibernateMin')].get()) < 30 or int(varList[nameList.index('hibernateMax')].get()) < 30):
            numDangers += 1
            dangersList.append('\n•You are running hibernate mode with a short cooldown! You might experience lag if a bunch of hibernate modes overlap!')
        if int(varList[nameList.index('showDiscord')].get()) == 1:
            numDangers += 1
            dangersList.append('\n•Show on Discord is enabled! This could lead to potential embarassment if you\'re on your main account!')
    if int(varList[nameList.index('panicDisabled')].get()) == 1 or int(varList[nameList.index('runOnSaveQuit')].get()) == 1:
        logging.info('minor dangers found.')
        dangersList.append('\n\nMinor:')
        if int(varList[nameList.index('panicDisabled')].get()) == 1:
            numDangers += 1
            dangersList.append('\n•Panic Hotkey is disabled! If you want to easily close EdgeWare, read the tooltip in the Annoyance tab for other ways to panic!')
        if int(varList[nameList.index('runOnSaveQuit')].get()) == 1:
            numDangers += 1
            dangersList.append('\n•EdgeWare will run on Save & Exit (AKA: when you hit Yes!)')
    dangers = ' '.join(dangersList)
    if numDangers > 0:
        logging.info('safe mode intercepted save! asking user...')
        if messagebox.askyesno('Dangerous Setting Detected!', f'There are {numDangers} potentially dangerous settings detected! Do you want to save these settings anyways? {dangers}', icon='warning') == False:
            logging.info('user cancelled save.')
            return False


def validateBooru(name:str) -> bool:
    return requests.get(BOORU_URL.replace(BOORU_FLAG, name)).status_code == 200

def getLiveVersion(url:str, id:int) -> str:
    test = settings['toggleInternet']
    if settings['toggleInternet'] == 0 or settings['toggleInternet'] == '0':
        try:
            logging.info('fetching github version')
            with open(urllib.request.urlretrieve(url)[0], 'r') as liveDCfg:
                return(liveDCfg.read().split('\n')[1].split(',')[id])
        except Exception as e:
            logging.warning('failed to fetch github version.\n\tReason: {e}')
            return 'Could not check version.'
    else:
        logging.info(f'user has connection to github disabled. Version will not be checked. {test}')
        return 'Version check disabled!'

def addList(tkListObj:Listbox, key:str, title:str, text:str):
    name = simpledialog.askstring(title, text)
    if name != '' and name != None:
       settings[key] = f'{settings[key]}>{name}'
       tkListObj.insert(2, name)

def removeList(tkListObj:Listbox, key:str, title:str, text:str):
    index = int(tkListObj.curselection()[0])
    itemName = tkListObj.get(index)
    if index > 0:
        settings[key] = settings[key].replace(f'>{itemName}', '')
        tkListObj.delete(tkListObj.curselection())
    else:
        messagebox.showwarning(title, text)

def removeList_(tkListObj:Listbox, key:str, title:str, text:str):
    index = int(tkListObj.curselection()[0])
    itemName = tkListObj.get(index)
    print(settings[key])
    print(itemName)
    print(len(settings[key].split('>')))
    if len(settings[key].split('>')) > 1:
        if index > 0:
            settings[key] = settings[key].replace(f'>{itemName}', '')
        else:
            settings[key] = settings[key].replace(f'{itemName}>', '')
        tkListObj.delete(tkListObj.curselection())
    else:
        messagebox.showwarning(title, text)

def resetList(tkListObj:Listbox, key:str, default):
    try:
        tkListObj.delete(0,999)
    except Exception as e:
        print(e)
    settings[key] = default
    for setting in settings[key].split('>'):
        tkListObj.insert(1,setting)

def addWallpaper(tkListObj:Listbox):
    file = filedialog.askopenfile('r', filetypes=[
        ('image file', '.jpg .jpeg .png')
    ])
    if not isinstance(file, type(None)):
        lname =  simpledialog.askstring('Wallpaper Name','Wallpaper Label\n(Name displayed in list)')
        if not isinstance(lname, type(None)):
            print(file.name.split('/')[-1])
            settings['wallpaperDat'][lname] = file.name.split('/')[-1]
            tkListObj.insert(1, lname)

def removeWallpaper(tkListObj):
    index = int(tkListObj.curselection()[0])
    itemName = tkListObj.get(index)
    if index > 0:
        del settings['wallpaperDat'][itemName]
        tkListObj.delete(tkListObj.curselection())
    else:
        messagebox.showwarning('Remove Default', 'You cannot remove the default wallpaper.')

def autoImportWallpapers(tkListObj:Listbox):
    allow_ = confirmBox(tkListObj, 'Confirm', 'Current list will be cleared before new list is imported from the /resource folder. Is that okay?')
    if allow_:
        #clear list
        while True:
            try:
                del settings['wallpaperDat'][tkListObj.get(1)]
                tkListObj.delete(1)
            except:
                break
        for file in os.listdir(os.path.join(PATH, 'resource')):
            if (file.endswith('.png') or file.endswith('.jpg') or file.endswith('.jpeg')) and file != 'wallpaper.png':
                name_ = file.split('.')[0]
                tkListObj.insert(1, name_)
                settings['wallpaperDat'][name_] = file

def updateMax(obj, value:int):
    obj.configure(to=int(value))

def updateText(objList:Entry or Label, var:str, var_Label:str):
    try:
        for obj in objList:
            if isinstance(obj, Entry):
                obj.delete(0, 9999)
                obj.insert(1, var)
            elif isinstance(obj, Label):
                obj.configure(text=f'Expected value: {defaultSettings[var_Label]}')
    except:
        print('idk what would cause this but just in case uwu')

def refresh():
    os.startfile('config.pyw')
    os.kill(os.getpid(), 9)

def assignJSON(key:str, var:int or str):
    settings[key] = var
    with open(f'{PATH}config.cfg', 'w') as f:
        f.write(json.dumps(settings))

def toggleAssociateSettings(ownerState:bool, objList:list):
    toggleAssociateSettings_manual(ownerState, objList, 'SystemButtonFace', 'gray35')

def toggleAssociateSettings_manual(ownerState:bool, objList:list, colorOn:int, colorOff:int):
    logging.info(f'toggling state of {objList} to {ownerState}')
    for tkObject in objList:
        if not tkObject.winfo_class() == 'Frame' and not tkObject.winfo_class() == 'Label':
            tkObject.configure(state=('normal' if ownerState else 'disabled'))
        tkObject.configure(bg=(colorOn if ownerState else colorOff))

def shortcut_script(pth_str:str, startup_path:str, title:str):
    #strings for batch script to write vbs script to create shortcut on desktop
    #stupid and confusing? yes. the only way i could find to do this? also yes.
    print(pth_str)
    return ['@echo off\n'
            'set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"\n',
            'echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%\n',
            f'echo sLinkFile = "{startup_path}\\{title}.lnk" >> %SCRIPT%\n',
            'echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%\n',
            f'echo oLink.WorkingDirectory = "{pth_str}\\" >> %SCRIPT%\n',
            f'echo oLink.TargetPath = "{pth_str}\\start.pyw" >> %SCRIPT%\n',
            'echo oLink.Save >> %SCRIPT%\n',
            'cscript /nologo %SCRIPT%\n',
            'del %SCRIPT%']

#uses the above script to create a shortcut on desktop with given specs
def make_shortcut(tList:list) -> bool:
    with open(PATH + '\\tmp.bat', 'w') as bat:
        bat.writelines(shortcut_script(tList[0], tList[1], tList[2])) #write built shortcut script text to temporary batch file
    try:
        logging.info(f'making shortcut to {tList[2]}')
        subprocess.call(PATH + '\\tmp.bat')
        os.remove(PATH + '\\tmp.bat')
        return True
    except Exception as e:
        print('failed')
        logging.warning(f'failed to call or remove temp batch file for making shortcuts\n\tReason: {e}')
        return False

def toggleStartupBat(state:bool):
    try:
        startup_path = os.path.expanduser('~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\')
        logging.info(f'trying to toggle startup bat to {state}')
        if state:
            make_shortcut([PATH, startup_path, 'edgeware']) #i scream at my previous and current incompetence and poor programming
            logging.info('toggled startup run on.')
        else:
            os.remove(os.path.join(startup_path, 'edgeware.lnk'))
            logging.info('toggled startup run off.')
    except Exception as e:
        errText = str(e).lower().replace(os.environ['USERPROFILE'].lower().replace('\\', '\\\\'), '[USERNAME_REDACTED]')
        logging.warning(f'failed to toggle startup bat.\n\tReason: {errText}')
        print('uwu')

def assign(obj:StringVar or IntVar or BooleanVar, var:str or int or bool):
    try:
        obj.set(var)
    except:
        ''
        #no assignment

def getKeyboardInput(button:Button, var:StringVar):
    child = Tk()
    child.resizable(False,False)
    child.title('Key Listener')
    child.wm_attributes('-topmost', 1)
    child.geometry('250x250')
    child.focus_force()
    Label(child, text='Press any key or exit').pack(expand=1, fill='both')
    child.bind('<KeyPress>', lambda key: assignKey(child, button, var, key))
    child.mainloop()

def assignKey(parent:Tk, button:Button, var:StringVar, key):
    button.configure(text=f'Set Panic Button\n<{key.keysym}>')
    var.set(str(key.keysym))
    parent.destroy()


def getPresets() -> list[str]:
    presetFolderPath = os.path.join(PATH, 'presets')
    if not os.path.exists(presetFolderPath):
        os.mkdir(presetFolderPath)
    return os.listdir(presetFolderPath) if len(os.listdir(presetFolderPath)) > 0 else None

def applyPreset(name:str):
    try:
        os.remove(os.path.join(PATH, 'config.cfg'))
        shutil.copyfile(os.path.join(PATH, 'presets', f'{name}.cfg'), os.path.join(PATH, 'config.cfg'))
        refresh()
    except Exception as e:
        messagebox.showerror('Error', 'Failed to load preset.\n\n{e}')

def savePreset(name:str) -> bool:
    try:
        if name is not None and name != '':
            shutil.copyfile(os.path.join(PATH, 'config.cfg'), os.path.join(PATH, 'presets', f'{name.lower()}.cfg'))
            with open(os.path.join(PATH, 'presets', f'{name.lower()}.cfg'), 'rw') as file:
                file_json = json.loads(file.readline())
                file_json['drivePath'] = 'C:/Users/'
                file.write(json.dumps(file_json))
            return True
        return False
    except:
        return True

def getDescriptText(name:str) -> str:
    try:
        with open(os.path.join(PATH, 'presets', f'{name}.txt'), 'r') as file:
            text = ''
            for line in file.readlines():
                text += line
            return text
    except:
        return 'This preset has no description file.'

def updateMoods(type:str, id:str, check:bool):
    try:
        if settings['toggleMoodSet'] != True:
            if UNIQUE_ID != '0' and os.path.exists(PATH + '\\resource\\'):
                with open(f'{PATH}\\moods\\unnamed\\{UNIQUE_ID}.json', 'r') as mood:
                    mood_dict = json.loads(mood.read())
                    if check:
                        if type == 'mediaTree':
                            #logging.info('mediaTree')
                            if id not in mood_dict["media"]:
                                mood_dict["media"].append(id)
                        if type == 'captionsTree':
                            #logging.info('captionsTree')
                            if id not in mood_dict["captions"]:
                                mood_dict["captions"].append(id)
                        if type == 'promptsTree':
                            #logging.info('promptsTree')
                            if id not in mood_dict["prompts"]:
                                mood_dict["prompts"].append(id)
                    else:
                        if type == 'mediaTree':
                            #logging.info('mediaTree uncheck')
                            if id in mood_dict["media"]:
                                mood_dict["media"].remove(id)
                        if type == 'captionsTree':
                            #logging.info('captionsTree uncheck')
                            if id in mood_dict["captions"]:
                                mood_dict["captions"].remove(id)
                        if type == 'promptsTree':
                            #logging.info('promptsTree uncheck')
                            if id in mood_dict["prompts"]:
                                mood_dict["prompts"].remove(id)
                with open(f'{PATH}\\moods\\unnamed\\{UNIQUE_ID}.json', 'w') as mood:
                    #logging.info(mood_dict)
                    mood.write(json.dumps(mood_dict))
    except Exception as e:
        logging.warning(f'error updating mood files. {e}')


if __name__ == '__main__':
    try:
        show_window()
    except Exception as e:
        logging.fatal(f'Config encountered fatal error:\n{e}')
        messagebox.showerror('Could not start', f'Could not start config.\n[{e}]')
