import os

def play_sound(current_colour, new_colour):
    if current_colour == 'red' and new_colour == 'green':
        os.system("aplay red_to_green.wav")
    elif current_colour == 'green' and new_colour == 'red':
        os.system("aplay green_to_red.wav")


