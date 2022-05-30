from view import View
from stegano import Stegano

class Controller:

    def __init__(self):
        self.stegano = Stegano()
        self.view = View(self, self.stegano)

    def run(self):
        self.view.run()