"""Qualify private debug aliases after the successful v3 source/cart link."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

P=R/'build/smb3plus-peach-air-frame-1031-v2'
O=R/'build/smb3plus-peach-complete-controller-1031-v3';J=O/'joint'


def main():
    assert not (O/'source-stage.json').exists()
    parent=json.loads(B.read(P/'source-stage.json'));B.bound(parent)
    old,new=[scoped_load(p/'candidate.nes') for p in [P/'joint',J]]
    expected={'MbFloatDataEnd','Sink','Override','Maintain','MbPeachFloatClear','Root',
        'MbPeachAfterJump::Sink','MbPeachAfterJump::Override','MbPeachAfterJump::Maintain',
        'MbPeachAfterJump::Done','MbPeachJumpRoot::Store','MbPeachJumpRoot::Root'}
    changed=[]
    for name,sym in old['syms'].items():
        if sym.get('type')!='lab':continue
        if name not in new['syms'] or address(old,name)!=address(new,name):
            assert name in expected and 'exp' not in sym,name
            changed.append(dict(name=name,old=address(old,name),new=address(new,name) if name in new['syms'] else None))
    assert {r['name'] for r in changed}==expected
    for alias,scope in [('Sink','MbPeachAfterJump::Sink'),('Override','MbPeachAfterJump::Override'),
        ('Maintain','MbPeachAfterJump::Maintain'),('Root','MbPeachJumpRoot::Root')]:
        assert old['syms'][alias]['scope']==old['syms'][scope]['scope']
        assert address(old,alias)==address(old,scope)
    code_at=location(old,'M3Native::Player_JumpFlyFlutter')
    permission_load=bytes([0xad])+address(old,'M3Native::Player_AllowAirJump').to_bytes(2,'little')
    prefix=old['raw'][code_at:location(old,'M3Native::PRG008_AC41')]
    assert prefix.count(permission_load)==2 and prefix.startswith(permission_load)
    at=code_at+prefix.rindex(permission_load)
    code_end=location(old,'M3Native::PRG008_AD1A')
    needle=bytes([0x20])+address(old,'MbPeachJumpRoot').to_bytes(2,'little')
    assert old['raw'][code_at:code_end].count(needle)==1
    jump_at=old['raw'].index(needle,code_at,code_end)
    leaf_at=location(old,'M3Native::PRG008_B082')-6
    assert old['raw'][leaf_at:leaf_at+3]==bytes([0xb9])+address(old,'M3Native::Player_TailWagFlyFrames').to_bytes(2,'little')
    envelopes=[dict(name='freshA permission load',at=at,size=3),dict(name='root velocity restored',at=jump_at,size=3),
        dict(name='leaf frame table load',at=leaf_at,size=3)]
    for name in ['M3Form1ChrHi','M3Form5ChrLo','M3Form6ChrHi']:
        envelopes.append(dict(name=name,at=location(old,name),size=81))
    for name in ['MbPeachAfterOverride','MbPeachLeafOverride']:
        pos=location(new,name);n=int(new['syms'][name]['size'])
        assert old['raw'][pos:pos+n]==bytes([255])*n
        envelopes.append(dict(name=name,at=pos,size=n))
    allowed={i for e in envelopes for i in range(e['at'],e['at']+e['size'])}
    delta=[i for i,(a,b) in enumerate(zip(old['raw'],new['raw'])) if a!=b]
    assert len(old['raw'])==len(new['raw']) and set(delta)<=allowed
    assert old['raw'][:16]==new['raw'][:16]
    assert old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
    logs=[O/(n+'.json') for n in ['main-build','union-build','chr-build','final-link']]
    assert all(json.loads(B.read(p))['returncode']==0 for p in logs)
    files=[Path(__file__),P/'source-stage.json',*logs]
    files += [R/'tools/audit'/f'prepare_smb3plus_peach_complete_controller_1031_v{i}.py' for i in [1,2,3]]
    files += [R/'tools/reference'/f'smb3plus_peach_complete_controller_1031_v{i}.s' for i in [1,2]]
    files += [J/p for p in ['src/smb3_native_controller.inc','src/smb3_mario_art.inc','smb3plus_float_data.s','smb3plus_menu_name.s','entrypoint.s','candidate.nes','candidate.dbg','candidate.lbl']]
    d=dict(status='PRIVATE_SMB3PLUS_FRESH_A_AND_HOVER_POSE_CONSUMERS',source=True,native=False,installed=False,
        parent=parent['candidate'],candidate=B.sha(J/'candidate.nes'),joint=str(J),
        changed_own_private_labels=changed,source_owned_ROM_envelopes=envelopes,changed_bytes=len(delta),
        all_other_existing_callable_labels_preserved=True,CHR_byte_exact=True,
        corrections=['Fresh-A state producer occurs before native air-jump permission.',
            'Higher forms consult original Anchor before producing Ready2.',
            'Leaf/tanooki pose uses original32:AF80..AFA4.'],
        helpers={n:int(new['syms'][n]['size']) for n in ['MbPeachJumpRoot','MbPeachAfterJump','MbPeachFloatClear','MbPeachLeafFrame','MbPeachAfterOverride','MbPeachLeafOverride','MbPeachSinkOverride']},
        retained_negatives='V1/V2 compile overflow preserved. V3 linked successfully; its observer rejected the intentionally removed private Sink alias. This independent qualifier checks actual scope/export metadata, every other label, all changed bytes and all four real build recipes.',
        limits=['Whole-controller, foreign ABI, interrupt, graphics and native checks still required.',
            'Ground pound, custom stomp delay, special art and kick audio unfinished; no admission or installation.'],
        bindings={str(p):B.sha(p) for p in files})
    B.write(O/'source-stage.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(candidate=d['candidate'],helpers=d['helpers'],changed_bytes=len(delta),native=False)))


if __name__=='__main__':main()
