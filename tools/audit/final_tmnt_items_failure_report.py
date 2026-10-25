"""Preserve and explain turtle fixture failures without rewriting receipts."""
from pathlib import Path
import argparse
import hashlib
import json
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load

ROM='52918588bab0eec3f3a1f857bf084d2d799e88a5c781c75233c098ccc5f54f3f'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    b=scoped_load(a.root/'preparation529-v1/frozen-current/candidate.nes')
    q=Arena(b,19);q.set('TnSeq',0x80);q.set('RgCrouch',0)
    c,_=q.invoke('TnHeadTop');assert c.a==0xf8
    head=dict(cpu_return=c.a,signed_top_offset=-8,player_y=176,actual_top=168,
              failed_block=dict(top=160,bottom_exclusive=176,overlaps_standing_head=True),
              corrected_block=dict(top=144,bottom_exclusive=160,overlaps_standing_head=False))
    rows=[]
    explanations={
        1:'Lower block initially overlaps native standing head; side resolution moves X112 to127 before real jump, so jump misses. Later ordinary timer death is downstream of missed-block waiting. Fixture geometry/timer policy corrected; no game patch.',
        2:'Capitalized boolean identifiers serialize to nil: actual mode isEasy, injury-after-rise flag disabled. Kiai correctly grants at128HP; expected112 is invalid fixture expectation. Local literals/numeric readback corrected.',
        3:'New contact introduced when native TnHurt expires but InjuryTimer still2. Source contact latches enemy collision bit then correctly skips injury; continuous overlap retains latch after timer0. Wait both actual protection timers before a new staged enemy.',
        4:'Diagnostic repetition of v3; same inputs/assertions plus exact live body/branch snapshots. Confirms source protection/latch behavior; not a game defect.'}
    for version in range(1,5):
        d=a.root/f'leonardo-hard-native-v{version}';z=json.loads((d/'proof.json').read_text())
        assert not z['passed'] and z['ROM_sha256']==ROM
        rows.append(dict(version=version,folder=str(d),classification='fixture_error_not_game_defect',
                         explanation=explanations[version],failure=z['first_failure'],
                         files={name:sha(d/name)for name in ['proof.json','first-failure.json','first-failure.argb','events.jsonl','updates.csv','run.lua','config.json']}))
    d=a.root/'leonardo-hard-native-v4'
    events=[json.loads(s)for s in (d/'events.jsonl').read_text().splitlines()]
    traces=[e for e in events if e['kind']=='repeated-contact-diagnostic']
    first=traces[0];at_injury=next(e for e in traces if e['data']['hook']=='InjurePlayer')
    assert first['data']['TnHurt']==0 and first['data']['InjuryTimer']==2
    assert first['data']['Enemy_CollisionBits']==0 and at_injury['data']['Enemy_CollisionBits']==1
    assert first['data']['playerBox']==[115,168,125,200]and first['data']['enemyBox']==[119,198,129,204]
    assert first['data']['CrossoverBehaviorVersion']==1 and first['data']['CheatInvincible']==0
    counts={name:sum(e['data']['hook']==name for e in traces)for name in sorted(set(e['data']['hook']for e in traces))}
    assert counts['InjurePlayer']==1 and 'ForceInjury'not in counts and 'TnInjuryStatus'not in counts
    pos=location(b,'HandlePECollisions');at=address(b,'Enemy_CollisionBits')
    stores=[dict(pc=address(b,'HandlePECollisions')+i,bank=(pos-16)//8192,bytes=list(b['raw'][pos+i:pos+i+3]))for i in range(64)if b['raw'][pos+i:pos+i+3]==bytes([0x9d,at&255,at>>8])]
    assert len(stores)==1
    z=dict(audit_passed=True,goal_complete=False,ROM_sha256=ROM,game_defects_proved=[],
           native_fixture_failures=rows,head_control=head,
           repeated_contact=dict(first_body_contact=first,protected_injury_entry=at_injury,
               hook_counts=counts,correct_native_collision_latch_store=stores[0],
               explanation='Actual overlapping boxes; native InjuryTimer2 at new contact. Correct latch/skip, no first wrong gameplay write. New fixture waits TnHurt0 AND InjuryTimer0 and does not clear timers/latches by injection.'),
           script_sha256=sha(Path(__file__)),scope='Read-only failure ledger plus one actual-ROM direct CPU head-offset control. Old failures unchanged; no game fix or passing new native case inferred.')
    f=a.output/'proof.json';f.write_text(json.dumps(z,indent=2)+'\n')
    print(json.dumps(dict(audit_passed=True,failures=4,game_defects_proved=0,proof=str(f),sha256=sha(f))))


if __name__=='__main__':main()
