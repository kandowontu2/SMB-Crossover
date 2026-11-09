"""Interrupt the new Mini state selector and right-to-left sweep continuation."""

import argparse
import inspect
import json
from pathlib import Path

import check_mini_jump_lane_reuse_1110 as J
import check_mini_sweep_center_irq_1110 as IRQ
from check_mini_funded_actor_1108_v3 import install
from measure_mini_kernel_transport_1109 import replace_one


class ScratchGuard(IRQ.ScratchGuard):
    def check_scratch(self,address):
        super().check_scratch(address)
        if self.in_vector and isinstance(address,int) and self.rawtags[2]==2:
            assert not (0xc240<=address<=0xc24c or 0xc2e0<=address<=0xc2e9), (
                'ISR Mini classifier or tile scratch access',hex(address))


def qualify(image):
    # Reuse the exact linked-vector oracle and native stack entrance. Only
    # the watched code interval and seeded source scenarios change here.
    source = inspect.getsource(IRQ.qualify)
    source = replace_one(source, "start = find('a9008d7dc2')",
                         "start = find('8a48ae40c2bd')")
    source = replace_one(source,"end = find('a9008d02c28d03c28d22c28d23c28d4ec2')",
                         "end = find('ad70c28d50c2ad71c28d51c2') + 12")
    source = replace_one(source,"center = find('18ad54c26d55c2c9806a8d7ec2')",
                         "flip = find('ade0c249088de0c2')\n"
                         "    full = find('ad54c24c')\n"
                         "    reuse = find('ad54c28d7ac2ad70c2')")
    source = replace_one(source,"('ground_left',(252,176,4,-5602,0,0x42,1))):",
                         "('ground_left',(252,176,4,-5602,0,0x42,1)),\n"
                         "                          ('rise_cross',(1530,135,13,5602,-6144,0xc1,0)),\n"
                         "                          ('rise_wall',(1511,135,13,5602,-6144,0xc1,0)),\n"
                         "                          ('state_end',(1511,135,14,0,0,0,0))):")
    source = replace_one(source,'            setup(bus,*args)',
                         "            setup(bus,*args)\n"
                         "            if name=='rise_wall':\n"
                         "                bus[M.address(bundle,'Block_Buffer_2')+0x8e]=0x54")
    source = replace_one(source,"            assert (center in seen)==name.startswith('rise_'),(name,hex(center))",
                         "            if name in ('rise_right','rise_left','rise_cross','rise_wall'):\n"
                         "                assert (flip in seen)==(name=='rise_left'),(name,hex(flip))\n"
                         "                assert (full in seen)==(name in ('rise_cross','rise_wall')),(name,hex(full))\n"
                         "                assert (reuse in seen)==(name in ('rise_right','rise_left')),(name,hex(reuse))")
    scope = dict(vars(IRQ),ScratchGuard=ScratchGuard)
    exec(compile(source,str(Path(__file__)), 'exec'),scope)
    return scope['qualify'](image)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    proof = args.output/'proof.json'
    q = json.loads(proof.read_text())
    old,_ = J.base_image()
    assert J.M.sha(old)==q['parent_SHA256']
    candidate = install(old,q['patches'])
    assert J.M.sha(candidate)==q['expected_memory_only_SHA256']
    result = qualify(candidate)
    refs = Path(__file__),Path(IRQ.__file__),proof
    result.update(passed=True,memory_image_SHA256=J.M.sha(candidate),ROM_written=False,
                  bindings={p.resolve().relative_to(J.R).as_posix():J.M.sha(p.read_bytes()) for p in refs})
    (args.output/'irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
