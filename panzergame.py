"""
authors: Anton Schmidt, Peter van der Linden
email: peter@vanderlinden.at
license: gpl, see http://www.gnu.org/licenses/gpl-3.0.de.html
download: https://github.com/petzivienna/panzergame
idea: vertical shooter with python3 and pygame
"""
import pygame
import random
import os
#import time
#import math

"""Best game: 10 waves by Ines"""

def randomize_color(color, delta=50):
    d=random.randint(-delta, delta)
    color = color + d
    color = min(255,color)
    color = max(0, color)
    return color

def make_text(msg="pygame is cool", fontcolor=(255, 0, 255), fontsize=42, font=None):
    """returns pygame surface with text. You still need to blit the surface."""
    myfont = pygame.font.SysFont(font, fontsize)
    mytext = myfont.render(msg, True, fontcolor)
    mytext = mytext.convert_alpha()
    return mytext

def write(background, text, x=50, y=150, color=(0,0,0),
          fontsize=None, center=False):
        """write text on pygame surface. """
        if fontsize is None:
            fontsize = 24
        font = pygame.font.SysFont('mono', fontsize, bold=True)
        fw, fh = font.size(text)
        surface = font.render(text, True, color)
        if center: # center text around x,y
            background.blit(surface, (x-fw//2, y-fh//2))
        else:      # topleft corner is x,y
            background.blit(surface, (x,y))

def elastic_collision(sprite1, sprite2):
        """elasitc collision between 2 VectorSprites (calculated as disc's).
           The function alters the dx and dy movement vectors of both sprites.
           The sprites need the property .mass, .radius, pos.x pos.y, move.x, move.y
           by Leonard Michlmayr"""
        if sprite1.static and sprite2.static:
            return
        dirx = sprite1.pos.x - sprite2.pos.x
        diry = sprite1.pos.y - sprite2.pos.y
        sumofmasses = sprite1.mass + sprite2.mass
        sx = (sprite1.move.x * sprite1.mass + sprite2.move.x * sprite2.mass) / sumofmasses
        sy = (sprite1.move.y * sprite1.mass + sprite2.move.y * sprite2.mass) / sumofmasses
        bdxs = sprite2.move.x - sx
        bdys = sprite2.move.y - sy
        cbdxs = sprite1.move.x - sx
        cbdys = sprite1.move.y - sy
        distancesquare = dirx * dirx + diry * diry
        if distancesquare == 0:
            dirx = random.randint(0,11) - 5.5
            diry = random.randint(0,11) - 5.5
            distancesquare = dirx * dirx + diry * diry
        dp = (bdxs * dirx + bdys * diry) # scalar product
        dp /= distancesquare # divide by distance * distance.
        cdp = (cbdxs * dirx + cbdys * diry)
        cdp /= distancesquare
        if dp > 0:
            if not sprite2.static:
                sprite2.move.x -= 2 * dirx * dp
                sprite2.move.y -= 2 * diry * dp
            if not sprite1.static:
                sprite1.move.x -= 2 * dirx * cdp
                sprite1.move.y -= 2 * diry * cdp

class Flytext(pygame.sprite.Sprite):
    def __init__(self, x, y, text="hallo", color=(255, 0, 0),
                 dx=0, dy=-50, duration=2, acceleration_factor = 1.0, delay = 0, fontsize=22):
        """a text flying upward and for a short time and disappearing"""
        self._layer = 7  # order of sprite layers (before / behind other sprites)
        pygame.sprite.Sprite.__init__(self, self.groups)  # THIS LINE IS IMPORTANT !!
        self.text = text
        self.r, self.g, self.b = color[0], color[1], color[2]
        self.dx = dx
        self.dy = dy
        self.x, self.y = x, y
        self.duration = duration  # duration of flight in seconds
        self.acc = acceleration_factor  # if < 1, Text moves slower. if > 1, text moves faster.
        self.image = make_text(self.text, (self.r, self.g, self.b), fontsize)  # font 22
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.time = 0 - delay

    def update(self, seconds):
        self.time += seconds
        if self.time < 0:
            self.rect.center = (-100,-100)
        else:
            self.y += self.dy * seconds
            self.x += self.dx * seconds
            self.dy *= self.acc  # slower and slower
            self.dx *= self.acc
            self.rect.center = (self.x, self.y)
            if self.time > self.duration:
                self.kill()      # remove Sprite from screen and from groups

class Mouse(pygame.sprite.Sprite):
    def __init__(self, radius = 50, color=(255,0,0), x=320, y=240,
                    startx=100,starty=100, control="mouse", ):
        """create a (black) surface and paint a blue Mouse on it"""
        self._layer=10
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.radius = radius
        self.color = color
        self.startx=startx
        self.starty=starty
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.r = color[0]
        self.g = color[1]
        self.b = color[2]
        self.delta = -10
        self.age = 0
        self.pos = pygame.mouse.get_pos()
        self.move = 0
        self.tail=[]
        self.create_image()
        self.rect = self.image.get_rect()
        self.control = control # "mouse" "keyboard1" "keyboard2"
        self.pushed = False

    def create_image(self):

        self.image = pygame.surface.Surface((self.radius*0.5, self.radius*0.5))
        delta1 = 12.5
        delta2 = 25
        w = self.radius*0.5 / 100.0
        h = self.radius*0.5 / 100.0
        # pointing down / up
        for y in (0,2,4):
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (35*w,0+y),(50*w,15*h+y),2)
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (50*w,15*h+y),(65*w,0+y),2)

            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (35*w,100*h-y),(50*w,85*h-y),2)
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (50*w,85*h-y),(65*w,100*h-y),2)
        # pointing right / left
        for x in (0,2,4):
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (0+x,35*h),(15*w+x,50*h),2)
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (15*w+x,50*h),(0+x,65*h),2)

            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (100*w-x,35*h),(85*w-x,50*h),2)
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (85*w-x,50*h),(100*w-x,65*h),2)
        self.image.set_colorkey((0,0,0))
        self.rect=self.image.get_rect()
        self.rect.center = self.x, self.y

    def update(self, seconds):
        if self.control == "mouse":
            self.x, self.y = pygame.mouse.get_pos()
        elif self.control == "keyboard1":
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_LSHIFT]:
                delta = 2
            else:
                delta = 9
            if pressed[pygame.K_w]:
                self.y -= delta
            if pressed[pygame.K_s]:
                self.y += delta
            if pressed[pygame.K_a]:
                self.x -= delta
            if pressed[pygame.K_d]:
                self.x += delta
        elif self.control == "keyboard2":
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_RSHIFT]:
                delta = 2
            else:
                delta = 9
            if pressed[pygame.K_UP]:
                self.y -= delta
            if pressed[pygame.K_DOWN]:
                self.y += delta
            if pressed[pygame.K_LEFT]:
                self.x -= delta
            if pressed[pygame.K_RIGHT]:
                self.x += delta
        elif self.control == "joystick1":
            pass
        elif self.control == "joystick2":
            pass
        if self.x < 0:
            self.x = 0
        elif self.x > Viewer.width:
            self.x = Viewer.width
        if self.y < 0:
            self.y = 0
        elif self.y > Viewer.height:
            self.y = Viewer.height
        self.tail.insert(0,(self.x,self.y))
        self.tail = self.tail[:128]
        self.rect.center = self.x, self.y
        self.r += self.delta   # self.r can take the values from 255 to 101
        if self.r < 151:
            self.r = 151
            self.delta = 10
        if self.r > 255:
            self.r = 255
            self.delta = -10
        self.create_image()

