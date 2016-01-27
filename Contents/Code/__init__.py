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
from rgb_cie import Converter
	
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
	global auth, plex, hue, converter, active_clients, firstrun
	Log('Validating Prefs')
	auth = HueCheck().check_username()
	if auth is False:
		Log("Please update your Hue preferences and try again")
	if auth is True:
		Log("Hue username is registered... Starting!")
	converter = Converter()
	hue = Hue()
	CompileRooms()
	hue.get_hue_light_groups()
	InitiateCurrentStatus()
	plex = Plex()
	active_clients = []
	Log("Classes initiated")
	if "thread_websocket" in str(threading.enumerate()):
		Log("Closing daemon...")
		ws.close()
	if not "thread_websocket" in str(threading.enumerate()):
		Log("Starting websocket daemon...")
		threading.Thread(target=run_websocket_watcher,name='thread_websocket').start()
	if "thread_clients" in str(threading.enumerate()):
		Log("Setting firstrun to True")
		firstrun = True
	if not "thread_clients" in str(threading.enumerate()):
		Log("Starting clients daemon...")
		threading.Thread(target=watch_clients,name='thread_clients').start()
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

	def get_hue_light_groups(self):
		Log("-Getting available groups")
		groups = B.groups
		Log("Available groups: " +str(groups))
		Log("Configured groups: " + str(ReturnAllGroups()))
		Log("Configured color groups: " + str(ReturnColorGroups()))
		Log("Configured lux groups: " + str(ReturnLuxGroups()))
		Log("Configured on/off groups: " + str(ReturnOnOffGroups()))
		#########################
		#########################
		#########################
		Log("-Getting available lights")
		lights = B.lights
		Log("Available lights: " +str(lights))
		Log("Configured lights: " + str(ReturnAllLights()))
		Log("Configured color lights: " + str(ReturnColorLights()))
		Log("Configured lux lights: " + str(ReturnLuxLights()))
		Log("Configured on/off lights: " + str(ReturnOnOffLights()))

	def get_hue_light_initial_state(self, client_name, room):
		dico = {}
		for group in ReturnColorGroupsFromClient(client_name, room):
			line = {}
			try:
				line['on'] = B.get_group(group, 'on')
				line['bri'] = B.get_group(group, 'bri')
				line['hue'] = B.get_group(group, 'hue')
				line['sat'] = B.get_group(group, 'sat')
				dico[group] = line
			except:
				Log("Something went wrong")
		for group in ReturnLuxGroupsFromClient(client_name, room):
			line = {}
			try:
				line['on'] = B.get_group(group, 'on')
				line['bri'] = B.get_group(group, 'bri')
				dico[group] = line
			except:
				Log("Something went wrong")
		for group in ReturnOnOffGroupsFromClient(client_name, room):
			line = {}
			try:
				line['on'] = B.get_group(group, 'on')
				dico[group] = line
			except:
				Log("Something went wrong")
		GROUPS_INITIAL_STATE[client_name + str(room)] = dico
		Log("Lamp initial state...")
		Log(dico)
		#########################
		#########################
		#########################
		dico = {}
		for light in ReturnColorLightsFromClient(client_name, room):
			line = {}
			try:
				line['on'] = B.get_light(light, 'on')
				line['bri'] = B.get_light(light, 'bri')
				line['hue'] = B.get_light(light, 'hue')
				line['sat'] = B.get_light(light, 'sat')
				dico[light] = line
			except:
				Log("Something went wrong")
		for light in ReturnLuxLightsFromClient(client_name, room):
			line = {}
			try:
				line['on'] = B.get_light(light, 'on')
				line['bri'] = B.get_light(light, 'bri')
				dico[light] = line
			except:
				Log("Something went wrong")
		for light in ReturnOnOffLightsFromClient(client_name, room):
			line = {}
			try:
				line['on'] = B.get_light(light, 'on')
				dico[lightsht] = line
			except:
				Log("Something went wrong")
		LIGHT_GROUPS_INITIAL_STATE[client_name + str(room)] = dico
		Log("Group initial state...")
		Log(dico)

	def update_light_state(self, powered, brightness, client_name, room, transitiontime, xy):
		Log("--Updating groups")
		command =  {'on' : powered, 'bri' : brightness, 'transitiontime' : transitiontime}
		command_lux = {'on' : powered, 'bri' : brightness, 'transitiontime' : transitiontime}
		command_onoff = {'on' : powered, 'transitiontime' : transitiontime}
		if not xy == None:
			Log("---triggering preset action")
			command =  {'on' : powered, 'bri' : brightness, 'transitiontime' : transitiontime, 'xy': xy}
		if ReturnFromClient(client_name, "randomize", room) is True and powered is True and xy == None:
			Log("---Randomizing")
			hue = random.randint(0,65535)
			sat = random.randint(100,254)
			command =  {'on' : powered, 'bri' : brightness, 'sat': sat, 'hue': hue, 'transitiontime' : transitiontime}
		if powered is False:
			command =  {'on' : powered, 'transitiontime' : transitiontime}
			command_lux = {'on' : powered, 'transitiontime' : transitiontime}
		groups = ReturnColorGroupsFromClient(client_name, room)
		luxgroups = ReturnLuxGroupsFromClient(client_name, room)
		onoffgroups = ReturnOnOffGroupsFromClient(client_name, room)
		try:
			Log("initial color group state: %s"% GROUPS_INITIAL_STATE[client_name + str(room)])
			for group in GROUPS_INITIAL_STATE[client_name + str(room)]:
				if ReturnFromClient(client_name, "only_on", room) is True and GROUPS_INITIAL_STATE[client_name + str(room)][group]["on"] is False:
					Log("Removing group %s"%group)
					if group in groups:
						groups.remove(group)
					if group in luxgroups:
						luxgroups.remove(group)
					if group in onoffgroups:
						onoffgroups.remove(group)
				else:
					Log("only_on is set to false")
		except:
			Log("Error getting group initial state")
		try:
			if groups:
				Log("updating color groups: %s"% B.set_group(groups, command))
			else:
				Log("No colorgroups to trigger")
		except:
			Log("Something went wrong with color groups")
		try:
			if luxgroups:
				Log("updating lux groups: %s"% B.set_group(luxgroups, command_lux))
			else:
				Log("No luxgroup to trigger")
		except:
			Log("Something went wrong with lux groups")
		try:
			if onoffgroups:
				Log("updating on/off groups: %s"% B.set_group(onoffgroups, command_onoff))
			else:
				Log("No onoffgroups to trigger")
		except:
			Log("Something went wrong with on/off groups")
		#########################
		#########################
		#########################
		#########################
		Log("--Updating lights")
		command =  {'on' : powered, 'bri' : brightness, 'transitiontime' : transitiontime}
		command_lux = {'on' : powered, 'bri' : brightness, 'transitiontime' : transitiontime}
		command_onoff = {'on' : powered, 'transitiontime' : transitiontime}
		if not xy == None:
			Log("---triggering preset action")
			command =  {'on' : powered, 'bri' : brightness, 'transitiontime' : transitiontime, 'xy': xy}
		if ReturnFromClient(client_name, "randomize", room) is True and powered is True and xy == None:
			Log("---Randomizing")
			hue = random.randint(0,65535)
			sat = random.randint(100,254)
			command =  {'on' : powered, 'bri' : brightness, 'sat': sat, 'hue': hue, 'transitiontime' : transitiontime}
		if powered is False:
			command =  {'on' : powered, 'transitiontime' : transitiontime}
			command_lux = {'on' : powered, 'transitiontime' : transitiontime}
		lights = ReturnColorLightsFromClient(client_name, room)
		luxlights = ReturnLuxLightsFromClient(client_name, room)
		onofflights = ReturnOnOffLightsFromClient(client_name, room)
		try:
			Log("initial lights state: %s"% LIGHT_GROUPS_INITIAL_STATE)
			for light in LIGHT_GROUPS_INITIAL_STATE[client_name + str(room)]:
				if ReturnFromClient(client_name, "only_on", room) is True and LIGHT_GROUPS_INITIAL_STATE[client_name + str(room)][light]["on"] is False:
					Log("Removing light %s"%light)
					if light in lights:
						lights.remove(light)
					if light in luxlights:
						luxlights.remove(light)
					if light in onofflights:
						onofflights.remove(light)
				else:
					Log("only_on is set to false")
		except:
			Log("Error getting group initial state")
		try:
			if lights:
				Log("updating color lights: %s"% B.set_light(lights, command))
			else:
				Log("No colorlight to trigger")
		except:
			Log("Something went wrong with color lights")
		try:
			if luxlights:
				Log("updating lux lights: %s"% B.set_light(luxlights, command_lux))
			else:
				Log("No luxlight to trigger")
		except:
			Log("Something went wrong with lux lights")
		try:
			if onofflights:
				Log("updating on/off lights: %s"% B.set_light(onofflights, command_onoff))
			else:
				Log("No onofflight to trigger")
		except:
			Log("Something went wrong with on/off lights")

	def reset_lights_state(self, client_name, room, transitiontime):
		Log("--Reset groups")
		groups = GROUPS_INITIAL_STATE[client_name + str(room)]

		colorgroups = ReturnColorGroupsFromClient(client_name, room)
		luxgroups = ReturnLuxGroupsFromClient(client_name, room)
		onoffgroups = ReturnOnOffGroupsFromClient(client_name, room)

		for group in groups:
			if group in colorgroups:
				Log("%s is a color group, triggering bri, on, sat, hue parameters"% group)
				command = {'on': groups[group]['on'], 'bri': groups[group]['bri'], 'hue':groups[group]['hue'], 'sat': groups[group]['sat'], 'transitiontime': transitiontime}
			if group in luxgroups:
				Log("%s is a lux group, triggering on, bri parameters"% group)
				command = {'on': groups[group]['on'], 'bri': groups[group]['bri'], 'transitiontime': transitiontime}
			if group in onoffgroups:
				Log("%s is a on/off group, triggering on parameter"% group)
				command = {'on': groups[group]['on']}
			try:
				if ReturnFromClient(client_name, "only_on", room) is True and GROUPS_INITIAL_STATE[client_name + str(room)][group]["on"] is False:
					Log("Not triggering group %s because only_on is set to true and group was off"%group)
				else:
					Log(B.set_group(group, command))
			except:
				Log("Something went wrong while resetting group %s"%group)
		#########################
		#########################
		#########################
		Log("--Reset lights")
		lights = LIGHT_GROUPS_INITIAL_STATE[client_name + str(room)]

		colorlights = ReturnColorLightsFromClient(client_name, room)
		luxlights = ReturnLuxLightsFromClient(client_name, room)
		onofflights = ReturnOnOffLightsFromClient(client_name, room)

		for light in lights:
			if light in colorlights:
				Log("%s is a color light, triggering bri, on, sat, hue parameters"% light)
				command = {'on': lights[light]['on'], 'bri': lights[light]['bri'], 'hue':lights[light]['hue'], 'sat': lights[light]['sat'], 'transitiontime': transitiontime}
			if light in luxlights:
				Log("%s is a lux light, triggering on, bri parameters"% light)
				command = {'on': lights[light]['on'], 'bri': lights[light]['bri'], 'transitiontime': transitiontime}
			if light in onofflights:
				Log("%s is a on/off light, triggering on parameter"% light)
				command = {'on': lights[light]['on']}
			try:
				if ReturnFromClient(client_name, "only_on", room) is True and LIGHT_GROUPS_INITIAL_STATE[client_name + str(room)][light]["on"] is False:
					Log("Not triggering light %s because only_on is set to true and light was off"%light)
				else:
					Log(B.set_light(light, command))
			except:
				Log("Something went wrong while resetting light %s"%light)

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

	def get_plex_clients(self):
		r = requests.get('http://' + Prefs['PLEX_ADDRESS'] + '/clients?X-Plex-Token=' + ACCESS_TOKEN, headers=HEADERS)
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
			lights = [x for x in pattern.split(Prefs['HUE_LIGHTS_' + str(j)]) if x]
			onofflights = []
			luxlights = []
			colorlights = []
			for light in lights:
				try:
					B.get_light(light, 'on')
				except:
					Log("Skipping this light")
				else:
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
			groups = [x for x in pattern.split(Prefs['HUE_GROUPS_' + str(j)]) if x]
			onoffgroups = []
			luxgroups = []
			colorgroups = []
			for group in groups:
				if (not B.get_group(group, 'lights') == None):
					try:
						B.get_group(group, 'bri')
					except:
						onoffgroups.append(group)
					else:			
						try:
							B.get_group(group, 'sat')
							B.get_group(group, 'hue')
						except:
							luxgroups.append(group)
						else:
							colorgroups.append(group)
			room['groups'] = colorgroups
			room['luxgroups'] = luxgroups
			room['onoffgroups'] = onoffgroups
			room['users'] = [x for x in pattern.split(Prefs['PLEX_AUTHORIZED_USERS_' + str(j)]) if x]
			room['playing'] = Prefs['HUE_ACTION_PLAYING_' + str(j)]
			room['paused'] = Prefs['HUE_ACTION_PAUSED_' + str(j)]
			room['stopped'] = Prefs['HUE_ACTION_STOPPED_' + str(j)]
			room['transition_start'] = Prefs['HUE_TRANSITION_START_' + str(j)]
			room['transition_paused'] = Prefs['HUE_TRANSITION_PAUSED_' + str(j)]
			room['transition_resumed'] = Prefs['HUE_TRANSITION_RESUMED_' + str(j)]
			room['transition_stopped'] = Prefs['HUE_TRANSITION_STOPPED_' + str(j)]
			room['transition_on'] = Prefs['PLEX_TRANSITION_ON_' + str(j)]
			room['transition_off'] = Prefs['PLEX_TRANSITION_OFF_' + str(j)]
			room['dim'] = Prefs['HUE_DIM_' + str(j)]
			room['randomize'] = Prefs['HUE_RANDOMIZE_' + str(j)]
			room['dark'] = Prefs['HUE_DARK_' + str(j)]
			room['min_duration'] = Prefs['PLEX_DURATION_' + str(j)]
			room['only_on'] = Prefs['HUE_ONLY_ON_' + str(j)]
			room['turned_on'] = Prefs['PLEX_ON_' + str(j)]
			room['turned_off'] = Prefs['PLEX_OFF_' + str(j)]
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
	Log("Initiating current status, lights initial states and durations for active rooms")
	global CURRENT_STATUS, CURRENT_MEDIA, GROUPS_INITIAL_STATE, LIGHT_GROUPS_INITIAL_STATE, DURATIONS
	CURRENT_STATUS = {}
	CURRENT_MEDIA = {}
	DURATIONS = {}
	GROUPS_INITIAL_STATE = {}
	LIGHT_GROUPS_INITIAL_STATE = {}
	for room, client_name in ReturnClients().iteritems():
		CURRENT_STATUS[client_name + str(room)] = ''
		CURRENT_MEDIA[client_name + str(room)] = ''
		DURATIONS[client_name + str(room)] = ''
	Log(CURRENT_STATUS)
	Log(DURATIONS)

