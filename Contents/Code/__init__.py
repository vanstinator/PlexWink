import os
import time
from time import sleep
from datetime import datetime, date
import websocket
from phue import Bridge
import sys
import requests
import json
import re
import threading
import random
from astral import Astral
import pytz

import xml.etree.ElementTree as ElementTree
	
####################################################################################################

PREFIX       = "/applications/HelloHue"
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
	ValidatePrefs()
	var = [
			{
				"client": "RasPlex",
				"Lights": [
					"Living Colors 1",
					"Living Colors 2"
					],
				"Users": [
					"ledge74",
					"ledge741"
					]
				},
				{
				"client": "RasPlex2",
				"Lights": [
					"Living Colors 12",
					"Living Colors 22"
					],
				"Users": [
					"ledge742",
					"ledge7412"
					]
				}
			]
	ii = json.dumps(var)

	jj = json.loads(ii)

	for client in jj:
		Log(client["client"])
		Log(str(client["Lights"]))
		for lights in client["Lights"]:
			Log(lights)
		for users in client["Users"]:
			Log(users)

####################################################################################################
# Main menu
####################################################################################################
@handler(PREFIX, NAME, art=R(ART), thumb=R(ICON))
def MainMenu(header=NAME, message="Hello"):
	oc = ObjectContainer(no_cache=True,no_history=True, replace_parent=True)
	if message is not "Hello":
		oc.header = header
		oc.message = message
	if auth is False:
		oc.add(ConnectBridge())
	if auth is True:
		oc.add(DirectoryObject(
			key = Callback(MyLights),
			title = 'My Lights',
			thumb = R(PREFS_ICON)))
		if "thread_websocket" in str(threading.enumerate()):
			oc.add(DisableHelloHue())
		if not "thread_websocket" in str(threading.enumerate()):
			oc.add(EnableHelloHue())
	oc.add(DirectoryObject(
		key = Callback(AdvancedMenu),
		title = 'Advanced Menu',
		thumb = R(PREFS_ICON)))
	# Add item for setting preferences	
	oc.add(PrefsObject(title = L('Preferences'), thumb = R(PREFS_ICON)))
	return oc

####################################################################################################
# Advanced Menu
####################################################################################################
@route(PREFIX + '/AdvancedMenu')
def AdvancedMenu(header="AdvancedMenu", message="Hello"):
	oc = ObjectContainer(title2 = "Advanced Menu",no_cache=True,no_history=True, replace_parent=True)
	if message is not "Hello":
		oc.header = header
		oc.message = message
	oc.add(PopupDirectoryObject(
		key = Callback(ResetPlexToken),
		title = 'Reset Plex.TV token',
		thumb = R(PREFS_ICON)))
	oc.add(PopupDirectoryObject(
		key = Callback(ResetHueToken),
		title = 'Reset Hue token',
		thumb = R(PREFS_ICON)))
	oc.add(RestartHelloHue())
	return oc
####################################################################################################
# Reset Plex Token
####################################################################################################
def ResetPlexToken():
	if Dict["token"]:
		Dict["token"] = ""
		if Dict["token"]:
			Log("TokenStillDetected")
			return AdvancedMenu(header="AdvancedMenu", message="Error while deleting.")
		else:
			Log("Token deleted")
			ValidatePrefs()
			return AdvancedMenu(header="AdvancedMenu", message="Token Deleted.")
	else:
		Log("Plex Foiray")

####################################################################################################
# Advanced Menu
####################################################################################################
def ResetHueToken():
	if Dict["HUE_USERNAME"]:
		Dict["HUE_USERNAME"] = ""
		if Dict["HUE_USERNAME"]:
			Log("TokenStillDetected")
			return AdvancedMenu(header="AdvancedMenu", message="Error while deleting.")
		else:
			Log("Token deleted")
			ValidatePrefs()
			return AdvancedMenu(header="AdvancedMenu", message="Token Deleted.")
	else:
		Log("Hue Foiray")
