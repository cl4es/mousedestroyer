#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyglet
from pyglet.window import mouse
import sys
import math
import random
from threading import Lock

window = pyglet.window.Window()

class Tower(pyglet.sprite.Sprite):
    def __init__(self, x, y):
        
        self.base = pyglet.sprite.Sprite(window.tower_base,batch=window.tower_batch,x=x,y=y)
        super(Tower,self).__init__(window.tower,batch=window.tower_batch, x=x,y=y)
        self.x_speed = 30.0*(random.random()-0.5)
        self.y_speed = 10+5.0*(random.random())
        self.cooldown = 0.0
        self.live = True
        
    def center(self):
        return (self.x,self.y)
        
class Monster(pyglet.sprite.Sprite):
    def __init__(self):
        super(Monster,self).__init__(window.monster,batch=window.monster_batch, x=random.randint(100,window.width-120),y=window.height+20)
        self.x_speed = 0 #20.0*(random.random()-0.5)
        self.y_speed = 60+40.0*(random.random())
        self.lives = 2
        
    
    def center(self):
        return (self.x,self.y)
        
class Shot(pyglet.sprite.Sprite):    
    def __init__(self, tower, monster):
        super(Shot,self).__init__(window.shot, batch=window.missiles_batch, x=tower.x, y=tower.y)
        self.tower = tower
        self.monster = monster
        self.speed = 300.0
        self.live = True
        
    def center(self):
        return (self.x+1,self.y+1)

@window.event
def on_text(text):
    if text == 'n':
        # Restart game
        window.cash = 1000
        window.lives = 25
        window.score = 0
        window.t = 0.0
        
        towers = window.towers
        monsters = window.monsters
        window.towers = []
        window.monsters = []
        for x in monsters:
            x.delete()
        for x in towers:
            x.delete()
            
        window.label.text = "GO"
        window.alpha = 1.0

@window.event
def on_mouse_press(x, y, button, modifiers):
    #print "Clicked: %s %s %s" % (x, y, button)
    if button == mouse.LEFT and window.lives > 0 and window.cash >= 200:
        window.towers.append( Tower(x, y) )
        window.cash -= 200
        
@window.event
def on_draw():
    window.clear()
    background.blit(0,0)
    window.missiles_batch.draw()
    window.monster_batch.draw()
    window.tower_batch.draw()
    window.label.color = (255,255,255,int(255*max(0.0, window.alpha)))
    window.label.draw()
    
    
    if window.lives >= 0:
        window.lives_label.text = "%s" % window.lives
        window.score_label.text = "%s" % window.score
        window.cash_label.text = "%s" % window.cash
        window.label_batch.draw()
        if window.lives == 0:
            window.game_over.draw()
            window.instruction.draw()
    else:
        window.splash.draw()
        window.instruction.draw()
    
def calc_angle(origin,target):
    ox,oy = origin.center()
    tx,ty = target.center()
    return  -90-(math.atan2(oy-ty, ox-tx))*57.295779513082323
    
    
def update(dt):
    window.t += dt
    if window.lives > 0:
        window.monstertime += dt
        monstery = 0.5/(1+window.t*0.075)
        if window.monstertime > monstery and monstery > 0.000001:
            monsters = math.floor(window.monstertime / monstery)
            for i in xrange(int(monsters)):
                
                window.monsters.append(Monster())
            window.monstertime -= monsters*monstery

    if window.lives == 0:
        for tower in window.towers:
            tower.y_speed += 30*dt
            tower.y -= dt * tower.y_speed
            tower.x += dt * tower.x_speed
    else:
        for tower in window.towers:
            tower.cooldown -= dt
    
    window.alpha -= dt
    first = True
    for missile in window.missiles:
        if not missile.monster or not missile.monster.lives:
            # Monster has disappeared :(
            missile.live = False
        dx = missile.monster.x - missile.x
        dy = missile.monster.y - missile.y
        if (dx**2 + dy**2) <= (dt*missile.speed)**2:
            # HIT!
            missile.monster.lives = max(0, missile.monster.lives-1)
            missile.live = False
            if missile.monster.lives == 0:
                window.cash += 5
                window.score += 1
        else:
            angle = math.atan2(dy,dx)
            dxx = math.cos(angle)
            dyy = math.sin(angle)     
            missile.x += missile.speed * dt * dxx
            missile.y += missile.speed * dt * dyy
        first = False
    for monster in window.monsters:
        if window.lives > 0:
            for tower in window.towers:
                if tower.live and monster.lives:
                    if tower.cooldown < 0.0  and (monster.x - tower.x)**2 + (monster.y - tower.y)**2 < 10000:
                        tower.rotation=calc_angle(tower, monster)
                        window.missiles.append(Shot(tower,monster))
                        tower.cooldown = 0.5

        if monster.lives:
            #monster.y_speed += 30*dt
            monster.y -= dt * monster.y_speed 
            monster.x += dt * monster.x_speed

            if monster.y < -40:
                window.lives = max(0, window.lives-1)
                monster.lives = 0

    dead_stuff = [s for s in window.towers if not s.live]
    for dead in dead_stuff:
        dead.delete()
    dead_stuff = [s for s in window.missiles if not s.live]
    for dead in dead_stuff:
        dead.delete()
    dead_stuff = [s for s in window.monsters if not s.lives]
    for dead in dead_stuff:
        dead.delete()
    
    towers = [tower for tower in window.towers if tower.live]
    monsters = [monster for monster in window.monsters if monster.lives]
    missiles = [missile for missile in window.missiles if missile.live]
    
    window.monsters = monsters
    window.towers = towers
    window.missiles = missiles
    
