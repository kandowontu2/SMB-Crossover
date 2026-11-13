"""Pure controller-only fifth stock pickup extension; exact526, no ROM edits."""

import argparse
from collections import defaultdict
from functools import lru_cache
from hashlib import sha256
import json
from multiprocessing.connection import Client, Listener
import sys
import time
from unittest.mock import patch

import compose_karnov_ladder_native_1113 as Feature
import replay_karnov_ladder_stock_1113 as Four
import check_karnov_natural_bomb_1113 as Native
from check_ff_stdout_controller_source_1110 import LuaRuntime
from lupa.lua54 import LuaError

PIN=Four.CANDIDATE
BASE='00187419e40f04b1d60f16792a1359ffae1caea4614f6d6ae30d3ff8c20e0f62'
SOURCE=Feature.Owner.R/'tools/reference/karnov_ladder_fifth_1113.lua'


def candidate():
    raw=Feature.Owner.NIGHTLY.read_bytes()
    if sha256(raw).hexdigest()==PIN:return raw
    if sha256(raw).hexdigest()=='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc':
        import compose_prince_entrance_current_1113 as Prince
        assert Prince.PARENT==PIN
        parent=Prince.reverse(raw);assert sha256(parent).hexdigest()==PIN
        return parent
    assert sha256(raw).hexdigest()==Four.PARENT
    image,_=Feature.proposal_current(raw);assert sha256(image).hexdigest()==PIN
    return image


def census(raw):
    assert sha256(raw).hexdigest()==PIN
    b=dict(Native.W.Symbols.bundle(),raw=raw);out={};holes={}
    for name in('L_GroundArea6','L_UndergroundArea1'):
        at=Native.W.location(b,name);page=0;rows=[];gaps=[]
        for offset in range(2,1000,2):
            first=raw[at+offset]
            if first==253:break
            second=raw[at+offset+1]
            if second&128:page+=1
            y=first&15
            if y==13 and not second&64 and not second&128:page=second&31
            if y<12 and not second&112 and second&15 in(0,4):
                rows.append(dict(left=page*256+(first>>4)*16,top=(y+2)*16,
                    stream_offset=offset,bytes=bytes((first,second)).hex(),kind=second&15))
            if y==12 and second&112==0:
                gaps.append(dict(left=page*256+(first>>4)*16,width=((second&15)+1)*16,bytes=bytes((first,second)).hex()))
        out[name]=rows;holes[name]=gaps
    assert[(r['left'],r['top'])for r in out['L_GroundArea6']]==[(336,144),(1248,144),(1744,80)]
    assert[(r['left'],r['top'])for r in out['L_UndergroundArea1']]==[(160,144),(1104,128),(2400,128)]
    return dict(actual_ROM_stream_small_object_decode=out,decoded_empty_holes=holes,native_parser_route_validation_pending=True)


@lru_cache(maxsize=1)
def four_controller(raw):
    assert sha256(raw).hexdigest()==PIN
    text=Four.controller(raw,wait_for_entry=True);assert sha256(text.encode()).hexdigest()==BASE
    return text


