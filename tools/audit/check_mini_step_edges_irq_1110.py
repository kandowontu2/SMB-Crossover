"""Check the Mini edge successor through native lag-NMI and hardware IRQ."""

import argparse
import inspect
import json
from pathlib import Path

import check_mini_step_alu_irq_1110 as AluIRQ
import check_mini_step_edges_1110 as Edges
import check_mini_sweep_center_irq_1110 as IRQ
from check_mini_funded_actor_1108_v3 import install
from measure_mini_kernel_transport_1109 import replace_one


SPANS = ((0xa593,0xa61f),(0xa73c,0xa761),(0xab49,0xab7a),
         (0xaff8,0xb01e),(0xb0b1,0xb0b7),(0xb180,0xb199))


def qualify(image):
    code = image[Edges.L.CODE:Edges.L.CODE+5120]
    signatures = {0xa5e6:'c900d01a',0xa601:'4c3ca7',0xa73c:'a9018d7dc2a220',
                  0xb004:'2080b18d58c28d5ac2',0xb180:'ad72c20a2e73c2'}
    for pc,data in signatures.items():
        expected = bytes.fromhex(data)
        assert code[pc-0xa000:pc-0xa000+len(expected)]==expected,hex(pc)
    source = inspect.getsource(IRQ.qualify)
    source = replace_one(source,"    start = find('a9008d7dc2')\n"
                                "    end = find('a9008d02c28d03c28d22c28d23c28d4ec2')\n"
                                "    center = find('18ad54c26d55c2c9806a8d7ec2')\n",
                                '    assert spans\n')
    source = replace_one(source,'not start<=pc<end','not any(lo<=pc<hi for lo,hi in spans)')
    source = replace_one(source,"('ground_left',(252,176,4,-5602,0,0x42,1))):",
                                "('ground_left',(252,176,4,-5602,0,0x42,1)),\n"
                                "                          ('stationary',(711,176,4,0,256,0,0)),\n"
                                "                          ('crouch',(711,176,7,0,256,4,1))):")
    source = replace_one(source,"            assert (center in seen)==name.startswith('rise_'),(name,hex(center))",
                                "            assert 0xb180 in seen and 0xa73c in seen,(name,seen)\n"
                                "            if name=='stationary':\n"
                                "                assert 0xa601 in seen and 0xa604 not in seen,seen\n"
                                "            if name=='crouch':\n"
                                "                assert 0xb0b1 in seen,seen")
    scope = dict(vars(IRQ),ScratchGuard=AluIRQ.ScratchGuard,spans=SPANS)
    exec(compile(source,str(Path(__file__)),'exec'),scope)
    return scope['qualify'](image)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',required=True,type=Path)
    args = cli.parse_args()
    proof_path = args.output/'proof.json'
    proof = json.loads(proof_path.read_text())
    before = Edges.BASE.read_bytes()
    assert proof['passed'] and Edges.M.sha(before)==Edges.PIN==proof['parent_SHA256']
    for path,h in proof['bindings'].items():
        assert Edges.M.sha(Path(path).read_bytes())==h,path
    after = install(before,proof['patches'])
    assert Edges.M.sha(after)==proof['expected_memory_only_SHA256']
    result = qualify(after)
    result.update(passed=True,parent_SHA256=Edges.PIN,ROM_written=False,
                  memory_image_SHA256=Edges.M.sha(after),
                  bindings={str(p.resolve()):Edges.M.sha(p.read_bytes()) for p in
                            (Path(__file__),Path(IRQ.__file__),Path(IRQ.Q.__file__),
                             Path(AluIRQ.__file__),proof_path,Edges.R/'src/reset.s')})
    (args.output/'irq.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
