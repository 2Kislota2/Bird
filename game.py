from pygame import *
from random import randint
import sounddevice as sd
import numpy as np
# import socket
# import json
# from threading import Thread


WIDTH, HEIGHT = 800, 600
init()
mixer.init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Flappy Bird")

image_bootom = image.load("Tupe_l.png")
image_bootom = transform.scale(image_bootom,(140,300))
img_top = transform.flip(image_bootom, False,True)

class Sprite():
    def __init__(self,x,y,w,h,img=None):
        self.rect = Rect(x,y,w,h)
        self.rect.x = x
        self.rect.y = y
        self.rect.w = w
        self.rect.h = h
        self.img = None
        if img:
            self.img = img

    def draw(self,screen):
        if self.img:
            screen.blit(self.img,(self.rect.x, self.rect.y))
            
        else:
            draw.rect(screen,(255,255,0), self.rect)


class Tube(Sprite):
    def update(self):
        self.rect.x -= 7
        
    def draw(self,screen):
        if self.img:
            screen.blit(self.img,(self.rect.x, self.rect.y))
            # draw.rect(screen,(255,0,0), self.rect)
        else:
            draw.rect(screen,(0,255,0), self.rect)

    
class Player(Sprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_w]:
            self.rect.y -= 5
        if keys[K_s]:
            self.rect.y += 5
            
player = Player(x=100,y=50,w=20,h=20)         

window_size = 1200, 800
def generate_pipes(count, pipe_width=140, gap=280, min_y = -200,
                   max_y=0, distance=650):
    pipes = []
    start_x = window_size[0]

    for i in range(count):
        y = randint(min_y, max_y)

        top_pipe = Tube(start_x, y, pipe_width, 300, img_top )
        bottom_pipe = Tube(start_x, y+300 + gap,
                           pipe_width, 300, image_bootom)

        pipes.extend([top_pipe, bottom_pipe])
        start_x += distance

    return pipes


fs = 16000
block = 256
mic_level = 0.0

y_vel = 0.0
gravity = 0.6
tresh = 0.01
impulse = -8.0


def audi_cb(indata,frames,time,status):
    global mic_level
    if status:
        return
    
    rms = float(np.sqrt(np.mean(indata**2)))
    mic_level = 0.85 * mic_level + 0.15 * rms



pipes = generate_pipes(150)
wait = 40
lose = False
running = True

with sd.InputStream(samplerate=fs, channels=1, blocksize=block, callback=audi_cb):
    while running:
        for e in event.get():
            if e.type == QUIT:
                running = False
            if len(pipes) < 8:
                pipes += generate_pipes(150)
                
                
        screen.fill((0,0,0))
        
        if mic_level > tresh:
            y_vel = impulse
        y_vel += gravity
        player.rect.y += int(y_vel)
        
        if player.rect.bottom > HEIGHT:
           player.rect.bottom = HEIGHT
           y_vel = 0.0
        if player.rect.top < 0:
           player.rect.top = 0
           if y_vel < 0:
               y_vel = 0.0
           
        for pipe in pipes:
            pipe.draw(screen)
            pipe.update()
            if pipe.rect.x <= -100:
                pipes.remove(pipe)
                
            if player.rect.colliderect(pipe.rect):
                lose = True
                
        if lose and wait > 1:
            for pipe in pipes:
                pipe.rect.x += 25
            wait -=1
        else:
            lose = False
            wait = 40
                
        
        player.draw(screen)   
        player.update()
            
        display.update()
        clock.tick(60)

quit()