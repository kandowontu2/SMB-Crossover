"""Interrupt the arithmetic successor through the real Mini GameLoop ingress."""

import argparse
import inspect
import json
from pathlib import Path

import check_mini_step_alu_1110 as P
import check_mini_sweep_center_irq_1110 as IRQ
from check_mini_funded_actor_1108_v3 import install
from measure_mini_kernel_transport_1109 import replace_one


class ScratchGuard(IRQ.ScratchGuard):
    def check_scratch(self,address):
        super().check_scratch(address)
        if self.in_vector and isinstance(address,int) and self.rawtags[2]==2:
            assert not (0xc200<=address<0xc27f or 0xc2e0<=address<=0xc2e9),(
                'ISR touched the live Mini step state',hex(address))


def qualify(image,spans):
    source=inspect.getsource(IRQ.qualify)
    source=replace_one(source,"    start = find('a9008d7dc2')\n"
                             "    end = find('a9008d02c28d03c28d22c28d23c28d4ec2')\n"
                             "    center = find('18ad54c26d55c2c9806a8d7ec2')\n",
                             '    assert len(spans)==5\n')
    source=replace_one(source,'not start<=pc<end','not any(lo<=pc<hi for lo,hi in spans)')
    source=replace_one(source,"            assert (center in seen)==name.startswith('rise_'),(name,hex(center))",
                             '            assert all(lo in seen for lo in (0xa3e5,0xaac7,0xacbf)),(name,seen)')
    scope=dict(vars(IRQ),ScratchGuard=ScratchGuard,spans=spans)
    exec(compile(source,str(Path(__file__)),'exec'),scope)
    return scope['qualify'](image)


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args=cli.parse_args()
    path=args.output/'proof.json'
    proof=json.loads(path.read_text())
    before=P.BASE.read_bytes()
    assert proof['passed'] and P.M.sha(before)==P.PIN==proof['parent_SHA256']
    candidate=install(before,proof['patches'])
    assert P.M.sha(candidate)==proof['expected_memory_only_SHA256']
    result=qualify(candidate,proof['code_spans'])
    result.update(passed=True,parent_SHA256=P.PIN,ROM_written=False,
                  memory_image_SHA256=P.M.sha(candidate),
                  bindings={str(p.resolve()):P.M.sha(p.read_bytes()) for p in
                            (Path(__file__),Path(IRQ.__file__),Path(IRQ.Q.__file__),path,P.R/'src/reset.s')})
    (args.output/'irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