####################################################################################################
# Lights Menu
####################################################################################################
@route(PREFIX + '/MyLights')
def MyLights(header="My Lights"):
	oc = ObjectContainer(title2 =header)
	oc.no_history = True
	oc.no_cache = True
	oc.replace_parent = True
	i = 0
	bigarray = []
	for lights in B.lights:
		i += 1
		menu_text = "Turn On"
		menu_action = True
		if lights.on == True:
			menu_text = "Turn Off"
			menu_action = False
		array = []
		array.append(lights.name)
		bigarray.append(lights.name)
		Log(array)
		oc.add(DirectoryObject(
			key = Callback(LightAction,
				light_id = array,
				on = menu_action),
			title = menu_text + " " + lights.name,
			thumb = R(PREFS_ICON)))
	if i == 0:
		oc.add(DirectoryObject(
			key = Callback(MainMenu),
			title = "No lights available",
			thumb = R(PREFS_ICON)))
	else:
		oc.add(DirectoryObject(
			key = Callback(LightAction,
				light_id = bigarray,
				on = True),
			title = "Turn all lights on",
			thumb = R(PREFS_ICON)))
		oc.add(DirectoryObject(
			key = Callback(LightAction,
				light_id = bigarray,
				on = False),
			title = "Turn all lights off",
			thumb = R(PREFS_ICON)))
	return oc

####################################################################################################
# Lights action
####################################################################################################
def LightAction(light_id, on):
	command =  {'on' : on}
	try: Log(B.set_light(light_id, command))
	except:
		pass
	return MyLights()

####################################################################################################
# Item menu to signin to Hue Bridge
####################################################################################################
def ConnectBridge():
	return PopupDirectoryObject(
		key   = Callback(ConnectBridgeCallback),
		title = 'Press button on your bridge and click to connect',
		thumb = R('hellohue.png'),
	)
####################################################################################################
# Returns object to signin to Hue Bridge
####################################################################################################
def ConnectBridgeCallback():
	Log("Trying to connect")
	x = HueCheck().connect_to_bridge()
	if x == "ErrorAuth":
		message = "Error. Have you pushed the button on your bridge?"
	elif x == "ErrorReach":
		message = "Error. Wrong bridge IP?"
	else:
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
	#threading.Thread(target=run_websocket_watcher,name='thread_websocket').start()
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

	global auth, plex, hue
	Log('Validating Prefs')
	auth = HueCheck().check_username()
	if auth is False:
		Log("Please update your Hue preferences and try again")
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
			threading.Thread(target=run_websocket_watcher,name='thread_websocket').start()
		Log(threading.enumerate())
	return MainMenu(header=NAME)

####################################################################################################
# Philips Hue Commands
####################################################################################################

class HueCheck:
	def __init__(self):
		Log("Checking if username is registered and if bridge if reachable")
	def check_username(self):
		Dict['HUE_USERNAME'] = "newdeveloper"
		if Dict['HUE_USERNAME']:
			try:
				r = requests.get('http://' + Prefs['HUE_BRIDGE_IP'] + '/api/' + Dict['HUE_USERNAME'])
			except requests.exceptions.RequestException as e:
				Log("Error while connecting to bridge (wrong bridge IP/not reachable): "+str(e))
				return False
			data = json.loads(str(r.text))
			try:
				e = data['lights']
			except (ValueError, KeyError, TypeError):
				Log("Error while connecting to bridge (wrong username).")
				return False
			else:
				return True
		else:
			return False
	def connect_to_bridge(self):
		if Prefs['HUE_BRIDGE_IP']:
			Log("Trying to connect")
			try:
				r = requests.post('http://' + Prefs['HUE_BRIDGE_IP'] + '/api/', json={"devicetype": "HelloHue"})
			except requests.exceptions.RequestException as e:
				Log("Error while connecting to bridge (wrong bridge IP/not reachable): "+str(e))
				return "ErrorReach"
			data = r.json()
			try:
				for x in data:
					e = x['success']['username']
				Log("Received username : " + e)
				Log("Storing in dict")
				Dict['HUE_USERNAME'] = e
				ValidatePrefs()
			except (ValueError, KeyError, TypeError):
				return "ErrorAuth"
		else:
			return e