class VectorSprite(pygame.sprite.Sprite):
    """base class for sprites. this class inherits from pygames sprite class"""
    number = 0
    numbers = {} # { number, Sprite }

    def __init__(self, **kwargs):
        self._default_parameters(**kwargs)
        self._overwrite_parameters()
        pygame.sprite.Sprite.__init__(self, self.groups) #call parent class. NEVER FORGET !
        self.number = VectorSprite.number # unique number for each sprite
        VectorSprite.number += 1
        VectorSprite.numbers[self.number] = self
        #if "color" not in kwargs:
        #    self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        self.create_image()
        self.distance_traveled = 0 # in pixel
        self.rect.center = (-300,-300) # avoid blinking image in topleft corner
        if self.angle != 0:
            self.set_angle(self.angle)
        self.tail = []

    def _overwrite_parameters(self):
        """change parameters before create_image is called"""
        pass

    def _default_parameters(self, **kwargs):
        """get unlimited named arguments and turn them into attributes
           default values for missing keywords"""

        for key, arg in kwargs.items():
            setattr(self, key, arg)
        if "layer" not in kwargs:
            self._layer = 4
        else:
            self._layer = self.layer
        if "static" not in kwargs:
            self.static = False
        if "pos" not in kwargs:
            self.pos = pygame.math.Vector2(random.randint(0, Viewer.width),-50)
        if "move" not in kwargs:
            self.move = pygame.math.Vector2(0,0)
        if "friction" not in kwargs:
            self.friction = 1.0 # no friction
        if "radius" not in kwargs:
            self.radius = 5
        if "width" not in kwargs:
            self.width = self.radius * 2
        if "height" not in kwargs:
            self.height = self.radius * 2

        if "hitpoints" not in kwargs:
            self.hitpoints = 100
        self.hitpointsfull = self.hitpoints # makes a copy
        if "mass" not in kwargs:
            self.mass = 10
        if "damage" not in kwargs:
            self.damage = 10
        if "bounce_on_edge" not in kwargs:
            self.bounce_on_edge = False
        if "kill_on_edge" not in kwargs:
            self.kill_on_edge = False
        if "angle" not in kwargs:
            self.angle = 0 # facing right?
        if "max_age" not in kwargs:
            self.max_age = None
        if "max_distance" not in kwargs:
            self.max_distance = None
        if "picture" not in kwargs:
            self.picture = None
        if "bossnumber" not in kwargs:
            self.bossnumber = None
        if "kill_with_boss" not in kwargs:
            self.kill_with_boss = False
        if "sticky_with_boss" not in kwargs:
            self.sticky_with_boss = False
        if "mass" not in kwargs:
            self.mass = 15
        if "upkey" not in kwargs:
            self.upkey = None
        if "downkey" not in kwargs:
            self.downkey = None
        if "rightkey" not in kwargs:
            self.rightkey = None
        if "leftkey" not in kwargs:
            self.leftkey = None
        if "speed" not in kwargs:
            self.speed = None
        if "age" not in kwargs:
            self.age = 0 # age in seconds
        if "warp_on_edge" not in kwargs:
            self.warp_on_edge = False
        if "gravity" not in kwargs:
            self.gravity = None
        if "survive_north" not in kwargs:
            self.survive_north = False
        if "survive_south" not in kwargs:
            self.survive_south = False
        if "survive_west" not in kwargs:
            self.survive_west = False
        if "survive_east" not in kwargs:
            self.survive_east = False
        if "speed" not in kwargs:
            self.speed = 0
        if "color" not in kwargs:
            self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

    def kill(self):
        if self.number in self.numbers:
           del VectorSprite.numbers[self.number] # remove Sprite from numbers dict
        pygame.sprite.Sprite.kill(self)

    def create_image(self):
        if self.picture is not None:
            self.image = self.picture.copy()
        else:
            self.image = pygame.Surface((self.width,self.height))
            self.image.fill((self.color))
        self.image = self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect= self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height

    def rotate(self, by_degree):
        """rotates a sprite and changes it's angle by by_degree"""
        self.angle += by_degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def set_angle(self, degree):
        """rotates a sprite and changes it's angle to degree"""
        self.angle = degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def update(self, seconds):
        """calculate movement, position and bouncing on edge"""
        # ----- kill because... ------
        if self.hitpoints <= 0:
            self.kill()
        if self.max_age is not None and self.age > self.max_age:
            self.kill()
        if self.max_distance is not None and self.distance_traveled > self.max_distance:
            self.kill()
        # ---- movement with/without boss ----
        if self.bossnumber is not None:
            if self.kill_with_boss:
                if self.bossnumber not in VectorSprite.numbers:
                    self.kill()
            if self.sticky_with_boss and self.bossnumber in VectorSprite.numbers:
                boss = VectorSprite.numbers[self.bossnumber]
                self.pos = pygame.math.Vector2(boss.pos.x, boss.pos.y)
                self.set_angle(boss.angle)
        self.pos += self.move * seconds
        self.move *= self.friction
        self.distance_traveled += self.move.length() * seconds
        self.age += seconds
        self.wallbounce()
        self.rect.center = ( round(self.pos.x, 0), -round(self.pos.y, 0) )

    def wallbounce(self):
        # ---- bounce / kill on screen edge ----
        # ------- left edge ----
        if self.pos.x < 0:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.x = 0
                self.move.x *= -1
            elif self.warp_on_edge:
                self.pos.x = Viewer.width
        # -------- upper edge -----
        if self.pos.y  > 0:
            if self.kill_on_edge and not self.survive_north:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.y = 0
                self.move.y *= -1
            elif self.warp_on_edge:
                self.pos.y = -Viewer.height
        # -------- right edge -----
        if self.pos.x  > Viewer.width:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.x = Viewer.width
                self.move.x *= -1
            elif self.warp_on_edge:
                self.pos.x = 0
        # --------- lower edge ------------
        if self.pos.y   < -Viewer.height:
            if self.kill_on_edge:
                self.hitpoints = 0
                self.kill()
            elif self.bounce_on_edge:
                self.pos.y = -Viewer.height
                self.move.y *= -1
            elif self.warp_on_edge:
                self.pos.y = 0


