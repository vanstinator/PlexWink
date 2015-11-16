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
		oc.add(DirectoryObject(key = Callback(MyLights),title = 'My Lights',thumb = R(PREFS_ICON)))
		if "thread_websocket" in str(threading.enumerate()):
			oc.add(DisableHelloHue())
		if not "thread_websocket" in str(threading.enumerate()):
			oc.add(EnableHelloHue())
	oc.add(DirectoryObject(key = Callback(AdvancedMenu),title = 'Advanced Menu',thumb = R(PREFS_ICON)))
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
	oc.add(PopupDirectoryObject(key = Callback(ResetPlexToken),title = 'Reset Plex.TV token',thumb = R(PREFS_ICON)))
	oc.add(PopupDirectoryObject(key = Callback(ResetHueToken),title = 'Reset Hue token',thumb = R(PREFS_ICON)))
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
	bigarray = []
	i = 0
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
		oc.add(DirectoryObject(key = Callback(LightAction,light_id = array,on = menu_action),title = menu_text + " " + lights.name,thumb = R(PREFS_ICON)))
	if i == 0:
		oc.add(DirectoryObject(key = Callback(MainMenu),title = "No lights available",thumb = R(PREFS_ICON)))
	else:
		oc.add(DirectoryObject(key = Callback(LightAction,light_id = bigarray,on = True),title = "Turn all lights on",thumb = R(PREFS_ICON)))
		oc.add(DirectoryObject(key = Callback(LightAction,light_id = bigarray,on = False),title = "Turn all lights off",thumb = R(PREFS_ICON)))
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
	return PopupDirectoryObject(key= Callback(ConnectBridgeCallback),title = 'Press button on your bridge and click to connect',thumb = R('hellohue.png'))
####################################################################################################
# Callback to signin to Hue Bridge
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
	return PopupDirectoryObject(key= Callback(ValidatePrefs),title = 'Restart HelloHue (must do after changing plex.tv login/password)',thumb = R('hellohue.png'))
####################################################################################################
# Item menu to enable the Channel
####################################################################################################
def EnableHelloHue():
	return PopupDirectoryObject(key= Callback(EnableHelloHueCallback),title = 'Enable HelloHue',thumb = R('hellohue.png'))

####################################################################################################
# Callback to enable the Channel
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
	return PopupDirectoryObject(key= Callback(DisableHelloHueCallback),title ='Disable HelloHue',thumb = R('hellohue.png'))

####################################################################################################
# Callback to disable the Channel
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
		hue = Hue()
		CompileRooms()
		hue.get_hue_light_groups()
		InitiateCurrentStatus()
		plex = Plex()
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
# Philips Hue Check Commands
####################################################################################################

class HueCheck:
	def __init__(self):
		Log("Checking if username is registered and if bridge if reachable")
	def check_username(self):
		#Dict['HUE_USERNAME'] = "newdeveloper"
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

####################################################################################################
# Philips Hue Commands
####################################################################################################

