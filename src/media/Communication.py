import json

class Communication:
    def __init__(self, type:str):
        self.type = type
    def toString(self):
        return(
            json.dumps(
                {
                    'type': self.type
                }
            )
        )
