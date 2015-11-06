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

PREFIX       = "/video/HelloHue"
NAME         = 'HelloHue'
ART          = 'background.png'
ICON         = 'hellohue.png'
PREFS_ICON   = 'hellohue.png'
PROFILE_ICON = 'hellohue.png'

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
	auth = HueCheck().check_username()
	if auth is False:
		Log("Username not registered.")
		oc.add(ConnectBridge())
	if auth is True:
		if "thread_websocket" in str(threading.enumerate()):
			oc.add(DisableHelloHue())
		if not "thread_websocket" in str(threading.enumerate()):
			oc.add(EnableHelloHue())
	
	oc.add(RestartHelloHue())

	# Add item for setting preferences	
	oc.add(PrefsObject(title = L('Preferences'), thumb = R(PREFS_ICON)))

	return oc

####################################################################################################
# Item menu to signin to Hue Bridge
####################################################################################################
def ConnectBridge():
	return PopupDirectoryObject(
		key   = Callback(ConnectBridgeCallback),
		title = 'Press button and your bridge and click to connect',
		thumb = R('hellohue.png'),
	)
####################################################################################################
# Returns object to signin to Hue Bridge
####################################################################################################
def ConnectBridgeCallback():
	Log("Trying to connect")
	x = HueCheck().connect_to_bridge()
	message = "Error. Have you pushed the button on your bridge?"
	if not x == "Error":
		message = "Connected :)"
	return MainMenu(header=NAME, message=message)

####################################################################################################
# Item menu to Restart the Channel
####################################################################################################
def RestartHelloHue():
	return PopupDirectoryObject(
		key   = Callback(ValidatePrefs),
		title = 'Restart HelloHue (must do after changing plex.tv login/password)',
		thumb = R('hellohue.png'),
	)
####################################################################################################
# Item menu to enable the Channel
####################################################################################################
def EnableHelloHue():
	return PopupDirectoryObject(
		key   = Callback(EnableHelloHueCallback),
		title = 'Enable HelloHue',
		thumb = R('hellohue.png'),
	)

####################################################################################################
# Return object to enable the Channel
####################################################################################################
def EnableHelloHueCallback():
	Log("Trying to enable thread")
	#threading.Thread(target=run_websocket_lister,name='thread_websocket').start()
	if not "thread_websocket" in str(threading.enumerate()):
		ValidatePrefs()
	Log(threading.enumerate())
	return MainMenu(header=NAME, message='HelloHue is now enabled.')

####################################################################################################
# Item menu to disable the Channel
####################################################################################################
def DisableHelloHue():
	return PopupDirectoryObject(
		key   = Callback(DisableHelloHueCallback),
		title = 'Disable HelloHue',
		thumb = R('hellohue.png'),
	)

####################################################################################################
# Return object to disable the Channel
####################################################################################################
def DisableHelloHueCallback():
	Log("Trying to disable thread")
	if "thread_websocket" in str(threading.enumerate()):
		ws.close()
	Log(threading.enumerate())
	return MainMenu(header=NAME, message='HelloHue is now disabled.')

####################################################################################################
# Called by the framework every time a user changes the prefs // Used to restard the Channel
####################################################################################################
@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():

	global plex, hue
	Log('Validating Prefs')
	auth = HueCheck().check_username()
	if auth is False:
		Log("Hue username not registered. Can't do nothing")
	if auth is True:
		Log("Hue username is registered... Starting!")
		plex = Plex()
		hue = Hue()
		Log("Classes initiated")
		if "thread_websocket" in str(threading.enumerate()):
			Log("Closing daemon...")
			ws.close()
		if not "thread_websocket" in str(threading.enumerate()):
			Log("Starting daemon...")
			threading.Thread(target=run_websocket_lister,name='thread_websocket').start()
		Log(threading.enumerate())
	return MainMenu(header=NAME)

####################################################################################################
# Philips Hue Commands
####################################################################################################

class HueCheck:
	def __init__(self):
		Log("Checking if username is registered")
	def check_username(self):
		if Prefs['HUE_USERNAME']:
			r = requests.get('http://' + Prefs['HUE_BRIDGE_IP'] + '/api/' + Prefs['HUE_USERNAME'])
			data = json.loads(str(r.text))
			try:
				e = data['lights']
			except (ValueError, KeyError, TypeError):
				return False
			else:
				return True
	def connect_to_bridge(self):
		if Prefs['HUE_BRIDGE_IP']:
			Log("Trying to connect")
			r = requests.post('http://' + Prefs['HUE_BRIDGE_IP'] + '/api/', json={"devicetype": "HelloHue"})
			data = r.json()
			try:
				for x in data:
					e = x['success']['username']
				Log("Received username : " + e)
				Log("Storing in preferences")
				r = requests.get('http://' + Prefs['PLEX_ADDRESS'] + '/video/HelloHue/:/prefs/set?HUE_USERNAME=' + e)
				ValidatePrefs()
			except (ValueError, KeyError, TypeError):
				return "Error"
			else:
				return e

