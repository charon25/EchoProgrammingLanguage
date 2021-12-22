

class Error:

    ERROR_DESC = {
        0: 'Unknown command : %c',
        1: 'Not a number (parameter %p) : %c',
        2: 'Invalid range (parameter %p) : %c',
        3: 'Invalid direction (parameter %p) : %c',
        4: 'Invalid condition (parameter %p) : %c'
    }

    @staticmethod
    def is_in_range(value: str, min: int = 0, max: int = 256) -> bool:
        return min < int(value) < max
    
    @staticmethod
    def is_direction(value: str) -> bool:
        return int(value) & 15 > 0

    @staticmethod
    def is_distance(value: str) -> bool:
        return Error.is_in_range(value, 0, 256)

    @staticmethod
    def is_condition(value: str) -> bool:
        return int(value) & 7 > 0
