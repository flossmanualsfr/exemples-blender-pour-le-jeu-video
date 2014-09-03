#!/usr/bin/env python3
from pyOSC import OSCServer
import sys
import bge
from bge import logic
from time import sleep

server = OSCServer( ("localhost", 7120) )
server.timeout = 0
run = True

mycont=logic.getCurrentController()
joueur=mycont.owner

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
    self.timed_out = True

# funny python's way to add a method to an instance of a class
import types
server.handle_timeout = types.MethodType(handle_timeout, server)

def user_callback(path, tags, args, source):
    # which user will be determined by path:
    # we just throw away all slashes and join together what's left
    user = ''.join(path.split("/"))
    # tags will contain 'fff'
    # args is a OSCMessage with data
    # source is where the message came from (in case you need to reply)
    print ("Now do something with", user,args[0],args[1],args[2]) 
    joueur.localPosition.x=args[0]
    joueur.localPosition.y=args[1]
    joueur.localPosition.z=args[2]
    

#def quit_callback(path, tags, args, source):
#    # don't do this at home (or it'll quit blender)
#    global run
#    run = False
#    server.close()

server.addMsgHandler( "/user/1", user_callback )

#server.addMsgHandler( "/quit", quit_callback )

# user script that's called by the game engine every frame
def each_frame():
    # clear timed_out flag
    server.timed_out = False
    # handle all pending requests then return
    while not server.timed_out:
        server.handle_request()

# simulate a "game engine"

def quit():
    server.close()