class Triangle(VectorSprite):
    
    
    def _overwrite_parameters(self):
        self.pos = pygame.math.Vector2(random.randint(
                   0, Viewer.width) , -1)
        self.kill_on_edge = True
        self.move = pygame.math.Vector2(
                        random.randint(-20,20),
                       -random.randint(50,175))
    
    def create_image(self):
        self.image = pygame.Surface((50,50))
        bild = random.choice ((1,2,3,4)) #
        if bild == 1:
            #deltaflügler
            pygame.draw.line(self.image, (200,0,0), (0,0), (40,0),3)
            pygame.draw.line(self.image, (200,0,0), (0,0), (20,40),3)
            pygame.draw.line(self.image, (200,0,0), (20,40), (40,0),3)
            #rufzeichen
            pygame.draw.line(self.image, (0,0,255), (20,25), (20,0),7)
            #triebwerke
            pygame.draw.line(self.image, (0,0,255), (0,0), (0,40),1)
            pygame.draw.line(self.image, (0,0,255), (40,0), (40,40),3)
        if bild == 2:
            #Tie-fighter
            pygame.draw.line(self.image, (0,0,255), (20,0), (40,20),3)
            pygame.draw.line(self.image, (0,0,255), (40,20), (20,40),3)
            pygame.draw.line(self.image, (0,0,255), (20,40), (0,20),3)
            pygame.draw.line(self.image, (0,0,255), (0,20), (20,0),3)
            pygame.draw.line(self.image, (0,0,255), (0,0), (0,40),3)
            pygame.draw.line(self.image, (0,0,255), (40,0), (40,40),3)
            pygame.draw.circle(self.image, (255,0,0), (20,20),11,2)
            pygame.draw.line(self.image, (255,0,0), (9,20), (31,20),2)
            pygame.draw.line(self.image, (255,0,0), (20,9), (20,31),2)
        if bild == 3:
            # pingufighter
            pygame.draw.polygon(self.image, (255,0,0),[(20,0), (40,40), (0,40)]   )
            pygame.draw.circle(self.image, (0,0,255), (20,20), 10)
        if bild == 4:
            # pentagramm
            pygame.draw.polygon(self.image,(255,0,0),[(15,0),(50,20),(10,50),(40,0),(38,40)])    
            
            
        #gemeinsamer Teil   
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        
class Plasma(VectorSprite):
    
    def _overwrite_parameters(self):
         self.kill_on_edge = True
         self.radius = 10
         self.delta = 1
         self.damage = 50
         
    def create_image(self):
        self.image = pygame.Surface((self.radius*2,self.radius*2))
        r = 255
        g = 255
        b = random.randint(128,255)
        pygame.draw.circle(self.image, (r,g,b), (self.radius,self.radius), self.radius)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        
    def update(self, seconds):
        VectorSprite.update(self, seconds)
        self.radius += self.delta
        if self.radius > 20:
            self.radius = 20
            self.delta = -1
        if self.radius < 10:
            self.radius = 10
            self.delta = 1
        oldcenter = self.rect.center
        self.create_image()
        self.rect.center = oldcenter



class PowerUp(VectorSprite):

    def _overwrite_parameters(self):
        self.pos = pygame.math.Vector2(random.randint(
                   0, Viewer.width) , -1)
        self.kill_on_edge = True
        self.move = pygame.math.Vector2(
                        random.randint(-20,20),
                       -random.randint(50,175))
        self._layer = 4
        self.angle = 270
        self.hitpoints = 4
        self.color = random.choice(((255,0,0), (0,255,0),
                                    (0,0,255)
                                  ))
          #                          (255,0,255), ( 255,255,0), (0,255,255),
          #                          (125,128,128),(255,255,255)))

    def create_image(self):
        self.image = pygame.Surface((40,40))
        pygame.draw.circle(self.image, self.color, (20,20), 20)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()


class Enemy1(VectorSprite):

    def _overwrite_parameters(self):
        #self.pos = pygame.math.Vector2(random.randint(
        #           0, Viewer.width) , -1)
        self.kill_on_edge = True
        self.survive_north = True
        self.move = pygame.math.Vector2(0,-random.randint(50,100))
        self._layer = 4
        self.angle = 270
        self.hitpoints = 40


    def create_image(self):
        self.image = Viewer.images["enemy1"]
        #self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

    def update(self,seconds):
        VectorSprite.update(self,seconds)
        self.ai()
        self.fire()

    def ai(self):
        #pass
        if self.pos.y < 0 and random.random() < 0.2:
            self.move += pygame.math.Vector2(random.choice((-7,-5,-2,-1,1,2,5,7)),random.choice((-3,-2,-1,1,2,3)))

    def fire(self):
        if random.random() < 0.03:
            Viewer.panzersound1.play()
            a = random.randint(130,220)
            v = pygame.math.Vector2(0,250)
            v.rotate_ip(a)
            Evilrocket(pos=pygame.math.Vector2(self.pos.x,
                                   self.pos.y), angle=a+90,
                                   move=v+self.move, max_age=10,
                                   kill_on_edge=True, color=self.color)
            # --- mzzleflash 25, 0  vor raumschiff
            #p = pygame.math.Vector2(25,0)
            #p.rotate_ip(self.angle)
            #Muzzle_flash(pos=pygame.math.Vector2(self.pos.x, self.pos.y) + p, max_age=0.1, angle = self.angle)

class Enemy2(Enemy1):

    def _overwrite_parameters(self):
        self.kill_on_edge = True
        self.survive_north = True
        self.move = pygame.math.Vector2(
                      0,-random.randint(10,25))
        self._layer = 4
        self.angle = 270
        self.hitpoints = 120
        self.speeds = [100,150,200,250]


    def create_image(self):
        self.image = Viewer.images["enemy2"]
        #self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

    def update(self,seconds):
        VectorSprite.update(self,seconds)
        #self.ai()
        self.fire()

    def firesound(self):
        Viewer.panzersound2.play()
 
    def fire(self):
        if random.random() < 0.005:
            self.firesound()
            
            a = random.randint(260,280)
            #sspeeds = [100,150,200,250]
            for speed in self.speeds:
                v = pygame.math.Vector2(speed, 0)
                v.rotate_ip(a)
                Evilrocket(pos=pygame.math.Vector2(self.pos.x,
                                   self.pos.y), angle=a+0,
                                   move=v+self.move, max_age=10,
                                   kill_on_edge=True, color=self.color)


