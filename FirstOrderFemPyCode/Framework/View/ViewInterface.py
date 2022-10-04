import abc


class ViewInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def accept(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def reject(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def closing(self) -> None:
        raise NotImplementedError

    class CallbackInterface(metaclass=abc.ABCMeta):
        @abc.abstractmethod
        def onAccept(self) -> None:
            raise NotImplementedError

        @abc.abstractmethod
        def onReject(self) -> None:
            raise NotImplementedError

        @abc.abstractmethod
        def onClose(self) -> None:
            raise NotImplementedError
