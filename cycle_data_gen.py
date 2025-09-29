import asyncio
import typing
import itertools
async def read_data(data_iter:typing.Iterable):
    for item in itertools.cycle(data_iter):
        yield item

def write_data(collector:list,path:str):
    df = pd.DateFrame(collector)
    pd.to_csv(df,path,mode='a',head=False)

async def supervisor(period:floatm, chunk_size:int, path:str):
    # is_head = True
    collector = []
    data = transfer_data()
    # get columns
    columns = get_columns()
    k = 0
    # write columns
    asyncio with open(path,'w') as f:
        pd.to_csv(columns=columns)
    async for item in read_data(data):
        try:
            await asyncio.sleep(period)
        except asyncio.CancelledError:
            write_data(collector,path)
            break
        collector.append(item)

    if len(collector) > chunk_size:
        await asyncio.to_thread(write_data,collector,path)
        collector.clear()
        k += 1
        print(f'written {k}')

def main():
    asyncio.run(supervisor(period,chunk_size,path))