def controller(raw):
    assert sha256(raw).hexdigest()==PIN
    text=four_controller(raw)
    body,hooks=SOURCE.read_text().split('-- COUNTER_HOOKS\n')
    def replace(before,after):
        nonlocal text
        assert text.count(before)==1,before
        text=text.replace(before,after)
    replace('local pickups,births,scenes,trace={},{},{},{}',
        'local pickups,births,scenes,trace={},{},{},{}\nlocal stockFifth')
    replace('local function control()',body+'\nlocal function control()')
    replace(''' if #pickups>=4 then
  if not armed then return routeAge%8<2 and 68 or 0 end
  return 0
 end''',''' if #pickups>=4 then return fifthControl(x,y,ground,item)end''')
    replace('local function probe(name,q,limit)',hooks+'\nlocal function probe(name,q,limit)')
    replace('native_blast_contacts=blastCalls','native_blast_contacts=blastCalls,fifth=stockFifth')
    replace('if a.flag==1 and a.id==37 and a.state==65 then helpers[#helpers+1]={frame=frame,',
        "if a.flag==1 and((a.id==37 and a.state==65)or(a.id==40 and a.state==66))then helpers[#helpers+1]={axis=a.state==66 and 'horizontal'or 'vertical',frame=frame,")
    replace("and r('Enemy_ID',h.slot)==37 and r('Enemy_State',h.slot)==65 and r('Enemy_X_Position',h.slot)+256*r('Enemy_PageLoc',h.slot)==h.left",
        "and r('Enemy_ID',h.slot)==(h.axis=='horizontal'and 40 or 37)and r('Enemy_State',h.slot)==(h.axis=='horizontal'and 66 or 65)and(h.axis=='horizontal'or r('Enemy_X_Position',h.slot)+256*r('Enemy_PageLoc',h.slot)==h.left)")
    replace("q.after=state();q.erased=r('Enemy_Flag',q.item.slot)==0",'''q.after=state()
   if #pickups==4 then
    q.native={sound=r('Square2SoundQueue'),popup=r('FloateyNum_Control',q.item.slot),inventory=r('InvPickup',q.item.slot)}
    assert(q.native.sound&32~=0 and q.native.popup==6 and q.native.inventory==0,'Fifth native sound/popup/inventory erasure')
    assert(q.after.shot==2 and q.after.cycle==3 and q.after.owned&4~=0 and q.after.option==2,'Fifth original earned Ladder progression')
   end
   q.erased=r('Enemy_Flag',q.item.slot)==0''')
    replace("if #pickups>=4 and armed and blastSeen and kr(0xc0)==0 then finish(true,'naturally-earned-and-used-bomb');return end",
        "if #pickups>=5 and stockFifth.complete then finish(true,'Five stock native pickups and original Ladder use');return end")
    b=dict(Native.W.Symbols.bundle(),raw=raw)
    pre='local GAMELOOP_OFFSET='+str(Native.W.location(b,'GameLoop')-16)+'\n'
    pre+='local FIFTH_GAMELOOP='+str(Native.W.address(b,'GameLoop'))+'\n'
    pre+='local FIFTH_IDLE='+str(Native.W.address(b,'IdleLoop'))+'\n'
    pre+='local FIFTH_R2='+str(Native.W.address(b,'R2'))+'\n'
    pre+='local FIFTH_MOVE='+str(Native.W.address(b,'KrMovement'))+'\n'
    pre+='local MTILE_ATTRIBUTES_OFFSET='+str(Native.W.location(b,'MTileAttribute')-16)+'\n'
    pre+='local FIFTH_PLANT_DOWN='+str(Native.W.address(b,'PiranhaPlantDownYPos'))+'\n'
    pre+='local FIFTH_SOUND='+str(Native.W.address(b,'Square2SoundQueue'))+'\n'
    pre+='local FIFTH_POPUP='+str(Native.W.address(b,'FloateyNum_Control'))+'\n'
    pre+='local FIFTH_VRAM_OFFSET='+str(Native.W.address(b,'VRAM_Buffer1_Offset'))+'\n'
    # Locals are added to the existing bound field table, never guessed.
    text=text.replace('local L={','local L={VRAM_Buffer1_Offset=FIFTH_VRAM_OFFSET,Square2SoundQueue=FIFTH_SOUND,FloateyNum_Control=FIFTH_POPUP,PiranhaPlantDownYPos=FIFTH_PLANT_DOWN,GameLoop=FIFTH_GAMELOOP,IdleLoop=FIFTH_IDLE,R2=FIFTH_R2,KrMovement=FIFTH_MOVE,',1)
    result=pre+text
    assert all(s not in result for s in('emu.write','io.open','loadState','saveState','takeScreenshot'))
    LuaRuntime().compile(result)
    return result


