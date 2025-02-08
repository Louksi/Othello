class IllegalSize(Exception):
    def __init__(self, size: int):
        self.message = f"Can't make board of size {size}"