####################################################################################################
# Return all configured clients from preferences
####################################################################################################

def ReturnClients():
	client_list = {}
	for clients in rooms:
		client_list[clients['room']] = clients['client']
	return client_list

####################################################################################################
# Return all color groups attached a specific client
####################################################################################################

def ReturnColorGroupsFromClient(client_name, room):
	groups_list = []
	for clients in rooms:
		if clients['client'] == client_name and clients['room'] == room:
			for group in clients['groups']:
				groups_list.append(group)
	return groups_list

####################################################################################################
# Return all Lux groups attached a specific client
####################################################################################################

def ReturnLuxGroupsFromClient(client_name, room):
	groups_list = []
	for clients in rooms:
		if clients['client'] == client_name and clients['room'] == room:
			for group in clients['luxgroups']:
				groups_list.append(group)
	return groups_list

def ReturnRoomFromClient(client_name):
	rooms_list = []
	for clients in rooms:
		if clients['client'] == client_name:
			rooms_list.append(clients['room'])
	return rooms_list

####################################################################################################
# Return all On Off groups attached a specific client
####################################################################################################

def ReturnOnOffGroupsFromClient(client_name, room):
	groups_list = []
	for clients in rooms:
		if clients['client'] == client_name and clients['room'] == room:
			for group in clients['onoffgroups']:
				groups_list.append(group)
	return groups_list

