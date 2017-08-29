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

    @property
    def any_set(self) -> bool:
        return any((self.__stop.is_set(), self.__done.is_set()))
