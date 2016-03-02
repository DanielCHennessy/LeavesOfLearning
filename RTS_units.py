# RTS_units.py
# units for RTS game
# January 2016
#

import pygame
import math
from RTS_defs import *
from RTS_GUI import smxtal_img
from RTS_buildings import Explosion

# running ID for units - start at 500,000
next_id_unit = 500001

class Unit():
    def __init__(self, whichtype, ident):
        self.x = -1
        self.y = -1
        self.ident = ident   # unique ID for each unit/building in game
        self.whichtype = whichtype   # What species or type of unit is this?
        self.displayname = "ChUcK NoRrIs"  # Display name (please overwrite this default)
        self.faction = 0    # To what team/faction do I belong?
        self.maxhp = 100
        self.hp = self.maxhp
        self.bleeding = 0   # hp per clock tick to bleed
        self.bleedtime = 0  # how many more clock ticks am I bleeding?
        self.xp = 0
        self.level = 1      # upgrade level
        self.maxv = 10      # max velocity pixels/clock tick
        self.width = 10     # width on screen in pixels
        self.height = 10
        self.heading = 0    # 0 = N, 1 = NE, 2 = E...
        self.attacking = 0  # ID of unit I'm attacking
        self.goal = 0       # tuple of coords where I'm walking
        self.clickradius = 50
        self.maintenance = 0 # maintenance cost in "maintenance units"
        self.training_timer = 0   # hbs until done training
        self.attackrate = 100 # clock ticks between attacks
        self.attacktimer = 0  # how many hbs until next possible attack?
        self.attackdamage = 10
        self.mybase = 0     # id of my command center
        self.aggro_radius = 500  # how many pixels away will we attack a spotted enemy?

        # todo: add maintenance cost, training timer

    def can_move(self):
        return True

    def move(self):
        if self.attacking:
            enemy = locate(self.attacking)
            if not enemy:
                self.attacking = 0   # enemy is dead
            elif distance( self, enemy ) < self.attackrange + enemy.clickradius:
                self.attack(enemy)    # attack instead of moving
                return
            else:
                self.goal = (enemy.x, enemy.y)  # move toward enemy
        if not self.goal:
            return
        direction = math.atan2(self.goal[1]-self.y, self.goal[0]-self.x)
        togo = distance(self, self.goal)
        if togo < self.maxv:
            (self.x, self.y) = self.goal
            self.goal = 0
        else:
            # todo: check if something is in the way so we don't walk through stuff
            xmove = int( self.maxv * math.cos(direction) )
            ymove = int( self.maxv * math.sin(direction) )
            self.x += xmove
            self.y += ymove
            imgpath = self.get_img_filename(direction)
            self.image = pygame.image.load(imgpath)

    def attack(self, enemy):
        if self.attacktimer > 0:
            self.attacktimer -= 1
            return
        self.attacktimer = self.attackrate  # reset attack timer
        enemy.hitme(self.attackdamage, self)
        self.xp += enemy.level
        # todo: implement checking for new level
        # display attack sprite here?
        #print "Unit %d attacking unit %d for damage %d"%(self.ident,enemy.ident,self.attackdamage)

    # gets image filename and also changes heading variable, since
    # I don't want to check direction twice.  Maybe this isn't the
    # best way to do it, though?
    def get_img_filename(self, direction):
        imgpath = self.imagestem
        if direction > 5*math.pi/8 and direction <= 7*math.pi/8:
            self.heading = 5
            imgpath += "sw"
        elif direction > 3*math.pi/8 and direction <= 5*math.pi/8:
            self.heading = 4
            imgpath += "s"
        elif direction > math.pi/8 and direction <= 3*math.pi/8:
            self.heading = 3
            imgpath += "se"
        elif direction > -math.pi/8 and direction <= math.pi/8:
            self.heading = 2
            imgpath += "e"
        elif direction > -3*math.pi/8 and direction <= -math.pi/8:
            self.heading = 1
            imgpath += "ne"
        elif direction > -5*math.pi/8 and direction <= -3*math.pi/8:
            self.heading = 0
            imgpath += "n"
        elif direction > -7*math.pi/8 and direction <= -5*math.pi/8:
            self.heading = 7
            imgpath += "nw"
        else:
            self.heading = 6
            imgpath += "w"
        if self.attacking:
            enemy = locate(self.attacking)
            if enemy and distance( self, enemy ) < self.attackrange + enemy.clickradius:
                imgpath += "_a"
        imgpath += ".png"
        return imgpath

    def checkbounds(self):
        if self.x - self.width//2 < 0:
            self.x = self.width//2
        elif self.x + self.width//2 > MAX_X:
            self.x = MAX_X - self.width//2
        if self.y - self.height//2 < 0:
            self.y = self.height//2
        elif self.y + self.height//2 > MAX_Y:
            self.y = MAX_Y - self.height//2

    def hitme(self, howmuch, fromwhere):
        # modify damage here with shields, etc...
        self.hp -= howmuch
        if (self.hp <= 0):
            self.die()
        # I just got attacked; consider attacking back?
        if not self.attacking:
            self.attacking = fromwhere.ident
            # todo: install list of units currently attacking us
            # instead of just storing the first one.  Also update
            # behavior here if our attacker dies somehow.

    def die(self):
        # spawn explosion graphic here?
        allunits.remove(self)
        expl = Explosion(self.width, 18*2)
        expl.x = self.x
        expl.y = self.y
        allobjects.append(expl)

    def heart_beat(self):
        # bleed, if necessary
        if (self.bleedtime > 0):
            self.hp -= self.bleeding
            self.bleedtime -= 1
            if (self.hp <= 0):
                self.die()
        else:
            self.bleeding = 0

        # attack our nearby enemy, if we haven't yet this hb?
        # this is currently implemented in move() which is called every
        # clock tick, so let's not repeat it... but maybe it ought to
        # move to here instead

        # If we're not attacking or doing something interesting,
        # check to see if there is an enemy nearby to attack:
        if self.aggro_radius > 0 and not self.attacking:
            for e in allunits + allbuildings:
                if e.faction != self.faction and distance(self,e) < self.aggro_radius:
                    self.attacking = e.ident
                    print "Unit",self.ident,"aggros to",e.ident
                    break
        

    def get_extra_status_graphics(self):
        # Mask this method so that your unit can display info besides
        # just its health bar to the status bar.  For example, charge
        # level, or how full a miner is with crystals would go in
        # this function.  Return a list of graphics.  See other units
        # for examples.
        return []

    def can_build(self):
        # list of tuples: ("unit type",crystal cost,gold cost,train time)
        return []

    def try_build(self, what):
        print "Attempting build", what

    def possible_actions(self):
        return []  # I'm not at all sure this is the best implementation

    def try_action(self,what):
        # called from the action button on the game status bar
        print "Attempting action", what
    

    