####################################################################################################
# Return the list of all groups
####################################################################################################

def ReturnAllGroups():
	groups_list = []
	for clients in rooms:
		for group in clients['groups']:
			if not group in groups_list:
				groups_list.append(group)
		for luxgroup in clients['luxgroups']:
			if not luxgroup in groups_list:
				groups_list.append(luxgroup)
		for onoffgroup in clients['onoffgroups']:
			if not onoffgroup in groups_list:
				groups_list.append(onoffgroup)
	return groups_list

####################################################################################################
# Return the list of all color groups
####################################################################################################

def ReturnColorGroups():
	groups_list = []
	for clients in rooms:
		for group in clients['groups']:
			if not group in groups_list:
				groups_list.append(group)
	return groups_list

####################################################################################################
# Return the list of all lux groups
####################################################################################################

def ReturnLuxGroups():
	groups_list = []
	for clients in rooms:
		for luxgroup in clients['luxgroups']:
			if not luxgroup in groups_list:
				groups_list.append(luxgroup)
	return groups_list

####################################################################################################
# Return the list of all lux groups
####################################################################################################

def ReturnOnOffGroups():
	groups_list = []
	for clients in rooms:
		for onoffgroup in clients['onoffgroups']:
			if not onoffgroup in groups_list:
				groups_list.append(onoffgroup)
	return groups_list

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
	ws = websocket.WebSocketApp("ws://" + Prefs['PLEX_ADDRESS'] + "/:/websockets/notifications?X-Plex-Token=" + ACCESS_TOKEN, on_message = on_message)
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
# Get currently playing item duration
####################################################################################################

