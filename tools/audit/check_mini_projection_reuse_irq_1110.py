"""Exercise genuine native IRQ and FF NMI at both modified projection spans."""

import argparse
import inspect
import json
from pathlib import Path

import check_mini_projection_reuse_1110 as P
import check_mini_sweep_center_irq_1110 as IRQ
from check_mini_funded_actor_1108_v3 import install
from measure_mini_kernel_transport_1109 import replace_one


class ScratchGuard(IRQ.ScratchGuard):
    def check_scratch(self,address):
        super().check_scratch(address)
        if self.in_vector and isinstance(address,int) and self.rawtags[2]==2:
            assert not 0xc2e0<=address<=0xc2e9,('ISR touched the live tile packet',hex(address))


def qualify(image,spans):
    # Keep the existing real IdleLoop stack entrance and complete vector
    # continuation oracle. Select only the two changed instruction ranges.
    source = inspect.getsource(IRQ.qualify)
    old_window = """    start = find('a9008d7dc2')
    end = find('a9008d02c28d03c28d22c28d23c28d4ec2')
    center = find('18ad54c26d55c2c9806a8d7ec2')
"""
    source = replace_one(source,old_window,
                         "    xbound,ybound = spans\n"
                         "    for lo,hi in spans:\n"
                         "        assert hi-lo==21 and kernel[lo-0xa000:lo-0xa000+4]==bytes.fromhex('ad72c218')\n")
    source = replace_one(source,'not start<=pc<end',
                         'not any(lo<=pc<hi for lo,hi in spans)')
    source = replace_one(source,"('ground_left',(252,176,4,-5602,0,0x42,1))):",
                         "('ground_left',(252,176,4,-5602,0,0x42,1)),\n"
                         "                          ('rise_y_wrap',(1511,231,13,5602,-6144,0xc1,0)),\n"
                         "                          ('ground_x_wrap',(255,176,4,-5602,0,0x42,1))):")
    source = replace_one(source,"            assert (center in seen)==name.startswith('rise_'),(name,hex(center))",
                         "            assert xbound[0] in seen and (ybound[0] in seen)==(not name.startswith('rise_')),(name,seen)")
    scope = dict(vars(IRQ),ScratchGuard=ScratchGuard,spans=spans)
    exec(compile(source,str(Path(__file__)),'exec'),scope)
    return scope['qualify'](image)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    output = args.output.resolve()
    path = output/'proof.json'
    proof = json.loads(path.read_text())
    assert output.is_relative_to(P.R/'build') and proof['passed']
    raw = P.BASE.read_bytes()
    assert P.M.sha(raw)==P.PIN==proof['parent_SHA256']
    candidate = install(raw,proof['patches'])
    assert P.M.sha(candidate)==proof['expected_memory_only_SHA256']
    result = qualify(candidate,proof['Mini_sweep_CPU_spans'])
    q = result|dict(passed=True,ROM_written=False,parent_SHA256=P.PIN,
                    memory_image_SHA256=P.M.sha(candidate),
                    bindings={f.resolve().relative_to(P.R).as_posix():P.M.sha(f.read_bytes())
                              for f in (Path(__file__),Path(IRQ.__file__),Path(IRQ.Q.__file__),
                                        path,P.R/'src/reset.s')})
    (output/'irq.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
