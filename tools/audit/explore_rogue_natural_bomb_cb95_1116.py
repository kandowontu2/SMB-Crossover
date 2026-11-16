"""Actual cb95 genuine MF followed by retained ordinary route; RAM-only Bomb lead."""
from collections import defaultdict, Counter
from pathlib import Path
from unittest.mock import patch
import argparse, json
import current_rogue_missile_cb95_1116 as J
import replay_rogue_full11_current_1114 as Retained
from check_ff_stdout_controller_source_1110 import LuaRuntime

N,W,Frames,H=J.N,J.W,J.Frames,J.H


def load_current():
    actual=J.ROM.read_bytes();pin=H(actual)
    if pin==J.PIN:J.C.inverse(actual);raw=actual;kind='exactcb95'
    else:
        assert pin==J.C.PARENT,('Exact owning9826/cb95 only',pin)
        raw=J.C.proposal(actual)[0];kind='strict9826 to owningcb95 in RAM'
    return raw,dict(actual_input_SHA256=pin,owning_CPU_SHA256=J.PIN,binding=kind)


def run(raw,limit=7000):
    assert H(raw)==J.PIN
    ref=J.reference(raw);old=J.Previous.mf_controller(ref)
    assert old.count(J.Previous.PIN)==1
    text=old.replace(J.Previous.PIN,J.PIN,1)
    assert text.replace(J.PIN,J.Previous.PIN,1)==old
    q=J.bindings(raw);b=q['bundle'];m=J.cold(raw);lua=LuaRuntime(unpack_returned_tuples=True)
    callbacks={0:defaultdict(list),1:defaultdict(list)};events=defaultdict(list)
    ctx=dict(cpu=None,pc=0,status=None,receipt=None,mode='MF');counts=Counter();pending=[];objects=[]
    r=lambda n,i=0:N.get(m,n,i)
    def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else -1
    def state():return dict(Main=counts['GameLoop_returned'],x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),
        native=r('Player_State'),action=r('RdAction'),VY=r('RdVY'),VX=r('RdVX'),held=r('RdHeld'),fresh=r('RdFresh'),
        world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaPointer'),engine=r('GameEngineSubroutine'),
        camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),health_raw=[r('RdHealthLo'),r('RdHealthHi')],
        tank=r('RdTanks'),gear=r('RdGear'),missiles=r('RdMissiles'),max_missiles=r('RdMaxMissiles'),life=r('NumberofLives'))
    def actor(i):return dict(slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),state=r('Enemy_State',i),
        x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i),
        kind=r('PowerUpType',i),private=r('InvPickup',i),owner=r('InvPickupOwner',i),raw=r('InvPickupSaveLo',i))
    api=lua.table();api.memType=lua.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2))
    api.callbackType=lua.table_from(dict(exec=0,write=1));api.eventType=lua.table_from(dict(inputPolled=0,endFrame=1))
    def read(at,kind=0):
        if kind==1:return m.ram[at//8192][at%8192]
        if kind==2:return raw[16+at]
        assert kind==0;return m[at]
    def mapped(pc):
        if pc<0x8000:return None
        t=tag(pc);return lua.table_from(dict(memType=2 if t&128 else 1,address=(t&127)*8192+(pc&8191)))
    def cpu_state():
        c=ctx['cpu'];d={f'cpu.{k}':getattr(c,k)if c else 0 for k in('pc','sp','a','x','y','p')}
        d['cpu.pc']=ctx['pc'];d['cpu.ps']=d['cpu.p'];return lua.table_from(d)
    def memory(fn,kind,lo,hi=None):
        for at in range(lo,(hi if hi is not None else lo)+1):callbacks[kind][at].append(fn)
    def pad(p,port=0):
        if isinstance(p,tuple):p=p[0]  # Lua assignment consumes the first return.
        assert port==0;m.controller_pad=sum(v for n,v in(('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))if p[n])
    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):ctx['receipt']=json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '))
    api.read=read;api.convertAddress=mapped;api.getState=cpu_state;api.setInput=pad;api.addMemoryCallback=memory
    api.addEventCallback=lambda fn,kind:events[kind].append(fn);api.stop=lambda status:ctx.update(status=status)
    lua.globals().emu=api;lua.globals().print=emit;lua.globals().CPU_CONTROLLER_OPENING=True;lua.execute(text)
    probe=lua.execute('return {right=true,a=true},{diagnostic=true}')
    assert isinstance(probe,tuple)and len(probe)==2
    pad(probe);assert m.controller_pad==129
    m.controller_pad=0  # Controller input only; no game-state fixture writes.
    registration=dict(exec_addresses=len(callbacks[0]),write_addresses=len(callbacks[1]),events={k:len(v)for k,v in events.items()})
    assert registration==dict(exec_addresses=13,write_addresses=10,events={0:1,1:1}),registration
    sources={};policy=Retained.route('rogue_dawn_11_v9.lua',sources)
    choose=lua.execute('local ROSTER_CONFIG={rogue_tile_attributes={'+','.join(map(str,q['attributes'] if 'attributes'in q else list(raw[W.location(b,'MTileAttribute'):W.location(b,'MTileAttribute')+256])))+'}}\n'+policy)
    phase_events=[];cache=None;first_injury=None;fault=None;ground=0;laststage=None;prefix=None;done=False
    watched=('GameLoop','RdControlStep','RdControlDispatch','RdLifeMovement')
    points={(128+(W.location(b,n)-16)//8192,W.address(b,n)):n for n in watched}
    def context():
        s=state();c=dict(frame=counts['GameLoop_returned'],poll=counts['GameLoop_returned'],char=2,variant=1,r=r,
            x=s['x'],y=s['y'],yHigh=r('Player_Y_HighPos'),state=s['native'],vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),
            status=r('PlayerStatus'),world=s['world'],level=s['level'],area=s['area'],areaType=r('AreaType'),engine=s['engine'],camera=s['camera'],
            lastA=bool(r('RdHeld')&128),grounded=s['native']==0)
        c['block']=lambda x,y:0 if y<32 or y>=240 else r('Block_Buffer_1',(int(x)//256)%2*208+((int(y)-32)//16)*16+(int(x)%256)//16)
        def enemy():
            aa=[a for i in range(6)if(a:=actor(i))['flag']and a['flag']<128 and(a['id']<21 or a['id']in(45,51))and a['state']<32 and not(a['id']==6 and a['state']>=2)and -160<a['x']-s['x']<160]
            if not aa:return None
            a=min(aa,key=lambda a:abs(a['x']-s['x']));return lua.table_from(dict(a,dx=a['x']-s['x']))
        c['enemy']=enemy;return lua.table_from(c)
    def inspect_cache():
        left,right=r('ScreenLeft_PageLoc'),r('ScreenRight_PageLoc');rows=[]
        for page in range(left,right+1):
            for row in range(13):
                for col in range(16):
                    t=r('Block_Buffer_1',page%2*208+row*16+col)
                    if t in(0xc1,0x55,0x5a,0x57,0x5c,0x60):rows.append(dict(x=page*256+col*16,y=32+row*16,tile=t))
        return dict(state=state(),left_page=left,right_page=right,power_tiles=[a for a in rows if a['tile']in(0xc1,0x55,0x5a)],special_tiles=rows,
            table_file=W.location(b,'BrickQBlockMetatiles'),table_hex=raw[W.location(b,'BrickQBlockMetatiles'):W.location(b,'BrickQBlockMetatiles')+14].hex())
    def after_main():
        nonlocal laststage,cache,done,ground
        s=state();assert r('SelectedCharacter')==2 and r('RdVariant')==1 and s['life']==2 and s['engine']!=11 and sum(s['health_raw'])>0,('Actual legal progression guard',s)
        assert s['tank']==1 and s['gear']==0 and s['missiles']==s['max_missiles']==5,('Earned MF resources preserved',s)
        stage=(s['world'],s['level'],s['area'],s['engine'])
        if stage!=laststage and len(phase_events)<16:phase_events.append(s);laststage=stage
        if(s['world'],s['level'],s['engine'])==(0,1,8):
            m.controller_pad=0
            if r('Player_Y_HighPos')==1 and s['native']==0 and s['y']>=176:ground+=1
            else:ground=0
            if ground==25:cache=inspect_cache();done=True
        elif s['engine']==8 and s['level']==0:pad(choose(context()))
        else:m.controller_pad=0
    base=N.NesMPU;old_write=type(m).__setitem__
    class CPU(base):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);objects.append(self)
        def settle(self):
            while pending and(self.pc,self.sp,tag(self.pc))==pending[-1]['return']:
                p=pending.pop();counts[p['name']+'_returned']+=1
                if p['name']=='GameLoop':after_main()
        def step(self):
            ctx.update(cpu=self,pc=self.pc)
            if ctx['mode']=='MF':
                for fn in tuple(callbacks[0].get(self.pc,())):fn()
            else:
                self.settle();name=points.get((tag(self.pc),self.pc))
                if name:
                    counts[name+'_entered']+=1
                    ret=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                    pending.append(dict(name=name,return_=(ret,(self.sp+2)&255,tag(ret))));pending[-1]['return']=pending[-1].pop('return_')
            return super().step()
    def write(bus,at,value):
        if bus is m and isinstance(at,int)and ctx['mode']=='MF':
            for fn in tuple(callbacks[1].get(at,())):fn(at,value)
        return old_write(bus,at,value)
    try:
        with patch.object(N,'NesMPU',CPU),patch.object(type(m),'__setitem__',write):
            for tick in range(limit):
                if ctx['mode']=='MF':
                    for fn in tuple(events[0]):fn()
                Frames.frame(m,whole_pass=True)
                if ctx['mode']=='MF':
                    for fn in tuple(events[1]):fn()
                    if ctx['status']is not None:
                        assert ctx['status']==0 and ctx['receipt']['passed'],('Unchanged genuine MF prefix',ctx['receipt'])
                        prefix=ctx['receipt'];ctx.update(mode='travel',status=None);after_main()
                else:
                    for c in objects:c.settle()
                    assert not pending,('Completed public frame scopes',pending)
                objects.clear()
                if done:break
                if tick%500==499:print('PROGRESS '+json.dumps(dict(source_passes=tick+1,mode=ctx['mode'],state=state())),flush=True)
    except Exception as e:fault=dict(error=repr(e),state=state(),pending=[p['name']for p in pending])
    result=dict(passed=done and fault is None,scope='Genuine frozen MF then retained v9 ordinary stage progression to actual1-2 cache only',
        fault=fault,owning_SHA256=J.PIN,MF_Lua_SHA256=H(text.encode()),executed_registration=registration,
        MF_passed=bool(prefix and prefix.get('passed')),MF_terminal=prefix.get('terminal')if prefix else None,
        MF_completed_gate=prefix.get('score_credit')if prefix else None,policy_sources=sources,source_passes=tick+1,
        travel_counts=dict(counts),phase_events=phase_events,actual_stage_cache=cache,terminal=state(),
        no_bomb_acquisition_claim=True,no_gameplay_resource_actor_seeds=True,outputs=0,native=False)
    result['receipt_SHA256']=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--limit',type=int,default=7000);a=p.parse_args();assert 100<=a.limit<=9500
    raw,provenance=load_current()
    def deny(*a,**kw):raise AssertionError('Natural Bomb source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.limit)
    print('RESULT '+json.dumps(dict(input=provenance,result=q),separators=(',',':')),flush=True)