def get_playing_item_duration(video, client_name, room):
	Log("getting duration")
	duration = int(video.get('duration'))
	DURATIONS[client_name + str(room)] = duration
	return duration

####################################################################################################
# Compare duration with preference
####################################################################################################

def compare_duration(duration, pref):
	if pref == "Disabled":
		Log("Duration pref is disabled: triggering")
		return True
	else:
		if pref == "1 minute":
			compared = 1 * 60 * 1000
		elif pref == "5 minutes":
			compared = 5 * 60 * 1000
		elif pref == "15 minutes":
			compared = 15 * 60 * 1000
		elif pref == "25 minutes":
			compared = 25 * 60 * 1000
		elif pref == "35 minutes":
			compared = 35 * 60 * 1000
		elif pref == "45 minutes":
			compared = 45 * 60 * 1000
		elif pref == "55 minutes":
			compared = 55 * 60 * 1000
		elif pref == "1 hour":
			compared = 60 * 60 * 1000
		elif pref == "1 hour and 20 minutes":
			compared = 80 * 60 * 1000
		elif pref == "1 hour and 40 minutes":
			compared = 100 * 60 * 1000
		elif pref == "2 hours":
			compared = 120 * 60 * 1000
		if duration > compared:
			Log("Duration is greater than preferences: triggering")
			return True
		else:
			Log("Duration is shorter than preferences: not triggering")
			return False

