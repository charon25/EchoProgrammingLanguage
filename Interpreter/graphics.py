from typing import List

from systems import Sound, Wall


class Graphics:

    LETTERS = 'ouaesrvwnm.@#'

    @staticmethod
    def render(command: str, sounds: List[Sound], walls: List[Wall], sound_sum: int, min_distance: int = 0):
        max_distance = 0

        for wall in walls:
            max_distance = max(max_distance, wall.distance + 1)
        for sound in sounds:
            max_distance = max(max_distance, sound.distance + 1)

        max_distance = max(max_distance, min_distance)

        directions = [[' '] * max_distance for _ in range(4)]
        for wall in walls:
            directions[wall.direction][wall.distance] = '|'
                
        letters_indexes = [0] * 4
        intensities = [[], [], [], []]
        for direction, sound in enumerate(sounds):
            letter = Graphics.LETTERS[letters_indexes[sound.direction] % len(Graphics.LETTERS)]
            directions[sound.direction][sound.distance - 1] = letter
            intensities[sound.direction].append((letter, sound.intensity))
            letters_indexes[sound.direction] += 1
        
        output = ['' for _ in range(7)]
        for direction in range(4):
            output[2 * direction] = str(direction) + ''.join(directions[direction])
            if len(intensities[direction]) > 0:
                output[2 * direction] += '  ' + ', '.join(f'{letter} = {intensity}' for letter, intensity in intensities[direction])
        output[3] = f'X   Sound sum : {sound_sum}'

        dots = ' ' + '·' * max_distance
        output[1] = dots
        output[5] = dots

        hor_limit = '=' * max(map(len, output))

        return '\n'.join([hor_limit + ' ' + ' '.join(command)] + output + [hor_limit])
