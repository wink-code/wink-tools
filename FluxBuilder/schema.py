from typing import Dict, List, Any

Schema: Dict[str,Any]={
    'bucket':{
        'type':'str',
        'required': True,
        'help': 'InfluxDB bucket name'
    },
    'start':{
        'type': 'str',
        'default': '-1h',
        'help': 'start time, such as -30d, -2h, 2025-10-25T02:40:00Z'
    },
    'stop':{
        'type': 'str',
        'required': False,
        'help': "stop time, allow to be empty"
    },
    'measurement':{
        'type': 'str',
        'required': False,
        'help': 'measurement filter value'
    },
    'field':{
        'type': 'str',
        'required': False,
        'help': 'field name filter value'
    },
    'tag_filters':{
        'type': 'list',
        'item':{
            'tag': {'type':'str'},
            'op': {'type':'choices', 'choices':['==','!=','=~','!~']},
            'value': {'type': 'str'}
        },
        'default': [],
        'help': 'tag filter form'
    },
    'aggregate':{
        'type': 'dict',
        'required': False,
        'fields':{
            'every': {'type':'str','default':'1m'},
            'fn': {'type': 'choices', 'choices':['mean','sum','count','last'],'default':'mean'},
            'createEmpty': {'type':'bool', 'default':False}
        }
    },
    'yield_name':{
        'type': 'str',
        'required': False,
        'help': 'yield costomized name'
    }
}
