from random import randint, random
from time import sleep


class RetrievalControl:
    def __init__(self, min_value, max_value):
        self.__min_value = min_value
        self.__max_value = max_value

    def generage_random_num(self):
        return randint(self.__min_value, self.__max_value) + random()

    @property
    def wait(self):
        duration = self.generage_random_num()
        print(f'Wait {duration:0.2f} seconds!')
        sleep(duration)
