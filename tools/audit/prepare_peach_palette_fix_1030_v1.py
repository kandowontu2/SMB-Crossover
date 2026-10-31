"""Correct Peach's palette using her actual donor OAM/palette consumer.

The prior test authenticated palette memory but selected the wrong row.
Keep all historical evidence immutable; build a separate successor.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address
from benj_mario_donor_trace_1030_v1 import Bus,MPU,DONOR,EXPECTED
from prepare_benj_mario_source_art_1030_v1 import call

P=R/'build/benj-menu-unlocked-1030-v3'
O=R/'build/peach-palette-fix-1030-v1'
J=O/'joint'


def save(p,d): B.write(p,json.dumps(d,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--finish-existing',action='store_true')
    args=parser.parse_args()
    assert not O.exists() or (args.finish_existing and not (O/'source-stage.json').exists())
    h=json.loads(B.read(P/'handoff.json'));B.bound(h)
    assert B.sha(P/'handoff.json')=='4c3ae5f151776f374494fb9f553bc0a2d3b7491e66ff0c1ef65d8926cf3741ed'
    assert h['candidate']=='98048319d382e7a5c4e7186704b6e3b939eda4eec9bdd6e098c402cbd30799b6'
    donor_raw=DONOR.read_bytes();assert hashlib.sha256(donor_raw).hexdigest()==EXPECTED
    trace=R/'build/benj-peach-palette-trace-1030-v2'
    t=json.loads(B.read(trace/'trace.json'))
    assert t['source_sha256']==EXPECTED and t['snapshots'][-1]['character']==3
    assert t['snapshots'][-1]['palette'][25:28]==[0x16,0x30,0x27]
    assert all(q[2]&3==2 for q in t['snapshots'][-1]['visible_oam'])
    # Execute the real original palette selector. Normal Peach is P2;
    # this is not a guess from her character number (3) or an unused row.
    b=Bus(donor_raw);b.ram[:0x8000]=(trace/'ram.bin').read_bytes()
    b.reg=t['mapper_registers'];b.select=t['mapper_select'];b.remap()
    c=MPU(memory=b,pc=0x751d);b.cpu=c
    assert bytes(b[0x751d:0x7532])==bytes.fromhex('ae5307bc0b62ad5607c902d004b934ef60b930ef60')
    selectors=[]
    for status in [0,1,2]:
        b.ram[0x753]=0;b.ram[0x620b]=3;b.ram[0x756]=status
        cost=call(b,c,0x751d)
        assert c.a==(0 if status==2 else 2)
        selectors.append(dict(status=status,palette_index=c.a,CPU=cost))
    if not J.exists():shutil.copytree(P/'joint',J)
    def rt(s): return s.replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix())
    for p in J.rglob('*'):
        if p.is_file()and p.suffix in ['.s','.inc','.cfg']:
            B.write(p,rt(B.read(p)))
    p=J/'peach_float_core.s';s=B.read(p)
    old='Colors:.byte $16,$30,$27,$0f,$36,$17'
    replacement='; Normal donor Peach actually uses P2, just like Toad.\nColors:.byte $16,$30,$27,$16,$30,$27'
    assert (s.count(old),s.count(replacement)) in [(1,0),(0,1)]
    if old in s:B.write(p,s.replace(old,replacement))
    for label in ['main-build','union-build','final-link']:
        command=[rt(x)for x in json.loads(B.read(P/(label+'.json')))['command']]
        validate(command,J,cwd=R)
        z=subprocess.run(command,cwd=R,capture_output=True,text=True)
        save(O/(label+'.json'),dict(command=command,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr))
        assert z.returncode==0,(label,z.stderr)
    from prepare_cv3_dmc_mirror import prepare
    prepare(R,J/'candidate.nes')
    old,new=[load(p/'candidate.nes')for p in [P/'joint',J]]
    delta=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
    assert len(old['raw'])==len(new['raw'])and len(delta)==3
    assert delta==list(range(delta[0],delta[0]+3))
    assert bytes(old['raw'][i]for i in delta)==bytes.fromhex('0f3617')
    assert bytes(new['raw'][i]for i in delta)==bytes.fromhex('163027')
    assert (P/'joint/candidate.lbl').read_bytes()==(J/'candidate.lbl').read_bytes(),'No public or private entry moves'
    d=dict(source=True,native=False,installed=False,status='PEACH_NORMAL_PALETTE_CORRECTION_SOURCE_BUILT',
        parent=h['candidate'],parent_handoff_sha256=B.sha(P/'handoff.json'),candidate=B.sha(J/'candidate.nes'),
        joint=str(J),delta_offsets=delta,old_colors='0f3617',normal_source_colors='163027',
        donor_palette_selectors=selectors,donor_visible_OAM_palette=2,
        correction='The earlier test checked the wrong expected palette: P3 was an enemy palette, not Peach\'s actual P2.',
        limits=['Fire/star/area palette progression remains incomplete; this fixes the normal body row.',
                'No native qualification or installation yet.'],
        bindings={str(p):B.sha(p)for p in [Path(__file__),P/'handoff.json',R/'tools/audit/benj_peach_palette_trace_1030_v1.py',
            trace/'trace.json',trace/'ram.bin',trace/'ppu.bin',trace/'oam.bin',J/'peach_float_core.s',
            J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',O/'main-build.json',O/'union-build.json',O/'final-link.json']})
    save(O/'source-stage.json',d)
    print(json.dumps({k:v for k,v in d.items()if k!='bindings'},indent=2))


if __name__=='__main__':main()
