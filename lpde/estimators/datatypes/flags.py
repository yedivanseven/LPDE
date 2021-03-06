from multiprocessing import Event


class Flags:
    def __init__(self):
        self.__stop = Event()
        self.__done = Event()

    @property
    def stop(self) -> Event:
        return self.__stop

    @property
    def done(self) -> Event:
        return self.__done


if __name__ == '__main__':
    flag = Flags()
    print(flag.stop.is_set())
    flag.stop.set()
    print(flag.stop.is_set())
    flag.stop.clear()
    print(flag.stop.is_set())
    flag.done.set()
    print(flag.done.is_set())
