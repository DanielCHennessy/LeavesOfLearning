# RTS_buildings.py
# buildings for RTS game
# January 2016
#

import pygame
import math
import random
from RTS_defs import *

# running ID for buildings - start at 50000
next_id_building = 50001

class Building():
    def __init__(self, whichtype, ident):
        self.x = -1
        self.y = -1
        self.ident = ident   # unique ID for each unit/building in game
        self.whichtype = whichtype   # What species or type of building is this?
        self.displayname = "Vomitorium"  # Display text (overwrite the default!)
        self.faction = 0    # To what team/faction do I belong?
        self.maxhp = 50000
        self.hp = self.maxhp
        self.bleeding = 0   # hp per clock tick to bleed
        self.bleedtime = 0  # how many more clock ticks am I bleeding?
        self.level = 1      # upgrade level
        self.width = 200    # width on screen in pixels
        self.height = 200
        self.heading = 0    # 0 = N, 1 = NE, 2 = E...
        self.attacking = 0  # ID of unit I'm attacking  (turrets can rotate and attack)
        self.clickradius = 200
        self.maintenance = 0 # maintenance cost in, uh, "maintenance units"
        self.supply = 0     # how many maintenance units this building supplies
        self.queue = []     # queue for build/actions to do
        self.timer = 0      # hbs left on current build/action
        self.maxtime = 1000 # hbs to do whatever we're doing/building

        # todo: add maintenance cost, training timer, can_build list,
        # queue for build/action, actions possible

    def can_move(self):
        return False

    def hitme(self, howmuch, fromwhere):
        # modify damage here with shields, etc...
        self.hp -= howmuch
        if (self.hp <= 0):
            self.die()

    def die(self):
        allbuildings.remove(self)
        expl = Explosion(self.width, 18*5)
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

    def get_extra_status_graphics(self):
        # see definition in RTS_units.py for what this does
        return []

    
class CommandCenter(Building):  
    def __init__(self):
        global next_id_building
        myid = next_id_building
        next_id_building += 1
        Building.__init__(self, COMMAND_CENTER, myid)
        self.image = pygame.image.load('RTS_images/CommandCenter.png')
        self.width = 400
        self.height = 400
        self.displayname = "Command Center"
        self.clickradius = 200
        self.maxhp = 100000
        self.hp = self.maxhp
        self.train_timer = 0
        self.miner_train_time = 2000    # in hbs... todo: find a better way of storing this info?
        self.miner_train_cost = 1000

    def level_up(self):
        self.level += 1
        self.maxhp += 10000
        self.hp += 10000

    # on select: load buttons, functions...

    def can_build(self):
        return [("Miner",self.miner_train_cost,0,self.miner_train_time)]

    def try_build(self, what):
        if what != "Miner":
            print "Command Center can only build miners so far"
            return
        if query_resources(R_CRYSTALS) < self.miner_train_cost:
            print "Insufficient crystals to build a miner"
            return
        if self.train_timer > 0:
            print "Already training something"
            return
        self.train_timer = self.miner_train_time
        add_resources(R_CRYSTALS, -1 * self.miner_train_cost)

    def heart_beat(self):
        Building.heart_beat(self)
        if self.train_timer > 0:
            self.train_timer -= 1
            if self.train_timer < 1:
                # We trained something
                # For now, it's always a miner
                from RTS_units import Miner
                e = Miner()
                e.x = self.x - 250
                e.y = self.y + 100
                e.faction = self.faction
                e.mybase = self.ident
                allunits.append(e)

    
    def get_extra_status_graphics(self):
        if self.train_timer < 1:
            return Building.get_extra_status_graphics(self)
        graphic = pygame.Surface((115,10))
        graphic.blit(pygame.transform.scale(pygame.image.load('RTS_images/miner_n.png'),(10,10)), (0,0))
        pygame.draw.rect(graphic, black, [15,0,100,10])
        barlen = ((self.miner_train_time - self.train_timer) * 100)//self.miner_train_time
        pygame.draw.rect(graphic, yellow, [15,0,barlen,10])
        return [ graphic ]

class LaserTurret(Building):  
    def __init__(self):
        global next_id_building
        myid = next_id_building
        next_id_building += 1
        Building.__init__(self, LASER_TURRET, myid)
        # fix image later, just a stationary bad one for now:
        self.image = pygame.image.load('RTS_images/sprite_enemy_smalltank_turret_3.png')
        self.width = 35*6
        self.height = 26*6
        self.displayname = "Laser Turret"
        self.clickradius = 200
        self.maxhp = 10000
        self.hp = self.maxhp
        self.heading = 5
        self.aggro_radius = 500    # this is basically the attack range
        self.attacking = 0
        self.attackrate = 10
        self.attacktimer = 0
        self.attackdamage = 100
        self.xp = 0  # will turrets use xp or be manually upgraded, or both?

    def level_up(self):
        self.level += 1
        self.maxhp += 1000
        self.hp += 1000
        self.attackdamage += 10

    def heart_beat(self):
        # mask hb method so turret can attack
        # this might need to go in a general turret class rather than
        # in each individual turret class definition
        Building.heart_beat(self)   # first call inherited hb
        # if we don't have a target, look for one:
        if not self.attacking:
            for e in allunits:
                if e.faction != self.faction and distance(self,e) < self.aggro_radius:
                    self.attacking = e.ident
                    print "Turret",self.ident,"aggros to",e.ident
                    break
        # If we have a target, attack it
        if self.attacking:
            enemy = locate(self.attacking)
            if not enemy:
                self.attacking = 0   # enemy is dead
            elif distance( self, enemy ) < self.aggro_radius:
                self.attack(enemy)    # attack instead of moving
                return

    def attack(self, enemy):
        if self.attacktimer > 0:
            self.attacktimer -= 1
            return
        self.attacktimer = self.attackrate  # reset attack timer
        enemy.hitme(self.attackdamage, self)
        self.xp += enemy.level