class Hue:
	def __init__(self):
		Log("Initializing Hue class")
		global B, LIGHT_GROUPS
		B = Bridge(Prefs['HUE_BRIDGE_IP'], Dict['HUE_USERNAME'])
		Log("Bridge found: " + str(B))

		#Log("-Getting available lights")
		#self.get_hue_light_groups()

	def get_hue_light_groups(self):
		Log("-Getting available lights")
		lights = B.lights
		Log("Available lights: " +str(lights))
		Log("Configured lights: " + str(ReturnAllLights()))
		Log("Configured color lights: " + str(ReturnColorLights()))
		Log("Configured lux lights: " + str(ReturnLuxLights()))
		Log("Configured on/off lights: " + str(ReturnOnOffLights()))

	def get_hue_light_initial_state(self, client_name, room):
		dico = {}
		for light in ReturnColorLightsFromClient(client_name, room):
			line = {}
			line['on'] = B.get_light(light, 'on')
			line['bri'] = B.get_light(light, 'bri')
			line['hue'] = B.get_light(light, 'hue')
			line['sat'] = B.get_light(light, 'sat')
			dico[light] = line
		for light in ReturnLuxLightsFromClient(client_name, room):
			line = {}
			line['on'] = B.get_light(light, 'on')
			line['bri'] = B.get_light(light, 'bri')
			dico[light] = line
		for light in ReturnOnOffLightsFromClient(client_name, room):
			line = {}
			line['on'] = B.get_light(light, 'on')
			dico[light] = line
		LIGHT_GROUPS_INITIAL_STATE[client_name + str(room)] = dico
		Log(dico)
		#return dico

	def update_light_state(self, powered, brightness, client_name, room):
		Log("--Updating lights")
		command =  {'on' : powered, 'bri' : brightness}
		command_lux = {'on' : powered, 'bri' : brightness}
		command_onoff = {'on' : powered}
		if ReturnFromClient(client_name, "randomize", room) is True and powered is True:
			Log("---Randomizing")
			hue = random.randint(0,65535)
			sat = random.randint(100,254)
			command =  {'on' : powered, 'bri' : brightness, 'sat': sat, 'hue': hue}
		if powered is False:
			command =  {'on' : powered}
			command_lux = {'on' : powered}
		lights = ReturnColorLightsFromClient(client_name, room)
		luxlights = ReturnLuxLightsFromClient(client_name, room)
		onofflights = ReturnOnOffLightsFromClient(client_name, room)
		Log(B.set_light(lights, command))
		Log(B.set_light(luxlights, command_lux))
		Log(B.set_light(onofflights, command_onoff))

	def reset_lights_state(self, client_name, room):
		Log("--Reset lights")
		lights = LIGHT_GROUPS_INITIAL_STATE[client_name + str(room)]
		#Log("lights : %s" % lights)
		for light in lights:
			#Log("light : %s" % light)
			try:
				lights[light]['bri']
			except:
				Log("%s is a on/off light, triggering on parameter"% light)
				command = {'on': lights[light]['on']}
			else:
				try:
					lights[light]['hue']
					lights[light]['sat']
				except:
					Log("%s is a lux light, triggering on, bri parameters"% light)
					command = {'on': lights[light]['on'], 'bri': lights[light]['bri']}
				else:
					Log("%s is a color light, triggering bri, on, sat, hue parameters"% light)
					command = {'on': lights[light]['on'], 'bri': lights[light]['bri'], 'hue':lights[light]['hue'], 'sat': lights[light]['sat']}
			Log(B.set_light(light, command))

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
# Compile rooms in list/dictionary on plugin start or pref change
####################################################################################################

def CompileRooms():
	global rooms
	pattern = re.compile("^\s+|\s*,\s*|\s+$")
	rooms = []
	j = 1
	while j < 6:
		if Prefs['HUE_ROOM_' + str(j)] is True and not Prefs['PLEX_CLIENT_' + str(j)] == '' and not Prefs['HUE_LIGHTS_' + str(j)] == '' and not Prefs['PLEX_AUTHORIZED_USERS_' + str(j)] == '':
			room= {}
			room['client'] = Prefs['PLEX_CLIENT_' + str(j)]
			#room['lights'] = [x for x in pattern.split(Prefs['HUE_LIGHTS_' + str(j)]) if x]
			lights = [x for x in pattern.split(Prefs['HUE_LIGHTS_' + str(j)]) if x]
			onofflights = []
			luxlights = []
			colorlights = []
			for light in lights:
				#Log("Trying for light %s"% light)
				try:
					B.get_light(light, 'bri')
				except:
					onofflights.append(light)
				else:			
					try:
						B.get_light(light, 'sat')
						B.get_light(light, 'hue')
					except:
						luxlights.append(light)
					else:
						colorlights.append(light)
			room['lights'] = colorlights
			room['luxlights'] = luxlights
			room['onofflights'] = onofflights
			room['users'] = [x for x in pattern.split(Prefs['PLEX_AUTHORIZED_USERS_' + str(j)]) if x]
			room['playing'] = Prefs['HUE_ACTION_PLAYING_' + str(j)]
			room['paused'] = Prefs['HUE_ACTION_PAUSED_' + str(j)]
			room['stopped'] = Prefs['HUE_ACTION_STOPPED_' + str(j)]
			room['dim'] = Prefs['HUE_DIM_' + str(j)]
			room['randomize'] = Prefs['HUE_RANDOMIZE_' + str(j)]
			room['dark'] = Prefs['HUE_DARK_' + str(j)]
			room['room'] = j
			rooms.append(room)
			Log("Adding room %s to rooms .." %j)
		else:
			Log("skipping room %s." %j)
		j += 1
	Log("Room check done")
	Log(rooms)

####################################################################################################
# Put all available clients status to '' on plugin start or pref change
####################################################################################################

def InitiateCurrentStatus():
	Log("Initiating current status")
	global CURRENT_STATUS, LIGHT_GROUPS_INITIAL_STATE
	CURRENT_STATUS = {}
	LIGHT_GROUPS_INITIAL_STATE = {}
	for room, client in ReturnClients().iteritems():
		CURRENT_STATUS[client + str(room)] = ''
	Log(CURRENT_STATUS)

####################################################################################################
# Return all configured clients from preferences
####################################################################################################

def ReturnClients():
	#client_list = []
	client_list = {}
	for clients in rooms:
		#client_list.append(clients['client'])
		client_list[clients['room']] = clients['client']
	#Log(client_list)
	return client_list

