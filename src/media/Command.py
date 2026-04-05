import json
from Communication import Communication

class Command(Communication):
    def __init__(self, command_type:str = 'pause', command_increment:int = 0):
        self.type = command_type
        self.increment = command_increment
    def toString(self):
        return(
            json.dumps(
                {
                    'communicationType':'command',
                    'type': self.type,
                    'increment': self.increment
                }
            )
        )
