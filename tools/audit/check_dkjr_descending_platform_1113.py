"""Zero-output qualification of the strict descending-only native successor."""
import argparse
from hashlib import sha256
from itertools import product
import json
import re
from unittest.mock import patch

import compose_dkjr_descending_platform_1113 as T
import check_dkjr_platform_contact_1113 as Q

P,H,N,W,L,C=Q.P,Q.H,Q.N,Q.W,Q.L,Q.C


def caller_domain(parent):
    b=W.Symbols.bundle();b['raw']=parent
    text=(P.B.R/'src/object.s').read_text()
    body=text.split('RunEnemyObjectsBody:\n',1)[1].split('MiscObjectsCore:',1)[0]
    names=re.findall(r'^\s*\.word\s+(\w+)',body,re.M)
    table=b''.join(W.address(b,name).to_bytes(2,'little')for name in names)
    bank=parent[16:8208];at=bank.find(table)
    assert at>=0 and bank.find(table,at+1)<0
    indices=[i for i,name in enumerate(names)if name=='RunLargePlatform']
    assert indices==list(range(16,23)),indices
    assert bank[at-3:at]==bytes((0x20,))+W.address(b,'JumpEngine').to_bytes(2,'little')
    assert body.count('sbc #$14')==1 and body.count('cpy #$15')==1
    # All source references are the seven dispatch words and definition.
    references=[]
    for path in(P.B.R/'src').glob('*.s'):
        for line in path.read_text().splitlines():
            if re.search(r'\bRunLargePlatform\b',line.split(';',1)[0]):references.append(line.strip())
    assert references.count('.word RunLargePlatform')==7
    assert len(references)==8 and references.count('RunLargePlatform:')==1,references
    target=W.address(b,'RunLargePlatform')
    direct=[]
    for i in range(8190):
        if bank[i]in(0x20,0x4c)and bank[i+1:i+3]==target.to_bytes(2,'little'):
            direct.append((0xa000+i,bank[i]))
    assert not direct,direct
    return dict(actual_native_table_PC=0xa000+at,table_entries=len(names),
        actual_RunLargePlatform_ID_domain=list(range(0x24,0x2b)),sole_source_table_entries=7,
        other_same_bank_direct_callers=direct,
        scope='Actual native indexed actor dispatch. Direct out-of-domain fixture calls are outside this private API contract; no runtime upper-bound byte is claimed.')


def components(seed,candidate):
    compiled=Q.mounted(seed,candidate);steps=0
    def contact(m,delta,_sample):
        # Explicit actor motion input belongs to this component fixture.
        # Real native motion and controls are exercised by the route separately.
        C.field(m,'Enemy_Y_Speed',255 if delta<0 else delta)
        return Q.compiled_contact(m,delta,None)
    with patch.object(C,'native_contact',contact):
        for C.SLOT,deltas in product(range(6),((1,)*8,(0,)*8,(2,)*8,(1,2,0,1,0,2,1,2))):
            _,row=C.trajectory(compiled,True,deltas)
            assert len(row['steps'])==8
            for step in row['steps']:
                v=step['after_native']
                assert step['contact']==dict(passenger=C.SLOT,native_position_calls=1),(C.SLOT,deltas,step)
                assert(v['source'],v['prior'],v['fallStart'],v['fallLimit'])==(1,1,0,22)
                assert(v['nativeY'],v['sourceY'])==(v['top']-32,v['top']-17)
                steps+=1
        negatives=[]
        for C.SLOT in range(6):negatives+=C.negatives(compiled)
    clipping=0
    for C.SLOT,footer,speed in product(range(6),range(256),(0,1,255)):
        m=C.setup(compiled);m[0x65b]=footer;C.field(m,'Enemy_Y_Speed',speed)
        Q.compiled_contact(m,0,None)
        assert m[0x65b]==footer
        clipping+=1
    gate=0;C.SLOT=3;base=C.setup(compiled)
    for footer,speed in product((136,254),range(256)):
        m=L.clone(base);m[0x65b]=footer;C.field(m,'Enemy_Y_Speed',speed)
        top=footer+2 if footer<254 else 255;C.field(m,'Enemy_Y_Position',top)
        seen=[]
        def watch(cpu):
            if cpu.pc==0xb453 and cpu.memory.rawtags[1]==128:seen.append(cpu.memory[0x65b])
        Q.direct(m,T.ENTRY,x=C.SLOT,observe=watch)
        assert seen==[footer+2 if speed<128 and footer<254 else footer],(footer,speed,seen)
        assert m[0x65b]==footer
        gate+=1
    return dict(compiled_downward_stationary_contact_updates=steps,
        compiled_jump_gap_highfall_negatives=len(negatives),all_footer_speed_slot_restorations=clipping,
        all256_native_speed_sign_and_overflow_gate_cases=gate,
        overflow_guard_retained=True,source_motor_body_and_helpers_unchanged=True)


