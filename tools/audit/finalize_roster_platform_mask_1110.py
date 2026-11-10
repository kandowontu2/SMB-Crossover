"""Freeze disjoint d133-to5f helper rows; no native ROM is emitted."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import check_manual_roster_bridge_mask_1110 as M

I,P,R=M.I,M.P,M.R
OUT=I.OUT
BASE=R/'build/remaining-roster-native-1110/candidate.nes'
BASE_PIN='d1333adf3d9e62354ccfab9c21490f95bc972200c513183a309d90eed09728d8'
FINAL_PIN='5f072bfdacdf4fc2e5bf81d1a46eb5b3720fecbc8d6b9b4e94766babfad01b70'
SHA=lambda p:sha256(Path(p).read_bytes()).hexdigest()
RECEIPTS=('leaf-proof.json','ff-foot-proof.json','ff-foot-qualification.json',
    'carry-29.json','paired-irq-V.json','paired-irq-H.json',
    'carry-irq-22-0.json','carry-irq-29-0.json',
    'isr-family-commit.json','bridge-mask-proof.json','bridge-mask-irq.json')


def main():
    bindings={};proofs={}
    def bind(path,digest=None):
        key=path.relative_to(R).as_posix();actual=SHA(path)
        assert digest is None or actual==digest,(key,digest,actual)
        assert key not in bindings or bindings[key]==actual,key
        bindings[key]=actual
    for name in RECEIPTS:
        path=OUT/name;q=json.loads(path.read_text());assert q['passed'],name
        for key,digest in q.get('bindings',{}).items():bind(R/key,digest)
        bind(path);proofs[name]=q
    bind(Path(__file__));bind(BASE)
    base=BASE.read_bytes();assert I.SHA(base)==BASE_PIN
    foot=proofs['ff-foot-proof.json'];mask=proofs['bridge-mask-proof.json']
    assert foot['expected_memory_only_SHA256']==mask['parent_SHA256']
    intermediate=P.install(base,foot['patches'])
    assert I.SHA(intermediate)==mask['current_roster_parent_SHA256']==M.CURRENT_PIN
    sequential=P.install(intermediate,mask['patches'])
    assert I.SHA(sequential)==mask['current_roster_mask_SHA256']==FINAL_PIN
    rows=deepcopy(foot['patches']);folded=0
    for patch in mask['patches']:
        at=patch['file_offset'];old=bytes.fromhex(patch['old_hex']);new=bytes.fromhex(patch['new_hex'])
        assert len(old)==len(new)==3
        matches=[row for row in rows if row['file_offset']<=at
            and at+len(old)<=row['file_offset']+len(bytes.fromhex(row['new_hex']))]
        assert len(matches)==1
        row=matches[0];relative=at-row['file_offset'];data=bytearray.fromhex(row['new_hex'])
        assert row['file_offset']==P.at(126,0x837b) and len(data)==31
        assert data[relative:relative+len(old)]==old
        data[relative:relative+len(old)]=new;row['new_hex']=data.hex()
        row['role']='Same31B source bridge: HpCount>0 always enters; AND12/BEQ excludesMini41 and admits22/29/34'
        folded+=1
    assert folded==1
    rows.sort(key=lambda row:row['file_offset']);end=0
    for row in rows:
        at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex'])
        assert at>=end and len(old)==len(new)>0
        assert base[at:at+len(old)]==old
        end=at+len(old)
    final=P.install(base,rows)
    assert final==sequential and I.SHA(final)==FINAL_PIN
    assert len(rows)==8 and len(final)==len(base)
    identities=[[o,v] for o,count in ((22,4),(29,6)) for v in range(count)]
    for axis,name in ((0x28,'paired-irq-V.json'),(0x24,'paired-irq-H.json')):
        q=proofs[name]
        assert q['axis']==axis and q['identities']==identities
        assert q['expected_memory_only_SHA256']==foot['expected_memory_only_SHA256']
        assert q['exact_complete_ISR_state_and_hardware']
        assert all(q['vectors']['counts'][kind]>0 for kind in ('lag_FF','IRQ','nested_IRQ'))
    assert proofs['bridge-mask-irq.json']['expected_memory_only_SHA256']==FINAL_PIN
    for owner in (0,5,41):
        assert mask['baseline74fde'][str(owner)]['native_CPU_overhead']=={'0':44}
    common=dict(stage='Any active gameplay stage at the current player position; qualified fixture1-1',
        width=32,initial_top='native playerY+32',
        vertical=dict(left='max(0,playerWorldX-8)',center='left+16'),
        horizontal=dict(left='playerWorldX+24',center='playerWorldX+40',
            first_direction='right',stroke=112,repeat='right112,left112,repeat'))
    characters=[dict(owner=o,variant=v,name=name) for o,names in
        ((22,('Fighter','White Mage','Black Mage','Thief')),
         (29,('Hulk Hogan','Ted DiBiase','Bam Bam Bigelow','Honky Tonk Man','Randy Savage','Andre the Giant')))
        for v,name in enumerate(names)]
    result=dict(passed=True,source_ready=True,source_CPU_only=True,Mesen_run=False,ROM_written=False,
        interrupt_pending=False,native_pending=True,native_ingress_pending=False,
        parent_SHA256=BASE_PIN,expected_memory_only_SHA256=FINAL_PIN,
        original_source_parent_SHA256=I.PIN,
        reconstructed_intermediate_SHA256=M.CURRENT_PIN,
        strict_nonoverlapping_rows=True,mask_folded_into31B_bridge=True,
        patches=rows,labels=foot['labels'],layout=foot['layout'],
        input_controls=dict(vertical='Up+Select',horizontal='Down+Select',
            physical_players=[1,2],independent_axes=True,fresh_chord_replaces_matching_axis=True,held_no_repeat=True),
        characters=characters,geometry=common,
        source_qualification=dict(
            input_and_actual_births='All10variants and both physical controllers, fresh edges/held/replacements; actual20updateGameCore births for all10.',
            complete_foreground='44actualGameCoreupdates with exactpublicstate/AXYP for raw0..37/41/42 on27d→5f; exact74fde cycles for0/5/41. Isolated predicateallraw0..44 exact4bankRAM/actors/player, with observed ABI flags recorded.',
            foreign_scope='Prince38/DKJr40 and the remaining omitted cold-owner identities do not have fabricated startup scenes or a wholeGameCore parity claim here. Prince38 remains admitted; DKJr40 joins the fast rejected path whenHpCount0 (HpCount>0 still enters). All45isolated predicate4bankRAM/actors/player equality is proven; long native startup and final composition regression belong to root native receipts.',
            native_pending='Root must qualify the final combined ROM; preceding27d all10nativehelper results and any5f tests are not asserted as this final manifest native approval.',
            interrupt='Frozen70all10V/H birth +actualFF/WWFcarry pairedbaselineIRQ closure; only changed3B bridge has separate genuineIdleLoop/GameLoop/Core paired d133 IRQ cuts, fullresumes. Immediate legitimate audio/familycommit effects are source-typed and exactly baseline-matched; final native/mapper/helper state remains exact.'),
        source_receipts={name:dict(path=(OUT/name).relative_to(R).as_posix(),SHA256=SHA(OUT/name)) for name in RECEIPTS},
        bindings=dict(sorted(bindings.items())))
    target=OUT/'final-qualified-proof.json'
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(source_READY=True,proof=target.relative_to(R).as_posix(),
        proof_SHA256=SHA(target),expected_memory_only_SHA256=FINAL_PIN,
        nonoverlap_rows=len(rows),interrupt_pending=False,native_pending=True,ROM_written=False)))


if __name__=='__main__':main()