class Hue:
	def __init__(self):
		Log("Initializing Hue class")
		global B, LIGHT_GROUPS
		B = Bridge(Prefs['HUE_BRIDGE_IP'], Dict['HUE_USERNAME'])
		Log("Bridge found: " + str(B))

		Log("-Getting available lights")
		LIGHT_GROUPS = self.get_hue_light_groups()

	def get_hue_light_groups(self):
		lights = B.lights
		Log("Available lights: " +str(lights))
		pattern = re.compile("^\s+|\s*,\s*|\s+$")
		configuredlights = [x for x in pattern.split(Prefs['HUE_LIGHTS']) if x]
		Log("Configured lights: " + str(configuredlights))
		array = []
		for l in lights:
			for local_group in configuredlights:
				if l.name == local_group:
					array.append(l.name)
		return array

	def get_hue_light_initial_state(self):
		global LIGHT_GROUPS_INITIAL_STATE
		dico = {}
		for light in LIGHT_GROUPS:
			line = {}
			line['on'] = B.get_light(light, 'on')
			line['bri'] = B.get_light(light, 'bri')
			dico[light] = line
		LIGHT_GROUPS_INITIAL_STATE = dico
		return dico

	def update_light_state(self, powered, brightness=254):
		Log("--Updating lights")
		command =  {'on' : powered, 'bri' : brightness}
		if Prefs['HUE_RANDOMIZE'] is True and powered is True:
			Log("---Randomizing")
			hue = random.randint(0,65535)
			sat = random.randint(100,254)
			command =  {'on' : powered, 'bri' : brightness, 'sat': sat, 'hue': hue}
		if powered is False:
			command =  {'on' : powered}
		B.set_light(LIGHT_GROUPS, command)

	def reset_lights_state(self):
		Log("--Reset lights")
		lights = LIGHT_GROUPS_INITIAL_STATE
		for light in lights:
			command = {'on': lights[light]['on'], 'bri': lights[light]['bri']}
			B.set_light(light, command)

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
		if Dict["token"] == "Error" or not Dict["token"]:
			TOKEN = self.get_plex_token()
			ACCESS_TOKEN = TOKEN
		else:
			Log("Token retrieved from Dict")
			ACCESS_TOKEN = Dict["token"]

	def get_plex_token(self):
		plexauth = {'user[login]': Prefs['PLEX_USERNAME'], 'user[password]': Prefs['PLEX_PASSWORD']}
		r = requests.post('https://plex.tv/users/sign_in.json', params=plexauth, headers=HEADERS)
		data = json.loads(r.text)
		try:
			Dict["token"] = data['user']['authentication_token']
			Log("Token retrieved and saved")
			return Dict["token"]
		except (ValueError, KeyError, TypeError):
			Log("Error while retrieving token")
			Dict["token"] = "Error"
			return Dict["token"]

	def get_plex_status(self):
		r = requests.get('http://' + Prefs['PLEX_ADDRESS'] + '/status/sessions?X-Plex-Token=' + ACCESS_TOKEN, headers=HEADERS)
		e = ElementTree.fromstring(r.text.encode('utf-8'))
		return e

####################################################################################################
# PlexHue Commands
####################################################################################################

def run_websocket_watcher():
	global ws
	Log('Starting websocket listener')
	websocket.enableTrace(True)
	ws = websocket.WebSocketApp("ws://" + Prefs['PLEX_ADDRESS'] + "/:/websockets/notifications?X-Plex-Token=" + ACCESS_TOKEN,
		on_message = on_message)
		# on_error = on_error,
		# on_close = on_close)
	# ws.on_open = on_open
	Log("Up and running, listening")
	ws.run_forever()

CURRENT_STATUS = ''


