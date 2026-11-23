"""Arthur cold verifier and exact archived-carrier conflict A/B; stdout only.

The diagnostic image exists only in memory and is NEVER an install recipe:
its three replaced pages belong to current DK Jr. Root alone may --run the
read-only controller on the actual Downloads ROM, using the shared slot.
"""
import argparse
from collections import Counter, deque
import json
from pathlib import Path
from unittest.mock import patch
import zipfile

import run_arthur_mushroom_1123 as A
import run_dkjr_flower_draw_native_1123 as DK

PIN='d1a40df1a70768da51823f93e050141281603f09497d7c2193db4fa088db62b5'
LUA='c780d75a9e50b494d3b37663dcea5bf2ae16ef428c98802df319ccbefee5188a'
H,R,W,N,Stock=A.H,A.R,A.W,A.N,A.Stock
ARCHIVE=R/'build/_recovery/legacy-sources-2026-10-31.zip'
OBJECTS={
 'canonical':('c55591e05426204d47556d21554eeaf2b4cd01557e3442dadbe1f8cac3faefc8',2326),
 'emitter':('ecc8e11206a72245ab852dae2ff5577dd94daf67c88caa3b31bc4df6f32152e6',550),
 'atlas':('6f45c6b15a71ad82db1cb8efe21cd5dc26e19cc17312ca94d83ca98a114e8ce2',13312),
 'tail_census':('bcd0ba3b48ed64ecebc817b600aca5c3b6dc192c1d7c5c312bc2f483607831a6',215630),
}


def controller(raw):
    assert H(raw)==PIN
    b=dict(W.Symbols.bundle(),raw=raw)
    names=('SelectedCharacter CrossoverMenuState CrossoverMenuIndex OperMode OperMode_Task '
           'GameEngineSubroutine NumberofLives CrossoverBehaviorVersion ArHostReady ArR_04F0 '
           'ArR_053A Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos '
           'FamilyMainCommit DisableScreenFlag Mirror_PPUMASK NmiDisable').split()
    ram={n:W.address(b,n)for n in names};hooks={}
    for name,sym,delta in [('Main','GameLoop',0),('CacheLoad','ArCacheLoad',0),
        ('CacheCount','ArCacheLoad',0xdab6-0xd9b8),('CacheReject','ArCacheLoad',0xdc1a-0xd9b8),
        ('HuMovement','HuMovement',0),('Movement','ArHostMovement',0),('Step','ArStep',0)]:
        pc,at=W.address(b,sym)+delta,W.location(b,sym)+delta
        assert (at-16)%8192==pc%8192
        hooks[name]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+12]))
    text='local C='+Stock.value(dict(sha=PIN,ram=ram,hooks=hooks))+'\n'+NATIVE
    Stock.LuaRuntime().compile(text)
    assert not any(t in text for t in ('emu.write','setState','saveState','loadState','io.open','takeScreenshot','dofile'))
    return text.encode()


