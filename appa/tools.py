from typing import Generic, Dict, TypeVar, Union, cast, Iterator, Tuple, Generator, List
from typing_extensions import Protocol

M = TypeVar('M')
N = TypeVar('N')
C = TypeVar("C", bound="Comparable")

class Comparable(Protocol):
    def __lt__(self: C, other: C) -> bool: pass
    def __gt__(self: C, other: C) -> bool: pass

def minmax(iter: Iterator[C]) -> Tuple[C, C]:
    least = next(iter)
    most = least
    for item in iter:
        if item < least: least = item
        if item > most:  most = item
    return least, most

def flatten(*args: Union[M, Iterator[M]]) -> Iterator[M]:
    for arg in args:
        if isinstance(arg, Iterator):
            yield from arg
        else:
            yield arg

class BijectMap(Generic[M, N]):
    da: Dict[M, N] = {}
    db: Dict[N, M] = {}

    def insert_ab(self, a: M, b: N):
        self.da[a] = b
        self.db[b] = a
    def insert_ba(self, b: N, a: M):
        self.da[a] = b
        self.db[b] = a
    def get_a(self, a: M) -> N:
        return self.da[a]
    def get_b(self, b: N) -> M:
        return self.db[b]
    def __contains__(self, what: Union[M, N]):
        return what in self.da or what in self.db # type: ignore
    def __len__(self):
        return len(self.da)
    
    def a_iter(self) -> Iterator[M]:
        for a in self.da:
            yield a
    def b_iter(self) -> Iterator[N]:
        for b in self.db:
            yield b