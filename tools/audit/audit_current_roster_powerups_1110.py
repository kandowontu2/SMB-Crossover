"""Current100-name powerup routing/progression census, stdout only.

Actual menu/constructor/opening is controller-only. Pickup cases afterward
are explicit mature-actor CPU fixtures, not natural earned-item claims.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_current_roster_stage_ingress_1110 as Starts
import check_ff_white_mushroom_current_1110 as W
import check_ff_head_lifetime_irq_1110 as L

N=Starts.N
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='a5c54d7624ee961f11b45598ca7cf7fecc24de6ee87d8e8aa70dad55834f2eaa'
STARTS_PIN='dfe452834b2dc4a3e33e0e3adc5f749415248e0e6ff940caf451e7d99299f91b'


def cold(bundle,row):
    latest=[];Base=N.NesMPU
    class ObservedMPU(Base):
        def __init__(self,*args,**kw):
            super().__init__(*args,**kw)
            latest[:]=[self.memory]
    with patch.object(N,'NesMPU',ObservedMPU):result=Starts.stage(bundle,row)
    assert result['passed'] and latest and latest[0].bundle['raw']==bundle['raw']
    return result,latest[0]


def state(m,slot=5):
    names=('SelectedCharacter','PlayerStatus','PlayerSize','GameEngineSubroutine','TimerControl',
        'GuestPowerupActive','GuestPowerupAge','GuestPowerupOld','GuestPowerupTarget','GuestPowerupDisplay',
        'NumberofLives','StarInvincibleTimer','Square1SoundQueue','Square2SoundQueue','AreaMusicQueue')
    values={n:N.get(m,n) for n in names}
    values.update(actor_flag=N.get(m,'Enemy_Flag',slot),actor_id=N.get(m,'Enemy_ID',slot),
        actor_state=N.get(m,'Enemy_State',slot),kind=N.get(m,'PowerUpType',slot),
        floaty=N.get(m,'FloateyNum_Control',slot),floaty_timer=N.get(m,'FloateyNum_Timer',slot))
    return values


def collect(seed,kind):
    m=L.clone(seed);slot=5
    # Explicit native-handler fixture, after the real menu/scene constructor.
    N.put(m,NmiDisable=255,ObjectOffset=slot)
    for name,value in (('Enemy_Flag',1),('Enemy_ID',46),('Enemy_State',128),('PowerUpType',kind),
                       ('Enemy_X_Position',N.get(m,'Player_X_Position')),('Enemy_PageLoc',N.get(m,'Player_PageLoc')),
                       ('Enemy_Y_Position',N.get(m,'Player_Y_Position')),('Enemy_Y_HighPos',1)):
        m[W.address(m.bundle,name)+slot]=value
    N.invoke(m,'NrPrepare',a=kind,x=slot,y=0)
    # The preparation may choose a physical stationary item; actual mature
    # emergence is supplied explicitly, never presented as a natural birth.
    m[W.address(m.bundle,'Enemy_State')+slot]=128
    before=state(m);calls=Counter();Base=N.NesMPU
    tracked={}
    for name in ('HandlePowerUpCollision','NrPickup','HuPickup','HuPowerup','NrNativePowerupDispatch',
        'GuestBeginPowerup','GuestPowerupUpdate','MarioSourceBeginFreeze','MarioSourcePowerupCollision',
        'FwHostCollect','FwHostPowerupTick','DkHostCollect','DkHostPowerup','KbCollectPickup','KbPowerup'):
        if name in m.bundle['syms']:
            tracked[(((W.location(m.bundle,name)-16)//8192)|128,W.address(m.bundle,name))]=name
    class TracedMPU(Base):
        def step(self):
            if self.pc>=0x8000:
                name=tracked.get((self.memory.rawtags[(self.pc-0x8000)//8192],self.pc))
                if name:calls[name]+=1
            return super().step()
    with patch.object(N,'NesMPU',TracedMPU):
        result=N.invoke(m,'HandlePowerUpCollision',a=kind,x=slot,y=0)
        collected=state(m);ticks=0
        while N.get(m,'GuestPowerupActive') and ticks<70:
            N.invoke(m,'NrNativePowerupDispatch',a=0,x=0,y=0)
            ticks+=1
        after=state(m)
    m.controller_pad=0
    idle=W.address(m.bundle,'IdleLoop');W.clear_logs(m);N.consume(m)
    c=N.NesMPU(memory=m,pc=idle);c.sp,c.p=255,0x31;c.stPushWord(0xe33b)
    L.finish(m,c,(idle+12,252))
    resumed=state(m)
    issues=[]
    if after['GuestPowerupActive']:issues.append('hosted_freeze_did_not_finish_in70_native_progression_calls')
    if collected['actor_flag']:issues.append('mature_actor_not_erased_by_collection_callback')
    return dict(kind=kind,before=before,collected=collected,after=after,resumed=resumed,progression_calls=ticks,
        returned=result,calls=dict(calls),issues=issues,
        scope='Directed actual prepared+mature native-handler CPU fixture; actor/maturity explicitly supplied, not natural collection. Row33 progression calls only while actual hosted Active is set; no movement/PPU/native cadence claim.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--name');p.add_argument('--first-slot',type=int,default=0)
    p.add_argument('--last-slot',type=int,default=31);p.add_argument('--inventory-only',action='store_true')
    p.add_argument('--detail',action='store_true');p.add_argument('--quiet',action='store_true');args=p.parse_args()
    assert sha256(Path(Starts.__file__).read_bytes()).hexdigest()==STARTS_PIN
    raw=ROM.read_bytes();assert sha256(raw).hexdigest()==PIN
    inventory=Starts.C.inventory(raw)
    unique={(r['slot'],r['raw'],r['name']):r for r in inventory['rows']}
    assert len(unique)==100 and all(r['confirm_starts'] for r in unique.values())
    roster=[dict(name=r['name'],slot=r['slot'],cycle=r['cycle'],raw=r['raw'],variants=r['variants']) for r in unique.values()]
    if args.inventory_only:
        print(json.dumps(dict(passed=True,ROM_SHA256=PIN,named_entries=100,roster=roster,output_files=0)),flush=True);return
    bundle=W.Symbols.bundle();bundle['raw']=raw;results=[]
    for row in unique.values():
        if not args.first_slot<=row['slot']<=args.last_slot or (args.name and args.name not in row['name']):continue
        if not args.quiet:print(json.dumps(dict(event='powerup_constructor_start',name=row['name'],slot=row['slot'],cycle=row['cycle'])),flush=True)
        opening,m=cold(bundle,row)
        items=[]
        for kind in range(4):
            try:items.append(collect(m,kind))
            except Exception as error:items.append(dict(kind=kind,error=repr(error),issues=['callback_exception']))
        result=dict(name=row['name'],slot=row['slot'],cycle=row['cycle'],selected=N.get(m,'SelectedCharacter'),
            genuine_opening=opening,items=items)
        results.append(result)
        compact=[]
        for i in items:
            if 'error' in i:compact.append(i);continue
            compact.append(dict(kind=i['kind'],physical_kind=i['before']['kind'],
                status=[i[n]['PlayerStatus'] for n in ('before','collected','after','resumed')],
                engine=[i[n]['GameEngineSubroutine'] for n in ('collected','after','resumed')],
                freeze_calls=i['progression_calls'],active=i['resumed']['GuestPowerupActive'],
                timer=i['resumed']['TimerControl'],erased=not i['collected']['actor_flag'],
                star=i['collected']['StarInvincibleTimer'],floaty=i['collected']['floaty'],
                SFX=i['collected']['Square2SoundQueue'],calls=i['calls'],issues=i['issues']))
        if not args.quiet or any(i['issues'] for i in items):
            print(json.dumps(dict(event='powerup_profile',result=result if args.detail else
                dict(name=result['name'],slot=result['slot'],cycle=result['cycle'],selected=result['selected'],items=compact))),flush=True)
    assert results
    issues=[dict(name=r['name'],kind=i['kind'],issues=i['issues'],error=i.get('error')) for r in results for i in r['items'] if i['issues']]
    print(json.dumps(dict(passed=True,read_only_audit=True,ROM_SHA256=PIN,source_CPU_only=True,Mesen_run=False,
        output_files=0,ROM_written=False,full_roster_inventory=100,profiles=len(results),directed_pickup_cases=4*len(results),
        issues=issues,scope='Actual current menus plus genuine cold/opening initialization, followed by explicitly synthetic mature pickup callback/progression fixtures. Findings require source interpretation and natural-route followup; no all-powerup completion claim.')),flush=True)


if __name__=='__main__':main()
