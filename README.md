HelloHue for Plex and Philips Hue
=================

##### Control your Philips Hue lights via Plex!

**Credits**
This Channel is based on PlexWink by vanstinator.

### Behavior

This channel detects when a media is playing, paused or stopped on your Plex Clients. Then it checks if it's a video, the client name, and the user who owns the stream. If it matches your criteria it triggers your lights with the actions you have set up.
You can also turn your lights on and off inside the channel.

### Configuration

The config is pretty simple and only needs to be done once. Configure your settings following the details below.
One room is composed of **one client**, **one or multiple users** and **one or multiple lights**, as well as the actions : on play, on stop, on pause, dim value, and only trigger if it's dark outside.

* ```Plex.tv login``` is your Plex login.
* ```Plex.tv passwords``` is your Plex password. It is only sent to plex.tv to get an identification token (so you must have a working internet access).
* ```Plex Server Address``` is the local adress to reach your server.
* ```Philips Hue Bridge Address``` is the ip address of your Philips Bridge.
* ```Nearest city from your location``` Used to calculate to calculate sunrise/sunset hours at your location.
* ```Activate HelloHue in room 1``` Tick to activate room 1 (and fill the client, users and lights settings for room 1).
* ```Name of plex client able to trigger in room 1``` You can find the list of users in PMS -> settings -> devices. Only put ONE client per room. If your have two clients in the same room, activate an other room and fill the settings with the other clients name and the same lights names.
* ```Name of the users able to trigger in room 1``` You can find the list of users in PMS -> settings -> users -> myhome. You can put multiple users (comma separated values, case sensitive).
* ```Name of the lights to trigger in room 1``` is the list of lights that will be triggered in room 1. You can put multiple users (comma separated values, case sensitive).
* ```When a media is playing in room 1``` is the action that will fire when a media is playing in room 1.
* ```When a media is paused in room 1``` is the action that will fire when a media is paused in room 1.
* ```When a media is stopped in room 1``` is the action that will fire when a media is stopped in room 1.
* ```Choose dim value in room 1``` is the value your lights will dim to. (20 is the min brightness and 240 is max)
* ```Randomize hue and saturation on Dim/Turn On in room 1``` will randomize your light color each time the action turn on or dim is fired.
* ```Only trigger lights if it's dark outside in room 1``` Tick to only trigger your lights between sunrise and sunset.
* ```Activate HelloHue in room 2``` Same thing as ```Activate HelloHue in room 1``` ...
* ...

### Usage

**How to install:**
* go to ```Library/Application Support/Plex Media Server/Plug-ins/```
* If existing, delete ```HelloHue.bundle```
* get the release you want from *https://github.com/ledge74/HelloHue/releases*
* unzip the release
* restart your plex media server!!!
* more indepth: see [article](https://support.plex.tv/hc/en-us/articles/201187656-How-do-I-manually-install-a-channel-) on Plex website. 

**On first run:**

1. Configure your Channel preferences (see above for help, make sure that you are connected to the internet as the channel will request a token from plex.tv)
2. Go to the channel (on any device)
3. If you see, ```Press button and your bridge and click to connect``` click on this menu AFTER having pressed the physical button of your bridge.
4. The click on ```Advanced``` --> ```Restart HelloHue```
5. If you see the menu ```My Lights``` then you are all good!
6. Enjoy :)

**Use the channel:**

* ```My Lights``` allows you to trigger your lights from the channel
* ```Enable HelloHue``` disable the channel (stop listening to items being played)
* ```Disable HelloHue``` resumes the channel (start listening to items being played)
* ```Advanced``` --> ```Restart HelloHue`` takes into account your new Plex.TV login/password if you updated it in the channel settings.

### How to report a bug and ask for features

If you have a problem with this channel, [raise an issue on GitHub](https://forums.plex.tv/discussion/193095/rel-hellohue-control-your-philips-hue-lights-via-plex) or on the [Plex Forums](https://forums.plex.tv/discussion/193095/rel-hellohue-control-your-philips-hue-lights-via-plex). Don't forget to add a Log file of this channel : https://support.plex.tv/hc/en-us/articles/200250417-Plex-Media-Server-Log-Files