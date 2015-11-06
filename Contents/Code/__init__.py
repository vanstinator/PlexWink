import os
import time
from time import sleep
import websocket
from phue import Bridge
import sys
import requests
import json
import re
import threading

import xml.etree.ElementTree as ElementTree
	
####################################################################################################

PREFIX       = "/video/Hello_Hue"
NAME         = 'HelloHue'
ART          = 'background.png'
ICON         = 'hellohue.png'
PREFS_ICON   = 'hellohue.png'
PROFILE_ICON = 'hellohue.png'
alive = True

####################################################################################################

####################################################################################################
# Start function
####################################################################################################
def Start():

	
	Log('Starting HelloHue .. Hello World!')
	HTTP.CacheTime = 0
	ObjectContainer.title1 = NAME
	ObjectContainer.art = R(ART)
	#ObjectContainer.replace_parent = True
	ValidatePrefs()

####################################################################################################
# Main menu
####################################################################################################
@handler(PREFIX, NAME, art=R(ART), thumb=R(ICON))
def MainMenu(header=NAME, message="Hello"):

	oc = ObjectContainer()
	if message is not "Hello":
		oc.header = header
		oc.message = message
	#oc.add(LaunchPrismatikObject())

	if "thread_websocket" in str(threading.enumerate()):
		oc.add(DisableHelloHue())

	if not "thread_websocket" in str(threading.enumerate()):
		oc.add(EnableHelloHue())

	# Add item for setting preferences	
	oc.add(PrefsObject(title = L('Preferences'), thumb = R(PREFS_ICON)))

	return oc

####################################################################################################
# Returns object to Launch the Prismatik app
####################################################################################################
def EnableHelloHue():
	return PopupDirectoryObject(
		key   = Callback(EnableHelloHueCallback),
		title = 'Enable HelloHue',
		thumb = R('hellohue.png'),
	)

####################################################################################################
# Executes Applescript to Launch the Prismatik app
####################################################################################################
def EnableHelloHueCallback():
	Log("Trying to enable thread")
	threading.Thread(target=run_websocket_lister,name='thread_websocket').start()
	Log(threading.enumerate())
	return MainMenu(header=NAME, message='HelloHue is now enabled.')

####################################################################################################
# Returns object to Launch the Prismatik app
####################################################################################################
def DisableHelloHue():
	return PopupDirectoryObject(
		key   = Callback(DisableHelloHueCallback),
		title = 'Disable HelloHue',
		thumb = R('hellohue.png'),
	)

####################################################################################################
# Executes Applescript to Launch the Prismatik app
####################################################################################################
def DisableHelloHueCallback():
	Log("Trying to disable thread")
	alive = False
	ws.close()
	Log(threading.enumerate())
	return MainMenu(header=NAME, message='HelloHue is now disabled.')

####################################################################################################
# Called by the framework every time a user changes the prefs
####################################################################################################
@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():

	global plex, hue
	Log('Validating Prefs')
	#if Prefs['RESET']:
	#	ResetPrefs()
	plex = Plex()
	hue = Hue()
	threading.Thread(target=run_websocket_lister,name='thread_websocket').start()
	Log(threading.enumerate())

####################################################################################################
# Philips Hue Commands
####################################################################################################

class Hue:

	def __init__(self):
	    Log("Initializing Hue class")
	    global B, LIGHT_GROUPS, LIGHT_GROUPS_INITIAL_STATE
	    B = Bridge(Prefs['HUE_BRIDGE_IP'], 'newdeveloper')
	    B.connect()

	    Log("-Getting available lights")
	    LIGHT_GROUPS = self.get_hue_light_groups()
	    Log(LIGHT_GROUPS)

	    Log("-Getting lights initial state")
	    LIGHT_GROUPS_INITIAL_STATE = self.get_hue_light_initial_state()
	    Log(LIGHT_GROUPS_INITIAL_STATE)

	def get_hue_light_groups(self):
	    lights = B.lights
	    Log(lights)
	    Log(Prefs['HUE_LIGHTS'])
	    pattern = re.compile("^\s+|\s*,\s*|\s+$")
	    configuredlights = [x for x in pattern.split(Prefs['HUE_LIGHTS']) if x]
	    Log(configuredlights)
	    # Print light names
	    array = []
	    for l in lights:
	        for local_group in configuredlights:
	            if l.name == local_group:
	                array.append(l.name)
	    return array

	def get_hue_light_initial_state(self):
	    B = Bridge(Prefs['HUE_BRIDGE_IP'], 'newdeveloper')
	    B.connect()
	    array = []
	    for light in LIGHT_GROUPS:
	        subarray = []
	        subarray.append(light)
	        subarray.append(B.get_light(light, 'on'))
	        subarray.append(B.get_light(light, 'bri'))
	        array.append(subarray)
	    return array