def run(raw,*,limit=1000,stop_on_stall=False,return_model=False,input_model=None,history=None,checkpoint_x=None,checkpoints=None,checkpoint_pickups=4,stop_on_native_head=False,stop_at_pickups=None,observer_early_heads=None):
    began=time.perf_counter();bundle=dict(Native.W.Symbols.bundle(),raw=raw)
    if input_model is None:opening,m=Native.C.cold(bundle,dict(name='KARNOV',slot=7,cycle=1,raw=34))
    else:opening,m=dict(genuine_prefix_derived_development_fork=True),input_model
    lua=LuaRuntime(unpack_returned_tuples=True);text=controller(raw)
    events={};callbacks=defaultdict(list);context=dict(cpu=None,exit=None,receipt=None,milestones=list(history or[]))
    emu=lua.table();emu.memType=lua.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2,nesPpuDebug=3))
    emu.eventType=lua.table_from(dict(inputPolled=0,endFrame=1));emu.callbackType=lua.table_from(dict(exec=0))
    def read(at,kind=0):
        if kind==1:return m.ram[at//8192][at%8192]
        if kind==2:return raw[16+at]
        if kind==3:return m.vram[at&0x3fff]
        return m[at]
    def mapped(at):
        if at<0x8000:return None
        tag=m.rawtags[(at-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(at&8191)))
    def get_state():
        c=context['cpu'];return lua.table_from({f'cpu.{k}':getattr(c,k)if c else 0 for k in('pc','sp','a','x','y')})
    def set_input(pad,port):
        assert port==0
        m.controller_pad=sum(bit for name,bit in(('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))if pad[name])
    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):context['receipt']=json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '))
        elif line.startswith('KARNOV_NATURAL_PICKUP '):context['milestones'].append(json.loads(line.removeprefix('KARNOV_NATURAL_PICKUP ')))
    def add_memory(fn,kind,lo,hi=None):
        for at in range(lo,lo+1 if hi is None else hi+1):callbacks[at].append(fn)
    emu.read,emu.convertAddress,emu.getState,emu.setInput=read,mapped,get_state,set_input
    emu.addMemoryCallback=add_memory;emu.addEventCallback=lambda fn,kind:events.setdefault(kind,fn)
    emu.stop=lambda code:context.update(exit=code)
    lua.globals().emu=emu;lua.globals().print=emit;lua.globals().CPU_CONTROLLER_OPENING=True
    def to_lua(value):
        if isinstance(value,(list,dict)):
            table=lua.table()
            for key,item in(value.items()if isinstance(value,dict)else enumerate(value,1)):table[key]=to_lua(item)
            return table
        return value
    suffix=''
    if history:
        lua.globals().CPU_FIFTH_HISTORY=to_lua(history)
        retired=len(history)>=4 and m.ram[2][0xbb]==0 and m.ram[2][0x8f]&2==0
        active=m.ram[2][0xc0]
        underground=Native.N.get(m,'LevelNumber')==1 and Native.N.get(m,'AreaType')==2 and(Native.Base.player(m)['x']>48 or Native.Base.player(m)['state']==0 and Native.Base.player(m)['y']>=160)
        suffix='\npickups=CPU_FIFTH_HISTORY;armed='+str(retired or active>=128).lower()+';blastSeen='+str(retired or active>=129).lower()+';undergroundReady='+str(underground).lower()+';routePhase="travel"\n'
    if observer_early_heads:
        assert history and all(h['tile']==193 and h['native_pad']&128 for h in observer_early_heads)
        lua.globals().CPU_EARLY_HEAD_HISTORY=to_lua(observer_early_heads)
        suffix+='\nearly.heads=CPU_EARLY_HEAD_HISTORY\n'
    lua.execute(text+suffix+'\nKARNOV_FIFTH_CPU_STATE=function()return stockFifth end\nKARNOV_FIFTH_CPU_HELPERS=function()return helpers end\nKARNOV_FIFTH_CPU_BOOTS=function()return bootsUsed end\n');parent=Native.N.NesMPU
    class Observed(parent):
        def step(self):
            context['cpu']=self
            for fn in tuple(callbacks.get(self.pc,())):fn()
            return parent.step(self)
    stall=0;lastx=None;controller_error=None
    with patch.object(Native.N,'NesMPU',Observed):
        for tick in range(limit):
            try:
                events[0]();Native.Frames.frame(m)
                c=context['cpu'];assert(c.pc,c.sp)==(Native.W.address(m.bundle,'IdleLoop')+12,252)
                for fn in tuple(callbacks.get(c.pc,())):fn()
                events[1]()
            except LuaError as error:
                controller_error=str(error);break
            if(tick+1)%1000==0:
                print('KARNOV_FIFTH_CPU_PROGRESS '+json.dumps(dict(updates=tick+1,seconds=round(time.perf_counter()-began,1),
                    pickups=len(context['milestones']),player=Native.Base.player(m))),flush=True)
            if stop_on_stall and len(context['milestones'])==4:
                x=Native.Base.player(m)['x']
                stall=stall+1 if x==lastx and x>=1500 else 0;lastx=x
                if stall>=80:break
            if checkpoints is not None and len(context['milestones'])==checkpoint_pickups and m.ram[2][0x68]==0 and Native.N.get(m,'GameEngineSubroutine')==8:
                for mark in(1536,1680,1729,1888,2080,2192,2368,2400,2440):
                    name=f'auto-{mark}'
                    if name not in checkpoints and Native.Base.player(m)['x']>=mark:checkpoints[name]=Native.N.fork(m)
            if checkpoint_x is not None and len(context['milestones'])==checkpoint_pickups and Native.Base.player(m)['x']>=checkpoint_x and m.ram[2][0xc0]==0:break
            if stop_at_pickups is not None and len(context['milestones'])>=stop_at_pickups:break
            if stop_on_native_head:
                early=lua.globals().KARNOV_FIFTH_CPU_STATE()['early']
                if early is not None and any(h['tile']==193 and h['native_pad']&128 for _,h in early['heads'].items()):break
            if context['exit']is not None:break
    def plain(value):
        if hasattr(value,'items'):
            values=dict(value.items())
            if values and all(type(k)is int for k in values):return[plain(values[i])for i in range(1,len(values)+1)]
            return{k:plain(v)for k,v in values.items()}
        return value
    report=dict(passed=context['exit']==0 and controller_error is None,stopped=context['exit']is not None,controller_error=controller_error,
        seconds=round(time.perf_counter()-began,2),actual_Main_NMI_updates=tick+1,
        opening=opening,receipt=context['receipt'],pickups=context['milestones'],
        terminal=Native.Base.player(m),source=dict(shot=m.ram[2][0x65],health=m.ram[2][0x68],
            cycle=m.ram[2][0x860],selected=m.ram[2][0x8e],owned=m.ram[2][0x8f],
            boots=m.ram[2][0xbd],bomb=m.ram[2][0xbb],scene=m.ram[2][0x5e]),
        fifth=plain(lua.globals().KARNOV_FIFTH_CPU_STATE()),terminal_pad=m.controller_pad,
        manual_helpers=plain(lua.globals().KARNOV_FIFTH_CPU_HELPERS()),
        boots_activation=plain(lua.globals().KARNOV_FIFTH_CPU_BOOTS()),
        actors=[Native.Base.actor(m,i)for i in range(6)],
        geometry=[dict(left=x,rows={y:m[Native.W.address(m.bundle,'Block_Buffer_1')+((x//256)%2)*208+((y-32)//16)*16+(x%256)//16]for y in range(112,224,16)})for x in range(max(0,Native.Base.player(m)['x']//16*16-64),Native.Base.player(m)['x']//16*16+193,16)],
        controller_SHA256=sha256(text.encode()).hexdigest(),ROM_SHA256=PIN,
        ROM_or_runtime_fixture_edits=0,new_helper_allocations=0,output_files=0,Mesen_run=False)
    return(report,m)if return_model else report


def serve_suffix_development(raw,limit,checkpoint_x=1536):
    models={};prefix,seed=run(raw,limit=limit,checkpoint_x=checkpoint_x,return_model=True,checkpoints=models)
    assert len(prefix['pickups'])==4 and'auto-1536'in models,prefix
    if prefix['source']['health']!=0 or prefix['terminal']['x']<checkpoint_x:
        seed=models[max(models,key=lambda key:int(key.split('-')[1]))]
    assert seed.ram[2][0x68]==0 and Native.N.get(seed,'GameEngineSubroutine')==8
    models['seed']=seed;rows=[]
    # Loopback IPC retains the genuine CPU model in this bounded process.
    # It creates no files, state dumps or native-gameplay-field writes.
    with Listener(('127.0.0.1',0),authkey=b'karnov-fifth-1113')as listener:
        print('KARNOV_FIFTH_MEMORY_READY '+json.dumps(dict(port=listener.address[1],prefix_Main=prefix['actual_Main_NMI_updates'],
            player=Native.Base.player(seed),actors=prefix['actors'],geometry=prefix['geometry'],genuine_checkpoints=list(models))),flush=True)
        while True:
            with listener.accept()as connection:
                command=connection.recv()
                if command['op']=='close':connection.send(dict(closed=True));break
                assert command['op']=='suffix'and command.get('from','seed')in models
                name=command.get('name','suffix');assert name in('one','two','three')
                report,model=run(raw,limit=min(command.get('frames',2500),3000),
                    input_model=Native.N.fork(models[command.get('from','seed')]),history=prefix['pickups'],return_model=True,checkpoints=models)
                report['genuine_checkpoints']=list(models)
                models[name]=model;rows.append(dict(name=name,passed=report['passed'],updates=report['actual_Main_NMI_updates'],terminal=report['terminal']))
                connection.send(report)
    return dict(genuine_prefix_Main=prefix['actual_Main_NMI_updates'],development_forks=rows,
        final_unbroken_replay_claim=False,runtime_field_grants_or_reseeds=0,output_files=0)


def interactive_development(raw,limit):
    # The saved model comes from the complete ordinary-controller prefix.
    # Only controller metadata is restored in new Lua VMs; no game field is
    # granted or changed in any clone. These branches are development proofs.
    prefix,seed=run(raw,limit=limit,stop_on_stall=True,return_model=True)
    assert len(prefix['pickups'])==4 and prefix['source']['health']==0
    models={'seed':seed};reports=[]
    print('KARNOV_FIFTH_PREFIX_READY '+json.dumps(prefix,separators=(',',':')),flush=True)
    for line in sys.stdin:
        command=json.loads(line)
        if command['op']=='close':break
        if command['op']=='suffix':
            name=command.get('name','suffix');source=command.get('from','seed')
            assert source in models and name!='seed'and len(models)<8
            report,model=run(raw,limit=min(command.get('frames',2200),3000),
                input_model=Native.N.fork(models[source]),history=prefix['pickups'],return_model=True)
            models[name]=model;reports.append(report)
        elif command['op']=='pad':
            name=command['name'];assert name in models and name!='seed';m=models[name]
            value=command['pad'];assert 0<=value<=255
            for tick in range(min(command.get('frames',1),1200)):
                m.controller_pad=value;Native.Frames.frame(m)
                if Native.N.get(m,'NumberofLives')!=2 or m.ram[2][0x68]&128:break
                if'world_x_at_least'in command and Native.Base.player(m)['x']>=command['world_x_at_least']:break
            report=dict(ordinary_pad=value,updates=tick+1,terminal=Native.Base.player(m),
                source_health=m.ram[2][0x68],actors=[Native.Base.actor(m,i)for i in range(6)])
        else:raise AssertionError('Only source suffix or ordinary pad input commands are accepted')
        print('KARNOV_FIFTH_DEVELOPMENT '+json.dumps(report,separators=(',',':')),flush=True)
    return dict(genuine_prefix_Main=prefix['actual_Main_NMI_updates'],development_branches=len(reports),
        final_unbroken_replay_claim=False,runtime_field_grants_or_reseeds=0,output_files=0)


def development(raw,limit):
    prefix,seed=run(raw,limit=limit,stop_on_stall=True,return_model=True)
    assert len(prefix['pickups'])==4 and prefix['source']['health']==0 and prefix['terminal']['lives']==2,prefix
    rows=[];parent=Native.N.NesMPU
    for name in('standing-fire','jump-right','existing-lift'):
        m=Native.N.fork(seed);births=[];minimum=255;path=[];target=1648
        class Probe(parent):
            def step(self):
                if self.pc==0xbffc and self.memory.rawtags[1]==192 and self.x<6:
                    a=Native.Base.actor(self.memory,self.x)
                    if a['flag']==1 and a['id']==37 and a['state']==65:
                        births.append(dict(slot=self.x,left=a['x'],center=a['x']+16,initial_top=a['y'],width=32,stage='1-2'))
                return parent.step(self)
        ride=True
        with patch.object(Native.N,'NesMPU',Probe):
            for tick in range(220):
                s=Native.Base.player(m);minimum=min(minimum,s['y'])
                if name=='standing-fire':pad=1|(64 if tick%12<6 else 0)
                elif name=='jump-right':pad=1|(128 if tick<36 else 0)|(64 if tick%12<6 else 0)
                else:
                    if tick<3:pad=40
                    elif ride:
                        pad=0
                        if s['y']<=96:ride=False;flight=tick
                    else:pad=1|(128 if tick-flight<36 else 0)|(64 if tick%12<6 else 0)
                m.controller_pad=pad;Native.Frames.frame(m)
                if tick%20==0:path.append(dict(tick=tick,pad=pad,**Native.Base.player(m)))
                if Native.Base.player(m)['x']>=target or Native.N.get(m,'NumberofLives')!=2 or m.ram[2][0x68]&128:break
        rows.append(dict(policy=name,updates=tick+1,minimum_native_Y=minimum,terminal=Native.Base.player(m),
            source_health=m.ram[2][0x68],actors=[Native.Base.actor(m,i)for i in range(6)],
            manual_births=births,path=path,passed=Native.Base.player(m)['x']>=target))
    return dict(genuine_prefix=prefix,source_prefix_derived_development_forks=rows,
        native_or_final_unbroken_replay_claim=False,runtime_field_grants_or_reseeds=0,
        output_files=0,Mesen_run=False)


def full_suffix_development(raw,limit):
    prefix,seed=run(raw,limit=limit,stop_on_stall=True,return_model=True)
    assert len(prefix['pickups'])==4 and prefix['source']['health']==0,prefix
    print('KARNOV_FIFTH_DERIVED_READY '+json.dumps(dict(
        updates=prefix['actual_Main_NMI_updates'],player=prefix['terminal'],actors=prefix['actors'])),flush=True)
    result=run(raw,limit=3000,input_model=Native.N.fork(seed),history=prefix['pickups'])
    return dict(genuine_prefix=prefix,source_prefix_derived_complete_suffix=result,
        final_unbroken_replay_claim=False,runtime_field_grants_or_reseeds=0,output_files=0)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--limit',type=int,default=1000)
    p.add_argument('--census',action='store_true');p.add_argument('--develop',action='store_true');p.add_argument('--interactive-develop',action='store_true');p.add_argument('--develop-suffix',action='store_true')
    p.add_argument('--serve-suffix',action='store_true');p.add_argument('--checkpoint-x',type=int,default=1536);p.add_argument('--client-port',type=int);p.add_argument('--command-json')
    p.add_argument('--require-pass',action='store_true',help='Fail the source gate unless the complete unbroken route passes.')
    args=p.parse_args()
    if args.client_port:
        with Client(('127.0.0.1',args.client_port),authkey=b'karnov-fifth-1113')as connection:
            connection.send(json.loads(args.command_json));print(json.dumps(connection.recv(),separators=(',',':')),flush=True)
        raise SystemExit(0)
    raw=candidate()
    result=census(raw)if args.census else serve_suffix_development(raw,args.limit,args.checkpoint_x)if args.serve_suffix else full_suffix_development(raw,args.limit)if args.develop_suffix else interactive_development(raw,args.limit)if args.interactive_develop else development(raw,args.limit)if args.develop else run(raw,limit=args.limit)
    print(json.dumps(result,separators=(',',':')),flush=True)
    if args.require_pass:assert result.get('passed')is True,'Complete stock fifth-item/Ladder route did not pass'