####################################################################################################
# Compare duration with preference
####################################################################################################

def get_transition_time(pref):
	if pref == "0 ms":
		transitiontime = 0
	elif pref == "400 ms":
		transitiontime = 4
	elif pref == "1 sec":
		transitiontime = 1 * 10
	elif pref == "2 secs":
		transitiontime = 2 * 10
	elif pref == "3 secs":
		transitiontime = 3 * 10
	elif pref == "5 secs":
		transitiontime = 5 * 10
	elif pref == "10 secs":
		transitiontime = 10 * 10
	elif pref == "15 secs":
		transitiontime = 15 * 10
	elif pref == "30 secs":
		transitiontime = 30 * 10
	elif pref == "45 secs":
		transitiontime = 45 * 10
	elif pref == "1 min":
		transitiontime = 60 * 10
	elif pref == "2 mins":
		transitiontime = 120 * 10
	elif pref == "5 mins":
		transitiontime = 300 * 10
	else:
		transitiontime = 4
	return transitiontime

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
				client_name_room = client_name + str(room)
				if not client_name_room in ACTIVE_CLIENTS:
					ACTIVE_CLIENTS.append(client_name_room)
				configuredusers = ReturnUsersFromClient(client_name, room)
				for username in configuredusers:
					if item.find('User').get('title') == username:
						if item.find('Player').get('state') == 'playing' and CURRENT_STATUS[client_name + str(room)] != item.find('Player').get('state') and compare_duration(duration=get_playing_item_duration(item, client_name, room), pref=ReturnFromClient(client_name, "min_duration", room)) is True:
							plex_is_playing(client_name=client_name, room=room, user=item.find('User').get('title'), gptitle=item.get('grandparentTitle'), title=item.get('title'), state=item.find('Player').get('state'), item=item, transition_type="transition_resumed")
							somethingwasdone = True
						elif item.find('Player').get('state') == 'paused' and CURRENT_STATUS[client_name + str(room)] != item.find('Player').get('state') and compare_duration(duration=get_playing_item_duration(item, client_name, room), pref=ReturnFromClient(client_name, "min_duration", room)) is True:
							plex_is_playing(client_name=client_name, room=room, user=item.find('User').get('title'), gptitle=item.get('grandparentTitle'), title=item.get('title'), state=item.find('Player').get('state'), item=item, transition_type="transition_paused")
							somethingwasdone = True
						CURRENT_MEDIA[client_name + str(room)] = item.get('key')
	
	if somethingwasdone is True:
		return False

	for client_name_room in CURRENT_STATUS:
		if not client_name_room in ACTIVE_CLIENTS:
			if not CURRENT_STATUS[client_name_room] == 'stopped' and not CURRENT_STATUS[client_name_room] == '':
				CURRENT_STATUS[client_name_room] = ''
				client_name = client_name_room[:-1]
				room = int(client_name_room[-1:])
				Log(time.strftime("%I:%M:%S") + " - Playback stopped on %s in room %s - Waiting for new playback" % (client_name, room));
				transitiontime = get_transition_time(ReturnFromClient(client_name, "transition_stopped", room))
				if isitdark(client_name, room) is True and compare_duration(duration=DURATIONS[client_name_room], pref=ReturnFromClient(client_name, "min_duration", room)) is True:
					choose_action("stopped", client_name, room, transitiontime)
					DURATIONS[client_name_room] = ''

