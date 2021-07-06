class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def setX(self, x):
        self.x = x

    def setY(self, y):
        self.y = y

    def to_string(self):
        return str("x: ", self.x, "y: ", self.y)

    def same(self, point):
        # method returns true if two points are the same and false otherwise
        if self.x == point.getX() and self.y == point.getY():
            return True
        else:
            return False