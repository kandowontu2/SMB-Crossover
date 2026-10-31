"""Join actual fresh-A and leaf-frame consumers; move only own private clear."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

P=R/'build/smb3plus-peach-air-frame-1031-v2'
O=R/'build/smb3plus-peach-complete-controller-1031-v1';J=O/'joint'
S=R/'tools/reference/smb3plus_peach_complete_controller_1031_v1.s'


def once(t,a,b):
    assert t.count(a)==1,(a,t.count(a))
    return t.replace(a,b)


def main():
    assert not O.exists()
    stage=P/'source-stage.json';parent=json.loads(B.read(stage));B.bound(parent)
    negative=R/'build/smb3plus-whole-controller-probe-1031-v2/probe.json'
    assert not json.loads(B.read(negative))['passed']
    old=scoped_load(P/'joint/candidate.nes');shutil.copytree(P/'joint',J)
    def rt(t):return t.replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix())
    for p in J.rglob('*'):
        if p.is_file() and p.suffix in ['.s','.inc','.cfg']:B.write(p,rt(B.read(p)))
    parts={m[1]:m[0]+'\n' for m in re.finditer(r'\.proc (\w+)\n.*?\.endproc',B.read(S),re.S)}
    controller=J/'src/smb3_native_controller.inc';text=B.read(controller)
    text=once(text,' JSR ::MbPeachJumpRoot\n sec',' LDA Player_RootJumpVel\n sec')
    text=once(text,' jeq PRG008_AC9E\n LDA Player_AllowAirJump\n jne PRG008_AC41',
        ' jeq PRG008_AC9E\n JSR ::MbPeachJumpRoot\n jne PRG008_AC41')
    text=once(text,' LDA Player_TailWagFlyFrames,Y\n STA Player_Frame',
        ' JSR ::MbPeachLeafFrame\n STA Player_Frame')
    B.write(controller,text)
    art=J/'src/smb3_mario_art.inc';text=B.read(art)
    for name in ['MbPeachJumpRoot','MbPeachAfterJump']:
        m=re.search(r'\.proc '+name+r'\n.*?\.endproc\n',text,re.S);assert m
        text=text[:m.start()]+parts[name]+text[m.end():]
    m=re.search(r'\.proc MbPeachFloatClear\n.*?\.endproc\n',text,re.S);assert m
    clear=m[0];text=text[:m.start()]+parts['MbPeachLeafFrame']+text[m.end():]
    text=once(text,' .res 81-(*-M3Form6ChrHi),2\n',clear+' .res 81-(*-M3Form6ChrHi),2\n')
    B.write(art,text)
    data=J/'smb3plus_float_data.s'
    B.write(data,once(B.read(data),'MbFloatDataEnd:\n',parts['MbPeachAfterOverride']+'MbFloatDataEnd:\n'))
    menu=J/'smb3plus_menu_name.s'
    B.write(menu,once(B.read(menu),'.assert *<=$b100,lderror',parts['MbPeachLeafOverride']+'.assert *<=$b100,lderror'))
    recipes=[]
    for label in ['main-build','union-build','chr-build','final-link']:
        cmd=[rt(s) for s in json.loads(B.read(P/(label+'.json')))['command']]
        validate(cmd,J,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        B.write(O/(label+'.json'),json.dumps(dict(command=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr),indent=2)+'\n')
        assert p.returncode==0,(label,p.stderr);recipes.append(O/(label+'.json'))
    from prepare_cv3_dmc_mirror import prepare
    prepare(R,J/'candidate.nes');new=scoped_load(J/'candidate.nes')
    changed=[]
    for name,sym in old['syms'].items():
        if sym.get('type')=='lab' and address(old,name)!=address(new,name):
            assert 'exp' not in sym and (name.startswith(('MbPeachJumpRoot::','MbPeachAfterJump::','MbPeachFloatClear')) or name=='MbFloatDataEnd'),name
            changed.append(dict(name=name,old=address(old,name),new=address(new,name)))
    assert old['raw'][:16]==new['raw'][:16]
    assert old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
    sizes={n:int(new['syms'][n]['size']) for n in parts}
    assert sizes['MbPeachAfterJump']+15<=81
    assert sizes['MbPeachJumpRoot']<=43 and sizes['MbPeachLeafFrame']<=24
    assert address(new,'MbFloatDataEnd')<=0xd400
    assert address(new,'MbPeachLeafOverride')+sizes['MbPeachLeafOverride']<=0xb100
    d=dict(status='PRIVATE_SMB3PLUS_COMPLETE_CONTROLLER_CONSUMERS',source=True,native=False,installed=False,
        candidate=B.sha(J/'candidate.nes'),parent=parent['candidate'],joint=str(J),CHR_byte_exact=True,
        helpers=sizes,changed_own_private_labels=changed,foreign_callable_labels_preserved=True,
        corrections=['Fresh-A float hook runs before native air-jump permission, as donor32:A003.',
            'Donor30:BB50 consults anchor for forms4..6.',
            'Donor32:AF80 leaf/tanooki hover pose uses original power and prior-frame tests.'],
        storage='Move15B own Clear from form5low reserve into form6high reserve. The21B leaf farcall wrapper replaces its old slot. Pure47B A81 leaf override uses only the pre-reviewed free name tail before Rogue B100. No new RAM/global/CHR.',
        limits=['Whole-controller/foreign ABI/ISR/native checks required. Ground pound, custom stomp delay, special art and kick audio still unfinished. No admission/installation.'],
        bindings={str(p):B.sha(p) for p in [Path(__file__),S,stage,negative,controller,art,data,menu,J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',*recipes]})
    B.write(O/'source-stage.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(candidate=d['candidate'],helpers=sizes,native=False)))


if __name__=='__main__':main()