def plex_is_playing(client_name, room, user, gptitle, title, state, item, transition_type):
	transitiontime = get_transition_time(ReturnFromClient(client_name, transition_type, room))
	if  CURRENT_STATUS[client_name + str(room)] == '':
		Log(time.strftime("%I:%M:%S") + " - New Playback (saving initial lights state): - %s %s %s - %s on %s in room %s."% (user, CURRENT_STATUS[client_name + str(room)], gptitle, title, client_name, room))
		hue.get_hue_light_initial_state(client_name, room)
		transitiontime = get_transition_time(ReturnFromClient(client_name, "transition_start", room))
	CURRENT_STATUS[client_name + str(room)] = state
	Log(time.strftime("%I:%M:%S") + " - %s %s %s - %s on %s in room %s." % (user, CURRENT_STATUS[client_name + str(room)], gptitle, title, client_name, room))
	if isitdark(client_name, room) is True and compare_duration(duration=get_playing_item_duration(item, client_name, room), pref=ReturnFromClient(client_name, "min_duration", room)) is True:
		choose_action(CURRENT_STATUS[client_name + str(room)], client_name, room, transitiontime)

####################################################################################################
# Choose action based on playback status and preferences
####################################################################################################

def choose_action(state, client_name, room, transitiontime):
	Log("Selecting action with transitiontime %s"%transitiontime)
	if ReturnFromClient(client_name, state, room) == "Turn Off":
		turn_off_lights(client_name, room, transitiontime)
		pass
	elif ReturnFromClient(client_name, state, room) == "Turn On":
		turn_on_lights(client_name, room, transitiontime)
		pass
	elif ReturnFromClient(client_name, state, room) == "Dim":
		dim_lights(client_name, room, transitiontime)
		pass
	elif ReturnFromClient(client_name, state, room) == "Reset":
		reset_lights(client_name, room, transitiontime)
		pass
	elif ReturnFromClient(client_name, state, room) == "Preset 1":
		set_light_preset(client_name, room, transitiontime, "1")
		pass
	elif ReturnFromClient(client_name, state, room) == "Preset 2":
		set_light_preset(client_name, room, transitiontime, "2")
		pass
	elif ReturnFromClient(client_name, state, room) == "Preset 3":
		set_light_preset(client_name, room, transitiontime, "3")
		pass
	elif ReturnFromClient(client_name, state, room) == "Preset 4":
		set_light_preset(client_name, room, transitiontime, "4")
		pass
	elif ReturnFromClient(client_name, state, room) == "Preset 5":
		set_light_preset(client_name, room, transitiontime, "5")
		pass
	elif ReturnFromClient(client_name, state, room) == "Nothing":
		Log("Doing nothing")
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