def native_ids(seed,parent,candidate):
    cases=0;added=0;preserved=0;ascending=0;box_rows=set()
    for slot,kind,state,gap,side,player_dy,speed in product((0,3,5),range(37,43),(0,1,64,128,255),
            (-32,-29,-27,-24,-10,-6,-5,-1,0,1,2,3,8),(-20,0,20),(0,255),(0,1,255)):
        C.SLOT=slot;base=C.setup(seed);N.put(base,ObjectOffset=slot,Player_Y_Speed=player_dy)
        footer=base[0x65b];top=footer+gap
        C.field(base,'Enemy_ID',kind);C.field(base,'Enemy_State',state)
        C.field(base,'Enemy_Y_Position',top);C.field(base,'Enemy_Y_Speed',speed)
        C.field(base,'Enemy_X_Position',(944+side)&255)
        N.invoke(base,'GetEnemyOffscreenBits',x=slot);N.invoke(base,'RelativeEnemyPosition',x=slot)
        N.invoke(base,'LargePlatformBoundBox',x=slot)
        bbox=tuple(base[0x65c+4*slot:0x660+4*slot]);box_rows.add((kind,state,top,bbox[1]))
        if bbox[1]!=255:assert bbox[1]==top
        outcomes=[]
        for raw in(parent,candidate):
            m=Q.mounted(base,raw);m[0x16a]=85;r=Q.direct(m,Q.entry(raw),x=slot)
            assert m[0x65b]==footer
            outcomes.append((N.get(m,'PlatformCollisionFlag',slot),bytes(m[0x200:0x800]),
                tuple(bytes(q)for q in m.ram),tuple(m.rawtags),r['X'],r['Y'],r['SP']))
        old,new=outcomes
        if speed==255:
            assert new==old,('ascending original semantics',slot,kind,state,gap,side,player_dy)
            ascending+=1
        if old[0]==new[0]:
            assert new==old,(slot,kind,state,gap,side,player_dy,speed,'unchanged contact path')
            preserved+=int(old[0]<128)
        else:
            assert(old[0],new[0])==(255,slot)
            assert gap in(1,2)and player_dy==0 and state<128 and speed<128
            added+=1
        cases+=1
    balance=Q.balance_pairs(seed,parent,candidate)
    return dict(native_actor_state_head_side_player_speed_platform_speed_cases=cases,
        original_ascending_cases=ascending,existing_contacts_preserved=preserved,
        added_only_1_or2_pixel_nonnegative_speed_contacts=added,
        actual_bbox_top_versus_EnemyY_cases=len(box_rows),paired_ID24_original_behavior_cases=balance)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in('structure','incoming','components','native-ids','foreign','cost','first','full'):
        ap.add_argument('--'+name,action='store_true')
    a=ap.parse_args();Q.T=T
    parent=T.load_parent()
    candidate,info=T.transform(parent);assert T.reverse(candidate)==parent
    if a.structure:print('DKJR_DESCENDING_STRUCTURE '+json.dumps(dict(info,caller=caller_domain(parent)),separators=(',',':')),flush=True)
    _,seed=H.cold(parent,parent[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    for name,enabled,fn in(
        ('INCOMING',a.incoming,lambda:Q.incoming(seed)),
        ('COMPONENTS',a.components,lambda:components(seed,candidate)),
        ('NATIVE_IDS',a.native_ids,lambda:native_ids(seed,parent,candidate)),
        ('FOREIGN',a.foreign,lambda:Q.foreign(parent,candidate)),
        ('COST',a.cost,lambda:dict(rows=Q.cost(seed,parent,candidate))),
        ('FIRST',a.first,lambda:Q.route(seed,candidate)),
        ('FULL',a.full,lambda:Q.route(seed,candidate,full=True))):
        if enabled:print('DKJR_DESCENDING_'+name+' '+json.dumps(fn(),separators=(',',':')),flush=True)


if __name__=='__main__':main()