class Construction(Building):
    # Construction for what will eventually be a building
    def __init__(self):
        global next_id_building
        myid = next_id_building
        next_id_building += 1
        Building.__init__(self, CONSTRUCTION, myid)
        self.image = pygame.image.load('RTS_images/scaffolding.jpg')
        self.width = 400
        self.height = 400
        self.displayname = "Construction"
        self.clickradius = 200
        self.maxhp = 10000
        self.hp = self.maxhp

    def start_construction(self,whichtype,howlong):
        self.whichtype = whichtype
        self.maxtimer = howlong
        self.timer = howlong
        # todo: change image, size, displayname, etc here

    def heart_beat(self):
        Building.heart_beat(self)
        self.timer -= 1
        if self.timer < 1:
            # done with construction
            if self.whichtype == COMMAND_CENTER:
                b = CommandCenter()
            elif self.whichtype == LASER_TURRET:
                b = LaserTurret()
            else:
                # unknown building type: barf
                print "Unknown building type", self.whichtype
                return
            (b.x, b.y) = (self.x, self.y)
            allbuildings.append(b)
            allbuildings.remove(self)

    def get_extra_status_graphics(self):
        if self.timer < 1:
            return Building.get_extra_status_graphics(self)
        graphic = pygame.Surface((115,10))
        graphic.blit(smburst_img, (0,0)) # todo: better image: clock or something?
        pygame.draw.rect(graphic, black, [15,0,100,10])
        barlen = ((self.maxtimer - self.timer) * 100)//self.maxtimer
        pygame.draw.rect(graphic, yellow, [15,0,barlen,10])
        return [ graphic ]

### put buildings above this line, other objects below ##

class Object():
   # general object class used for crystals, things on the map that
   # aren't units or buildings...
   
    def __init__(self, whichtype, ident):
        self.x = -1
        self.y = -1
        self.ident = ident   # unique ID for each unit/building in game
        self.whichtype = whichtype   # What type of thing is this?
        self.displayname = "Random Thing"  # Display text (overwrite the default!)
        self.faction = 0    # In general random objects will probably have neutral faction
        self.maxhp = 1000000  # In general objects don't die
        self.hp = self.maxhp
        self.bleeding = 0   # hp per clock tick to bleed
        self.bleedtime = 0  # how many more clock ticks am I bleeding?
        self.level = 1      # upgrade level
        self.width = 200    # width on screen in pixels
        self.height = 200
        self.heading = 0    # 0 = N, 1 = NE, 2 = E...        
        self.clickradius = 200

    def can_move(self):
        return False

    def hitme(self, howmuch):
        # objects don't take damage in general
        pass

    def die(self):
        # in general, objects can't die, but let's define this anyway
        allobjects.remove(self)

    def heart_beat(self):
        # nothing to do every hb for most objects
        pass

    def get_extra_status_graphics(self):
        # see definition in RTS_units.py for what this does
        return []

class Crystal(Object):
    def __init__(self):
        global next_id_building
        myid = next_id_building
        next_id_building += 1
        Object.__init__(self, CRYSTAL, myid)
        whichtype = random.randrange(1,7)  # bad variable name, not self.whichtype
        whichfile = 'RTS_images/Crystal' + str(whichtype) + '.png'
        self.image = pygame.image.load(whichfile)
        if whichtype == 4:
            self.width = 65
            self.height = 50
        elif whichtype == 6:
            self.width = 64
            self.height = 54
        else:
            self.width = 50
            self.height = 50
        self.clickradius = 25

        self.maxfill = 5000 + random.randrange(0,5000)
        self.fill = self.maxfill

    def mine_me(self, howmuch):
        self.fill -= howmuch
        # todo: visual indication of fill level?
        if self.fill <= 0:
            # totally depleted; remove crystal
            self.die()  # OK, dumb way to handle it?
            # todo: when xtal gets depleted, miner stops mining but
            # ought to either go unload or find another xtal

class Explosion(Object):
    def __init__(self, size, timer):
        global next_id_building
        myid = next_id_building  # do explosions even need ids?  remove if not?
        next_id_building += 1
        Object.__init__(self, EXPLOSION, myid)
        self.size = size  # pixel size of explosion graphic
        self.timer = timer   # how many hbs to last
        self.stage = timer//18  # hbs per image change
        whichfile = 'RTS_images/sprite_explosion_medium_0.png'
        self.image = pygame.image.load(whichfile)
        self.image = pygame.transform.scale(self.image, (size,size))

    def heart_beat(self):
        self.timer -= 1
        if self.timer <= 0:
            allobjects.remove(self)
        else:
            for x in range(18):
                if self.timer < x*self.stage:
                    break
            whichfile = 'RTS_images/sprite_explosion_medium_'+str(17-x)+'.png'
            self.image = pygame.image.load(whichfile)
            self.image = pygame.transform.scale(self.image, (self.size,self.size))
            