def set_light_preset(client_name, room, transitiontime, preset):
	Log("Setting lights to preset %s"%preset)
	try:
		Log(converter.hexToCIE1931(Prefs['HUE_PRESET_'+ preset +'_HEX']))
	except:
		Log("Wrong hex color, doing nothing")
	else:
		hue.update_light_state(powered=True, brightness=int(Prefs['HUE_PRESET_'+ preset +'_BRI']), client_name=client_name, room=room, transitiontime=transitiontime, xy=converter.hexToCIE1931(Prefs['HUE_PRESET_'+ preset +'_HEX']))
	pass

def reset_lights(client_name, room, transitiontime):
	Log("Reseting lights")
	hue.reset_lights_state(client_name, room, transitiontime)
	pass

def turn_off_lights(client_name, room, transitiontime):
	Log("Turning off lights")
	hue.update_light_state(powered=False, brightness=254, client_name=client_name, room=room, transitiontime=transitiontime, xy=None)
	pass

def turn_on_lights(client_name, room, transitiontime):
	Log("Turning on lights")
	hue.update_light_state(powered=True, brightness=254, client_name=client_name, room=room, transitiontime=transitiontime, xy=None)
	pass

def dim_lights(client_name, room, transitiontime):
	Log("Dimming lights")
	dim_value = ReturnFromClient(client_name, "dim", room)
	hue.update_light_state(powered=True, brightness=int(float(dim_value)), client_name=client_name, room=room, transitiontime=transitiontime, xy=None)
	pass

def watch_clients():
	global firstrun
	firstrun = True
	while True:
		plex_status = plex.get_plex_clients()
		now_active = []
		for item in plex_status.findall('Server'):
			now_active.append(item.get('name'))
			if firstrun is True:
				active_clients.append(item.get('name'))
		#Log("now_active: %s"%now_active)
		#Log("active_clients: %s"%active_clients)
		#Log("firstrun: %s"%firstrun)
		if firstrun is False:
			for client in now_active:
				if not client in active_clients:
					Log(ReturnRoomFromClient(client))
					Log("%s detected, doing something"%client)
					for roooms in ReturnRoomFromClient(client):
						choose_action("turned_on", client, roooms, get_transition_time(ReturnFromClient(client, "transition_on", roooms)))
					active_clients.append(client)
			for client in active_clients:
				if not client in now_active:
					Log(ReturnRoomFromClient(client))
					Log("%s went away, doing something"%client)
					for roooms in ReturnRoomFromClient(client):
						choose_action("turned_off", client, roooms, get_transition_time(ReturnFromClient(client, "transition_off", roooms)))
					active_clients.remove(client)
		if firstrun is True:
			Log("Setting firstrun to False")
			firstrun = False
		sleep(1)
