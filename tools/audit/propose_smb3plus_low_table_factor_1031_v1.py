"""Measure a lossless source-table factor for the remaining donor abilities.

This produces a proposal only. It does not change a cartridge, menu, source
leaf or readiness. Five redundant81B tables can fund the missing original
ground-pound logic while keeping the original low-bank lookup results.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from private_build_outputs_v1 import validate

J=R/'build/smb3plus-peach-gravity-consumer-1031-v1/joint'
O=R/'build/smb3plus-low-table-factor-proposal-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists();O.mkdir()
    art=J/'src/smb3_mario_art.inc';text=art.read_text();b=scoped_load(J/'candidate.nes')
    arrays={int(m[1]):list(map(int,m[2].split(','))) for m in re.finditer(r'M3Form(\d)ChrLo: \.byte ([0-9,]+)',text)}
    assert set(arrays)=={0,1,2,3,4,6}
    arrays[5]=[v+4 for v in arrays[3]]
    offsets=[]
    for form in range(7):
        assert len(arrays[form])==81
        differences={(v-base)&255 for v,base in zip(arrays[form],arrays[0])}
        assert len(differences)==1;offsets.append(differences.pop())
        assert all((base+offsets[-1])&255==v for base,v in zip(arrays[0],arrays[form]))
    helper='''; UNADOPTED lossless low-table factor. Preserve X/Y, resultA and all P.
.setcpu "6502"
.macro phx
 txa
 pha
.endmacro
.macro plx
 pla
 tax
.endmacro
'''
    helper+=''.join(f'{n}=${address(b,n):04x}\n' for n in ['R0','M3RenderForm','SmChrBank'])
    helper+='''MbChrOffsets=$c000 ; proposed seven-byte table in retired form1Lo
.segment "CODE"
.export MbFactoredLow
.proc MbFactoredLow
 php
 phx
 ldx M3RenderForm
 lda (R0),y
 clc
 adc MbChrOffsets,x
 sta SmChrBank
 plx
 lda SmChrBank
 plp
 rts
.endproc
'''
    source=O/'proposal.s';source.write_text(helper,encoding='utf-8',newline='\n')
    obj=O/'proposal.o';cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-o',str(obj),str(source)]
    guard=validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    dump=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-segments',str(obj)],cwd=R,capture_output=True,text=True,check=True).stdout
    code=dump[dump.index('Name:                    "CODE"'):]
    size=int(re.search(r'Size:\s+(\d+)',code)[1]);assert size<=23
    out=dict(proposal_only=True,source=True,cartridge_modified=False,native=False,ready=False,
        parent=sha(J/'candidate.nes'),offsets=offsets,exact_form_frame_results=567,
        proposed_pointer_change='All seven low-table pointers reference original form0Lo. Add per-form modulo256 offset before publishing SmChrBank. High-table pointers and final CHR pages remain unchanged.',
        reclaimed_tables=[dict(form=f,bytes=81,PC=address(b,f'M3Form{f}ChrLo')) for f in [1,2,3,4,6]],
        total_redundant_bytes=405,offset_table_bytes=7,available_for_original_abilities=398,
        measured_helper_bytes=size,original_helper_reserved_bytes=23,
        limits=['No code adopted. Need exact9072 graphics/application-write comparison with precisely classified first low-pointer stores, original pixel/palette assertions, live interrupts and native replay before integrating.',
            'Retired low tables must be proven unconsumed by every actual pointer/direct consumer before writing ability code. Existing form5Lo code is not reclaimed.'],
        compile=dict(command=cmd,output_guard=guard,returncode=p.returncode,stderr=p.stderr,segment_dump=dump),
        bindings={str(q):sha(q) for q in [Path(__file__),art,J/'candidate.nes',J/'candidate.dbg',source,obj]})
    (O/'proposal.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(proposal_only=True,offsets=offsets,helper_bytes=size,available_bytes=398)))


if __name__=='__main__':main()