def snapshot(raw):
    b=dict(W.Symbols.bundle(),raw=raw);old=N.NesMPU;hits=Counter();recent=deque(maxlen=8);bad=[]
    points={(((W.location(b,n)-16)//8192)|128,W.address(b,n)):n for n in
            ('ArCacheLoad','ArHostEnsure','ArHostMovement','ArStep')}
    class CPU(old):
        def step(self):
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1
            name=points.get((tag,self.pc))
            if name:hits[name]+=1
            if tag==198 and 0xd9b8<=self.pc<=0xdc1a:
                recent.append(dict(pc=self.pc,a=self.a,x=self.x,y=self.y,p=self.p,ppu_address=m.ppu_addr))
                if self.pc==0xdc1a:bad.append(list(recent))
            return super().step()
    # All menu/Start and full native scene constructors remain original code.
    # Skipping the controller's ROM pin is restricted to this diagnostic A/B.
    with patch.object(A,'controller',lambda image:b''),patch.object(N,'NesMPU',CPU):
        m=A.cold(raw)
        for _ in range(12):m.controller_pad=1;A.Engine.Frames.frame(m,whole_pass=True)
    names=('SelectedCharacter','ArHostReady','ArR_04F0','ArR_053A','GameEngineSubroutine','NumberofLives')
    return dict(state={n:N.get(m,n)for n in names},x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
        hits=dict(hits),rejects=bad,cookie=bytes(m.ram[2][0x1fe0:0x1ff0]).hex(),PPU_reads=m.ppu_reads)


def audit(raw):
    assert H(raw)==PIN
    old=DK.without_flower(raw);assert H(old)==A.PIN
    with zipfile.ZipFile(ARCHIVE)as z:
        objects={name:z.read('objects/'+pin)for name,(pin,size)in OBJECTS.items()}
    for name,data in objects.items():assert (H(data),len(data))==OBJECTS[name]
    cache=(objects['canonical']+objects['emitter']).ljust(3072,b'\0')
    grant=json.loads((R/'docs/qa/allocations/dkjr-private-resources-1102-v20.json').read_text())
    rows=[]
    for i in range(3):
        page=881+i;block=cache[i*1024:(i+1)*1024]
        assert H(block)==next(q['SHA256']for q in grant['physical_preimages']if q['page']==page)
        rows.append(dict(page=page,Arthur_and_DK_grant_preimage_SHA256=H(block),
                         current_SHA256=H(raw[1048592+page*1024:1048592+(page+1)*1024])))
    assert raw[1048592+868*1024:1048592+881*1024]==objects['atlas']
    at=1048592+881*1024
    before=snapshot(old);current=snapshot(raw)
    assert before==current,'DK Flower delta must not alter this Arthur cold trace'
    diagnosis=snapshot(raw[:at]+cache+raw[at+3072:])
    assert current['state']['ArHostReady']==0 and current['hits'].get('ArStep',0)==0
    assert current['rejects'][0][-2]['pc']==0xdac1 and current['rejects'][0][-1]['pc']==0xdc1a
    assert current['rejects'][0][-1]['a']==0xed
    assert diagnosis['state']['ArHostReady']==167 and diagnosis['state']['ArR_053A']==64
    assert diagnosis['hits'].get('ArStep',0)>0 and diagnosis['cookie']=='a7200001cf57fa39c8a769b1c239f669'
    tails=json.loads(objects['tail_census'])['candidate_unreferenced_art_tails']
    return dict(passed=True,scope='Source diagnostic confirms carrier collision; not a repair grant or pickup pass',
        current_SHA256=PIN,prior_SHA256=A.PIN,objects={k:v[0]for k,v in OBJECTS.items()},
        exact_grant_preimages=rows,prior27_and_current_identical=current,
        diagnostic_only_restored_three_owned_DK_pages=diagnosis,
        proposed_Arthur_only_tails=tails,finite_tail_bytes=sum(q['bytes']for q in tails),
        data_and_emitter_bytes=2876,outputs=0,ROM_written=False,native=False)


def native(raw):
    program=controller(raw);assert LUA and H(program)==LUA
    out=Stock.OUT;candidate,script=out/'candidate.nes',out/'controller.lua'
    before=script.read_bytes();guard=Stock.check(A.ROM)
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    assert set(out.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Stock.preserve_script(script,candidate,raw)as stage:
            stage(program);q=Stock.run(script,A.ROM,out/'capture',PIN,150)
        assert q['script_SHA256']==LUA and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and A.ROM.read_bytes()==raw
        assert Stock.check(A.ROM)==guard
    return q


NATIVE=r'''
assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact Arthur cold nightly')
local input,age,main,active,counts,events,readyWrites={},0,0,nil,{},{},{}
local menu,pulseAge=CPU_CONTROLLER_OPENING and 'play' or 'title',0
local function r(n)return emu.read(assert(C.ram[n],n),emu.memType.nesDebug)end
local function state()
 local q={};for n,a in pairs(C.ram)do q[n]=emu.read(a,emu.memType.nesDebug)end
 q.x=r('Player_X_Position')+256*r('Player_PageLoc');return q
end
local function json(v)
 if type(v)=='string'then return string.format('%q',v)end
 if type(v)~='table'then return tostring(v)end
 local a={};if #v>0 then for _,z in ipairs(v)do a[#a+1]=json(z)end;return'['..table.concat(a,',')..']'end
 for k,z in pairs(v)do a[#a+1]=string.format('%q',tostring(k))..':'..json(z)end
 table.sort(a);return'{'..table.concat(a,',')..'}'
end
local done=false
local function finish(ok,reason)
 if done then return end;done=true
 local cookie={};for i=0,15 do cookie[#cookie+1]=emu.read(2*8192+0x1fe0+i,emu.memType.nesWorkRam)end
 print('SMB_NATIVE_RECEIPT '..json{passed=ok,reason=reason,ROM_SHA256=C.sha,frames=age,Main=main,
  actual_entries=events,counts=counts,ready_writes=readyWrites,cookie=cookie,terminal=state(),
  controller_only=true,game_state_writes=false,files=0,images=0})
 emu.stop(ok and 0 or 1)
end
for name,h in pairs(C.hooks)do
 emu.addMemoryCallback(function()
  local m=emu.convertAddress(h.pc)
  if not m or m.memType~=emu.memType.nesPrgRom or m.address~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual cold hook bytes '..name)end
  if name=='Main'then main=main+1;return end
  if r('SelectedCharacter')~=32 then return end
  counts[name]=(counts[name]or 0)+1
  if name~='Step'and name~='Movement'and name~='HuMovement'and #events<12 then
   local c=emu.getState();events[#events+1]={entry=name,pc=h.pc,physical=h.offset,a=c['cpu.a'],y=c['cpu.y'],player=state()}
  end
 end,emu.callbackType.exec,h.pc)
end
emu.addMemoryCallback(function(a,v)
 if r('SelectedCharacter')==32 and #readyWrites<12 then
  local c=emu.getState();readyWrites[#readyWrites+1]={value=v,pc=c['cpu.pc'],frame=age}
 end
end,emu.callbackType.write,C.ram.ArHostReady)
local function pulse(key)
 input=pulseAge<5 and {[key]=true}or{};pulseAge=pulseAge+1
 if pulseAge>=14 then pulseAge=0;return true end
end
emu.addEventCallback(function()emu.setInput(input,0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;age=age+1
 if age>=2400 then return finish(false,'Bounded cold menu/scene entry')end
 if menu=='title'then
  if age<70 then input={};return end
  if r('CrossoverMenuState')~=2 then pulse('start');return end
  menu='menu';pulseAge=0
 end
 if menu=='menu'then
  local i=r('CrossoverMenuIndex');if i~=31 then pulse(i<24 and 'up'or'left');return end
  assert(r('SelectedCharacter')==32,'Arthur selected by actual menu')
  menu='start';pulseAge=0
 end
 if menu=='start'then
  if r('OperMode')~=1 then pulse('start');return end
  menu='play';input={}
 end
 if r('OperMode')~=1 or r('OperMode_Task')~=3 or r('GameEngineSubroutine')~=8 then input={};return end
 assert(r('SelectedCharacter')==32 and r('CrossoverBehaviorVersion')==0 and r('NumberofLives')==2,'Original Easy Arthur start')
 active=active or main
 input={right=true}
 if main-active>=8 then
  local ok=r('ArHostReady')==167 and(counts.Movement or 0)>0 and(counts.Step or 0)>0
  finish(ok,ok and'Actual cache and source movement active'or'Arthur cache rejected or own movement unavailable')
 end
end,emu.eventType.endFrame)
'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group();g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true')
    args=p.parse_args();raw=A.ROM.read_bytes();assert H(raw)==PIN
    if args.run:q=native(raw)
    else:
        def deny(*a,**k):raise AssertionError('Cold source verifier attempted output/emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            q=audit(raw)if args.source else dict(passed=True,ROM_sha256=PIN,controller_SHA256=H(controller(raw)),outputs=0)
    q['controller_SHA256']=H(controller(raw))
    print('ARTHUR_COLD '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
