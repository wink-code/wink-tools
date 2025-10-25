from node import *
class FluxPrinter:
    def visit(self, node:Node):
        name = node.__class__.__name__
        return getattr(self, f"visit_{name}")(node)
    
    def visit_PipeExpr(self, n:PipeExpr):
        return '|>'.join(child.accept(self) for child in n.body)
    
    def visit_From(self, n:From):
        return f'from (bucket:"{n.bucket}")'
    
    def visit_Range(self, n:Range):
        stop = f', stop={n.stop}' if n.stop else ''
        return f'start:{n.start} {stop}'

    def visit_Filter(self, n:Filter):
        return f'filter(fn: (r)=> {n.pred.accept(self)})'

    def visit_BinaryExpr(self, n:BinaryExpr):
        r = f'"{n.right}"' if isinstance(n.right,str) else n.right
        return f'r.{n.left} {n.op} {r}'

    def visit_AggregateWindow(self, n:AggregateWindow):
        ce = str(n.createEmpty).lower()
        return f'aggregateWindow(every:{n.every}, fn:{n.fn}, createEmpty:{ce})'

    def visit_Yield(self, n:Yield):
        name = f'"{n.name}"' if n.name else ''
        return f'yield(name: {name})'