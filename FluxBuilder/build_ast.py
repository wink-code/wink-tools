from typing import Dict, Any
from node import *

def build_ast(clean:Dict[str,Any]) -> PipeExpr:
    pipe = PipeExpr()
    pipe.body.append(From(bucket=clean['bucket']))
    pipe.body.append(Range(start=clean['start'],stop=clean['stop']))

    # contribute filter action
    preds = []
    if clean.get('measurement'):
        preds.append(BinaryExpr('_measurement','==',clean['measurement']))
    if clean.get('field'):
        preds.append(BinaryExpr('_field','==',clean['field']))
    for tf in clean.get('tag_filters',[]):
        preds.append(BinaryExpr(tf['tag'],tf['op'],tf['value']))

    if preds:
        pipe.body.append(Filter(pred=preds[0]))
    
    if clean.get('aggregate'):
        agg = clean['aggregate']
        pipe.body.append(AggregateWindow(every=agg['every'],fn=agg['fn'],createEmpty=agg['createEmpty']))
    
    pipe.body.append(Yield(name=clean.get('yield_name')))
    return pipe


