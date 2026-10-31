"""Classify loader aliases of private labels after the successful v4 link.

V4's final observer treated unqualified aliases Navigation/M3NoToggle as
public entries. Their scope/export metadata proves they are the same two
private branch labels. Check every other label and every changed ROM byte.
"""
from pathlib import Path
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from check_tmnt_render_oa import load,address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load

O=R/'build/smb3plus-menu-host-1031-v4';J=O/'joint'
H=R/'build/smb3plus-peach-float-host-1031-v4/handoff.json'


def main():
    assert not (O/'source-stage.json').exists()
    h=json.loads(B.read(H));B.bound(h);parent=Path(h['joint'])
    old,new=[scoped_load(p/'candidate.nes') for p in [parent,J]]
    logs=[O/(name+'.json') for name in ['main-build','union-build','chr-build','final-link']]
    for p in logs:assert json.loads(B.read(p))['returncode']==0,p
    changed=[]
    allowed={'Navigation','M3NoToggle','CrossoverMenuInput::Navigation','CrossoverMenuInput::M3NoToggle',
        'M3StatusNameDispatch::Names','M3StatusNameDispatch::Loop','M3StatusNameDispatch::Done'}
    for name,sym in old['syms'].items():
        if sym.get('type')!='lab':continue
        if address(old,name)!=address(new,name):
            assert name in allowed and 'exp' not in sym,name
            changed.append(dict(name=name,old=address(old,name),new=address(new,name)))
    assert {q['name'] for q in changed}==allowed
    for name in ['Navigation','M3NoToggle']:
        assert old['syms'][name]['scope']==old['syms']['CrossoverMenuInput::'+name]['scope']
        assert address(old,name)==address(old,'CrossoverMenuInput::'+name)
        assert address(new,name)==address(new,'CrossoverMenuInput::'+name)
    # These are the only source-owned envelopes that may change.
    envelopes=[('Select branch/padding',location(old,'CrossoverMenuInput::CdNoToggle'),
        address(old,'CrossoverMenuInput::GbPitNavContinue')-address(old,'CrossoverMenuInput::CdNoToggle')),
        ('Names route',location(old,'NrQueueSelectName::M3OtherName')-9,9),
        ('Exact prior status span',location(old,'M3StatusNameDispatch'),82),
        ('Four status offsets in prior palette padding',location(new,'MbStatusNameOffsets'),4),
        ('A81 name helper in former gap',location(new,'MbMenuNameSelect'),int(new['syms']['MbMenuNameSelect']['size']))]
    permitted={i for _,at,n in envelopes for i in range(at,at+n)}
    differences=[i for i,(a,b) in enumerate(zip(old['raw'],new['raw'])) if a!=b]
    assert len(old['raw'])==len(new['raw']) and set(differences)<=permitted
    helper=envelopes[-1];assert helper[1]==16+81*8192+0x105b and helper[2]<=165
    assert old['raw'][helper[1]:helper[1]+165]==bytes([255])*165
    assert address(old,'M3StatusNameDispatch')==address(new,'M3StatusNameDispatch')
    assert int(new['syms']['M3StatusNameDispatch']['size'])==82
    assert old['raw'][:16]==new['raw'][:16]
    assert old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
    paths=[Path(__file__),H,*logs]
    paths += [R/'tools/audit'/f'prepare_smb3plus_menu_host_1031_v{i}.py' for i in range(1,5)]
    paths += [J/p for p in ['entrypoint.s','private.cfg','smb3plus_menu_name.s','src/character_select.s',
        'src/new_roster_dispatch.s','src/smb3_mario_dispatch.s','src/smb3_mario_render.s',
        'candidate.nes','candidate.dbg','candidate.lbl']]
    d=dict(status='PRIVATE_FOUR_SMB3_MENU_SOURCE_NOT_ADMITTED',source=True,native=False,
        installed=False,publication_allowed=False,parent=h['candidate'],candidate=B.sha(J/'candidate.nes'),
        joint=str(J),changed_private_label_aliases=changed,all_other_existing_label_PCs_exact=True,
        CHR_byte_exact=True,ROM_changed_bytes=len(differences),source_owned_envelopes=envelopes,
        Select_cycle=[0,1,2,3],status_names=['MARIO3 ','LUIGI3 ',' TOAD3 ',' PEACH3'],
        helper_bytes=helper[2],helper_available_bytes=165,
        retained_negatives=['V1 unresolved farcall RES expression; exact final link assertion replaces it.',
            'V2 appended names overlapped occupied Celeste code. No such append is in this cart.',
            'V3 hit assembler segment limit. V4 appends its helper to the existing A81 segment.',
            'V4 observer rejected two non-exported private-label aliases; this qualifier checks their actual scopes and every other existing label/changed byte.'],
        limits=['Private64-parent candidate; Bowser66 successor composition is still required.',
            'Actual menu, status ABI, interrupt and native host tests remain; no playable admission or installed change.',
            'Donor ground-pound, custom stomp delay, special art and kick sound remain unfinished.'],
        bindings={str(p):B.sha(p) for p in paths})
    B.write(O/'source-stage.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(candidate=d['candidate'],changed_bytes=len(differences),
        helper_bytes=helper[2],all_other_labels_exact=True,native=False)))


if __name__=='__main__':main()
