from schema import Schema
from typing import Dict, Any

class Validator:
    def __init__(self, schema):
        self.schema = schema
    
    def validate(self, raw:Dict[str,Any])->Dict[str,Any]:
        cleaned: Dict[str, Any] = {}
        for key, rule in self.schema.items():
            value = raw.get(key, rule.get('default'))
            if  rule.get('required') and value is None:
                raise ValueError(f'{key} is required.')
            cleaned[key] = self._check_type(value, rule)
        return cleaned
    
    def _check_type(self, v, rule):
        if v is None:
            return None
        
        t = rule['type']
        if t == 'str':
            return str(v)
        if t == 'bool':
            return bool(v)
        if t == 'choices':
            if v not in rule['choices']:
                raise ValueError(f'value{v} is not in the options.')
            return v
        if t == 'list':
            if not isinstance(v, list):
                raise ValueError(f'{v} is not list.')
            sub = Validator(rule['item'])
            collector = []
            for item in v:
                collector.append(sub.validate(item))
            return collector
            # return [self._check_type(item, rule['item']) for item in v]
        if t == 'dict':
            sub = Validator(rule['fields'])
            return sub.validate(v)
        raise TypeError(f"Unknown type{t}")
    
