"""Five native resolver triples; actual earned item plus honest tier armor."""
import argparse
from hashlib import sha256
import json
import sys

import check_wwf_earned_powerup_1110 as Route

Images=Route.Images
C,W,N,L=Route.C,Route.W,Route.N,Route.L
sys.path.insert(0,str(W.R/'tools/reference'))
import sonic_sms_compact_cold_worker_1110 as Asm

PIN='6d83dea872b42cd39c14d756334a801c8f7da7dfa63ecea16d9f13835c63638d'
SOURCE=W.R/'tools/reference/wwf_native_powerup_policy_1110.s'


def proposal(raw):
    assert sha256(raw).hexdigest()==PIN
    b=W.Symbols.bundle();at=W.location(b,'WfResolveTargets');pc=W.address(b,'WfResolveTargets')
    assert (at,pc)==(792556,0xb7dc)
    defs={};names={'GuestInjuryStart':('GuestInjuryStart','GuestInjuryBank'),
        'NativePlayerStatus':('RemainingPower::EasyPower','NativeStatusBank'),
        'NativeMatureRule':('NrPickupCollision::Own','NativeMatureBank'),
        'MarioSourcePowerupCollision':('MarioSourcePowerupCollision','NativeCollectBank'),
        'GuestPowerupUpdate':('GuestPowerupUpdate','NativeTickBank')}
    for alias,(name,bank) in names.items():
        defs[alias]=W.address(b,name)+(2 if alias=='NativeMatureRule' else 0)
        defs[bank]=((W.location(b,name)-16)//8192)|128
    mature=W.location(b,'NrPickupCollision::Own')+2
    assert raw[mature:mature+14]==bytes.fromhex('b534c902b006b51f300218603860')
    status=W.location(b,'RemainingPower::EasyPower')
    assert raw[status:status+4]==bytes.fromhex('ad5b0760')
    placements={'INJURY':5,'STATUS':6,'MATURE':23,'COLLECT':24,'TICK':33}
    code=Asm.assemble('\n'.join(f'{n}=${v:04x}' for n,v in defs.items())+'\n'+SOURCE.read_text(),
        {name:(pc+3*row,3) for name,row in placements.items()})
    image=bytearray(raw);patches=[]
    for section,row in placements.items():
        offset=at+3*row;old=raw[offset:offset+3]
        assert old==bytes.fromhex('96b7e0' if row==6 else '99b7e0')
        new=code['images'][section];assert len(new)==3
        image[offset:offset+3]=new;patches.append(dict(row=row,old=old.hex(),new=new.hex(),offset=offset))
    assert sum(a!=z for a,z in zip(raw,image))<=15
    return bytes(image),dict(parent=PIN,patches=patches,source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),
        private_kernel_state_art_cookie_unchanged=True,original_motor_combat_unchanged=True,
        adaptation='Native tier armor and standard pickups; original WWF endurance/gear remain unfinished')


def damage(earned):
    m=L.clone(earned);before={n:N.get(m,n) for n in ('PlayerStatus','NumberofLives','GameEngineSubroutine','InjuryTimer')}
    assert before['PlayerStatus'] in (1,2) and before['NumberofLives']==2
    result=N.invoke(m,'ForceInjury',a=83,x=0,y=0)
    after={n:N.get(m,n) for n in ('PlayerStatus','NumberofLives','GameEngineSubroutine','InjuryTimer','GuestHurtTicks','GuestLegacyHurt','GuestPowerupActive')}
    assert after['NumberofLives']==2 and after['PlayerStatus']==0 and after['GameEngineSubroutine']!=11,(before,after,result)
    for _ in range(240):m.controller_pad=0;Route.Frames.frame(m)
    final={n:N.get(m,n) for n in ('PlayerStatus','NumberofLives','GameEngineSubroutine','InjuryTimer','GuestHurtTicks','GuestInvulTicks','GuestPowerupActive')}
    assert (final['PlayerStatus'],final['NumberofLives'],final['GameEngineSubroutine'],final['InjuryTimer'],final['GuestHurtTicks'])==(0,2,8,0,0),final
    return dict(before=before,after=after,recovered=final,
        scope='Directed actual native damage call after the naturally earned tier; no synthetic tier grant, not a natural enemy-hit claim')


def main():
    p=argparse.ArgumentParser();p.add_argument('--role',type=int,choices=range(6),default=0);p.add_argument('--all',action='store_true');a=p.parse_args()
    parent=Images.proposal(Images.Ex.proposal(Images.Route.A5.proposal(W.ROM.read_bytes())[0])[0])[0]
    image,record=proposal(parent);b=W.Symbols.bundle();b['raw']=image
    inventory=C.Starts.C.inventory(image);results=[]
    for role in (range(6) if a.all else [a.role]):
        row=next(r for r in inventory['rows'] if r['slot']==28 and r['cycle']==role)
        print(json.dumps(dict(event='WWF_role_start',name=row['name'],role=role)),flush=True)
        opening,m=C.cold(b,row);q,earned=Route.route(m,return_arena=True,quiet=a.all)
        assert q['passed'] and q['calls']['GuestPowerupUpdate']==60,q
        collected=next(e for e in q['events'] if e['event']=='native_collection_return')
        assert collected['erased'] and collected['floaty']==6 and collected['sound']==32 and collected['carry'],collected
        injury=damage(earned)
        # Explicit directed fixtures after the genuine earned mushroom.
        # These are not natural flower/Star/1UP acquisition claims.
        typed=[C.collect(earned,kind) for kind in (1,2,3)]
        flower,star,life=typed
        assert not flower['issues'] and flower['resumed']['PlayerStatus']==2
        assert star['collected']['StarInvincibleTimer']==35 and life['collected']['floaty']==11
        result=dict(passed=True,name=row['name'],role=role,genuine_cold=opening,natural=q,
            directed_earned_tier_damage=injury,directed_remaining_types=[dict(kind=t['kind'],
                status=t['resumed']['PlayerStatus'],active=t['resumed']['GuestPowerupActive'],
                star=t['collected']['StarInvincibleTimer'],floaty=t['collected']['floaty']) for t in typed])
        results.append(result)
        print(json.dumps(dict(event='WWF_role_pass',result=result if not a.all else
            dict(name=row['name'],role=role,collection=collected,final=q['final'],Guest_ticks=q['calls']['GuestPowerupUpdate'],
                native_armor_damage=injury,directed_remaining_types=result['directed_remaining_types']))),flush=True)
    print(json.dumps(dict(passed=True,parent_ROM_SHA256=PIN,proposal_ROM_SHA256=sha256(image).hexdigest(),
        source_CPU_only=True,Mesen_run=False,ROM_written=False,output_files=0,roles=len(results),
        names=[r['name'] for r in results],record=record,
        scope='Naturally earned first mushroom/60ticks/resume and actual native damage applied afterward; other item kinds are explicitly directed callback fixtures. Original WWF endurance/gear, natural flower/Star/1UP and fullstage remain open.')),flush=True)


if __name__=='__main__':main()