class Miner(Unit):  
    def __init__(self):
        global next_id_unit
        myid = next_id_unit
        next_id_unit += 1
        Unit.__init__(self, MINER, myid)
        self.image = pygame.image.load('RTS_images/miner_n.png')
        self.imagestem = 'RTS_images/miner_'
        self.width = 100
        self.height = 100
        self.displayname = "Miner"
        self.maxv = 5
        self.maxhp = 1000
        self.hp = self.maxhp
        self.attackrange = 120
        self.miningrange = 120
        self.attackdamage = 10
        self.attackrate = 20  # clock ticks between attacks
        self.miningrate = 1   # units of crystal per clock tick
        self.maxcarry = 1000  # how many units we can carry
        self.carry = 0        # how many units we're carrying right now
        self.maintenance = 1
        self.behavior = "idle"   # idle, attacking, mining, unloading
        self.aggro_radius = 0   # Miners are not aggressive to enemies

    def level_up(self):
        self.level += 1
        self.attackdamage += 20
        self.attackrate -= 100
        self.miningrate += 1
        self.maxcarry += 200

    def can_build(self):
        blist = [("Factory",0,10000,10000),
                 ("Supply Depot",0,10000,10000),
                 ("Barracks",0,10000,10000)]
        if self.level >= 2:
            blist.append( ("Laboratory",0,10000,10000) )
        if self.level >= 3:
            blist.append( ("Laser Turret",0,10000,10000) )
            blist.append( ("Mortar Turret",0,10000,10000) )
        if self.level >= 4:
            blist.append( ("Repair Bay",0,10000,10000) )
        return blist

    def get_extra_status_graphics(self):
        graphic = pygame.Surface((115,10))
        graphic.blit(smxtal_img, (0,0))
        pygame.draw.rect(graphic, black, [15,0,100,10])
        barlen = (self.carry * 100)//(self.maxcarry)
        pygame.draw.rect(graphic, purple, [15,0,barlen,10])
        return [ graphic ]

    def attack(self, enemy):
        # We need to mask this function for our miner because
        # I implemented mining using attack code... the miner just
        # attacks the crystal to mine it.
        if enemy and enemy.whichtype != CRYSTAL:
            Unit.attack(self,enemy)   # use inherited version for everything else
            self.behavior = "attacking"
            return

        self.behavior = "mining"
        if self.carry < self.maxcarry:
            enemy.mine_me(self.miningrate)
            self.carry += self.miningrate
            self.xp += 1
        else:
            # full; return to base to unload
            self.behavior = "unloading"
            mybase = locate(self.mybase)
            self.goal = (mybase.x,mybase.y)
            self.attacking = 0

    def move(self):
        # let's mask move() as well so we can handle miner behavior
        if self.behavior == "unloading":
            if distance(self,locate(self.mybase)) < self.miningrange:
                # unload and go find more crystal to mine
                print "Miner", self.ident, "unloading", self.carry, "crystal at base"
                add_resources(1,self.carry)
                self.carry = 0
                self.behavior = "mining"
                nearest_known_crystal = 0
                closest = 999999
                for e in allobjects:
                    if e.whichtype == CRYSTAL:
                        # for now just pretend we can see every crystal on map
                        # todo: implement fog of war checking?
                        dist = distance(self,e)
                        if dist < closest:
                            self.attacking = e.ident
                            closest = dist

        Unit.move(self)   # call inherited move() to, you know, actually move


