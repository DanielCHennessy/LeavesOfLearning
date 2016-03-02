# RTS_defs.py
# defs for RTS game
# January 2016
#

import types
import pygame

#pygame.init()

# colors
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
darkred = (200,0,0)
green = (0,255,0)
darkgreen = (0,200,0)
blue = (0,0,255)
yellow = (255,255,0)
lightgray = (200,200,200)
darkgray = (100,100,100)
purple = (220,100,200)

# factions (faction 0 reserved for neutral)
FACTION1 = 1
FACTION2 = 2

# map size
MAX_X = 10000
MAX_Y = 10000

MAX_ZOOM_LEVEL = 4

# units (starting at 100)
MINER = 101
SOLDIER = 102
HEAVY = 103
BIKE = 104
TANK = 105
ARTILLERY = 106
MEDIC = 107

# buildings (starting at 500)
COMMAND_CENTER = 501
SUPPLY_DEPOT = 502
BARRACKS = 503
FACTORY = 504
REPAIR_BAY = 505
LABORATORY = 506
LASER_TURRET = 507
MORTAR_TURRET = 508

# objects (starting at 800)
CRYSTAL = 800
EXPLOSION = 801

# resource type defs
R_CRYSTALS = 1
R_CASHMONEY = 2

# running ID for units and buildings
#next_id = 1001

# text/font defs
largeText = pygame.font.Font('freesansbold.ttf',72)
medText = pygame.font.Font('freesansbold.ttf',36)
smallText = pygame.font.Font('freesansbold.ttf',18)

def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

# function to return distance between 2 points (Pythagorean Thm)
# pass in either instances of classes (units or buildings) or
# just tuple locations
def distance(p1, p2):
    (x1, x2, y1, y2) = (0, 0, 0, 0)
    if type(p1) is tuple:
        (x1, y1) = (p1[0], p1[1])
    elif type(p1) is types.InstanceType:
        (x1, y1) = (p1.x, p1.y)
    if type(p2) is tuple:
        (x2, y2) = (p2[0], p2[1])
    elif type(p2) is types.InstanceType:
        (x2, y2) = (p2.x, p2.y)
    return int( ((x2-x1)**2 + (y2-y1)**2)**(0.5) )

# list of all units in game
allunits = []

# list of all buildings in game
allbuildings = []

# list of all objects in game except units/buildings
allobjects = []

# My current resources (different players will be running different instances of
# this game and so these variables point to the current player's resources
my_resources_1 = 0   # crystals
my_resources_2 = 0   # cashmoney

def add_resources(which, howmuch):
    global my_resources_1, my_resources_2
    if which == 1:
        my_resources_1 += howmuch
    elif which == 2:
        my_resources_2 += howmuch
    else:
        print "Attempt to add bad resource type", which

def query_resources(which):
    if which == 1:
        return my_resources_1
    elif which == 2:
        return my_resources_2
    else:
        print "Attempt to query bad resource type", which

# locate() finds a unit or building by its unique ID
def locate(tag):
    for e in allunits:
        if e.ident == tag:
            return e
    for e in allbuildings:
        if e.ident == tag:
            return e
    for e in allobjects:
        if e.ident == tag:
            return e
    return 0

def healthbar(unit, pixsize):
    bar_height = 10
    if pixsize < 50:
        bar_height = pixsize//5
    graphic = pygame.Surface((pixsize, bar_height))
    pygame.draw.rect(graphic, black, [0,0,pixsize,bar_height])
    barlen = (unit.hp * pixsize)//(unit.maxhp)
    if (10 * unit.hp < 3 * unit.maxhp):
        color = red
    elif (10 * unit.hp < 6 * unit.maxhp):
        color = yellow
    else:
        color = green
    pygame.draw.rect(graphic, color, [0,0,barlen,bar_height])
    return graphic
    
#pygame.quit()

# todo: code a check_collide() routine that checks if I can put down
# a thing of a certain height and width at some spot without putting
# it on top of something else that's already on the map