class Enemy3(Enemy2):

    def _overwrite_parameters(self):
        Enemy2._overwrite_parameters(self)
        self.move = pygame.math.Vector2(
                      0.5,-random.randint(00,50))
        self.hitpoints = 550
        self.speeds = [100,150,200,250,260,270,280,290]


    def fire(self):
        """shoot a salvo towards a player"""
        
        if random.random() < 0.0095:
            Viewer.panzersound3.play()
            targets = []
            for player in [0,1]:
                if player in VectorSprite.numbers:
                   targets.append(VectorSprite.numbers[player])
            if len(targets) == 0:
                return
            t = random.choice(targets)
            rightvector = pygame.math.Vector2(10,0)
            diffvector = t.pos - self.pos
            a = rightvector.angle_to(diffvector)
            #a = random.randint(260,280)
            speeds = [200,220,240,260,280,300,320,340]
            for speed in speeds:
                v = pygame.math.Vector2(speed, 0)
                v.rotate_ip(a)
                Evilrocket(pos=pygame.math.Vector2(self.pos.x,
                                   self.pos.y), angle=a+0,
                                   move=v+self.move, max_age=10,
                                   kill_on_edge=True, color=self.color)


    def create_image(self):
        self.image = Viewer.images["tank1"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        
    def firesound(self):
        Viewer.panzersound2.play()
 
class Enemy4(Enemy2):

    def _overwrite_parameters(self):
        Enemy2._overwrite_parameters(self)
        self.move = pygame.math.Vector2(
                      1,-random.randint(10,25))
        self.hitpoints = 110

    def create_image(self):
        self.image = Viewer.images["tank2"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        
    def firesound(self):
        Viewer.panzersound4.play()
    
class Enemy5(Enemy2):

    def _overwrite_parameters(self):
        Enemy2._overwrite_parameters(self)
        self.move = pygame.math.Vector2(
                      -0.5,-random.randint(10,25))
        self.hitpoints = 105

    def create_image(self):
        self.image = Viewer.images["tank2"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        
    def firesound(self):
        Viewer.panzersound5.play()
 
class Enemy6(Enemy2):

    def _overwrite_parameters(self):
        Enemy2._overwrite_parameters(self)
        self.move = pygame.math.Vector2(
                      -1,-random.randint(10,25))
        self.hitpoints = 100

    def create_image(self):
        self.image = Viewer.images["tank3"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        
    def firesound(self):
        Viewer.panzersound6.play()
 

class Enemy7(Enemy2):

    def _overwrite_parameters(self):
        Enemy2._overwrite_parameters(self)
        self.move = pygame.math.Vector2(
                      0,-random.randint(10,25))
        self.hitpoints = 150

    def create_image(self):
        self.image = Viewer.images["tank4"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

class Enemy8(Enemy2):

    def _overwrite_parameters(self):
        Enemy2._overwrite_parameters(self)
        self.move = pygame.math.Vector2(
                      0,-random.randint(10,25))
        self.hitpoints = 130

    def create_image(self):
        self.image = Viewer.images["tank5"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

class Enemy9(Enemy2):

    def _overwrite_parameters(self):
        Enemy2._overwrite_parameters(self)
        self.move = pygame.math.Vector2(
                      2,-random.randint(10,25))
        self.hitpoints = 100

    def create_image(self):
        self.image = Viewer.images["tank6"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

class Enemy10(Enemy2):

    def _overwrite_parameters(self):
        Enemy2._overwrite_parameters(self)
        self.move = pygame.math.Vector2(
                      -2,-random.randint(10,25))
        self.hitpoints = 100

    def create_image(self):
        self.image = Viewer.images["tank7"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()



class Bunker1(VectorSprite):
    
    def _overwrite_parameters(self):
        
        Enemy2._overwrite_parameters(self)
        self.move = pygame.math.Vector2(0,-5)
        self.angle = -90
        self.hitpoints = 2500
        
        
    def create_image(self):
        self.image = Viewer.images["Bunker1"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

    def update(self, seconds):
        VectorSprite.update(self, seconds)
        if random.random() < 0.001:
            angle = random.randint(10,60)
            speed = random.randint(30,70)
            for a in range(270-angle, 270+angle+1, angle):
                v = pygame.math.Vector2(speed, 0)
                v.rotate_ip(a)
                p = pygame.math.Vector2(self.pos.x, self.pos.y)
                Plasma(pos = p, move= v)
            

class River(VectorSprite):
    
    
    def _overwrite_parameters(self):
        self.kill_on_edge = True
        self.survive_north = True
        self.move = pygame.math.Vector2(0,-5)
        self._layer = -5
        
        
    def create_image(self):
        self.image = Viewer.images["river"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        
        
                 
class Tree(VectorSprite):
    
    
    def _overwrite_parameters(self):
        
        Enemy2._overwrite_parameters(self)
        self.move = pygame.math.Vector2(0,-5)
    
    def create_image(self):
        self.image = Viewer.images["tree"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        self.set_angle(90)

class Boss1(Enemy1):

     def _overwrite_parameters(self):
        self.kill_on_edge = True
        self.survive_north = True
        self.move = pygame.math.Vector2(
                   0,-random.randint(1,5))
        self._layer = 4
        self.angle = 270
        self.hitpoints = 400

     def update(self,seconds):
        VectorSprite.update(self,seconds)
        #self.ai()
        self.fire()

     def fire(self):
        """shoot a salvo towards a player"""
        if random.random() < 0.0095:
            targets = []
            for player in [0,1]:
                if player in VectorSprite.numbers:
                   targets.append(VectorSprite.numbers[player])
            if len(targets) == 0:
                return
            t = random.choice(targets)
            rightvector = pygame.math.Vector2(10,0)
            diffvector = t.pos - self.pos
            a = rightvector.angle_to(diffvector)
            #a = random.randint(260,280)
            speeds = [100,120,140,160,180,200,220,240]
            for speed in speeds:
                v = pygame.math.Vector2(speed, 0)
                v.rotate_ip(a)
                Evilrocket(pos=pygame.math.Vector2(self.pos.x,
                                   self.pos.y), angle=a+0,
                                   move=v+self.move, max_age=10,
                                   kill_on_edge=True, color=self.color)


     def create_image(self):
        self.image = Viewer.images["boss1"]
        #self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

class Star(VectorSprite):

    def _overwrite_parameters(self):
        self.pos = pygame.math.Vector2(random.randint(
                   0, Viewer.width) , -1)
        self.kill_on_edge = True
        self.move = pygame.math.Vector2(0,-random.randint(75,250))
        self._layer = 1

    def create_image(self):
        self.image = pygame.Surface((16,16))
        color = random.randint(200,255)
        radius = random.choice((0,0,0,0,0,1,1,1,1,2,2,3,4,5,6,7,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8))
        pygame.draw.circle(self.image, (color, color, color),
                           (3,3), radius)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()






class Spaceship(VectorSprite):

    def _overwrite_parameters(self):
        self.friction = 0.980  #1.0 = no friction
        self.radius = 8
        self.mass = 3000
        self.angle= 90
        self.rockets = 50
        self.rockets0 = 2
        self.bonusrockets = {}
        self.speed = 10
        self.speed0 = 10
        self.bonusspeed = {}
        self.bulletproof = False
        



        self.firearc = 90

    def fire(self):
        p = pygame.math.Vector2(self.pos.x, self.pos.y)
        t = pygame.math.Vector2(25,0)
        t.rotate_ip(self.angle)
        sa = [ ]
        d = 90 / (self.rockets + 1) # rockets fly in a 90° arc
        start = -self.firearc / 2
        point = start+d
        while point < self.firearc / 2:
            sa.append(point)
            point += d
        # in sa are the desired shooting angles for rockets
        for point in sa:
            v = pygame.math.Vector2(188,0)
            v.rotate_ip(self.angle+point)
            v += self.move # adding speed of spaceship to rocket
            a = self.angle + point
            Rocket(pos=p+t, move=v, angle=a, bossnumber=self.number,
                   kill_on_edge = True, color= self.color, max_age=10)
        #--alt
        #v = pygame.math.Vector2(400,0)
        #v.rotate_ip(self.angle)
        #Rocket(pos=pygame.math.Vector2(self.pos.x,
        #                       self.pos.y), angle=self.angle,
        #                       move=v+self.move, max_age=10,
        #                       kill_on_edge=True, color=self.color,
        #                       bossnumber=self.number)
        # --- mzzleflash 25, 0  vor raumschiff
        p = pygame.math.Vector2(25,0)
        p.rotate_ip(self.angle)
        Muzzle_flash(pos=pygame.math.Vector2(self.pos.x, self.pos.y) + p, max_age=0.1, angle = self.angle)




    def update(self, seconds):
        # -- bonusrocketsverwalutng ---
        self.rockets = -1
        self.rockets += self.rockets0
        for time in self.bonusrockets:
            if time > self.age:
                self.rockets += self.bonusrockets[time]
        # ------- bonus speed verwaltung ----
        self.speed = 0
        self.speed += self.speed0
        for time in self.bonusspeed:
            if time > self.age:
                self.speed += self.bonusspeed[time]



        # ------------------------------
        VectorSprite.update(self, seconds)
        #if random.random() < 0.8:
        #    for x,y  in [(-30,-8), (-30,8)]:
        #         v = pygame.math.Vector2(x,y)
        #         v.rotate_ip(self.angle)
                 #c = randomize_color(160, 25)
                 #Smoke(max_age=2.5, pos=v+pygame.math.Vector2(
                 #      self.pos.x, self.pos.y), color=(c,c,c))

    def strafe_left(self):
        v = pygame.math.Vector2(self.speed, 0)
        v.rotate_ip(self.angle + 90)   # strafe left!!
        #self.move += v
        self.pos += v
        #Explosion(self.pos,
        #          minangle = self.angle - 90 -35,
        #          maxangle = self.angle - 90 +35,
        #          maxlifetime = 0.75,
        #          minsparks = 1,
        #          maxsparks = 10,
        #          minspeed = 50,
        #          red = 0, red_delta=0,
         #         green= 0, green_delta=0,
         #         blue = 200, blue_delta = 50
         #         )




    def strafe_right(self):
        v = pygame.math.Vector2(self.speed, 0)
        v.rotate_ip(self.angle - 90)   # strafe right!!
        #self.move += v
        self.pos += v
        #Explosion(self.pos,
        #          minangle = self.angle + 90 -35,
        #          maxangle = self.angle + 90 +35,
         #         maxlifetime = 0.75,
         #         minsparks = 1,
         #         maxsparks = 10,
         #         minspeed = 50,
         #         red = 0, red_delta=0,
         #         green= 0, green_delta=0,
         #         blue = 200, blue_delta = 50
          #        )





    def move_forward(self, speed=1):
        v = pygame.math.Vector2(self.speed,0)
        v.rotate_ip(self.angle)
        self.pos += v
        #self.move += v
        # --- engine glow ----
        #p = pygame.math.Vector2(-30,0)
        #p.rotate_ip(self.angle)
        #Muzzle_flash(pos=pygame.math.Vector2(self.pos.x, self.pos.y) + p, max_age=0.1, angle = self.angle+180)



        #for p in [(-30,8), (-30,-8)]:
        #       w=pygame.math.Vector2(p[0],p[1])
        #       w.rotate_ip(self.angle)
        #       Explosion(self.pos+w,
        #                  minsparks = 0,
        #                  maxsparks = 1,
        #                  minangle = self.angle+180-5,
        #                  maxangle = self.angle+180+5,
        #                  maxlifetime = 0.3,
        #                  minspeed = 100,
        #                  maxspeed = 200,
        #                  blue=0, blue_delta=0,
        #                  green = 214, green_delta=20,
        #                  red = 255, red_delta = 20
        #                  )
    def move_backward(self, speed=1):
        v = pygame.math.Vector2(self.speed,0)
        v.rotate_ip(self.angle)
        #self.move += -v
        self.pos += -v

    def turn_left(self, speed=3):
        self.rotate(speed)

    def turn_right(self, speed=3):
        self.rotate(-speed)

    def create_image(self):
        self.image = Viewer.images[self.imagename]
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()




class Smoke(VectorSprite):

    def _overwrite_parameters(self):
      self._layer = 1


    def create_image(self):
        self.image = pygame.Surface((50,50))
        pygame.draw.circle(self.image, self.color, (25,25),
                           int(self.age*3))
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()

    def update(self, seconds):
        VectorSprite.update(self, seconds)
        if self.gravity is not None:
            self.move += self.gravity * seconds
        self.create_image()
        self.rect=self.image.get_rect()
        self.rect.center=(self.pos.x, -self.pos.y)


class Spark(VectorSprite):

    def _overwrite_parameters(self):
        self._layer = 2
        self.kill_on_edge = True

    def create_image(self):
        r,g,b = self.color
        r = randomize_color(r,50)
        g = randomize_color(g,50)
        b = randomize_color(b,50)
        self.image = pygame.Surface((10,10))
        pygame.draw.line(self.image, (r,g,b),
                         (10,5), (5,5), 3)
        pygame.draw.line(self.image, (r,g,b),
                          (5,5), (2,5), 1)
        self.image.set_colorkey((0,0,0))
        self.rect= self.image.get_rect()
        self.image0 = self.image.copy()


class Explosion():
    """emits a lot of sparks, for Explosion or Spaceship engine"""
    def __init__(self, posvector, minangle=0, maxangle=360, maxlifetime=3,
                 minspeed=5, maxspeed=150, red=255, red_delta=0,
                 green=225, green_delta=25, blue=0, blue_delta=0,
                 minsparks=5, maxsparks=20):
        for s in range(random.randint(minsparks,maxsparks)):
            v = pygame.math.Vector2(1,0) # vector aiming right (0°)
            a = random.randint(minangle,maxangle)
            v.rotate_ip(a)
            speed = random.randint(minspeed, maxspeed)
            duration = random.random() * maxlifetime # in seconds
            red   = randomize_color(red, red_delta)
            green = randomize_color(green, green_delta)
            blue  = randomize_color(blue, blue_delta)
            Spark(pos=pygame.math.Vector2(posvector.x, posvector.y),
                  angle= a, move=v*speed, max_age = duration,
                  color=(red,green,blue), kill_on_edge = True)

class Rocket(VectorSprite):

    def _overwrite_parameters(self):
        self._layer = 1
        self.radius = 5
        self.mass = 80
        self.damage = 5

    def update(self, seconds):
        VectorSprite.update(self, seconds)
        #if random.random() < 0.5:
        #    Explosion(self.pos,
        #              minangle = self.angle+180-15,
        #              maxangle = self.angle+180+15,
        #              minsparks = 1,
        #              maxsparks = 5,
        #              maxlifetime = 0.5,
        #              red = 200, red_delta = 50,
        #              green= 0, green_delta=0,
        #              blue = 0, blue_delta=0,
        #              )
        # ---- Smoke ---
        #if random.random() < 0.35:
         #   Smoke(pos=pygame.math.Vector2(self.pos.x, self.pos.y),
         #         color=(100,100,100),
         #         max_age=2.5)

    def create_image(self):
        self.image = Viewer.images["bullet"]
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

        #self.image = pygame.Surface((20,10))
        #pygame.draw.polygon(self.image, self.color, [(0,0),(5,0), (20,5), (5,10), (0,10), (5,5)])
        #self.image.set_colorkey((0,0,0))
        #self.image.convert_alpha()
        #self.image0 = self.image.copy()
        #self.rect = self.image.get_rect()


class Evilrocket(VectorSprite):

    def _overwrite_parameters(self):
        self._layer = 1
        self.radius = 5
        self.mass = 80

    def update(self, seconds):
        VectorSprite.update(self, seconds)
        #if random.random() < 0.5:
        #    Explosion(self.pos,
        #              minangle = self.angle+180-15,
        #              maxangle = self.angle+180+15,
        #              minsparks = 1,
        #              maxsparks = 5,
        #              maxlifetime = 0.5,
        #              red = 200, red_delta = 50,
        #              green= 0, green_delta=0,
        #              blue = 0, blue_delta=0,
        #              )
        # ---- Smoke ---
        #if random.random() < 0.35:
         #   Smoke(pos=pygame.math.Vector2(self.pos.x, self.pos.y),
         #         color=(100,100,100),
         #         max_age=2.5)

    def create_image(self):
        self.image = Viewer.images["red_bullet"]
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

        #self.image = pygame.Surface((20,10))
        #pygame.draw.polygon(self.image, self.color, [(0,0),(5,0), (20,5), (5,10), (0,10), (5,5)])
        #self.image.set_colorkey((0,0,0))
        #self.image.convert_alpha()
        #self.image0 = self.image.copy()
        #self.rect = self.image.get_rect()


class Engine_glow(VectorSprite):

    def create_image(self):
        self.image = Viewer.images["engine_glow"]
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()


class Muzzle_flash(VectorSprite):

    def create_image(self):
        self.image = Viewer.images["muzzle_flash"]
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()




class Viewer(object):
    width = 0
    height = 0
    images = {}

    def __init__(self, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
           default arguments """
        pygame.mixer.pre_init(44100,-16, 2, 2048)
        pygame.init()
        Viewer.width = width    # make global readable
        Viewer.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        #self.background.fill((0,118,48)) # fill background white
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        # ------ background images ------
        self.backgroundfilenames = [] # every .jpg file in folder 'data'
        try:
            for root, dirs, files in os.walk("data"):
                for file in files:
                    if file[-4:] == ".jpg" or file[-5:] == ".jpeg":
                        self.backgroundfilenames.append(file)
            random.shuffle(self.backgroundfilenames) # remix sort order
        except:
            print("no folder 'data' or no jpg files in it")

        Viewer.bombchance = 0.015
        Viewer.rocketchance = 0.001
        Viewer.wave = 0
        self.age = 0
        # ------ joysticks ----
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
        self.prepare_sprites()
        self.loadbackground()

    def loadbackground(self):

        #try:
        #    self.background = pygame.image.load(os.path.join("data",
        #         random.choice(self.backgroundfilenames)))
        #except:
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((24,228,28)) # fill background white

        self.background = pygame.transform.scale(self.background,
                          (Viewer.width,Viewer.height))
        self.background.convert()


    def load_sprites(self):
        #try:
            # load sounds 
            
            Viewer.panzersound1 = pygame.mixer.Sound(
                 os.path.join("data", "panzersound1.wav"))
            Viewer.panzersound2 = pygame.mixer.Sound(
                 os.path.join("data","panzersound2.wav"))
            Viewer.panzersound3 = pygame.mixer.Sound(
                 os.path.join("data","panzersound3.wav"))
            Viewer.panzersound4 = pygame.mixer.Sound(
                 os.path.join("data", "panzersound4.wav"))
            Viewer.panzersound5 = pygame.mixer.Sound(
                 os.path.join("data","panzersound5.wav"))
            Viewer.panzersound6 = pygame.mixer.Sound(
                 os.path.join("data","panzersound6.wav"))
            Viewer.panzersound7 = pygame.mixer.Sound(
                 os.path.join("data","panzersound7.wav"))
            
            # -----
            Viewer.powersound1 = pygame.mixer.Sound(
                 os.path.join("data","power1.wav"))
            Viewer.powersound2 = pygame.mixer.Sound(
                 os.path.join("data","power2.wav"))
            Viewer.powersound3 = pygame.mixer.Sound(
                 os.path.join("data","power3.wav"))
            
            #-------
            Viewer.impact1 = pygame.mixer.Sound(
                 os.path.join("data","impact1.wav"))
            Viewer.impact2 = pygame.mixer.Sound(
                 os.path.join("data","impact2.wav"))
            Viewer.impact3 = pygame.mixer.Sound(
                 os.path.join("data","impact3.wav"))
            
            Viewer.images["player1"]= pygame.image.load(
                 os.path.join("data", "jeeprequestef9.png")).convert_alpha()
            Viewer.images["red_bullet"]= pygame.image.load(
                 os.path.join("data", "red_bullet.png")).convert_alpha()
            Viewer.images["enemy1"]=pygame.image.load(
                 os.path.join("data", "enemy1.png")).convert_alpha()
            Viewer.images["player2"]=pygame.image.load(
                 os.path.join("data", "jeeprequestef9.png")).convert_alpha()
            Viewer.images["bullet"]= pygame.image.load(
                 os.path.join("data", "bullet.png")).convert_alpha()
            Viewer.images["muzzle_flash"]=pygame.image.load(
                 os.path.join("data", "muzzle_flash.png")).convert_alpha()
            Viewer.images["engine_glow"]=pygame.image.load(
                 os.path.join("data", "engine_glow.png")).convert_alpha()
            Viewer.images["enemy2"]=pygame.image.load(
                 os.path.join("data", "tank1.png")).convert_alpha()
            Viewer.images["boss1"]=pygame.image.load(
                 os.path.join("data", "planet.png")).convert_alpha()
            Viewer.images["tank1"]=pygame.image.load(
                 os.path.join("data", "M-6_preview.png")).convert_alpha()
            Viewer.images["tank2"]=pygame.image.load(
                 os.path.join("data", "E-100_preview.png")).convert_alpha()
            Viewer.images["tank3"]=pygame.image.load(
                 os.path.join("data", "KV-2_preview.png")).convert_alpha()
            Viewer.images["tank4"]=pygame.image.load(
                 os.path.join("data", "Pz.Kpfw.IV-G_preview.png")).convert_alpha()
            Viewer.images["tank5"]=pygame.image.load(
                 os.path.join("data", "T34_preview.png")).convert_alpha()
            Viewer.images["tank6"]=pygame.image.load(
                 os.path.join("data", "Tiger-II_preview.png")).convert_alpha()
            Viewer.images["tank7"]=pygame.image.load(
                 os.path.join("data", "VK.3601h_preview.png")).convert_alpha()
            Viewer.images["tree"]=pygame.image.load(
                 os.path.join("data", "LPCsnowTrees.png")).convert_alpha()
            Viewer.images["terrain"]=pygame.image.load(
                 os.path.join("data", "terrain.png")).convert_alpha()
            Viewer.images["river"]=Viewer.images["terrain"].subsurface(
                  (576,159,671-576,193-159))
            Viewer.images["Bunker1"]=pygame.image.load(
                 os.path.join("data", "bunker1.png")).convert_alpha()


            # --- scalieren ---
            for name in Viewer.images:
                if name == "tank1":
                    Viewer.images[name] = pygame.transform.scale(
                                    Viewer.images[name], (100,50))

                if name == "tank2":
                    Viewer.images[name] = pygame.transform.scale(
                                    Viewer.images[name], (100,50))

                if name == "tank3":
                    Viewer.images[name] = pygame.transform.scale(
                                    Viewer.images[name], (100,50))

                if name == "tank4":
                    Viewer.images[name] = pygame.transform.scale(
                                    Viewer.images[name], (100,50))

                if name == "tank5":
                    Viewer.images[name] = pygame.transform.scale(
                                    Viewer.images[name], (100,50))

                if name == "tank6":
                    Viewer.images[name] = pygame.transform.scale(
                                    Viewer.images[name], (100,50))

                if name == "tank7":
                    Viewer.images[name] = pygame.transform.scale(
                                    Viewer.images[name], (100,50))

                if name == "boss1" :
                    Viewer.images[name] = pygame.transform.scale(
                                    Viewer.images[name], (150,150))
                if "player" in name:
                     Viewer.images[name] = pygame.transform.scale(
                                    Viewer.images[name], (50,50))
                if "enemy" in name:
                     Viewer.images[name] = pygame.transform.scale(
                                    Viewer.images[name], (50,50))
                if "muzzle_flash" in name:
                     Viewer.images[name] = pygame.transform.scale(
                                    Viewer.images[name], (50,30))
                        
                #if "tree" in name:
                #     Viewer.images[name] = pygame.transform.scale(
                #                    Viewer.images[name], (50,30))




        #except:
        #    print("problem loading player1.png or player2.png from folder data")


    def prepare_sprites(self):
        """painting on the surface and create sprites"""
        self.load_sprites()
        self.allgroup =  pygame.sprite.LayeredUpdates() # for drawing
        self.tracergroup = pygame.sprite.Group()
        self.mousegroup = pygame.sprite.Group()
        self.explosiongroup = pygame.sprite.Group()
        self.tailgroup = pygame.sprite.Group()
        self.playergroup = pygame.sprite.Group()
        self.rocketgroup = pygame.sprite.Group()
        self.evilrocketgroup = pygame.sprite.Group()
        self.enemygroup = pygame.sprite.Group()
        self.powerupgroup = pygame.sprite.Group()
        self.trianglegroup = pygame.sprite.Group()
        self.treegroup = pygame.sprite.Group()
        self.flytextgroup = pygame.sprite.Group()
        self.rivergroup = pygame.sprite.Group()
        self.bunkergroup = pygame.sprite.Group()

        Mouse.groups = self.allgroup, self.mousegroup, self.tailgroup
        VectorSprite.groups = self.allgroup
        Spaceship.groups = self.allgroup, self.playergroup  # , self.tailgroup
        Rocket.groups = self.allgroup, self.rocketgroup
        Evilrocket.groups = self.allgroup, self.evilrocketgroup
        #Ufo.groups = self.allgroup
        Flytext.groups = self.allgroup, self.flytextgroup
        Explosion.groups= self.allgroup, self.explosiongroup
        Muzzle_flash.groups= self.allgroup
        Enemy1.groups = self.allgroup, self.enemygroup
        PowerUp.groups = self.allgroup, self.powerupgroup
        Triangle.groups = self.allgroup,self.powerupgroup
        Tree.groups = self.allgroup, self.treegroup
        River.groups = self.allgroup, self.rivergroup
        Bunker1.groups = self.allgroup, self.bunkergroup
        Plasma.groups = self.allgroup, self.evilrocketgroup

        self.player1 =  Spaceship(imagename="player1", warp_on_edge=True, pos=pygame.math.Vector2(Viewer.width/2-100,-Viewer.height/2))
        #self.player2 =  Spaceship(imagename="player2", angle=180,warp_on_edge=True, pos=pygame.math.Vector2(Viewer.width/2+100,-Viewer.height/2))

        # --- engine glow ----
        #p = pygame.math.Vector2(-30,0)
        #p.rotate_ip(self.player1.angle)
        #Muzzle_flash(pos=pygame.math.Vector2(self.pos.x, self.pos.y) + p, max_age=0.1, angle = self.angle+180)
        #Engine_glow(bossnumber = self.player1.number, sticky_with_boss=True, angle = self.player1.angle+180)


    def menurun(self):
        running = True
        self.cursor = 150
        code = ""
        while running:
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            pygame.display.set_caption("player1 hp: {}".format(
                                 self.player1.hitpoints))
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_DOWN:
                        self.cursor += 100
                    elif event.key == pygame.K_UP:
                        self.cursor -= 100
                    elif event.key == pygame.K_RETURN:
                        #--menüauswertung----
                        if self.cursor == 150 and self.coins > 50:
                            Flytext(200,100, "Doublegun!")
                            self.coins -= 50
                            age = self.player1.age + 3600
                            if age in self.player1.bonusrockets:
                                self.player1.bonusrockets[self.player1.age+3600] += 1
                            else:
                                self.player1.bonusrockets[age] = 1
                        if self.cursor == 250 and self.coins > 60:
                            Flytext(200,100, "100 extra hp")
                            self.coins -= 60
                            self.player1.hitpoints += 100
                        if self.cursor == 350 and self.coins > 75:
                            Flytext(200,100, "10 extra speed")
                            self.coins -= 75
                            age = self.player1.age + 3600
                            if age in self.player1.bonusspeed:
                                self.player1.bonusspeed[self.player1.age+3600] = 10
                            else:
                                self.player1.bonusspeed[age] = 10
                                
                        if self.cursor == 450 and self.coins > 50:
                            Flytext(200,100, "cheatcode eingeben")
                            #self.coins -= 50
                    else:
                        # es war eine andere taste!
                        c = pygame.key.name(event.key)
                        Flytext(400,400, c)
                        code += c
                        if code == "superhp":
                            #if self.coins > 50:
                            Flytext(400,400,"cheat activated: unlimited hp")
                            #self.coins -=50
                            self.player1.bulletproof = True
                            
                            
                            
            if self.cursor < 150:
                self.cursor = 150
            if self.cursor > 450:
                self.cursor = 450
            
                        
            # ------delete everything on screen-------
            self.screen.blit(self.background, (0, 0))
            #---------write menu----------------------
            write(self.screen, "shopping menu:", x =100, y = 100)
            write(self.screen, "jour coins:{} ".format(self.coins), x =100, y = 200)
            write(self.screen, "buy doublegun for 50 coins", x =500, y = 150)
            write(self.screen, "buy 100 extra hp for 60 coins", x =500, y = 250)
            write(self.screen, "buy 10 extra speed for 75 coins", x =500, y = 350)
            write(self.screen, "unlimited hp for 3$", x =500, y = 450)
            write(self.screen, "-->", x = 400, y = self.cursor,color = (255,0,0))
            
            
            # -------------- UPDATE all sprites -------
            self.flytextgroup.update(seconds)

            # ----------- clear, draw , update, flip -----------------
            self.flytextgroup.draw(self.screen)
            
            # -------- next frame -------------
            pygame.display.flip()
    
    
    def run(self):
        """The mainloop"""
        self.coins = 1000
        running = True
        pygame.mouse.set_visible(False)
        oldleft, oldmiddle, oldright  = False, False, False
        self.snipertarget = None
        gameOver = False
        exittime = 0
        while running:
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            pygame.display.set_caption("player1 hp: {}".format(
                                 self.player1.hitpoints))
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            self.playtime += seconds
            if gameOver:
                if self.playtime > exittime:
                    break
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_m:
                        self.menurun()
                    #if event.key == pygame.K_x:
                    #    Ufo(pos=pygame.math.Vector2(100,-100))
                    # ------- change Background image ----
                    if event.key == pygame.K_b:
                        self.loadbackground()
                    # ------- fire player 1 -----
                    if event.key == pygame.K_TAB and self.player1.hitpoints >0:
                        self.player1.fire()
                    

            # ------delete everything on screen-------
            self.screen.blit(self.background, (0, 0))
            #self.screen.blit(Viewer.images["river"],(100,100)
            if random.random() < 0.0005:
                Enemy2()
            #------ Enemy3 (tank) -----
            if random.random() < 0.002:
                Enemy3()
            # ----- Enemy4(tank)-----------
            if random.random() < 0.0002:
                Enemy4()
            #--------Enemy5(tank)-------
            if random.random() < 0.0002:
                Enemy5()
            #--------Enemy6(tank)------
            if random.random() < 0.0002:
                Enemy6()
            #-----Enemy7(tank)--------
            if random.random() < 0.0002:
                Enemy7()
            #-------Enemy8(tank)------
            if random.random() < 0.0002:
                Enemy8()
            #-------Enemy9(tank)-----
            if random.random() < 0.0002:
                Enemy9()
            #-----Enemy10(tank)------
            if random.random() < 0.0002:
                Enemy10()
            # --------- Powerup ------------
            if random.random() < 0.04:
                PowerUp()
            ##----------triangle---
            #if random.random() < 0.07:
            #    Triangle()
            #--------tree----------------
            if random.random() < 0.005:
                Tree()
            #--------river-------------
            if random.random() < 0.005:
                River()
            #-------Bunker1---------
            if random.random() < 0.005:
                Bunker1()
   

            # ------ move indicator for player 1 -----
            #pygame.draw.circle(self.screen, (0,255,0), (100,100), 100,1)
            #glitter = (0, random.randint(128, 255), 0)
            #pygame.draw.line(self.screen, glitter, (100,100),
            #                (100 + self.player1.move.x, 100 - self.player1.move.y))


            # ------------ pressed keys ------
            pressed_keys = pygame.key.get_pressed()
            # ------- movement keys for player1 -------
            if pressed_keys[pygame.K_a]:
                self.player1.strafe_left()
            if pressed_keys[pygame.K_d]:
                self.player1.strafe_right()
            if pressed_keys[pygame.K_w]:
                self.player1.move_forward()
            if pressed_keys[pygame.K_s]:
                self.player1.move_backward()
            if pressed_keys[pygame.K_TAB]:
                if self.player1.hitpoints > 0:
                    self.player1.fire()

            # ------ mouse handler ------
            left,middle,right = pygame.mouse.get_pressed()
            oldleft, oldmiddle, oldright = left, middle, right


            # ------ joystick handler -------
            for number, j in enumerate(self.joysticks):
                if number == 0:
                    player = self.player1
                elif number ==1:
                    player = self.player2
                else:
                    continue
                x = j.get_axis(0)
                y = j.get_axis(1)
                if y > 0.5:
                    player.move_backward()
                if y < -0.5:
                    player.move_forward()
                if x > 0.5:
                    player.turn_right()
                if x < -0.5:
                    player.turn_left()

                buttons = j.get_numbuttons()
                for b in range(buttons):
                       pushed = j.get_button( b )
                       if b == 0 and pushed:
                           player.fire()
                       if b == 4 and pushed:
                           player.strafe_left()
                       if b == 5 and pushed:
                           player.strafe_right()




            # write text below sprites
            write(self.screen, "FPS: {:8.3}".format(
                self.clock.get_fps() ), x=10, y=10)

            # ----- collision detection between player and PowerUp---
            for p in self.playergroup:
                crashgroup=pygame.sprite.spritecollide(p,
                           self.powerupgroup, False,
                           pygame.sprite.collide_mask)
                for o in crashgroup:
                    if o.color == (255,0,0):
                        Viewer.powersound1.play()
                        Flytext(o.pos.x, - o.pos.y, "+50 hitpoints")
                        p.hitpoints += 50
                        Explosion(o.pos, red=255, green=0, blue=0)
                        o.kill()
                    elif o.color == (0,255,0):
                        Viewer.powersound2.play()
                        Flytext(o.pos.x, - o.pos.y, "+5 speed for 20 seconds")
                        p.bonusspeed[p.age+20] = 5
                        Explosion(o.pos, red=0, green=255, blue=0)
                        o.kill()
                    elif o.color == (0,0,255):
                        Viewer.powersound3.play()
                        Flytext(o.pos.x, -o.pos.y, "+1 Bonusrockets for 10 seconds")
                        p.bonusrockets[p.age+10] = 1
                        Explosion(o.pos, red=0, green=0, blue=255)
                        o.kill()


            
                        
            # ----- collision detection between tree and rocket -----
            for t in self.treegroup:
                crashgroup = pygame.sprite.spritecollide(t, self.rocketgroup,
                             False, pygame.sprite.collide_mask)
                for r in crashgroup:
                        t.hitpoints -= random.randint(4,9)
                        Explosion(pygame.math.Vector2(r.pos.x, r.pos.y))
                        r.kill()
                        
            # ----- collision detection between player and treegroup -----
            for p in self.playergroup:
                crashgroup = pygame.sprite.spritecollide(p, self.treegroup,
                             False, pygame.sprite.collide_mask)
                for t in crashgroup:
                    if t.bossnumber != p.number:
                        if not p.bulletproof:
                            p.hitpoints -= 5
                        Explosion(pygame.math.Vector2(t.pos.x, t.pos.y))
                        #elastic_collision(p, t)
                        t.kill()

            # ----- collision detection between player and Evilrocket -----
            for p in self.playergroup:
                crashgroup = pygame.sprite.spritecollide(p, self.evilrocketgroup,
                             False, pygame.sprite.collide_mask)
                for r in crashgroup:
                    #if r.bossnumber != p.number:
                    if not p.bulletproof:
                        p.hitpoints -= random.randint(3,6)
                    Explosion(pygame.math.Vector2(r.pos.x, r.pos.y))
                    #elastic_collision(p, r)
                    r.kill() 

            
            # ----- collision detection between enemy and rocket -----
            for e in self.enemygroup:
                crashgroup = pygame.sprite.spritecollide(e, self.rocketgroup,
                             False, pygame.sprite.collide_mask)
                for r in crashgroup:
                     e.hitpoints -= r.damage
                     self.coins += 1
                     if e.hitpoints <= 0:
                         self.coins += 100
                     Explosion(posvector=r.pos)
                     r.kill()
                        
            #collision detection between River and Enemy
            for r in self.rivergroup:
                crashgroup = pygame.sprite.spritecollide(r,
                    self.enemygroup, False, pygame.sprite.collide_rect)
                for e in crashgroup:
                    e.pos += e.move * -0.5 * seconds #river makes slow
                    
            # ----- collision detection between player and Bunker -----
            for p in self.playergroup:
                crashgroup = pygame.sprite.spritecollide(p, self.bunkergroup,
                             False, pygame.sprite.collide_rect)
                for b in crashgroup:
                    #if r.bossnumber != p.number:
                    if not p.bulletproof:
                        Explosion(pygame.math.Vector2(b.pos.x, b.pos.y))
                        #elastic_collision(p, b)
                        p.hitpoints -= 10           
            
            # ----- collision detection between Bunker and rocket -----
            for b in self.bunkergroup:
                crashgroup = pygame.sprite.spritecollide(b, self.rocketgroup,
                             False, pygame.sprite.collide_mask)
                for r in crashgroup:
                     b.hitpoints -= 1
                     if b.hitpoints <= 0:
                         self.coins += 10000
                     Explosion(posvector=r.pos)
                     r.kill() 
            
            
            
            
            
            
            # -------------- UPDATE all sprites -------
            self.allgroup.update(seconds)

            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)


            # --- Martins verbesserter Mousetail -----
            for mouse in self.tailgroup:
                if len(mouse.tail)>2:
                    for a in range(1,len(mouse.tail)):
                        r,g,b = mouse.color
                        pygame.draw.line(self.screen,(max(0,r-a),g,b),
                                     mouse.tail[a-1],
                                     mouse.tail[a],10-a*10//10)

            # -------- next frame -------------
            pygame.display.flip()
        #-----------------------------------------------------
        pygame.mouse.set_visible(True)
        pygame.quit()

if __name__ == '__main__':
    Viewer(1430,800).run() # try Viewer(800,600).run()
