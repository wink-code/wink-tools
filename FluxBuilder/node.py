from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field

@dataclass
class Node:
    def accept(self,visitor):
        return visitor.visit(self)

@dataclass
class PipeExpr(Node):
    body: List[Node] = field(default_factory=list)

@dataclass
class From(Node):
    bucket: str

@dataclass
class Range(Node):
    start: str
    stop: Optional[str]

@dataclass
class Filter(Node):
    pred: 'BinaryExpr'

@dataclass
class AggregateWindow(Node):
    every: str
    fn: str = 'mean'
    createEmpty: bool = False

@dataclass
class BinaryExpr(Node):
    left: str
    op: str
    right: Union[str,int,float,bool]

@dataclass
class Yield(Node):
    name: Optional[str] = None

