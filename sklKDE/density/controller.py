from multiprocessing import Array
from .parameters import ControllerParams, StreamerParams, GridMapperParams
from .streamer import Streamer
from .gridmapper import GridMapper

ARRAY = type(Array('d', 10))


class Controller:
    def __init__(self, params: ControllerParams) -> None:
        params = self.__params_type_checked(params)
        self.__data = params.data
        streamer_params = StreamerParams(params.bounds,
                                         params.producer,
                                         params.data)
        self.__stream = Streamer(streamer_params)
        gridmapper_params = GridMapperParams(params.kernel,
                                             params.bounds,
                                             params.grid,
                                             params.data)
        self.__gridmap = GridMapper(gridmapper_params)

    @property
    def alive(self) -> dict:
        return {'Streamer': self.__stream.is_alive(),
                'GridMapper': self.__gridmap.is_alive()}

    @property
    def gridmap(self) -> GridMapper:
        return self.__gridmap

    @property
    def stream(self) -> Streamer:
        return self.__stream

    def start(self) -> None:
        self.__stream.start()
        self.__gridmap.start()

    def stop(self) -> None:
        self.__gridmap.stop.set()
        self.__gridmap.join()
        self.__stream.stop.set()
        self.__stream.join()

    @staticmethod
    def __params_type_checked(value: ControllerParams) -> ControllerParams:
        if type(value) is not ControllerParams:
            raise TypeError('Parameters must be of type <ControllerParams>!')
        return value
