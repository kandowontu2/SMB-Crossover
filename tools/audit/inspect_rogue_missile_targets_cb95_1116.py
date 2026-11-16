"""One live post-MF target/cache snapshot; exact qualified cb95 missile inputs."""
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_rogue_missile_cb95_1116 as F
import explore_rogue_natural_bomb_cb95_1116 as Reader
from check_ff_stdout_controller_source_1110 import LuaRuntime

J,W,N,Frames,H=F.J,F.W,F.N,F.Frames,F.H


def once(s,a,z):assert s.count(a)==1,(a,s.count(a));return s.replace(a,z,1)


def controller(raw):
    old=F.controller(raw,'missile');b=J.bindings(raw)['bundle'];text=old;edits=[]
    def edit(a,z):
        nonlocal text
        text=once(text,a,z);edits.append((a,z))
    extra=('Enemy_Y_HighPos','Enemy_BoundBoxCtrl','MmEnemyHealthLo','MmEnemyHealthHi','MmEnemyFlash','ScreenRight_PageLoc')
    line=old.split('\n',1)[0];definitions=['C.ram['+F.Attack.J.Frozen.lua(n)+']='+str(W.address(b,n))for n in extra]
    at=W.location(b,'BoundBoxCtrlData');definitions.append('C.target_bbox='+F.Attack.J.Frozen.lua(list(raw[at:at+13*4])))
    edit(line,line+'\n'+'\n'.join(definitions))
    edit('local function finish(reason)','local target_context\nlocal function finish(reason)')
    edit('Mesen_images=0}', 'Mesen_images=0,target_context=target_context}')
    observer='''local function inspectTargets()
 local c=context();local q={player=state(),camera=c.camera,area=r('AreaPointer'),left_page=r('ScreenLeft_PageLoc'),right_page=r('ScreenRight_PageLoc'),actors={},cache={}}
 q.player_native_box={};for k=0,3 do q.player_native_box[#q.player_native_box+1]=r('BoundingBox_UL_Corner',k)end
 q.current_right_missile={x=pos('RdX','RdRoomHi')+8,y=r('RdY')-6,radius=2}
 for i=0,5 do local a=actor(i);if a.flag>0 then
  a.high=r('Enemy_Y_HighPos',i);a.boxctrl=r('Enemy_BoundBoxCtrl',i);a.HP={r('MmEnemyHealthLo',i),r('MmEnemyHealthHi',i)};a.hurt=r('MmEnemyFlash',i)
  a.native_box={};for k=0,3 do a.native_box[#a.native_box+1]=r('BoundingBox_UL_Corner',(i+1)*4+k)end
  if a.boxctrl<13 then local o=a.boxctrl*4;a.source_target_box={a.x+C.target_bbox[o+1],a.y+C.target_bbox[o+2],a.x+C.target_bbox[o+3],a.y+C.target_bbox[o+4]}end
  q.actors[#q.actors+1]=a
 end end
 for y=112,208,16 do local row={y=y,tiles={}};for x=1200,1376,16 do row.tiles[#row.tiles+1]=c.block(x,y)end;q.cache[#q.cache+1]=row end
 q.cache_world_x_begin=1200;q.cache_world_x_end=1376;q.cache_step=16
 return q
end
'''
    edit('local function attackDrive()',observer+'\nlocal function attackDrive()\n if not target_context then target_context=inspectTargets()end')
    restored=text
    for a,z in reversed(edits):restored=once(restored,z,a)
    assert restored==old;LuaRuntime().compile(text)
    assert not any(t in text for t in('emu.write','emu.setState','takeScreenshot','io.open','dofile','saveState','loadState'))
    return text


def run(raw,limit=3000,text=None):
    text=controller(raw)if text is None else text
    m=J.cold(raw);lua=LuaRuntime(unpack_returned_tuples=True)
    callbacks={0:defaultdict(list),1:defaultdict(list)};events=defaultdict(list);ctx=dict(cpu=None,pc=0,status=None,receipt=None)
    api=lua.table();api.memType=lua.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2))
    api.callbackType=lua.table_from(dict(exec=0,write=1));api.eventType=lua.table_from(dict(inputPolled=0,endFrame=1))
    def read(at,kind=0):
        if kind==1:return m.ram[at//8192][at%8192]
        if kind==2:return raw[16+at]
        assert kind==0;return m[at]
    def mapped(pc):
        if pc<0x8000:return None
        tag=m.rawtags[(pc-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(pc&8191)))
    def state():
        c=ctx['cpu'];d={f'cpu.{k}':getattr(c,k)if c else 0 for k in('pc','sp','a','x','y','p')}
        d['cpu.pc']=ctx['pc'];d['cpu.ps']=d['cpu.p'];return lua.table_from(d)
    def memory(fn,kind,lo,hi=None):
        assert kind in(0,1)
        for at in range(lo,(hi if hi is not None else lo)+1):callbacks[kind][at].append(fn)
    def pad(p,port):
        assert port==0;m.controller_pad=sum(v for n,v in(('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))if p[n])
    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):ctx['receipt']=json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '))
    api.read=read;api.convertAddress=mapped;api.getState=state;api.setInput=pad;api.addMemoryCallback=memory
    api.addEventCallback=lambda fn,kind:events[kind].append(fn);api.stop=lambda status:ctx.update(status=status)
    lua.globals().emu=api;lua.globals().print=emit;lua.globals().CPU_CONTROLLER_OPENING=True;lua.execute(text)
    registration=dict(exec_addresses=len(callbacks[0]),write_addresses=len(callbacks[1]),events={k:len(v)for k,v in events.items()})
    base=N.NesMPU;old_write=type(m).__setitem__
    class CPU(base):
        def step(self):
            ctx.update(cpu=self,pc=self.pc)
            for fn in tuple(callbacks[0].get(self.pc,())):fn()
            return super().step()
    def write(bus,at,value):
        if bus is m and isinstance(at,int):
            for fn in tuple(callbacks[1].get(at,())):fn(at,value)
        return old_write(bus,at,value)
    with patch.object(N,'NesMPU',CPU),patch.object(type(m),'__setitem__',write):
        for tick in range(limit):
            for fn in tuple(events[0]):fn()
            Frames.frame(m,whole_pass=True)
            for fn in tuple(events[1]):fn()
            if ctx['status']is not None:break
            if tick%500==499:print('PROGRESS '+json.dumps(dict(source_passes=tick+1,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'))),flush=True)
    q=ctx['receipt']or{}
    result=dict(passed=ctx['status']==0 and q.get('passed')is True,owning_SHA256=J.PIN,controller_SHA256=H(text.encode()),
        factory_SHA256=H(Path(__file__).read_bytes()),executed_registration=registration,source_passes=tick+1,receipt=q,
        receipt_inner_SHA256=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode()),actual_owning_CPU=True,outputs=0,native=False)
    result['receipt_SHA256']=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--limit',type=int,default=3000);a=p.parse_args();assert 2000<=a.limit<=4500
    raw,provenance=Reader.load_current()
    def deny(*a,**kw):raise AssertionError('Read-only missile target inspection attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.limit)
    print('RESULT '+json.dumps(dict(input=provenance,result=q),separators=(',',':')),flush=True)
