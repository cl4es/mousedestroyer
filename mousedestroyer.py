#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyglet
from pyglet.window import mouse
import sys
import math
import random
from threading import Lock

window = pyglet.window.Window()
window.label = pyglet.text.Label("", font_name="Arial", font_size=256,x=window.width//2,y=window.height//2,anchor_x='center',anchor_y="center")

window.label_batch = pyglet.graphics.Batch()

# Special labels
window.game_over = pyglet.text.Label("Game Over!", font_name="Arial", font_size=50,
    x=window.width//2,y=window.height//2+50,anchor_x='center',anchor_y="center")
window.splash = pyglet.text.Label("Mouse Destroyer!", font_name="Arial", font_size=50, 
    x=window.width//2,y=window.height//2+50,anchor_x='center',anchor_y="center")
window.instruction = pyglet.text.Label("press 'n' to play", font_name="Arial", font_size=32, 
    x=window.width//2,y=window.height//2-50,anchor_x='center',anchor_y="center")

window.lives_label = pyglet.text.Label("", font_name="Arial", font_size=32, x=20, y=30, anchor_x='left', anchor_y="center", batch=window.label_batch)
window.score_label = pyglet.text.Label("", font_name="Arial", font_size=32, x=window.width-20,y=30,anchor_x='right',anchor_y="center", batch=window.label_batch)
window.lives_text = pyglet.text.Label("Lives", font_name="Arial", font_size=32, x=20, y=70, anchor_x='left', anchor_y="center", batch=window.label_batch)
window.score_text = pyglet.text.Label("Score", font_name="Arial", font_size=32, x=window.width-20,y=70,anchor_x='right',anchor_y="center", batch=window.label_batch)

background = pyglet.resource.image("images/bg.png")
window.monster = pyglet.resource.image("images/monster.png")
window.tower = pyglet.resource.image("images/tower.png")

#window.set_icon(window.monster)
window.monsters = []
window.towers = []
window.monster_batch = pyglet.graphics.Batch()
window.tower_batch = pyglet.graphics.Batch()
window.monstertime = 0.0
window.alpha = 1.0
window.lock = Lock()
window.lives = -1
window.score = 0
window.t = 0.0
@window.event
def on_text(text):
    if text == 'n':
        # Restart game
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
            
    window.label.text = text
    window.alpha = 1.0

@window.event
def on_mouse_press(x, y, button, modifiers):
    #print "Clicked: %s %s %s" % (x, y, button)
    if button == mouse.LEFT and window.lives > 0:
            tower = pyglet.sprite.Sprite(window.tower,batch=window.tower_batch, x=x-16,y=y-16)
            tower.x_speed = 30.0*(random.random()-0.5)
            tower.y_speed = 10+5.0*(random.random())
            tower.live = True
            window.towers.append(tower)
        
@window.event
def on_draw():
    window.clear()
    background.blit(0,0)
    window.monster_batch.draw()
    window.tower_batch.draw()
    window.label.color = (255,255,255,int(255*max(0.0, window.alpha)))
    window.label.draw()
    
    
    if window.lives >= 0:
        window.lives_label.text = "%s" % window.lives
        window.score_label.text = "%s" % window.score
        window.label_batch.draw()
        if window.lives == 0:
            window.game_over.draw()
            window.instruction.draw()
    else:
        window.splash.draw()
        window.instruction.draw()
    
def update(dt):
    window.t += dt
    if window.lives > 0:
        window.monstertime += dt
        if window.monstertime > 0.2 * 1/(1+window.t*0.15):
            monster = pyglet.sprite.Sprite(window.monster,batch=window.monster_batch, x=random.randint(100,window.width-120),y=window.height+20)
            monster.x_speed = 20.0*(random.random()-0.5)
            monster.y_speed = 10+5.0*(random.random())
            monster.live = True
            window.monsters.append(monster)
            window.monstertime = 0.0
    window.alpha -= dt
    for monster in window.monsters:
        if window.lives > 0:
            for tower in window.towers:
                if tower.live and monster.live and abs(monster.x - tower.x) < 25 and abs(monster.y - tower.y) < 25:
                    monster.live = False
                    tower.live = False
                    window.score += 1
                    
        if monster.live:
            monster.y_speed += 30*dt
            monster.y -= dt * monster.y_speed 
            monster.x += dt * monster.x_speed
            
            if monster.y < -40:
                window.lives = max(0, window.lives-1)
                monster.live = False
                
    if window.lives == 0:
        for tower in window.towers:
            tower.y_speed += 30*dt
            tower.y -= dt * tower.y_speed
            tower.x += dt * tower.x_speed
            
    dead_stuff = [s for s in window.towers and window.monsters if not s.live]
    
    towers = [tower for tower in window.towers if tower.live]
    monsters = [monster for monster in window.monsters if monster.live]
    
    for dead in dead_stuff:
        dead.delete()
    
    window.monsters = monsters
    window.towers = towers
    

pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()