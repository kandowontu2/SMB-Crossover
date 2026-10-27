"""Mac-only native pickup boundary correction; no game edits/native execution."""
from pathlib import Path
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import current_mac_mike_powerups_prepare_v1 as old

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
FIXTURE=R/'tests/current-mac-powerups-v2.lua'
OLD=R/'tests/current-mac-mike-powerups.lua'

PRE="""hook('PhysicalPickup',function(s)
 if not entered then return end
 assert(C.mac and phase=='pickup'and s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==46 and r('Enemy_State',5)>=128,'Live mature Mac actor at genuine physical collision BEFORE erase')
 local t=C.plan[index]
 assert(r('PowerUpType',5)==t.pickup and r('InvPickupOwner',5)==C.character and r('LmStamp',5)==0xe0+t.pickup and r('InvPickup',5)==0xe0+t.pickup,'Actual matching mature Mac item/owner/stamp')
 assert(not rec.physical and not rec.pendingGrant,'One real collision/grant at a time')
 rec.physical={update=updates,slot=5,pickup=t.pickup,pc=C.hooks.PhysicalPickup.pc,bank=bank(C.hooks.PhysicalPickup.pc),erased=false}
 rec.physicalCollisions=(rec.physicalCollisions or 0)+1;event('live-physical-collision-before-erase',t.pickup)
end)
hook('PickupEraseReturn',function(s)
 if not entered then return end
 local p=assert(rec and rec.physical,'Genuine pickup collision precedes native erase return')
 assert(phase=='pickup'and s['cpu.x']==p.slot and p.update==updates and not p.erased and r('Enemy_Flag',p.slot)==0 and r('Enemy_ID',p.slot)==0 and r('Enemy_State',p.slot)==0,'Actual EraseEnemyObject returns with that pickup erased')
 p.erased=true;event('native-erase-return-before-family-grant',p.pickup)
end)
"""
BEFORE=" assert(phase=='pickup'and s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==46 and r('Enemy_State',5)>=128,'Actual physical mature pickup before source grant')"
AFTER=""" local p=assert(rec and rec.physical,'Actual physical collision receipt required at Mac grant')
 assert(phase=='pickup'and s['cpu.x']==5 and p.slot==5 and p.update==updates and p.erased and r('Enemy_Flag',5)==0 and r('Enemy_ID',5)==0 and r('Enemy_State',5)==0,'Same genuinely collected Mac pickup reaches family grant AFTER exact native erase')
 assert(p.pickup==C.plan[index].pickup,'Unchanged source item across erase/grant');rec.physical=nil"""


