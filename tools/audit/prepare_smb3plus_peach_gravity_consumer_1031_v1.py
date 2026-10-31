"""Place the original E966/BAC0 observer at the actual gravity store."""
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

P=R/'build/smb3plus-peach-complete-controller-1031-v3'
O=R/'build/smb3plus-peach-gravity-consumer-1031-v1';J=O/'joint'


def once(t,a,b):
    assert t.count(a)==1,(a,t.count(a))
    return t.replace(a,b)


def main():
    assert not O.exists()
    parent=json.loads(B.read(P/'source-stage.json'));B.bound(parent)
    negative=R/'build/smb3plus-whole-controller-edges-1031-v1/probe.json'
    assert not json.loads(B.read(negative))['passed']
    old=scoped_load(P/'joint/candidate.nes');shutil.copytree(P/'joint',J)
    def rt(t):return t.replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix())
    for p in J.rglob('*'):
        if p.is_file() and p.suffix in ['.s','.inc','.cfg']:B.write(p,rt(B.read(p)))
    body=J/'src/smb3_native_controller.inc';text=B.read(body)
    count=text.count(' JSR ::MbPeachAfterJump\n');assert count==7,count
    text=text.replace(' JSR ::MbPeachAfterJump\n',' JSR Player_JumpFlyFlutter\n')
    text=once(text,' adc Player_YVel\n STA Player_YVel\n LDA Player_WagCount',
        ' adc Player_YVel\n JSR ::MbPeachAfterJump\n LDA Player_WagCount')
    B.write(body,text)
    art=J/'src/smb3_mario_art.inc';text=B.read(art)
    text=once(text,'.proc MbPeachAfterJump\n jsr M3Native::Player_JumpFlyFlutter\n',
        '.proc MbPeachAfterJump\n sta M3Native::Player_YVel ; original E966 gravity store\n')
    # Source31:B6C0 leaves A=anchor after first setup; B5ED compares that A.
    # This matters at Y2. Do not replace that original consumer with a new
    # semantic "ready==2" rule.
    text=once(text,'.proc MbPeachFloatCheck\n lda MbFloatReady\n cmp #2\n',
        '.proc MbPeachFloatCheck\n cmp #2\n')
    B.write(art,text)
    logs=[]
    for label in ['main-build','union-build','chr-build','final-link']:
        cmd=[rt(s) for s in json.loads(B.read(P/(label+'.json')))['command']]
        validate(cmd,J,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        B.write(O/(label+'.json'),json.dumps(dict(command=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr),indent=2)+'\n')
        assert p.returncode==0,(label,p.stderr);logs.append(O/(label+'.json'))
    from prepare_cv3_dmc_mirror import prepare
    prepare(R,J/'candidate.nes');new=scoped_load(J/'candidate.nes')
    changes=[]
    for n,s in old['syms'].items():
        if s.get('type')=='lab' and address(old,n)!=address(new,n):
            assert 'exp' not in s and (n.startswith(('MbPeachFloatCheck::','MbPeachFloatActive::')) or n=='MbPeachFloatActive'),n
            changes.append(dict(name=n,old=address(old,n),new=address(new,n)))
    assert old['raw'][:16]==new['raw'][:16]
    assert old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
    allowed=set()
    for n,end in [('M3Native::Player_Control','M3Native::Player_FlyTime'),('MbPeachAfterJump',None),('M3Form5ChrHi',None)]:
        if n=='M3Native::Player_Control':
            lo=16+92*8192;size=0x14f2
        else:lo=location(old,n);size=65 if n=='MbPeachAfterJump' else 81
        allowed.update(range(lo,lo+size))
    delta=[i for i,(a,b) in enumerate(zip(old['raw'],new['raw'])) if a!=b]
    assert set(delta)<=allowed
    d=dict(status='PRIVATE_SMB3PLUS_ORIGINAL_GRAVITY_CALLBACK_CONSUMER',source=True,native=False,installed=False,
        candidate=B.sha(J/'candidate.nes'),parent=parent['candidate'],joint=str(J),
        CHR_byte_exact=True,changed_own_private_labels=changes,changed_bytes=len(delta),
        correction='Original8:ACD1 calls fixed E966 immediately after the gravity ADC. That stores VY, calls30:BAC0, then returns the native wag counter before later flutter logic. All7 outer dry calls are genuine native JumpFlyFlutter again. Source31:B5ED compares the actual A left by its producer.',
        limits=['Complete controller/foreign/graphics/ISR/native qualification required.',
            'Donor terrain is not the SMB1 terrain engine; HUD low-clearance source comparisons need the real level context.',
            'Ground pound, custom stomp delay, special art and kick audio unfinished; no admission or installation.'],
        bindings={str(p):B.sha(p) for p in [Path(__file__),P/'source-stage.json',negative,body,art,J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',*logs]})
    B.write(O/'source-stage.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(candidate=d['candidate'],changed_bytes=len(delta),native=False)))


if __name__=='__main__':main()
