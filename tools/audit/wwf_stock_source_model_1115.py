"""Extend the frozen original-CPU route driver with read-only write callbacks."""
from hashlib import sha256
from pathlib import Path
import inspect
import check_smb1_alts_full11_1114 as Previous


def run(raw,key,limit=4700):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()=='9f56378f3e7ac12765927ebfef824ba7de70805c4105b6a68d89a00280a9d87f'
    source=inspect.getsource(Previous.run)
    def once(old,new):
        nonlocal source
        assert source.count(old)==1,old;source=source.replace(old,new,1)
    once('callbacks=defaultdict(list);events=defaultdict(list)','callbacks=defaultdict(list);write_callbacks=defaultdict(list);events=defaultdict(list)')
    once('dict(exec=0)','dict(exec=0,write=1)')
    once('        assert kind==0\n        for at in range(lo,lo+1 if hi is None else hi+1):callbacks[at].append(fn)',
        '        assert kind in(0,1)\n        target=callbacks if kind==0 else write_callbacks\n        for at in range(lo,lo+1 if hi is None else hi+1):target[at].append(fn)')
    once('    base=N.NesMPU\n', '''    base=N.NesMPU
    old_bus=type(m)
    class WriteObserved(old_bus):
        def __setitem__(self,at,value):
            if isinstance(at,int):
                for fn in tuple(write_callbacks.get(at,())):fn(at,value)
            return super().__setitem__(at,value)
    m.__class__=WriteObserved
''')
    once("    q=ctx['receipt']or{}", "    m.__class__=old_bus\n    q=ctx['receipt']or{}")
    namespace=dict(Previous.__dict__)
    exec(compile(source,str(Path(__file__))+':readonly-callback-adapter','exec'),namespace)
    q=namespace['run'](raw,key,limit)
    q.update(source_driver_SHA256=sha256(Path(Previous.__file__).read_bytes()).hexdigest(),
        readonly_memory_write_callbacks=True,source_driver_gameplay_or_scheduler_change=False)
    return q
