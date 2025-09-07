import pygame as py
import random 

folder = "audio/"

ZEN_GARDEN = 0
LOOBOON = 1
BRAINIAC_MANIAC = 2
EAT = 3
START = 4
LOSE = 5
BONK = 6

def mp3(name):
    return folder + name+".mp3"

music_dict = [
    "zen_garden", #0
    "looboon",    #1
    "brainiac_maniac", #2
    "eat", #3
    "start", #4
    "lose", #5
    "bonk" #6
]

zombie_groan_dict = ["groan_0", "groan_1", "groan_2"]
zombie_appear_dict = ["digging_0", "digging_1"]

py.mixer.init()
py.mixer.set_num_channels(32)

class sfx:
    def __init__(self):
        self.zombie_groan_sound = [py.mixer.Sound(mp3(x)) for x in zombie_groan_dict]
        self.zombie_appear_sound = [py.mixer.Sound(mp3(x)) for x in zombie_appear_dict]
        self.sounds = [py.mixer.Sound(mp3(x)) for x in music_dict]

    # Sound.play(loops, max time, fade-in)
    # general play sound
    def play(self, sound, volume=1, loop=0, duration=0, fade_in=0):
        sound.set_volume(volume)
        sound.play(loop, duration, fade_in)

    # general stop sound
    def stop(self, sound):
        sound.stop()
        pass

    # play when game open, back to main menu
    def play_background(self):
        self.play(self.sounds[ZEN_GARDEN], 1, -1)

    def stop_background(self):
        self.stop(self.sounds[ZEN_GARDEN])

    # play game starts
    def play_start_sound(self):
        self.play(self.sounds[START], 1, 0)

    # play when game started in first 1 minute
    def play_looboon(self):
        self.play(self.sounds[LOOBOON], 1, -1, 0, 1000)

    def stop_looboon(self):
        self.stop(self.sounds[LOOBOON])

    def play_brain_maniac(self):
        self.play(self.sounds[BRAINIAC_MANIAC], 1, -1, 0, 1000)

    def stop_brain_maniac(self):
        self.stop(self.sounds[BRAINIAC_MANIAC])

    # play when game over
    def play_lose_sound(self):
        self.play(self.sounds[LOSE], 1, 0)

    # play when zombie come our house
    def play_eat_sound(self):
        self.play(self.sounds[EAT], 1, 0)

    # play when hit zombie
    def play_bonk_sound(self):
        self.play(self.sounds[BONK], 1, 0)

    # every 3 seconds check if there is a zombie in screen then play this sound
    def play_zombie_groan(self):
        rd = random.randint(0,2)
        self.play(self.zombie_groan_sound[rd], 0.8)

    # play when zombie appear
    def play_zombie_appear(self):
        rd = random.randint(0,1)
        self.play(self.zombie_appear_sound[rd], 0.3)