class Hue:

	def __init__(self):
	    Log("Initializing Hue class")
	    global B, LIGHT_GROUPS, LIGHT_GROUPS_INITIAL_STATE
	    B = Bridge(Prefs['HUE_BRIDGE_IP'], Prefs['HUE_USERNAME'])
	    Log("Bridge found: " + str(B))

	    Log("-Getting available lights")
	    LIGHT_GROUPS = self.get_hue_light_groups()

	    #Log("-Getting lights initial state")
	    #LIGHT_GROUPS_INITIAL_STATE = self.get_hue_light_initial_state()
	    #Log(LIGHT_GROUPS_INITIAL_STATE)

	def get_hue_light_groups(self):
	    lights = B.lights
	    Log("Available lights: " +str(lights))
	    pattern = re.compile("^\s+|\s*,\s*|\s+$")
	    configuredlights = [x for x in pattern.split(Prefs['HUE_LIGHTS']) if x]
	    Log("Configured lights: " + str(configuredlights))
	    # Print light names
	    array = []
	    for l in lights:
	        for local_group in configuredlights:
	            if l.name == local_group:
	                array.append(l.name)
	    return array

	def get_hue_light_initial_state(self):
	    array = []
	    for light in LIGHT_GROUPS:
	        subarray = []
	        subarray.append(light)
	        subarray.append(B.get_light(light, 'on'))
	        subarray.append(B.get_light(light, 'bri'))
	        array.append(subarray)
	    return array

def update_light_state(powered, brightness):
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
                   'X-Plex-Version': '1.0.1',
                   'X-Plex-Client-Identifier': 'HelloHue',
                   'X-Plex-Device': 'Server',
                   'X-Plex-Device-Name': 'HelloHue'}
        ACCESS_TOKEN = self.get_plex_token()
        if not ACCESS_TOKEN == "Error":
            Log("Token retrieved")

    def get_plex_token(self):
		auth = {'user[login]': Prefs['PLEX_USERNAME'], 'user[password]': Prefs['PLEX_PASSWORD']}
		r = requests.post('https://plex.tv/users/sign_in.json', params=auth, headers=HEADERS)
		data = json.loads(r.text)
		try:
			return data['user']['authentication_token']
		except (ValueError, KeyError, TypeError):
			return "Error"

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
	Log('Starting websocket listener')
	websocket.enableTrace(True)
	ws = websocket.WebSocketApp("ws://127.0.0.1:32400/:/websockets/notifications?X-Plex-Token=" + ACCESS_TOKEN,
	                          on_message = on_message)
	                          # on_error = on_error,
	                          # on_close = on_close)
	# ws.on_open = on_open
	Log("Up and running, listening")
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
							if Prefs['HUE_ACTION_PLAYING'] == "Turn Off":
								turn_off_lights()
							if Prefs['HUE_ACTION_PLAYING'] == "Turn On":
								turn_on_lights()
							if Prefs['HUE_ACTION_PLAYING'] == "Dim":
								dim_lights()
							if Prefs['HUE_ACTION_PLAYING'] == "Nothing":
								pass
							return False
						elif item.find('Player').get('state') == 'paused' and CURRENT_STATUS != item.find('Player').get('state'):
							CURRENT_STATUS = item.find('Player').get('state')
							Log(time.strftime("%I:%M:%S") + " - %s %s %s - %s on %s." % (item.find('User').get('title'), CURRENT_STATUS, item.get('grandparentTitle'), item.get('title'), client_name))
							if Prefs['HUE_ACTION_PAUSED'] == "Turn Off":
								turn_off_lights()
							if Prefs['HUE_ACTION_PAUSED'] == "Turn On":
								turn_on_lights()
							if Prefs['HUE_ACTION_PAUSED'] == "Dim":
								dim_lights()
							if Prefs['HUE_ACTION_PAUSED'] == "Nothing":
								pass
							return False
						else:
							return False


	if CURRENT_STATUS == 'stopped':
		print(time.strftime("%I:%M:%S") + " - Playback stopped");
		return False


	CURRENT_STATUS = 'stopped'
	print(time.strftime("%I:%M:%S") + " - Playback stopped");
	#reset_lights()
	if Prefs['HUE_ACTION_STOPPED'] == "Turn Off":
		turn_off_lights()
	if Prefs['HUE_ACTION_STOPPED'] == "Turn On":
		turn_on_lights()
	if Prefs['HUE_ACTION_STOPPED'] == "Dim":
		dim_lights()
	if Prefs['HUE_ACTION_STOPPED'] == "Nothing":
		pass


def reset_lights():
	Log("Reseting lights")
	Hue.reset_light_state()
	pass

def turn_off_lights():
	Log("Turning off lights")
	update_light_state(False, 50)
	pass

def turn_on_lights():
	Log("Turning on lights")
	update_light_state(True, 254)
	pass

def dim_lights():
	Log("Dimming lights")
	update_light_state(True, 100)
	pass

def on_message(ws, message):
    json_object = json.loads(message)
    Log(json_object)
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
