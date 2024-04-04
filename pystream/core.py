from abc import ABC, abstractmethod
from typing import Any, Callable


class IStream(ABC):
    def __init__(self, graph: Any, name: str) -> None:
        self._graph = graph
        self._name = name
        self._children: list[IStream] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def graph(self) -> Any:
        return self.graph

    @property
    def children(self) -> list["IStream"]:
        return self._children

    def emit(self, value: Any, upstream: "IStream" = None) -> None:
        print(f"[{self.name}] receiving {value}")
        for child in self._children:
            print(f"[{self.name}] emitting {value} to {child.name}")
            child.emit(value, upstream=self)


class IOutputStream(IStream):
    @abstractmethod
    def current_value(self) -> Any:
        pass


class Graph:
    def __init__(self):
        self._root_nodes: list[IStream] = []
        self._nodes: dict[str, IStream] = {}
        self._next_stream_id = 0

    @property
    def root_nodes(self) -> list[IStream]:
        return self._root_nodes

    @property
    def next_stream_id(self) -> int:
        return self._next_stream_id

    @property
    def stream_count(self) -> int:
        return len(self._nodes)

    def new_stream(self, name: str) -> IStream:
        assert name not in self._nodes, "Node name duplicated"
        new_stream = Stream(self, name)
        self._nodes[name] = new_stream
        self._next_stream_id += 1
        self._root_nodes.append(new_stream)
        return new_stream

    def register_stream(self, stream: IStream) -> None:
        assert stream.name not in self._nodes, "Node name duplicated"
        self._nodes[stream.name] = stream
        self._next_stream_id += 1


class Stream(IStream):
    def map(self, func: Callable, name: str = None) -> "Map":
        new_stream = Map(self._graph, name or f"map-{self._graph.next_stream_id}", func)
        self._graph.register_stream(new_stream)
        self._children.append(new_stream)
        return new_stream

    @classmethod
    def zip(cls, func: Callable, *upstreams: IStream, name: str = None) -> "Zip":
        graph = upstreams[0]._graph
        new_stream = Zip(graph, name or f"zip-{graph.next_stream_id}", func, *upstreams)
        graph.register_stream(new_stream)
        for upstream in upstreams:
            upstream.children.append(new_stream)
        return new_stream

    def output(self, name: str = None) -> "Output":
        new_stream = Output(self._graph, name or f"output-{self._graph.next_stream_id}")
        self._graph.register_stream(new_stream)
        self._children.append(new_stream)
        return new_stream


class Map(Stream):
    def __init__(self, graph: Graph, name: str, func: Callable) -> None:
        super().__init__(graph, name)
        self._func = func

    def emit(self, value: Any, upstream: "IStream" = None) -> None:
        print(f"[{self.name}] receiving {value}")
        result = self._func(value)
        print(f"[{self.name}] emitting {result}")
        super().emit(result, upstream=self)


class Zip(Stream):
    def __init__(
        self, graph: Graph, name: str, func: Callable, *upstreams: IStream
    ) -> None:
        super().__init__(graph, name)
        self._func = func
        self._upstreams = upstreams
        self._upstream_idx = {
            upstream.name: idx for idx, upstream in enumerate(upstreams)
        }
        self._current_inputs = [None] * len(self._upstreams)
        self._received = 0

    def emit(self, value: Any, upstream: "IStream" = None) -> None:
        print(f"[{self.name}] receiving {value}")
        assert upstream is not None

        idx = self._upstream_idx[upstream.name]
        assert self._current_inputs[idx] is None
        self._current_inputs[idx] = value
        self._received += 1

        if self._received != len(self._upstreams):
            return

        result = self._func(*self._current_inputs)

        # free up immediately
        self._current_inputs = [None] * len(self._upstreams)
        self._received = 0

        print(f"[{self.name}] emitting {result}")
        super().emit(result, upstream=self)


class Output(IOutputStream):
    def __init__(self, graph: Graph, name: str) -> None:
        super().__init__(graph, name)
        self._current_value = None

    def current_value(self) -> Any:
        return self._current_value

    def emit(self, value: Any, upstream: "IStream" = None) -> None:
        print(f"[{self.name}] receiving {value}")
        self._current_value = value