if __name__ == "__main__":
    window.label = pyglet.text.Label("", font_name="Arial", font_size=256,x=window.width//2,y=window.height//2,anchor_x='center',anchor_y="center")
    window.label_batch = pyglet.graphics.Batch()
    
    # Special labels
    window.game_over = pyglet.text.Label("Game Over!", font_name="Arial", font_size=50,
        x=window.width//2,y=window.height//2+50,anchor_x='center',anchor_y="center")
    window.splash = pyglet.text.Label("Bubble Defender!", font_name="Arial", font_size=50, 
        x=window.width//2,y=window.height//2+50,anchor_x='center',anchor_y="center")
    window.instruction = pyglet.text.Label("press 'n' to play", font_name="Arial", font_size=32, 
        x=window.width//2,y=window.height//2-50,anchor_x='center',anchor_y="center")
    
    window.lives_label = pyglet.text.Label("", font_name="Arial", font_size=32, x=20, y=30, anchor_x='left', anchor_y="center", batch=window.label_batch)
    window.score_label = pyglet.text.Label("", font_name="Arial", font_size=32, x=window.width-20,y=30,anchor_x='right',anchor_y="center", batch=window.label_batch)
    window.lives_text = pyglet.text.Label("Lives", font_name="Arial", font_size=32, x=20, y=70, anchor_x='left', anchor_y="center", batch=window.label_batch)
    window.score_text = pyglet.text.Label("Score", font_name="Arial", font_size=32, x=window.width-20,y=70,anchor_x='right',anchor_y="center", batch=window.label_batch)
    
    window.cash_label = pyglet.text.Label("", font_name="Arial", font_size=32, x=window.width//2,y=30,anchor_x='center',anchor_y="center", batch=window.label_batch)
    window.cash_text = pyglet.text.Label("Cash", font_name="Arial", font_size=32, x=window.width//2, y=70, anchor_x='center', anchor_y="center", batch=window.label_batch)
    
    background = pyglet.resource.image("images/bg.png")
    window.monster = pyglet.resource.image("images/monster.png")
    window.monster.anchor_x = 17
    window.monster.anchor_y = 17
    
    window.shot = pyglet.resource.image("images/shot1.png")
    window.tower = pyglet.resource.image("images/tower.png")
    window.tower.anchor_x = 16.5
    window.tower.anchor_y = 16.5
    
    window.tower_base = pyglet.resource.image("images/towerbase.png")
    window.tower_base.anchor_x = 16.5
    window.tower_base.anchor_y = 16.5

    
    window.monsters = []
    window.towers = []
    window.missiles = []
    window.monster_batch = pyglet.graphics.Batch()
    window.tower_batch = pyglet.graphics.Batch()
    window.missiles_batch = pyglet.graphics.Batch()
    window.monstertime = 0.0
    window.alpha = 1.0
    window.lock = Lock()
    window.lives = -1
    window.score = 0
    window.cash = 1000
    window.t = 0.0
    pyglet.clock.schedule_interval(update, 1/60.0)
    pyglet.app.run()