def update_light_state(powered, brightness):
    #headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN}
    #state_string = {'desired_state': {'brightness': brightness, 'powered': powered}};
    #for group_id in LIGHT_GROUPS:
    #    print(time.strftime("%I:%M:%S") + " - changing light group %s powered state to %s and brightness state to %s" % (group_id, "ON" if powered else "OFF", "DIM" if brightness == 0 else "FULL"));
    #    requests.post("https://winkapi.quirky.com/groups/" + group_id + "/activate", json=state_string,headers=headers);
    #for l.name in LIGHT_GROUPS:
    Log("--Updating lights")
    command =  {'on' : powered, 'bri' : brightness}
    B.set_light(LIGHT_GROUPS, command)

####################################################################################################
# Plex Commands
####################################################################################################

class Plex:
    def __init__(self):
        Log("Initializing Plex class")
        Log("-Getting Token")
        global HEADERS, ACCESS_TOKEN
        HEADERS = {'X-Plex-Product': 'Automating Home Lighting',
                   'X-Plex-Version': '1.2.0',
                   'X-Plex-Client-Identifier': 'PlexWink',
                   'X-Plex-Device': 'PC',
                   'X-Plex-Device-Name': 'PlexWink'}
        ACCESS_TOKEN = self.get_plex_token()
        Log(ACCESS_TOKEN)
        #print("-Getting Server")
        #PLEX_IP = self.get_plex_server()
        #print PLEX_IP

    def get_plex_server(self):
        auth = {'user[login]': Prefs['PLEX_USERNAME'], 'user[password]': Prefs['PLEX_PASSWORD']}
        r = requests.post('https://plex.tv/pms/servers.xml', params=auth)
        return r

    def get_plex_token(self):
        auth = {'user[login]': Prefs['PLEX_USERNAME'], 'user[password]': Prefs['PLEX_PASSWORD']}
        r = requests.post('https://plex.tv/users/sign_in.json', params=auth, headers=HEADERS)
        data = json.loads(r.text)
        return data['user']['authentication_token']

def get_plex_status():
    r = requests.get('http://' + Prefs['PLEX_ADDRESS'] + '/status/sessions?X-Plex-Token=' + ACCESS_TOKEN, headers=HEADERS)
    e = ElementTree.fromstring(r.text.encode('utf-8'))
    return e

####################################################################################################
# PlexHue Commands
####################################################################################################

CURRENT_STATUS = ''

def run_websocket_lister():
	global ws

	Log('Listening for playing items')
	Log(ACCESS_TOKEN)
	websocket.enableTrace(True)
	ws = websocket.WebSocketApp("ws://127.0.0.1:32400/:/websockets/notifications?X-Plex-Token=" + ACCESS_TOKEN,
	                          on_message = on_message)
	                          # on_error = on_error,
	                          # on_close = on_close)
	# ws.on_open = on_open
	Log("It's running")
	ws.run_forever()

def is_plex_playing(plex_status):
	global CURRENT_STATUS
	pattern = re.compile("^\s+|\s*,\s*|\s+$")
	configuredclients = [x for x in pattern.split(Prefs['PLEX_CLIENTS']) if x]
	configuredusers = [x for x in pattern.split(Prefs['PLEX_AUTHORIZED_USERS']) if x]
	for item in plex_status.findall('Video'):
		for client_name in configuredclients:
			if item.find('Player').get('title') == client_name:
				for username in configuredusers:
					if item.find('User').get('title') == username:
						if item.find('Player').get('state') == 'playing' and CURRENT_STATUS != item.find('Player').get('state'):
							CURRENT_STATUS = item.find('Player').get('state')
							Log(time.strftime("%I:%M:%S") + " - %s %s %s - %s on %s." % (item.find('User').get('title'), CURRENT_STATUS, item.get('grandparentTitle'), item.get('title'), client_name))
							turn_off_lights()
							return False
						elif item.find('Player').get('state') == 'paused' and CURRENT_STATUS != item.find('Player').get('state'):
							CURRENT_STATUS = item.find('Player').get('state')
							Log(time.strftime("%I:%M:%S") + " - %s %s %s - %s on %s." % (item.find('User').get('title'), CURRENT_STATUS, item.get('grandparentTitle'), item.get('title'), client_name))
							dim_lights()
							return False
						else:
							return False


	if CURRENT_STATUS == 'stopped':
		print(time.strftime("%I:%M:%S") + " - Playback stopped");
		return False


	CURRENT_STATUS = 'stopped'
	print(time.strftime("%I:%M:%S") + " - Playback stopped");
	#reset_lights()
	turn_off_lights()


def reset_lights():
    Hue.reset_light_state()
    pass

def turn_off_lights():
    update_light_state(False, 50)
    pass


def turn_on_lights():
    update_light_state(True, 254)
    pass


def dim_lights():
    Log("Dimming lights")
    update_light_state(True, 100)
    pass

def on_message(ws, message):
    json_object = json.loads(message)
    if json_object['type'] == 'playing':
        plex_status = get_plex_status()
        # if json_object['_children'][0]['state'] == 'playing':
        is_plex_playing(plex_status)
        # turn_off_lights()

        # elif json_object['_children'][0]['state'] == 'paused':
        #     if is_plex_paused(plex_status):
        #         dim_lights()
        #
        # elif json_object['_children'][0]['state'] == 'stopped':
        #     if is_plex_stopped(plex_status):
        #         turn_on_lights()

def on_close(ws):
    print "### closed ###"
