from typing import Dict, List, Set, Tuple, Union
import sys

from errors import Error
from graphics import Graphics
from systems import Sound, Wall


class Interpreter:
    def __init__(self, print_style) -> None:
        self.sounds: List[Sound] = []
        self.walls: List[Wall] = []
        self.noping: int = 0
        self.sound_sum: int = 0
        self.command_pointer: int = 0

        self.exited = False

        self.print_style = print_style

        self.sound_ids = 1
        self.wall_ids = -1


    def parse_lines(self, lines: List[str]) -> List[List[str]]:
        commands = []
        for line in lines:
            line = line.strip()

            if line == '' or not line[0].isalpha():
                continue

            command = line.split()
            command += [''] * (4 - len(command))
            commands.append(command)

        return commands


    def flatten(self, _for: Tuple[int, List[int]], fors: Dict[int, Tuple[int, List[int]]]) -> List[int]:
        repetitions, lines = _for
        new_lines = []
        for line in lines:
            if line in fors:
                new_lines.extend(self.flatten(fors[line], fors))
            else:
                new_lines.append(line)
        
        return new_lines * repetitions

    def flatten_code(self, commands: List[List[str]]) -> List[List[str]]:
        fors = {'_all_': [1, list(range(len(commands)))]}
        for line, command in enumerate(commands):
            if command[0] == 'for':
                fors[line] = (int(command[1]), list(range(line + 1, line + int(command[2]) + 1)))
        
        lines_indexes = self.flatten(fors['_all_'], fors)
        return [commands[line] for line in lines_indexes]



    def get_code_errors(self, commands: List[List[str]]) -> Union[None, Tuple[int, int, int]]:
        for l, command in enumerate(commands):
            operand = command[0]
            p1, p2, p3 = command[1:]
            if operand == 'nop':
                if p1 != '' and not p1.isnumeric():
                    return (l, 1, 1)
                if p1.isnumeric() and not Error.is_in_range(p1):
                    return (l, 2, 1)
            
            elif operand == 'send':
                if not p1.isnumeric():
                    return (l, 1, 1)
                if not Error.is_direction(p1):
                    return (l, 3, 1)
                if not p2.isnumeric():
                    return (l, 1, 2)
                if not Error.is_distance(p2):
                    return (l, 2, 2)
                if not p3.isnumeric():
                    return (l, 1, 3)
                if not Error.is_in_range(p3):
                    return (l, 2, 3)
            
            elif operand == 'redirect' or operand == 'predirect':
                if not p1.isnumeric():
                    return (l, 1, 1)
                if not Error.is_direction(p1):
                    return (l, 3, 1)
                if not p2.isnumeric():
                    return (l, 1, 2)
                if not Error.is_distance(p2):
                    return (l, 2, 2)
                if p3 != '' and not p3.isnumeric():
                    return (l, 1, 3)
            
            elif operand == 'condition' or operand == 'pcondition':
                if not p1.isnumeric():
                    return (l, 1, 1)
                if not Error.is_condition(p1):
                    return (l, 4, 1)
                if not p2.isnumeric():
                    return (l, 1, 2)
                if not Error.is_in_range(p2, min=-1):
                    return (l, 2, 2)
                if not p3.isnumeric():
                    return (l, 1, 3)
                if not Error.is_in_range(p3):
                    return (l, 2, 3)
            
            elif operand == 'for':
                if not p1.isnumeric():
                    return (l, 1, 1)
                if not Error.is_in_range(p1):
                    return (l, 2, 1)
                if not p2.isnumeric():
                    return (l, 1, 2)
                if not Error.is_in_range(p2):
                    return (l, 2, 2)
            
            elif operand == 'input':
                if not p1.isnumeric():
                    return (l, 1, 1)
                if not Error.is_direction(p1):
                    return (l, 3, 1)
                if not p2.isnumeric():
                    return (l, 1, 2)
                if not Error.is_distance(p2):
                    return (l, 2, 2)
            
            elif operand == 'wall':
                if not p1.isnumeric():
                    return (l, 1, 1)
                if not Error.is_direction(p1):
                    return (l, 3, 1)
                if not p2.isnumeric():
                    return (l, 1, 2)
                if not Error.is_distance(p2):
                    return (l, 2, 2)
            
            elif operand in ('print', 'exit'):
                pass
            
            else:
                return (l, 0, -1)

        return None

    def is_valid(self, command: List[str]) -> bool:
        if len(command) != 4:
            return False
        operand = command[0]
        param1, param2, param3 = command[1:]
        if operand == 'nop':
            return param1 == '' or param1.isnumeric()
        pass


    def update_system(self):
        self.sound_sum = 0
        destroyed_sounds: Set[Sound] = set()
        destroyed_walls: Set[Wall] = set()

        for sound in self.sounds:
            sound.move(self.walls, self.sounds)
            if sound.distance == 0:
                self.sound_sum += sound.intensity
                destroyed_sounds.add(sound)

        for sound in destroyed_sounds:
            if sound.wall in self.walls:
                destroyed_walls.add(sound.wall)
            if sound in self.sounds:
                self.sounds.remove(sound)
        
        for wall in self.walls:
            if wall.has_been_bounced_on:
                destroyed_walls.add(wall)

        for wall in destroyed_walls:
            self.walls.remove(wall)

        self.sound_sum = self.sound_sum % 256




    def send_sound(self, direction, intensity, distance) -> None:
        if 256 > intensity > 0:
            sound = Sound(direction, intensity % 256, distance, self.sound_ids)
            self.sound_ids += 1
            self.sounds.append(sound)
            self.walls.append(sound.wall)
        
    def spawn_wall(self, direction, distance):
        wall = Wall(direction, distance, self.wall_ids)
        self.wall_ids -= 1
        self.walls.append(wall)

    def get_directions(self, directions) -> List[int]:
        return [direction for direction in range(4) if directions & (2**direction)]

    def is_condition_fulfilled(self, condition: int, value: int) -> bool:
        smaller = (condition & 4) and (self.sound_sum < value)
        greater = (condition & 2) and (self.sound_sum > value)
        equal = (condition & 1) and (self.sound_sum == value)
        return any((smaller, greater, equal))

    def parse_data_input(self, data: str) -> int:
        if data == '':
            return 0
        if data.startswith('\\') and data[1:].isnumeric():
            return int(data[1:]) % 256
        
        return ord(data[0])

    def print(self):
        if self.print_style == 'ascii':
            print(chr(self.sound_sum), end='')
        elif self.print_style == 'numbers': 
            print(self.sound_sum)


    def execute_command(self, command: List[str]) -> None:
        operand = command[0]
        if operand == 'nop':
            self.noping = 0 if command[1] == '' else (int(command[1]) - 1)

        elif operand == 'send':
            for direction in self.get_directions(int(command[1])):
                self.send_sound(direction, int(command[3]), int(command[2]))

        elif operand == 'wall':
            for direction in self.get_directions(int(command[1])):
                self.spawn_wall(direction, int(command[2]))

        elif operand == 'redirect':
            for direction in self.get_directions(int(command[1])):
                if command[3] == '' or int(command[3]) & 1 == 0:
                    self.send_sound(direction, self.sound_sum, int(command[2]))
                else:
                    self.send_sound(direction, 256 - self.sound_sum, int(command[2]))

        elif operand == 'predirect':
            self.print()
            for direction in self.get_directions(int(command[1])):
                self.send_sound(direction, self.sound_sum, int(command[2]))

        elif operand == 'print':
            self.print()

        elif operand == 'condition':
            condition = int(command[1])
            condition_fulfilled = self.is_condition_fulfilled(condition, int(command[2]))
            if condition_fulfilled ^ bool(condition & 8):
                    self.command_pointer += int(command[3])

        elif operand == 'pcondition':
            self.print()
            condition = int(command[1])
            condition_fulfilled = self.is_condition_fulfilled(condition, int(command[2]))
            if condition_fulfilled ^ bool(condition & 8):
                    self.command_pointer += int(command[3])

        elif operand == 'input':
            data = self.parse_data_input(input('Character input : '))
            for direction in self.get_directions(int(command[1])):
                self.send_sound(direction, data, int(command[2]))
        
        elif operand == 'exit':
            self.exited = True
            

    def execute(self, lines: List[str]) -> None:
        commands = self.parse_lines(lines)
        errors = self.get_code_errors(commands)
        if errors is not None:
            print(Error.ERROR_DESC[errors[1]].replace('%p', str(errors[2])).replace('%c', ' '.join(commands[errors[0]])))
            return
        
        commands = self.flatten_code(commands)

        renders = []

        while not self.exited and (self.command_pointer < len(commands) or self.noping):
            if not self.noping:
                command = commands[self.command_pointer]
                self.execute_command(command)

                self.command_pointer += 1
            else:
                self.noping -= 1

            self.update_system()
            # print(command, self.sounds)
            renders.append(Graphics.render(command, self.sounds, self.walls, self.sound_sum, 10))

        with open('renders.txt', 'w', encoding='utf-8') as fo:
            fo.write('\n'.join(renders))
