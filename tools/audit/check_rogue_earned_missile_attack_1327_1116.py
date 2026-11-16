"""Ordinary earned missile attack on exact1327; original/public CPU, no seeds."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
import capture_rogue_earned_mf_1327_1116 as Capture
import audit_rogue_stock_foundation_1327_1116 as Foundation

J,N,W,Frames=Capture.J,Capture.N,Capture.J.W,Capture.Frames
CAPTURE_SHA='158f5b54e14a40cf67de1a9b4e53a5355bc7790e4c8b891b239c1f364f6436d2'
SOURCE_PINS={
 'rogue_dawn_weapons.s':'bcc48630d66cef7084ca994e0f6a9730f929ee8bcdf82a636c6b89f877949aa4',
 'rogue_dawn_host_weapons.s':'075fa975f98aba6578daecd6998ee3391cd409f7ad8441eea01e3dbda6e82bee',
 'rogue_dawn_host_weapons_gate.s':'a3187b1502706579bfe39daf4522127ef07d4fadbadeff4295dc36afed888cfb'}
NAMES=('GameLoop','RdControlStep','RdControlDispatch','RdLifeMovement','RdToggleMissile',
 'RdPrepareHorizontalShot','MissileCommit','MissileRequest','RdHostSpawnProjectile',
 'RdWxSpawn','RdWxPreStep','RdWxUpdateSlot','RdWxMove','RdWxCell','RdAttackAdmission',
 'RdWxActorContact','RdProjectileImpact','RdProjectileTerrainImpact','RdAnimateProjectile')


def bindings(raw):
    assert J.H(Path(Capture.__file__).read_bytes())==CAPTURE_SHA
    q=J.bindings(raw);b=q['bundle'];points={};rows={}
    for name,pin in SOURCE_PINS.items():assert J.H((J.R/'src'/name).read_bytes())==pin,name
    for name in NAMES:
        pc,at=W.address(b,name),W.location(b,name);tag=128+(at-16)//8192
        rows[name]=dict(PC=pc,file=at,tag=tag,first32=raw[at:at+32].hex())
        points[tag,pc]=name
    exact=[]
    for name in('MissileCommit','MissileRequest','RdToggleMissile','RdAttackAdmission'):
        code=Foundation.source_bytes(b,name,'rogue_dawn_weapons.s');at=W.location(b,name)
        assert raw[at:at+len(code)]==code,('Current source contract',name)
        exact.append(dict(name=name,bytes=len(code),SHA256=J.H(code)))
    # Full host dispatch is independently authenticated by its producer-current
    # byte span below, rather than assuming the retained .s alone is installed.
    at=rows['RdWxUpdateSlot']['file'];end=W.location(b,'RdWxRememberColor')
    rows['RdWxUpdateSlot']['whole_bytes']=end-at
    rows['RdWxUpdateSlot']['whole_hex']=raw[at:end].hex()
    return q,points,rows,exact


def run(raw,only_bindings=False):
    q,points,hooks,exact=bindings(raw)
    if only_bindings:return dict(passed=True,owning_SHA256=J.PIN,hooks=hooks,source_contracts=exact,outputs=0)
    m,prefix=Capture.capture(raw);assert prefix['passed'],prefix
    r=lambda n,i=0:N.get(m,n,i)
    def shot(slot):
        return dict(slot=slot,action=r('RdWAction',slot),x=r('RdWX',slot)+256*r('RdWHi',slot),
            y=r('RdWY',slot),vx=r('RdWVX',slot),vy=r('RdWVY',slot),age=r('RdWAge',slot),
            hit=r('RdWHit',slot),onscreen=r('RdWOnScreen',slot),animation=r('RdWAnim',slot))
    def state():
        return dict(x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),
            engine=r('GameEngineSubroutine'),life=r('NumberofLives'),action=r('RdAction'),facing=r('RdFacing'),
            held=r('RdHeld'),fresh=r('RdFresh'),mode=r('RdMissileMode'),missiles=r('RdMissiles'),
            maximum=r('RdMaxMissiles'),health=[r('RdHealthLo'),r('RdHealthHi')],tanks=r('RdTanks'),gear=r('RdGear'))
    baseline=state();counts=Counter();pending=[];path=Counter();events=[];writes=[];birth=None;selected=None;fault=None
    current=dict(inside=False,cpu=None,pc=0,tag=-1);scope=dict(frame=0,stage='release',age=0)
    tracked=('GameLoop','RdControlStep','RdControlDispatch','RdLifeMovement','RdToggleMissile',
        'RdPrepareHorizontalShot','MissileCommit','RdHostSpawnProjectile','RdWxSpawn','RdWxUpdateSlot')
    def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    def token(c):
        pc=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1)&65535
        return(pc,(c.sp+2)&255,tag(pc))
    base=N.NesMPU;cpus=[]
    class CPU(base):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);cpus.append(self)
        def settle(self):
            nonlocal birth,selected
            while pending and(self.pc,self.sp,tag(self.pc))==pending[-1]['return']:
                p=pending.pop();counts[p['name']+'_returned']+=1
                if p['name']=='RdWxUpdateSlot'and selected is not None and p['slot']==selected:
                    after=shot(selected);path['selected_updates']+=1
                    path['selected_moved']+=after['x']!=p['before']['x']or after['y']!=p['before']['y']
                    if len(events)<8:events.append(dict(kind='slot_update',before=p['before'],after=after,frame=scope['frame']))
                if p['name']=='RdWxSpawn'and birth is None:
                    slot=r('RdSlot');s=shot(slot)
                    if s['action']==11:
                        selected=slot;birth=dict(frame=scope['frame'],state=state(),shot=s,counts=dict(counts))
                        events.append(dict(kind='real_missile_spawn',**birth))
        def step(self):
            self.settle();t=tag(self.pc);name=points.get((t,self.pc));current.update(cpu=self,pc=self.pc,tag=t)
            if name:
                counts[name+'_entered']+=1
                if name in tracked:
                    p=dict(name=name,return_=token(self));p['return']=p.pop('return_')
                    if name=='RdWxUpdateSlot':p.update(slot=r('RdSlot'),before=shot(r('RdSlot')))
                    pending.append(p)
            if selected is not None and any(p['name']=='RdWxUpdateSlot'and p['slot']==selected for p in pending):
                path['%02X:%04X'%(t,self.pc)]+=1
            current['inside']=True
            try:return super().step()
            finally:current['inside']=False
    old_write=type(m).__setitem__;ammo=W.address(m.bundle,'RdMissiles');sfx=W.address(m.bundle,'RdSfx')
    def write(bus,at,value):
        if bus is m and current['inside']and isinstance(at,int)and at in(ammo,sfx):
            if len(writes)<8:writes.append(dict(frame=scope['frame'],PC=current['pc'],tag=current['tag'],
                address=at,old=m[at],new=value,SP=current['cpu'].sp))
        return old_write(bus,at,value)
    pads=[]
    try:
        with patch.object(N,'NesMPU',CPU),patch.object(type(m),'__setitem__',write):
            for frame in range(96):
                scope['frame']=frame;stage=scope['stage']
                # Each transition waits for the real source input-consumption
                # mirror. No direct routine call or resource construction.
                if stage=='release':
                    pad=0
                    if frame>=2 and not(r('RdHeld')&96):scope.update(stage='select',age=0)
                elif stage=='select':
                    pad=32
                    if r('RdMissileMode')==1:scope.update(stage='release-fire',age=0)
                elif stage=='release-fire':
                    pad=0
                    if scope['age']>=2 and not(r('RdHeld')&96):scope.update(stage='fire',age=0)
                elif stage=='fire':
                    pad=64
                    if birth is not None:scope.update(stage='observe',age=0)
                else:pad=0
                if not pads or pads[-1]['bits']!=pad:pads.append(dict(frame=frame,bits=pad,state=state()))
                m.controller_pad=pad;Frames.frame(m,whole_pass=True)
                for c in cpus:c.settle()
                cpus.clear();assert not pending,('Unreturned frame',pending)
                assert r('NumberofLives')==2 and r('GameEngineSubroutine')!=11
                assert(r('RdTanks'),r('RdGear'),r('RdMaxMissiles'))==(1,0,5)
                scope['age']+=1
                if birth and all(counts[n+'_returned']-birth['counts'].get(n+'_returned',0)>=26 for n in('GameLoop','RdControlStep','RdControlDispatch','RdLifeMovement')):break
    except Exception as error:fault=dict(error=repr(error),frame=scope['frame'],state=state())
    post={n:counts[n+'_returned']-(birth or{}).get('counts',{}).get(n+'_returned',0)for n in('GameLoop','RdControlStep','RdControlDispatch','RdLifeMovement')}
    post_entered={n:counts[n+'_entered']-(birth or{}).get('counts',{}).get(n+'_entered',0)for n in post}
    functional=fault is None and birth is not None and path['selected_moved']>0 and min(post.values())>=25 and min(post_entered.values())>=25
    result=dict(passed=functional,fault=fault,
        owning_SHA256=J.PIN,prefix_receipt_SHA256=prefix['receipt_SHA256'],prefix_terminal=prefix['receipt']['terminal'],
        hooks=hooks,source_contracts=exact,baseline=baseline,pads=pads,birth=birth,terminal=state(),
        final_shot=shot(selected)if selected is not None else None,counts=dict(counts),selected_update_path=dict(path),
        bounded_events=events,resource_request_writes=writes,postbirth_returned=post,postbirth_entered=post_entered,
        actual_current_CPU=True,no_actor_or_inventory_or_resource_seeds=True,outputs=0,native=False)
    result['receipt_SHA256']=J.H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--bindings',action='store_true');a=ap.parse_args()
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Earned missile source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.bindings)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
