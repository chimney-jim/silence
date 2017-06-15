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
import sys
import alsaaudio
import time as t
from collections import deque

def to_millis(timestamp):
    return int(timestamp * 1000)

class KeyEvent():

    key = None
    direction = None

    def __init__(self, key, direction):
        self.key = key
        self.direction = direction

    def __str__(self):
        return '{} | {}'.format(self.key, self.direction)

    def __eq__(self, other):
        if self.key != other.key:
            return False
        if self.direction != other.direction:
            return False
        return True

class TimestampedKeyEvent():

    key_event = None
    timestamp = None

    def __init__(self, key_event):
        self.key_event = key_event
        self.timestamp = t.time()

    def __str__(self):
        return 'key_event: {}, timestamp: {}'.format(str(self.key_event), self.timestamp)

class Silence():

    magic_key = None
    magic_sequence = None
    mic_mixer = None
    toggle_timing = None

    current_keys_down = set()
    key_event_buffer = deque(maxlen=4)

    def __init__(self, magic_key, mic_mixer, toggle_timing):
        self.magic_key = magic_key
        magic_key_down_event = KeyEvent(magic_key, 'down')
        magic_key_up_event = KeyEvent(magic_key, 'up')
        self.magic_sequence =[
            magic_key_up_event,
            magic_key_down_event,
            magic_key_up_event,
            magic_key_down_event]
        self.mic_mixer = mic_mixer
        self.toggle_timing = toggle_timing

    def __str__(self):
        key_event_buffer_str = list(str(event) for event in self.key_event_buffer)
        return '''
        magic_key: {},
        current_keys_down: {},
        key_event_buffer: {}'''.format(
            self.magic_key,
            self.current_keys_down,
            key_event_buffer_str)

    def set_key_down(self, pressed_key):
        key_pressed_event = TimestampedKeyEvent(KeyEvent(pressed_key, 'down'))
        self.current_keys_down.add(pressed_key)
        self.key_event_buffer.appendleft(key_pressed_event)
        if self.magic_key in self.current_keys_down:
            print('unmuting mic!')
            self.unmute_mic()

    def set_key_up(self, released_key):
        key_release_event = TimestampedKeyEvent(KeyEvent(released_key, 'up'))
        if released_key in self.current_keys_down:
            self.current_keys_down.remove(released_key)
        self.key_event_buffer.appendleft(key_release_event)

        timestamp_key_events = list(self.key_event_buffer)
        key_events = [tke.key_event for tke in timestamp_key_events]
        # print([str(ke) for ke in key_event_list])
        if key_events == self.magic_sequence:
            print('magic sequence match!!')
            timestamp_key_up_last, timestamp_key_up_first = [
                tke.timestamp for tke in timestamp_key_events
                if tke.key_event.direction == 'up']
            timestamp_key_up_delta = timestamp_key_up_last - timestamp_key_up_first
            if timestamp_key_up_delta < self.toggle_timing:
                print('timing is correct!')
                self.key_event_buffer.clear()
                self.toggle_mic()
        elif self.magic_key not in self.current_keys_down and key_events[0].key == self.magic_key:
            print('muting_mic')
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

silence = Silence(Key.f1, alsaaudio.Mixer(control='Capture'), 100)

def on_press(key):
    silence.set_key_down(key)
    # print(str(silence))

def on_release(key):
    silence.set_key_up(key)
    # print(str(silence))

with Listener(on_press=lambda key: on_press(key),
              on_release=lambda key: on_release(key)) as listener:
    listener.join()