def is_plex_playing(plex_status):
	global CURRENT_STATUS
	pattern = re.compile("^\s+|\s*,\s*|\s+$")
	configuredclients = [x for x in pattern.split(Prefs['PLEX_CLIENTS']) if x]
	configuredusers = [x for x in pattern.split(Prefs['PLEX_AUTHORIZED_USERS']) if x]
	i = 0
	j = 0
	for item in plex_status.findall('Video'):
		for client_name in configuredclients:
			if item.find('Player').get('title') == client_name:
				i += 1
				for username in configuredusers:
					if item.find('User').get('title') == username:
						j += 1
						if item.find('Player').get('state') == 'playing' and CURRENT_STATUS != item.find('Player').get('state'):
							if  CURRENT_STATUS == '':
								Log(time.strftime("%I:%M:%S") + " - New Playback (saving initial state): - %s %s %s - %s on %s."% (item.find('User').get('title'), CURRENT_STATUS, item.get('grandparentTitle'), item.get('title'), client_name))
								hue.get_hue_light_initial_state()
							CURRENT_STATUS = item.find('Player').get('state')
							Log(time.strftime("%I:%M:%S") + " - %s %s %s - %s on %s." % (item.find('User').get('title'), CURRENT_STATUS, item.get('grandparentTitle'), item.get('title'), client_name))
							if isitdark() is True:
								choose_action(CURRENT_STATUS)
							return False
						elif item.find('Player').get('state') == 'paused' and CURRENT_STATUS != item.find('Player').get('state'):
							if  CURRENT_STATUS == '':
								Log(time.strftime("%I:%M:%S") + " - New Playback (saving initial state): - %s %s %s - %s on %s."% (item.find('User').get('title'), CURRENT_STATUS, item.get('grandparentTitle'), item.get('title'), client_name))
								hue.get_hue_light_initial_state()
							CURRENT_STATUS = item.find('Player').get('state')
							Log(time.strftime("%I:%M:%S") + " - %s %s %s - %s on %s." % (item.find('User').get('title'), CURRENT_STATUS, item.get('grandparentTitle'), item.get('title'), client_name))
							if isitdark() is True:
								choose_action(CURRENT_STATUS)
							return False
						else:
							return False
	if i == 0:
		Log("No authorized clients are playing - skipping")
		return False

	if j == 0:
		Log("No authorized users are playing - skipping")
		return False

	if CURRENT_STATUS == 'stopped':
		Log(time.strftime("%I:%M:%S") + " - Waiting for new playback")
		CURRENT_STATUS = ''
		return False


	CURRENT_STATUS = 'stopped'
	Log(time.strftime("%I:%M:%S") + " - Playback stopped");
	if isitdark() is True:
		choose_action(CURRENT_STATUS)
	Log(CURRENT_STATUS)

def choose_action(state):
	Log("Selecting action")
	Log(state.upper())
	if Prefs['HUE_ACTION_' + state.upper()] == "Turn Off":
		turn_off_lights()
		return
	elif Prefs['HUE_ACTION_' + state.upper()] == "Turn On":
		turn_on_lights()
		return
	elif Prefs['HUE_ACTION_' + state.upper()] == "Dim":
		dim_lights()
	elif Prefs['HUE_ACTION_' + state.upper()] == "Nothing":
		return
	elif Prefs['HUE_ACTION_' + state.upper()] == "Reset":
		reset_lights()
		return
	else:
		Log("No matching action found")
		return

def isitdark():
	if Prefs['HUE_DARK'] is False:
		Log("Dark pref set to false: triggering")
		return True
	else:
		city_name = Prefs['HUE_CITY']
		a = Astral()
		city = a[city_name]
		today_date = date.today()
		sun = city.sun(date=today_date, local=True)
		utc=pytz.UTC
		#Log(Prefs['HUE_CITY'])
		#Log('Sunrise: %s' % str(sun['sunrise']))
		#Log('Sunset:  %s' % str(sun['sunset']))
		#Log('Now:  %s' % str(utc.localize(datetime.now())))
		if sun['sunrise'] <= utc.localize(datetime.now()) <= sun['sunset']:        
			Log("It's sunny outside: not trigerring")
			return False
		else:
			Log("It's dark outside: triggering")
			return True

def reset_lights():
	Log("Reseting lights")
	hue.reset_lights_state()
	pass

def turn_off_lights():
	Log("Turning off lights")
	hue.update_light_state(False)
	pass

def turn_on_lights():
	Log("Turning on lights")
	hue.update_light_state(True, 254)
	pass

def dim_lights():
	Log("Dimming lights")
	dim_value = int(float(Prefs['HUE_DIM']))
	hue.update_light_state(True, dim_value)
	pass

def on_message(ws, message):
	json_object = json.loads(message)
	#Log(json_object)
	if json_object['type'] == 'playing':
		plex_status = plex.get_plex_status()
		is_plex_playing(plex_status)

def on_close(ws):
	Log("### closed ###")