class Soldier(Unit):  
    def __init__(self):
        global next_id_unit
        myid = next_id_unit
        next_id_unit += 1
        Unit.__init__(self, SOLDIER, myid)
        self.image = pygame.image.load('RTS_images/sprite_enemy_sphereprobe_0.png')
        self.imagestem = 'RTS_images/sprite_enemy_sphereprobe_'
        self.imgnum = 0
        self.imgtime = 0
        self.width = 90
        self.height = 96
        self.displayname = "Soldier"
        self.maxv = 12
        self.maxhp = 5000
        self.hp = self.maxhp
        self.attackrange = 320
        self.attackdamage = 80
        self.attackrate = 10  # clock ticks between attacks
        self.maintenance = 1

    def level_up(self):
        self.level += 1
        self.maxhp += 1000
        self.hp += 1000
        self.attackdamage += 10
        self.attackrate -= 1

    def get_img_filename(self, direction):
        # just use sphere probe without regard to heading
        return self.imagestem + str(self.imgnum) + ".png"

    def heart_beat(self):
        Unit.heart_beat(self)  # call inherited hb method
        self.imgtime += 1  # update sphere probe image
        if self.imgtime > 139:
            self.imgtime = 0
        self.imgnum = self.imgtime//10
        if self.imgtime % 10 == 0:
            self.image = pygame.image.load(self.get_img_filename(0))
        # regen health while out of combat?
        if self.hp < self.maxhp and not self.attacking:
            self.hp += 1


class Tank(Unit):  
    def __init__(self):
        global next_id_unit
        myid = next_id_unit
        next_id_unit += 1
        Unit.__init__(self, TANK, myid)
        self.image = pygame.image.load('RTS_images/smalltank_s.png')
        self.imagestem = 'RTS_images/smalltank_'
        self.width = 96
        self.height = 96
        self.displayname = "Tank"
        self.maxv = 8
        self.maxhp = 15000
        self.hp = self.maxhp
        self.attackrange = 500
        self.attackdamage = 250
        self.attackrate = 25  # clock ticks between attacks
        self.maintenance = 2

    def level_up(self):
        self.level += 1
        self.maxhp += 2000
        self.hp += 2000
        self.attackdamage += 20
        self.attackrate -= 1


