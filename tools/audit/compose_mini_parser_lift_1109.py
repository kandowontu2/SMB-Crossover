"""Compose the independently qualified parser and native lift changes."""
import argparse
import json
from pathlib import Path
import shutil

from compose_mini_frame_budget_1108 import check_full_cpu, compose, load
from measure_parser_dual_shadow_1109 import BASE, PIN, R
from prepare_selected_native_packet_v1 import sha

PARSER = R/'build/parser-dual-shadow-1109/proof.json'
PARSER_IRQ = R/'build/parser-dual-shadow-irq-1109/health-batch-async-v3.json'
LIFT = R/'build/mini-active-actor-1108-v1/lift-bridge-v4.json'
LIFT_IRQ = LIFT.with_name('lift-bridge-v5-CPU.json')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert sha(BASE)==PIN
    parser_proof,lift,parser_irq,lift_irq=map(load,(PARSER,LIFT,PARSER_IRQ,LIFT_IRQ))
    for proof,irq,path,key in ((parser_proof,parser_irq,PARSER,'memory_image_SHA256'),
                               (lift,lift_irq,LIFT,'expected_memory_only_SHA256')):
        assert irq['passed'] and irq['base_SHA256']==PIN
        assert irq[key]==proof['expected_memory_only_SHA256']
        assert {Path(name).resolve():pin for name,pin in irq['bindings'].items()}[path]==sha(path)
    raw=BASE.read_bytes()
    candidate=bytearray(raw)
    for proof in (parser_proof,lift):
        compose(raw,candidate,proof,parent=PIN)
    assert candidate[1048592:]==raw[1048592:]
    rows=check_full_cpu(raw,candidate,{})
    assert all(row['min_saved']>=0 for row in rows)
    args.output.mkdir()
    rom=args.output/'candidate.nes'
    rom.write_bytes(candidate)
    for suffix in ('.dbg','.lbl'):
        shutil.copyfile(BASE.with_suffix(suffix),rom.with_suffix(suffix))
    data=load(BASE.with_suffix('.json'))
    data.update(parent_SHA256=PIN,candidate_SHA256=sha(rom),parser_lift_CPU=rows,
                parser_lift_proofs={str(path):sha(path) for path in (PARSER,PARSER_IRQ,LIFT,LIFT_IRQ)})
    (args.output/'candidate.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(candidate_SHA256=sha(rom),parser_lift_CPU=rows)))


if __name__=='__main__':
    main()
