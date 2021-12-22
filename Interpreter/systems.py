from __future__ import annotations
from typing import List, Tuple


class Wall:
    def __init__(self, direction, distance, id) -> None:
        self.direction = direction
        self.distance = distance
        self.id = id
        self.has_been_bounced_on = False
    
    def __str__(self) -> str:
        return f'Wall - ID : {self.id} | Dir : {self.direction} | Dist : {self.distance}'
    def __repr__(self) -> str:
        return str(self)

    def bounce(self, sound_id):
        if self.id < 0 or self.id == sound_id:
            self.has_been_bounced_on = True


class Sound:
    def __init__(self, direction, intensity, distance, id) -> None:
        self.direction = direction

        self.intensity = intensity

        self.just_created = True
        self.distance = 1
        self.previous_distance = None
        self.velocity = 1

        self.has_bounced_on_own_wall = False
        
        self.id = id

        self.wall = Wall(direction, distance, self.id)

    def __str__(self) -> str:
        return f'Sound - ID : {self.id} | Dir : {self.direction} | Int : {self.intensity} | Dist : {self.distance} | Wall dist : {self.wall.distance}'
    def __repr__(self) -> str:
        return str(self)
    
    def collides_with_wall(self, walls: List[Wall]) -> None:
        for wall in walls:
            if self.direction == wall.direction and self.distance == wall.distance:
                wall.bounce(self.id)
                return True
        return False

    def move(self, walls: List[Wall], sounds: List[Sound]) -> None:
        if self.just_created:
            self.just_created = False
            return

        if self.velocity > 0 and self.collides_with_wall(walls):
            self.velocity = -1

        self.previous_distance = self.distance
        self.distance += self.velocity

