# RTS_0_1_0.py
# This is version 0.1.0 of a RTS game built using Pygame
# written by Dan Hennessy, January 2016
# intended for my programming students to modify and expand
#

import pygame
import time
import random
import socket
import sys
import Queue
import thread
import os

pygame.init()

from RTS_defs import *
from RTS_units import *
from RTS_buildings import *
from RTS_GUI import *

#pygame.init()

display_width = 800
display_height = 700 - 160
statusbar_height = 160

gameDisplay = pygame.display.set_mode((display_width,(display_height+statusbar_height)))
pygame.display.set_caption('RTS 0.1.0')
clock = pygame.time.Clock()

view_center = [MAX_X//2, MAX_Y//2]
zoom_level = 1

scroll_speed = 40

bgImg = pygame.image.load('RTS_images/Mars.jpg')
bg_w = 512
bg_h = 512

# currently selected unit or building:
selected = 0

# What faction are we?
myfaction = FACTION1

# Container to hold list of currently active buttons on the game status bar
masterButtonList = ButtonList()

# Grab music files from the music directory to throw to our mixer:
musiclist = [name for name in os.listdir("RTS_Sounds/music/.") if name.endswith(".wav")]
print "Found", len(musiclist), "music files:"
print musiclist
pygame.mixer.music.load("RTS_Sounds/music/"+musiclist[0])
pygame.mixer.music.play()
# todo: when this one finishes, just grab the next one in the list and play it
# so it loops through everything in the music directory
pygame.mixer.music.set_endevent(pygame.USEREVENT)
music_index = 0

def draw_bg():
    numx = (display_width*zoom_level)//(bg_w) + 2
    numy = (display_height*zoom_level)//(bg_h) + 2
    ulcorner = (view_center[0]-(display_width*zoom_level)//2, view_center[1]-(display_height*zoom_level)//2)
    (num2x, num2y) = (ulcorner[0]//bg_w, ulcorner[1]//bg_h)
    startx = (num2x*bg_w - view_center[0])//zoom_level + display_width//2
    starty = (num2y*bg_h - view_center[1])//zoom_level + display_height//2
    bgImgScaled = bgImg
    if zoom_level > 1:
        bgImgScaled = pygame.transform.scale(bgImg, (bg_w//zoom_level, bg_h//zoom_level))
    for i in range(numx):
        for j in range(numy):
            gameDisplay.blit(bgImgScaled,(startx + i*(bg_w//zoom_level), starty + j*(bg_h//zoom_level)))

def draw_units():
    pix_w = display_width*zoom_level
    pix_h = display_height*zoom_level
    for e in allunits:
        e_xrel = (e.x - view_center[0])//zoom_level + display_width//2
        e_yrel = (e.y - view_center[1])//zoom_level + display_height//2
        e_img = e.image
        if zoom_level > 0:  # just always scale unit images...
            e_img = pygame.transform.scale(e.image, (e.width//zoom_level, e.height//zoom_level))
        if e_xrel > -100 and e_xrel < pix_w+100:
            if e_yrel > -100 and e_yrel < pix_h+100:
                gameDisplay.blit(e_img,(e_xrel-(e.width//zoom_level)//2,e_yrel-(e.height//zoom_level)//2))
                graphic = healthbar(e, (e.width//zoom_level))
                gameDisplay.blit(graphic,(e_xrel-(e.width//zoom_level)//2,e_yrel-(e.height//zoom_level)//2))
                # todo: only display health bar if damaged?

def draw_buildings():
    pix_w = display_width*zoom_level
    pix_h = display_height*zoom_level
    for e in allbuildings:
        e_xrel = (e.x - view_center[0])//zoom_level + display_width//2
        e_yrel = (e.y - view_center[1])//zoom_level + display_height//2
        e_img = e.image
        if zoom_level > 0:
            e_img = pygame.transform.scale(e.image, (e.width//zoom_level, e.height//zoom_level))
        if e_xrel > -100 and e_xrel < pix_w+100:
            if e_yrel > -100 and e_yrel < pix_h+100:
                gameDisplay.blit(e_img,(e_xrel-(e.width//zoom_level)//2,e_yrel-(e.height//zoom_level)//2))
                graphic = healthbar(e, (e.width//zoom_level))
                gameDisplay.blit(graphic,(e_xrel-(e.width//zoom_level)//2,e_yrel-(e.height//zoom_level)//2))

def draw_objects():
    pix_w = display_width*zoom_level
    pix_h = display_height*zoom_level
    for e in allobjects:
        e_xrel = (e.x - view_center[0])//zoom_level + display_width//2
        e_yrel = (e.y - view_center[1])//zoom_level + display_height//2
        e_img = e.image
        if zoom_level > 0:
            e_img = pygame.transform.scale(e.image, (e.width//zoom_level, e.height//zoom_level))
        if e_xrel > -100 and e_xrel < pix_w+100:
            if e_yrel > -100 and e_yrel < pix_h+100:
                gameDisplay.blit(e_img,(e_xrel-(e.width//zoom_level)//2,e_yrel-(e.height//zoom_level)//2))

def draw_statusbar():
    # really inefficient, but I'm just going to redefine our buttons every clock update
    masterButtonList.clear()
    
    labeltext = pygame.font.Font('freesansbold.ttf', 12)
    pygame.draw.rect(gameDisplay, lightgray, [0, display_height, display_width, statusbar_height])
    # selection window
    pygame.draw.rect(gameDisplay, black, [50, display_height+24, 115, 115], 2)
    TextSurf, TextRect = text_objects("Selection", labeltext, black)
    TextRect.topleft = (80, display_height+5)
    gameDisplay.blit(TextSurf, TextRect)
    if selected:
        # image
        tinyimg = pygame.transform.scale(selected.image, (100,100))
        gameDisplay.blit(tinyimg, (57,display_height+31))

        # hpbar and info
        TextSurf, TextRect = text_objects(selected.displayname, labeltext, black)
        TextRect.topleft = (180, display_height+5)
        gameDisplay.blit(TextSurf, TextRect)
        gameDisplay.blit(smheart_img, (175, display_height+25))
        graphic = healthbar(selected, 100)
        gameDisplay.blit(graphic, (190, display_height+25))

        extra_graphics_list = selected.get_extra_status_graphics()
        pixht = display_height + 45
        for gg in extra_graphics_list:
            gameDisplay.blit( gg, (175, pixht) )
            pixht += gg.get_height() + 10

        # todo: display level and/or xpbar somehow

        # action list
        actionlist = selected.possible_actions()
        pygame.draw.rect(gameDisplay, black, [320, display_height+24, 150, 120], 2)
        TextSurf, TextRect = text_objects("Actions", labeltext, black)
        TextRect.topleft = (340, display_height+5)
        gameDisplay.blit(TextSurf, TextRect)

        pixht = display_height + 30
        for gg in actionlist:
            newb = button(325,pixht,120,20,darkgreen,green,gg[0],lambda x=gg[0],ob=selected:ob.try_action(x))
            masterButtonList.add_button(newb)
            newb.display(gameDisplay)
            pixht += 25

        # build list
        buildlist = selected.can_build()
        pygame.draw.rect(gameDisplay, black, [500, display_height+24, 150, 120], 2)
        TextSurf, TextRect = text_objects("Build", labeltext, black)
        TextRect.topleft = (520, display_height+5)
        gameDisplay.blit(TextSurf, TextRect)

        pixht = display_height + 30
        for gg in buildlist:
            newb = button(520,pixht,120,20,darkgreen,green,gg[0],lambda x=gg[0],ob=selected:ob.try_build(x))
            masterButtonList.add_button(newb)
            newb.display(gameDisplay)
            pixht += 25

    # resources
    pygame.draw.rect(gameDisplay, black, [660, display_height+24, 120, statusbar_height-48], 2)
    TextSurf, TextRect = text_objects("Resources", labeltext, black)
    TextRect.topleft = (690, display_height+5)
    gameDisplay.blit(TextSurf, TextRect)
    gameDisplay.blit(smxtal_img, (690, display_height+34))
    xtal_text = str(query_resources(1))
    TextSurf, TextRect = text_objects(xtal_text, labeltext, black)
    TextRect.topleft = (710, display_height+34)
    gameDisplay.blit(TextSurf, TextRect)
    gameDisplay.blit(smcash_img, (690, display_height+54))
    cashmoney_text = str(query_resources(2))
    TextSurf, TextRect = text_objects(cashmoney_text, labeltext, black)
    TextRect.topleft = (710, display_height+54)
    gameDisplay.blit(TextSurf, TextRect)
    # todo: display maintenance info here
    
            
def check_scroll_bounds(coords):
    newcoords = coords
    pix_w = display_width*zoom_level
    pix_h = display_height*zoom_level
    if (newcoords[0] < pix_w//2):
        newcoords[0] = pix_w//2
    elif (newcoords[0] > MAX_X - pix_w//2):
        newcoords[0] = MAX_X - pix_w//2
    if (newcoords[1] < pix_h//2):
        newcoords[1] = pix_h//2
    elif (newcoords[1] > MAX_Y - pix_h//2):
        newcoords[1] = MAX_Y - pix_h//2
    return newcoords

def get_selection(ex, ey):
    for e in (allunits + allbuildings + allobjects):
        if distance(e, (ex,ey) ) < e.clickradius:
            if e.faction == myfaction:
                return e
    return 0

def get_attack_target(ex, ey):
    for e in (allunits + allbuildings):
        #print "Querying unit", e.ident, "of faction", e.faction, "at dist", distance(e,(ex,ey))
        if distance(e, (ex,ey) ) < e.clickradius:
            if e.faction != myfaction:
                return e
    return 0

def get_any_click_target(ex, ey):
    for e in (allunits + allbuildings + allobjects):
        if distance(e, (ex,ey) ) < e.clickradius:
            return e
    return 0

# Intro screen: loaded before the game starts
def intro_screen():
    intro = True
    playbutton = button(150,450,150,100,darkgreen,green,"Set Up Game",do_game_setup)
    #quitbutton = button(450,450,150,100,darkred,red,"Quit",pygame.quit)
    networkbutton = button(400,450,200,100,darkred,red,"Join Network Game",set_up_network)
    solobutton = button(650,450,100,100,darkgray,lightgray,"Solo",do_solo_game)

    buttons = [ playbutton, networkbutton, solobutton ]

    while intro:
        mouse_pos = pygame.mouse.get_pos()
        (mousex, mousey) = mouse_pos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                whichbutton = event.button
                if event.button == 1:  # capture only left-click
                    for b in buttons:
                        if b.is_in_button(mousex,mousey):
                            b.clicked()
            
        gameDisplay.fill((190,50,50))
        TextSurf, TextRect = text_objects("Horrible RTS", largeText, white)
        TextRect.center = (400, 250)
        gameDisplay.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("Knockoff Game", largeText, white)
        TextRect.center = (400, 350)
        gameDisplay.blit(TextSurf, TextRect)

        playbutton.display(gameDisplay)
        networkbutton.display(gameDisplay)
        solobutton.display(gameDisplay)
        
        pygame.display.update()
        clock.tick(15)

def do_solo_game():
    global my_resources_1, my_resources_2, view_center
    
    # Just set up a one-player dummy game for demo purposes
    # remove this whole functionality when we have the game working
    # for real

    view_center = [2000, 8000]
    # set up player faction units:

    b = CommandCenter()
    b.x = 2000
    b.y = 8000
    b.faction = FACTION1
    allbuildings.append(b)
    
    e = Miner()
    e.x = 1750
    e.y = 8200
    e.faction = FACTION1
    e.mybase = 50001
    allunits.append(e)

    e = Soldier()
    e.x = 2750
    e.y = 8200
    e.faction = FACTION1
    e.mybase = 50001
    allunits.append(e)

    e = Soldier()
    e.x = 3750
    e.y = 8200
    e.faction = FACTION1
    e.mybase = 50001
    allunits.append(e)

    e = Tank()
    e.x = 3050
    e.y = 7800
    e.faction = FACTION1
    e.mybase = 50001
    allunits.append(e)

    # ...and enemy units / buildings:
    b = CommandCenter()
    b.x = 8000
    b.y = 2000
    b.faction = FACTION2
    allbuildings.append(b)

    b = LaserTurret()
    b.x = 7500
    b.y = 2500
    b.faction = FACTION2
    allbuildings.append(b)

    e = Soldier()
    e.x = 5050
    e.y = 5200
    e.faction = FACTION2
    e.mybase = 50002
    allunits.append(e)

    e = Soldier()
    e.x = 7750
    e.y = 2200
    e.faction = FACTION2
    e.mybase = 50002
    allunits.append(e)


    # add some crystals to the map
    for i in range(20+random.randrange(0,11)):
        e = Crystal()
        e.x = 1000 + random.randrange(0,3000)
        e.y = 2000 + random.randrange(0,7000)
        allobjects.append(e)

    # starting resources
    add_resources(1,1000)  # 1000 xtal, 0 cashmoney
    
    game_loop()

# Called from intro screen to set up a server
def do_game_setup():

    def setup_server():
        print "Setting up server..."
        # more stuff here

    try:
        localname = socket.getfqdn()
        # sometimes socket.getfqdn() returns the local name, and
        # sometimes it returns a full path that might cause gethostbyname()
        # to barf.  Try to avoid problems, catch them, and then try
        # another way if issues arise...
        if '.' in localname:
            localname = split(localname,'.')[0]
        my_IP = socket.gethostbyname(localname)
    except:
        # try using gethostname().  If this doesn't work either,
        # we're hosed and I'll just let the program crash here.
        my_IP = socket.gethostbyname(socket.gethostname())
        ##print "Error getting Server local IP address"
        ##pygame.quit()
        ##quit()

    my_port = 7501
    
    doing_setup = True
    found_open_port = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    startbutton = button(350,450,100,80,pygame.transform.scale(button1_img, (100,80)),
                         pygame.transform.scale(button1_hover_img, (100,80)),
                         "Start", setup_server, True)
    buttons = [ startbutton ]
    while doing_setup:
        mouse_pos = pygame.mouse.get_pos()
        (mousex, mousey) = mouse_pos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                whichbutton = event.button
                if event.button == 1:  # capture only left-click
                    for b in buttons:
                        if b.is_in_button(mousex,mousey):
                            b.clicked()
            
        #gameDisplay.fill((160,100,100))
        gameDisplay.blit(pygame.transform.scale(hex_bg, (800,600)), (0,0))
        
        gameDisplay.blit(pygame.transform.scale(blankWindow1, (527,600)), (136,0))
        TextSurf, TextRect = text_objects("Setting up Server at", smallText, white)
        TextRect.center = (400, 250)
        gameDisplay.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects(my_IP, smallText, white)
        TextRect.center = (400, 300)
        gameDisplay.blit(TextSurf, TextRect)

        while ( (not found_open_port) and my_port < 7600 ):
            try:
                sock.bind((my_IP,my_port))
                found_open_port = True
                print "Server starting up at", my_IP, "port", my_port
            except:
                my_port += 1

        TextSurf, TextRect = text_objects("port "+str(my_port), smallText, white)
        TextRect.center = (400, 350)
        gameDisplay.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("Waiting for client to join...", smallText, white)
        TextRect.center = (400, 400)
        gameDisplay.blit(TextSurf, TextRect)         

        startbutton.display(gameDisplay)
        
        pygame.display.update()
        clock.tick(15)        

# called from intro screen to find server and join a game as client
def set_up_network():
    doing_setup = True
    

def game_loop():
    global view_center, selected, zoom_level, music_index

    gameExit = False
    scrolling_right = 0
    scrolling_down = 0

    while not gameExit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            #print event

            if event.type == pygame.USEREVENT:
                music_index += 1
                if (music_index >= len(musiclist)):
                    music_index = 0
                pygame.mixer.music.load("RTS_Sounds/music/"+musiclist[music_index])
                pygame.mixer.music.play()
                pygame.mixer.music.set_endevent(pygame.USEREVENT)
                print "Music mixer started playing file",musiclist[music_index]

            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a):
                    scrolling_right = -scroll_speed
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d):
                    scrolling_right = scroll_speed

                if (event.key == pygame.K_UP or event.key == pygame.K_w):
                    scrolling_down = -scroll_speed
                elif (event.key == pygame.K_DOWN or event.key == pygame.K_s):
                    scrolling_down = scroll_speed

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or \
                    event.key == pygame.K_a or event.key == pygame.K_d:
                    scrolling_right = 0
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN or \
                    event.key == pygame.K_w or event.key == pygame.K_s:
                    scrolling_down = 0

            if event.type == pygame.MOUSEBUTTONDOWN:
                mousex, mousey = event.pos
                whichbutton = event.button
                rel_x = view_center[0] + zoom_level*(mousex - display_width//2)
                rel_y = view_center[1] + zoom_level*(mousey - display_height//2)

                if event.button == 1:   # left-click: select, attack
                    if (mousey < display_height):
                        # click is in play area, not in status bar
                        if not selected:
                            selected = get_selection(rel_x,rel_y)
                        else:
                            # are we trying to select something else, or tell
                            # our selected unit to attack?
                            new_e = get_selection(rel_x,rel_y)
                            if (new_e):
                                selected = new_e
                            else:
                                # attack, if it's rival faction unit/building:
                                new_e = get_attack_target(rel_x,rel_y)
                                if (selected and new_e):
                                    selected.attacking = new_e.ident
                                    print "Unit", selected.ident, "attacks", new_e.ident
                                # mine crystal, if we're a miner clicking on a crystal
                                if selected and selected.whichtype == MINER:
                                    new_e = get_any_click_target(rel_x,rel_y)
                                    if new_e and new_e.whichtype == CRYSTAL:
                                        selected.attacking = new_e.ident
                                        print "Miner", selected.ident, "mines", new_e.ident
                    else:
                        # click was in status bar; look for buttons we may have pressed
                        whichbutton = masterButtonList.getButtonByCoords(mousex,mousey)
                        if whichbutton:
                            whichbutton.clicked()
                        
                elif event.button == 3:   # right-click: move
                    if (mousey < display_height):
                        # click is in play area, not in status bar
                        if (selected and selected.can_move() ):
                            if ((rel_x > selected.width//2) and (rel_x < MAX_X-(selected.width//2)) \
                                and (rel_y > selected.height//2) and (rel_y < MAX_Y-(selected.height//2))):
                                selected.goal = (rel_x, rel_y)
                                if selected.attacking:
                                    selected.attacking = 0    # stop attacking if we just told you to move instead
                                # todo: add path finding in case stuff is in the way
                        
                elif event.button == 4:   # wheel scroll up: zoom in
                    if zoom_level > 1:
                        zoom_level -= 1
                        # todo: instead of zooming in with new center on mouse pointer,
                        # maybe we should zoom such that mouse pointer remains over
                        # same point on the map?
                        view_center = [ rel_x, rel_y ]
                elif event.button == 5:   # wheel scroll down: zoom out
                    if zoom_level < MAX_ZOOM_LEVEL:
                        zoom_level += 1

        view_center[0] += scrolling_right
        view_center[1] += scrolling_down
        view_center = check_scroll_bounds(view_center)

        for e in allunits:
            e.heart_beat()
            e.move()

        for e in allbuildings:
            e.heart_beat()

        for e in allobjects:
            e.heart_beat()

        draw_bg()
        draw_objects()
        draw_units()
        draw_buildings()
        draw_statusbar()
        
        pygame.display.update()
        clock.tick(60)

intro_screen()
#game_loop()
pygame.quit()
quit()
