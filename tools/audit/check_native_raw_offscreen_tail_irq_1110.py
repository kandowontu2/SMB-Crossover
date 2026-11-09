"""Rebind the actual shared offscreen IRQ harness to the compact raw tail."""

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

import check_native_raw_offscreen_tail_1110 as T
import check_native_relative_offscreen_irq_1110 as IRQ
from check_mini_funded_actor_1108_v3 import install


def vectors(before,after):
    previous = IRQ.T
    # Reuse the unchanged harness's real native-actor setup and GameLoop
    # stack. Its first of two direct calls now enters the enemy bit wrapper.
    IRQ.T = SimpleNamespace(ENTRIES={'RelativeEnemyPosition':T.ENEMY},
                           SPANS=tuple((lo,hi) for _,lo,hi,_ in T.SPANS))
    try:
        return IRQ.vectors(before,after)
    finally:
        IRQ.T = previous


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert not (out/'irq.json').exists()
    path = out/'proof.json'
    proof = json.loads(path.read_text())
    before = T.BASE.read_bytes()
    assert proof['passed'] and T.P.sha(before)==T.PIN==proof['parent_SHA256']
    for file,digest in proof['bindings'].items():
        assert T.P.sha((T.R/file).read_bytes())==digest,file
    after = install(before,proof['patches'])
    assert T.P.sha(after)==proof['expected_memory_only_SHA256']
    result = vectors(before,after)
    q = result|dict(passed=True,ROM_written=False,parent_SHA256=T.PIN,
                    expected_memory_only_SHA256=T.P.sha(after),
                    bindings={p.resolve().relative_to(T.R).as_posix():T.P.sha(p.read_bytes())
                              for p in (Path(__file__),Path(IRQ.__file__),path,T.R/'src/reset.s')})
    (out/'irq.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='reached_foreground_sites'}),flush=True)


if __name__=='__main__':
    main()
