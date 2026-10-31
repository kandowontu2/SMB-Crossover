"""Port the donor's hover pose consumer without moving existing entries."""
from pathlib import Path
import json
import shutil
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from discover_smb3plus_chr_routes_1030_v1 import DONOR

P=R/'build/smb3plus-menu-host-1031-v4'
O=R/'build/smb3plus-peach-air-frame-1031-v1';J=O/'joint'
S=R/'tools/reference/smb3plus_peach_air_frame_1031_v1.s'


def once(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new)


def main():
    assert not O.exists()
    parent=json.loads(B.read(P/'source-stage.json'));B.bound(parent)
    negative=R/'build/smb3plus-whole-controller-probe-1031-v1/probe.json'
    failed=json.loads(B.read(negative));assert not failed['passed']
    assert any(c['character']==3 and any(x['field']=='Player_Frame' for x in c['differences']) for c in failed['cases'])
    old=scoped_load(P/'joint/candidate.nes')
    shutil.copytree(P/'joint',J)
    def rt(text):return text.replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix())
    for p in J.rglob('*'):
        if p.is_file() and p.suffix in ['.s','.inc','.cfg']:B.write(p,rt(B.read(p)))
    controller=J/'src/smb3_native_controller.inc'
    text=B.read(controller)
    span=' LDA #.lobyte(PF_JUMPBIG)\n LDY Player_YVel\n jmi PRG008_B0C3\n LDA #.lobyte(PF_FALLBIG)\n'
    text=once(text,span,' JSR ::MbPeachAirFrame\n .res 9,$ea\n')
    B.write(controller,text)
    data=J/'smb3plus_float_data.s';text=B.read(data)
    text=once(text,'MbFloatDataEnd:\n',B.read(S)+'\nMbFloatDataEnd:\n')
    B.write(data,text)
    recipes=[]
    for label in ['main-build','union-build','chr-build','final-link']:
        cmd=[rt(s) for s in json.loads(B.read(P/(label+'.json')))['command']]
        validate(cmd,J,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        B.write(O/(label+'.json'),json.dumps(dict(command=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr),indent=2)+'\n')
        assert p.returncode==0,(label,p.stderr)
        recipes.append(O/(label+'.json'))
    from prepare_cv3_dmc_mirror import prepare
    prepare(R,J/'candidate.nes');new=scoped_load(J/'candidate.nes')
    changed=[]
    for name,sym in old['syms'].items():
        if sym.get('type')=='lab' and address(old,name)!=address(new,name):
            assert name=='MbFloatDataEnd' and 'exp' not in sym,name
            changed.append(name)
    assert changed==['MbFloatDataEnd']
    assert old['raw'][:16]==new['raw'][:16]
    assert old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
    at=location(old,'M3Native::PRG008_B0C3')-12
    helper=location(new,'MbPeachAirFrame');size=int(new['syms']['MbPeachAirFrame']['size'])
    assert helper==16+91*8192+0x13b2 and size<=78
    assert old['raw'][helper:helper+size]==bytes([255])*size
    allowed=set(range(at,at+12))|set(range(helper,helper+size))
    diff=[i for i,(a,b) in enumerate(zip(old['raw'],new['raw'])) if a!=b]
    assert set(diff)<=allowed
    body=DONOR.read_bytes();bank=16+32*8192
    d=dict(status='PRIVATE_PEACH_SOURCE_HOVER_POSE_CONSUMER',source=True,native=False,installed=False,
        parent=parent['candidate'],candidate=B.sha(J/'candidate.nes'),joint=str(J),
        all_existing_callable_labels_preserved=True,changed_private_end_labels=changed,CHR_byte_exact=True,
        helper_bytes=size,ROM_changed_bytes=len(diff),
        original_source=dict(bank=32,PC=0xb140,end_exclusive=0xb170,bytes=body[bank+0x1140:bank+0x1170].hex()),
        correction='After BAC0 changes hover velocity to FF, donor32:B140 reverses the ordinary jump/fall pose. Microgoomba forces falling. Original dry/air/duck/fly predicates remain in the caller.',
        limits=['Private64 ancestor; not admitted or installed. Whole-controller, foreign ABI, vectors, graphics and native checks required.',
            'Ground pound, custom stomp delay, special art consumers and kick audio remain unfinished.'],
        bindings={str(p):B.sha(p) for p in [Path(__file__),S,DONOR,P/'source-stage.json',negative,
            controller,data,J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',*recipes]})
    B.write(O/'source-stage.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps({k:d[k] for k in ['candidate','helper_bytes','ROM_changed_bytes','all_existing_callable_labels_preserved','native']}))


if __name__=='__main__':main()
