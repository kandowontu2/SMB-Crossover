"""Interrupt the native Mini body box route and its original fallback."""

import argparse
import inspect
import json
from pathlib import Path

import check_mini_native_body_box_dispatch_1110 as D
import check_mini_sweep_center_irq_1110 as IRQ
from check_mini_funded_actor_1108_v3 import install
from measure_mini_kernel_transport_1109 import replace_one


def qualify(image):
    source = inspect.getsource(IRQ.qualify)
    start = source.index('    kernel = image[')
    end = source.index('    idle, loop, core =',start)
    source = source[:start]+source[end:]
    start = source.index("        for name,args in (('rise_right',")
    end = source.index('            bus = slim_fork(seed)',start)
    source = source[:start]+'''        setup_args = (1511,135,13,5602,-6144,0xc1,0)
        for name in ('mini_active','mini_box_rejected','foreign_mario','foreign_mac'):
'''+source[end:]
    source = replace_one(source,'            setup(bus,*args)',
                         '''            setup(bus,*setup_args)
            if name=='foreign_mario':
                N.put(bus,SelectedCharacter=0)
            elif name=='foreign_mac':
                N.put(bus,SelectedCharacter=15)''')
    source = replace_one(source,'''                if Q.tags(z)!=3 or not start<=pc<end or pc in seen:
                    return
                seen.add(pc)''', '''                tag = Q.tags(z)
                if name=='mini_box_rejected' and (tag,pc)==(221,0xa703):
                    # Corrupt one marker at the real body-box entry, after
                    # ordinary authenticated source movement has returned.
                    bus.ram[2][0x1fe0] = 0
                watched = (tag==221 and 0xa703<=pc<0xa788 or
                           tag==214 and (0xa2a9<=pc<0xa2b8 or 0xa454<=pc<0xa463) or
                           tag==254 and pc==0x9f4e)
                if not watched or (tag,pc) in seen:
                    return
                seen.add((tag,pc))''')
    source = replace_one(source,"            assert (center in seen)==name.startswith('rise_'),(name,hex(center))",
                         '''            assert (221,0xa703) in seen and (221,0xa776) in seen,name
            assert ((214,0xa2a9) in seen)==name.startswith('mini_'),name
            if name.startswith('mini_'):
                assert ((214,0xa45b) in seen)==(name=='mini_box_rejected'),name''')
    scope = dict(vars(IRQ))
    exec(compile(source,str(Path(__file__)), 'exec'),scope)
    return scope['qualify'](image)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    cpu = args.output/'proof.json'
    q = json.loads(cpu.read_text())
    raw = D.BASE.read_bytes()
    assert D.M.sha(raw)==q['parent_SHA256']==D.PIN
    image = install(raw,q['patches'])
    assert D.M.sha(image)==q['expected_memory_only_SHA256']
    result = qualify(image)
    refs = Path(__file__),Path(IRQ.__file__),cpu,D.R/'src/reset.s'
    result.update(passed=True,ROM_written=False,parent_SHA256=D.PIN,
                  expected_memory_only_SHA256=D.M.sha(image),
                  bindings={p.resolve().relative_to(D.R).as_posix():D.M.sha(p.read_bytes()) for p in refs})
    (args.output/'irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
