 #        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
 #                    Version 2, December 2004

 # Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>

 # Everyone is permitted to copy and distribute verbatim or modified
 # copies of this license document, and changing it is allowed as long
 # as the name is changed.

 #            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
 #   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

 #  0. You just DO WHAT THE FUCK YOU WANT TO.

from pynput.keyboard import Key, Listener
from collections import defaultdict
import sys
import alsaaudio

class Silence():

    magic_key = None
    mic_mixer = None

    current_keys_down = set()
    last_key_pressed = None
    last_key_released = None

    def __init__(self, magic_key, mic_mixer):
        self.magic_key = magic_key
        self.mic_mixer = mic_mixer

    def __str__(self):
        return 'magic_key: {}, current_keys_down: {}, last_key_pressed: {}, last_key_released: {}'.format(self.magic_key, self.current_keys_down, self.last_key_pressed, self.last_key_released)

    def set_key_down(self, pressed_key):
        self.current_keys_down.add(pressed_key)
        self.last_key_pressed = pressed_key
        if self.magic_key in self.current_keys_down:
            self.unmute_mic()

    def set_key_up(self, released_key):
        self.current_keys_down.remove(released_key)
        self.last_key_released = released_key
        if self.magic_key not in self.current_keys_down:
            self.mute_mic()

    def is_recording(self):
        is_recording_r, is_recording_l = self.mic_mixer.getrec()
        if is_recording_l is 1 and is_recording_r is 1:
            return True
        else:
            return False

    def toggle_mic(self):
        if not self.is_recording():
            self.mic_mixer.setrec(1)
        else:
            self.mic_mixer.setrec(0)

    def mute_mic(self):
        if self.is_recording():
            self.mic_mixer.setrec(0)

    def unmute_mic(self):
        if not self.is_recording():
            self.mic_mixer.setrec(1)

silence = Silence(Key.f1, alsaaudio.Mixer(control='Capture'))

def on_press(key):
    silence.set_key_down(key)
    print(str(silence))

def on_release(key):
    silence.set_key_up(key)
    print(str(silence))

with Listener(on_press=lambda key: on_press(key),
              on_release=lambda key: on_release(key)) as listener:
    listener.join()