####################################################################################################
# Return all color lights attached a specific client
####################################################################################################

def ReturnColorLightsFromClient(client_name, room):
	lights_list = []
	for clients in rooms:
		if clients['client'] == client_name and clients['room'] == room:
			for light in clients['lights']:
				lights_list.append(light)
	return lights_list

####################################################################################################
# Return all Lux lights attached a specific client
####################################################################################################

def ReturnLuxLightsFromClient(client_name, room):
	lights_list = []
	for clients in rooms:
		if clients['client'] == client_name and clients['room'] == room:
			for light in clients['luxlights']:
				lights_list.append(light)
	return lights_list

####################################################################################################
# Return all On Off lights attached a specific client
####################################################################################################

def ReturnOnOffLightsFromClient(client_name, room):
	lights_list = []
	for clients in rooms:
		if clients['client'] == client_name and clients['room'] == room:
			for light in clients['onofflights']:
				lights_list.append(light)
	return lights_list

####################################################################################################
# Return the list of all lights
####################################################################################################

def ReturnAllLights():
	lights_list = []
	for clients in rooms:
		for light in clients['lights']:
			if not light in lights_list:
				lights_list.append(light)
		for luxlight in clients['luxlights']:
			if not luxlight in lights_list:
				lights_list.append(luxlight)
		for onofflight in clients['onofflights']:
			if not onofflight in lights_list:
				lights_list.append(onofflight)
	return lights_list

####################################################################################################
# Return the list of all color lights
####################################################################################################

def ReturnColorLights():
	lights_list = []
	for clients in rooms:
		for light in clients['lights']:
			if not light in lights_list:
				lights_list.append(light)
	return lights_list

####################################################################################################
# Return the list of all lux lights
####################################################################################################

def ReturnLuxLights():
	lights_list = []
	for clients in rooms:
		for luxlight in clients['luxlights']:
			if not luxlight in lights_list:
				lights_list.append(luxlight)
	return lights_list

####################################################################################################
# Return the list of all lux lights
####################################################################################################

def ReturnOnOffLights():
	lights_list = []
	for clients in rooms:
		for onofflight in clients['onofflights']:
			if not onofflight in lights_list:
				lights_list.append(onofflight)
	return lights_list

####################################################################################################
# Return a list of authorized users for a specific client
####################################################################################################

def ReturnUsersFromClient(client_name, room):
	users_list = []
	for clients in rooms:
		if clients['client'] == client_name and clients['room'] == room:
			for light in clients['users']:
				users_list.append(light)
	return users_list


####################################################################################################
# Return a specific setting from a given client
####################################################################################################

def ReturnFromClient(client_name, param, room):
	for clients in rooms:
		if clients['client'] == client_name and clients['room'] == room:
			to_return = clients[param]
	return to_return

####################################################################################################
# Listen to Plex Media Server websocket 
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

####################################################################################################
# If websocket detected, trigger PMS sessions status analyze
####################################################################################################

def on_message(ws, message):
	json_object = json.loads(message)
	#Log(json_object)
	if json_object['type'] == 'playing':
		plex_status = plex.get_plex_status()
		is_plex_playing(plex_status)

def on_close(ws):
	Log("### closed ###")

####################################################################################################
# Parse PMS sessions status
####################################################################################################

