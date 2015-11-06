#Control your Philips Hue lights via Plex!

**Behavior**

This channel detects when a media is playing, paused or stopped on your Plex Clients. Then it checks if it's a video, the client name, and the user who owns the stream. If it matches your criteria it triggers your lights with the actions you have set up.

**Configuration**

The config is pretty simple and only needs to be done once.


`Philips Hue Bridge Address` is the ip address of your Philips Bridge

`Philips Hue API username` is the username used to communicate with your Bridge. If you don't know leave it blank, and run the channel.

`Name of the lights to trigger` is the list of lights that will be affected by the channel

`Plex.tv login` is your Plex login.

`Plex.tv passwords` is your Plex password. It is only sent to plex.tv to get an identification token (so you must have a working internet access).

`Plex Server Address` is the local adress to reach your server.

`Name of the users able to trigger` You can find the list of users in PMS -> settings -> users -> myhome

`Name of plex clients able to trigger` You can find the list of users in PMS -> settings -> devices

All those parameters are case sensitive and comma separated.

**How to use**

On first run:

* Configure your Channel preferences (see above for help)
* Go to the channel (on any device)
* If you see, `Press button and your bridge and click to connect` click on this menu AFTER having pressed the physical button of your bridge.
* The click on `Restart HelloHue`
* If you see : `Disable HelloHue` and `Restart HelloHue`
* Enjoy :)

Use the channel:

`Disable HelloHue` pauses the channel
`Enable HelloHue` resume the channel
`Restart HelloHue` takes into account your new Plex.TV login/password if you change it in the channel settings.

**How to report a bug**

If you have a problem with this channel, raise an issue on GitHub. Don't forget to add a Log file of this channel : https://support.plex.tv/hc/en-us/articles/200250417-Plex-Media-Server-Log-Files

**Credits**
This Channel is based on PlexWink by vanstinator.