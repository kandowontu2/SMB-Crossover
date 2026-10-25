"""Exhaustive sampled-Y domain test against the original getter/empty contract."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_probes_oe import run
from check_tmnt_render_oa import load,address,location


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom);rows=[];empty=visible=0
    table=location(old,'BlockBuffer_Y_Adder')
    for name,physical in [('LmVisibleSideProbe',93),('TnMacVisibleSideProbe',89)]:
        for shifted,y,x,flags in itertools.product(range(256),[3,5],[0,15,127,255],[0x30,0x71,0x39,0xee]):
            sample=(shifted+old['raw'][table+y])&255;valid=32<=sample<240
            overrides={'Player_Y_Position':shifted,'Player_X_Position':x}
            reference='BlockBufferColli_Side'if valid else 0x7e00
            before=run(old,reference,15,0,0,y,flags,overrides=overrides,physical=physical)
            after=run(new,name,15,0,0,y,flags,overrides=overrides,physical=physical)
            assert before[:4]==after[:4],(name,shifted,y,x,flags,valid,before[0],after[0],
                [(hex(i),before[1][i],after[1][i])for i in range(0x8000)if before[1][i]!=after[1][i]][:12])
            visible+=valid;empty+=not valid
            rows.append(dict(entry=name,shiftedY=shifted,index=y,x=x,flags=flags,sampleY=sample,
                             visible=valid,reference_cycles=before[4],candidate_cycles=after[4]))
    q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
           cases=len(rows),visible_original_getter_cases=visible,unmapped_empty_cases=empty,
           scope='Both actual linked bank-local wrappers, all256 shifted Y bytes, both real upper-side indices, four X/cell edges and four flag states. In-domain samples execute the unmodified original getter; out-of-domain samples execute an independent LDA0/STA R3/RTS reference. Exact registers/meaningful flags/SP, application RAM except discarded stack/SMC/safecall/mapper bookkeeping, hardware and final banks. No out-of-domain native getter calls permitted; native reproduction/routes remain separate.')
    (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