def main():
    out=R/'build/current-ab221-mac-hard-items-v2'
    assert not out.exists()
    assert sha(OLD)=='b70ef2cacfc57837b18fade5973e2c8af2309644047069a7b15ddb0feaa905a0'
    assert sha(Path(old.__file__))=='25f07ac574beacea299a382cfe618f9798ae6f409ed99a43f9dd75c42b291890'
    body=OLD.read_text();assert body.count(BEFORE)==1
    assert body.count("hook('Collect',function(s)")==1
    updated=body.replace("hook('Collect',function(s)",PRE+"hook('Collect',function(s)").replace(BEFORE,AFTER)
    assert updated.replace(AFTER,BEFORE).replace(PRE,'')==body
    assert not FIXTURE.exists();FIXTURE.write_text(updated,newline='\n')
    text=Path(old.__file__).read_text()
    before="fixture=R/'tests/current-mac-mike-powerups.lua'"
    assert text.count(before)==1;text=text.replace(before,"fixture=R/'tests/current-mac-powerups-v2.lua'")
    text=text.replace("choices=['mac','mike']","choices=['mac']")
    before="if n in ['Collect','Injury','Defeat','Reflect','DropCollect']"
    assert text.count(before)==1
    text=text.replace(before,"if n in ['Collect','Injury','Defeat','Reflect','DropCollect','PhysicalPickup','PickupEraseReturn']")
    before="            if n=='Collect':"
    after="""            if n=='PhysicalPickup':
                assert mac and phase=='pickup'and c.x==5 and q.get('Enemy_Flag',5)!=0 and q.get('Enemy_ID',5)==46 and q.get('Enemy_State',5)>=128
                assert not rec.get('physical')and not rec.get('pending_grant')
                assert q.get('PowerUpType',5)==t['pickup']and q.get('LmStamp',5)==224+t['pickup']and q.get('InvPickup',5)==224+t['pickup']and q.get('InvPickupOwner',5)==15
                rec['physical']=dict(call=calls,slot=5,erased=False,pickup=t['pickup']);rec['physical_collisions']=rec.get('physical_collisions',0)+1
            elif n=='PickupEraseReturn':
                p=rec.get('physical');assert p and not p['erased']and c.x==5 and p['call']==calls
                assert all(q.get(n,5)==0 for n in ['Enemy_Flag','Enemy_ID','Enemy_State']);p['erased']=True
            elif n=='Collect':"""
    assert text.count(before)==1;text=text.replace(before,after)
    before="                    assert phase=='pickup'and c.x==5"
    after="""                    assert phase=='pickup'and c.x==5
                    p=rec.get('physical');assert p and p['erased']and p['call']==calls and p['pickup']==t['pickup']
                    assert all(q.get(n,5)==0 for n in ['Enemy_Flag','Enemy_ID','Enemy_State']);rec['physical']=None"""
    assert text.count(before)==1;text=text.replace(before,after)
    ns={'__file__':str(Path(__file__)),'__name__':'_mac_pickup_boundary_v2'}
    exec(compile(text,str(Path(old.__file__)),'exec'),ns)
    inherited=ns['hooks_for']
    def hooks(b):
        h,sfx=inherited(b);entry=h['PhysicalPickup'];pc=entry['pc']
        off=ns['location'](b,'MarioSourcePowerupCollision')
        assert entry['bytes']==[32,ns['address'](b,'EraseEnemyObject')&255,ns['address'](b,'EraseEnemyObject')>>8]
        assert list(b['raw'][off+3:off+5])==[169,6]
        h['PickupEraseReturn']=dict(pc=pc+3,banks=entry['banks'],bytes=list(b['raw'][off+3:off+6]),source_symbol='MarioSourcePowerupCollision',source_delta=3)
        return h,sfx
    ns['hooks_for']=hooks
    argv=sys.argv;sys.argv=[str(Path(__file__)),'--identity','mac','--output',str(out)]
    try:ns['main']()
    finally:sys.argv=argv
    ready=out/'prepared-not-run.json';z=json.loads(ready.read_text())
    oldready=R/'build/current-ab221-mac-hard-items-v1/prepared-not-run.json'
    negative=R/'build/current-ab221-mac-hard-items-v1/native'
    negfiles=[negative/n for n in ['components.csv','mega_proto_body_palette_9ea-run.log','01-normal.png']]
    assert all(p.is_file()for p in negfiles)
    extra={Path(__file__),Path(old.__file__),OLD,oldready,*negfiles,
           R/'src/mario_source.s',R/'src/common.s',R/'src/roll_dispatch.s',R/'src/little_mac_pickups.s'}
    paths={Path(p['path'])for p in z['bindings']}|extra
    z.update(successor_scope='Native observer boundary correction only: mature live actor at actual MarioSourcePowerupCollision before EraseEnemyObject; exact same-update real erase return; family grant checks exact erased state and original item/owner; original13cases/mechanics/caps/hardware guards unchanged.',
        original_native_negative='v1 first mushroom wall905/update511, strict observer demanded live actor at LmCollectGate after native erase. No game defect established.',
        Lua_VM_executed=False,native_run=False)
    z['bindings']=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)]
    put(ready,z)
    put(out/'observer-correction.json',dict(native_run=False,Lua_VM_executed=False,
        exact_reverse_fixture=True,unchanged_source_campaigns=13,
        hooks={n:json.loads((out/'config.json').read_text())['hooks'][n]for n in ['PhysicalPickup','PickupEraseReturn','Collect']},
        original_negative=[dict(path=str(p),sha256=sha(p))for p in negfiles],
        original_assumption=BEFORE,corrected_boundaries=PRE+'\n'+AFTER,
        no_game_or_mechanics_guard_change=True))
    print(json.dumps(dict(ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),native_run=False)))


if __name__=='__main__':main()
