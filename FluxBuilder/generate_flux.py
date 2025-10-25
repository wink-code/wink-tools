from validator import Validator
from build_ast import build_ast
from schema import Schema
from printer import FluxPrinter
from typing import Dict, Any

def generate_flux(raw: Dict[str,Any])->str:
    clean = Validator(Schema).validate(raw)
    ast = build_ast(clean)
    return ast.accept(FluxPrinter())

if __name__=='__main__':
    job = {
        'bucket': 'mydb',
        'start': '-30m',
        'measurement': 'cpu',
        'tag_filters':[
            {'tag':'host','op':'==','value':'server01'}
        ],
        'aggregate':{
            'every': '1m',
            'fn': 'mean'
        },
        'yield_name': 'mean_cpu'
    }
    job1 = {
        'bucket': 'test_data',
        'start': '2025-07-18T12:00:00Z',
        'stop': '2025-08-20T12:00:00Z',
        'measurement': 'processing_quantity',
        'field': '1',
        'aggregate': {
            'every': '1m',
            'fn':'mean'
        },
        'yield_name': 'processing-quantity of machine 1'
    }

    print(generate_flux(job1))