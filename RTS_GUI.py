# RTS_GUI.py
# GUI elements (buttons, etc. for RTS game)
# Dan Hennessy, January 2006
#

import pygame
from RTS_defs import *

blankWindow1 = pygame.image.load('RTS_images/Blank_Window_1.png')  # 1186 x 1350
button1_img = pygame.image.load('RTS_images/Button1.png') # 317 x 116
button1_hover_img = pygame.image.load('RTS_images/Button1_hover.png')
hex_bg = pygame.image.load('RTS_images/BG.png') # 3000 x 2400

smheart_img = pygame.image.load('RTS_images/smheart.png')
smxtal_img = pygame.image.load('RTS_images/sm_xtal.png')
smcash_img = pygame.image.load('RTS_images/sm_cashmoney.png')
smburst_img = pygame.image.load('RTS_images/smburst.png')

class button():
    def __init__(self, x, y, w, h, inactive_color, active_color, text, action=None, disabled=False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        # button color: pass in just an RGB tuple to get a rectangle
        # with inactive and active (hover) coloring; pass in a Pygame
        # surface if you'd rather use an image.
        if (type(inactive_color) is tuple):
            self.inactive_color = inactive_color
            self.inactive_img = None
        else:
            self.inactive_color = None
            self.inactive_img = inactive_color
        if (type(active_color) is tuple):
            self.active_color = active_color
            self.active_img = None
        else:
            self.active_color = None
            self.active_img = active_color
        self.text = text
        self.textcolor = white
        self.action = action
        self.disabled = disabled
        
    def is_in_button(self,x,y):
        if ( self.x <= x <= (self.x + self.w) ) and ( self.y <= y <= (self.y + self.h) ):
            return True
        return False
    
    def clicked(self):
        if self.action and not self.disabled:
            self.action()

    def display(self, where):
        mouse_pos = pygame.mouse.get_pos()
        if self.is_in_button(mouse_pos[0],mouse_pos[1]):
            whichcolor = self.active_color
            whichimg = self.active_img
        else:
            whichcolor = self.inactive_color
            whichimg = self.inactive_img

        if self.disabled:
            if (whichcolor != None):
                whichcolor = (self.inactive_color[0]//2,
                              self.inactive_color[1]//2,
                              self.inactive_color[2]//2)    # total ugly hack
            elif (whichimg != None):
                # figure out how to "gray out" images later
                # probably using pygame.surfarray
                pass
        if (whichcolor != None):
            pygame.draw.rect(where, whichcolor, (self.x, self.y, self.w, self.h))
        else:
            where.blit(whichimg, (self.x, self.y))
        TextSurf, TextRect = text_objects(self.text, smallText, self.textcolor)
        TextRect.center = (self.x + (self.w//2) , self.y + (self.h//2))
        where.blit(TextSurf, TextRect)

class ButtonList:
    # container class to hold current lists of buttons on the
    # status bar and (maybe later) what they do

    def __init__(self):
        self.buttonlist = []

    def add_button(self, b):
        self.buttonlist.append(b)

    def clear(self):
        self.buttonlist = []

    def getButtonByCoords(self,x,y):
        for b in self.buttonlist:
            if b.is_in_button(x,y):
                return b
        return None
                