def is_plex_playing(plex_status):
	configuredclients = ReturnClients()
	ACTIVE_CLIENTS = []
	somethingwasdone = False
	for item in plex_status.findall('Video'):
		for room, client_name in configuredclients.iteritems():
			if item.find('Player').get('title') == client_name:
				#Log('Ok')
				client_name_room = client_name + str(room)
				if not client_name_room in ACTIVE_CLIENTS:
					ACTIVE_CLIENTS.append(client_name_room)
				configuredusers = ReturnUsersFromClient(client_name, room)
				for username in configuredusers:
					#Log("Ok2")
					if item.find('User').get('title') == username:
						#Log("Ok3")
						if item.find('Player').get('state') == 'playing' and CURRENT_STATUS[client_name + str(room)] != item.find('Player').get('state'):
							#Log("Ok4")
							if  CURRENT_STATUS[client_name + str(room)] == '':
								#Log("Ok5")
								Log(time.strftime("%I:%M:%S") + " - New Playback (saving initial lights state): - %s %s %s - %s on %s in room %s."% (item.find('User').get('title'), CURRENT_STATUS[client_name + str(room)], item.get('grandparentTitle'), item.get('title'), client_name, room))
								hue.get_hue_light_initial_state(client_name, room)
							#Log("Ok6")
							CURRENT_STATUS[client_name + str(room)] = item.find('Player').get('state')
							Log(time.strftime("%I:%M:%S") + " - %s %s %s - %s on %s in room %s." % (item.find('User').get('title'), CURRENT_STATUS[client_name + str(room)], item.get('grandparentTitle'), item.get('title'), client_name, room))
							if isitdark(client_name, room) is True:
								#Log("Ok7")
								choose_action(CURRENT_STATUS[client_name + str(room)], client_name, room)
							#return False
							somethingwasdone = True
						elif item.find('Player').get('state') == 'paused' and CURRENT_STATUS[client_name + str(room)] != item.find('Player').get('state'):
							if  CURRENT_STATUS[client_name + str(room)] == '':
								Log(time.strftime("%I:%M:%S") + " - New Playback (saving initial lights state): - %s %s %s - %s on %s in room %s."% (item.find('User').get('title'), CURRENT_STATUS[client_name + str(room)], item.get('grandparentTitle'), item.get('title'), client_name, room))
								hue.get_hue_light_initial_state(client_name, room)
								#Log("Ok8")
							CURRENT_STATUS[client_name + str(room)] = item.find('Player').get('state')
							Log(time.strftime("%I:%M:%S") + " - %s %s %s - %s on %s in room %s." % (item.find('User').get('title'), CURRENT_STATUS[client_name + str(room)], item.get('grandparentTitle'), item.get('title'), client_name, room))
							if isitdark(client_name, room) is True:
								choose_action(CURRENT_STATUS[client_name + str(room)], client_name, room)
							#return False
							somethingwasdone = True
	
	if somethingwasdone is True:
		return False

	for client_name_room in CURRENT_STATUS:
		if not client_name_room in ACTIVE_CLIENTS:
			if not CURRENT_STATUS[client_name_room] == 'stopped' and not CURRENT_STATUS[client_name_room] == '':
				CURRENT_STATUS[client_name_room] = ''
				client_name = client_name_room[:-1]
				room = int(client_name_room[-1:])
				Log(time.strftime("%I:%M:%S") + " - Playback stopped on %s in room %s - Waiting for new playback" % (client_name, room));
				if isitdark(client_name, room) is True:
					choose_action("stopped", client_name, room)

####################################################################################################
# Choose action based on playback status and preferences
####################################################################################################

def choose_action(state, client_name, room):
	Log("Selecting action")
	if ReturnFromClient(client_name, state, room) == "Turn Off":
		turn_off_lights(client_name, room)
		pass
	elif ReturnFromClient(client_name, state, room) == "Turn On":
		turn_on_lights(client_name, room)
		pass
	elif ReturnFromClient(client_name, state, room) == "Dim":
		dim_lights(client_name, room)
	elif ReturnFromClient(client_name, state, room) == "Nothing":
		Log("Doing nothing")
		pass
	elif ReturnFromClient(client_name, state, room) == "Reset":
		reset_lights(client_name, room)
		pass
	else:
		Log("No matching action found")
		pass

####################################################################################################
# Calculate if it's dark outside at user's location
####################################################################################################

def isitdark(client_name, room):
	if ReturnFromClient(client_name, "dark", room) is False:
		Log("Dark pref set to false: triggering")
		return True
	else:
		city_name = Prefs['HUE_CITY']
		a = Astral()
		city = a[city_name]
		today_date = date.today()
		sun = city.sun(date=today_date, local=True)
		utc=pytz.UTC
		if sun['sunrise'] <= utc.localize(datetime.utcnow()) <= sun['sunset']:
			if sun['sunset'] >= utc.localize(datetime.utcnow()):
				event = "sunset"
				timediff = sun['sunset'] - utc.localize(datetime.utcnow())
			if sun['sunset'] <= utc.localize(datetime.utcnow()):
				event = "sunrise"
				timediff = utc.localize(datetime.utcnow()) - sun['sunrise']
			Log("It's sunny outside: not trigerring (%s in %s)" % (event, timediff))
			return False
		else:
			Log("It's dark outside: triggering")
			return True

####################################################################################################
# Execute lights actions
####################################################################################################

def reset_lights(client_name, room):
	Log("Reseting lights")
	hue.reset_lights_state(client_name, room)
	pass

def turn_off_lights(client_name, room):
	Log("Turning off lights")
	hue.update_light_state(powered=False, brightness=254, client_name=client_name, room=room)
	pass

def turn_on_lights(client_name, room):
	Log("Turning on lights")
	hue.update_light_state(powered=True, brightness=254, client_name=client_name, room=room)
	pass

def dim_lights(client_name, room):
	Log("Dimming lights")
	dim_value = ReturnFromClient(client_name, "dim", room)
	hue.update_light_state(powered=True, brightness=int(float(dim_value)), client_name=client_name, room=room)
	pass
