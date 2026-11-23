"""Ordinary-input offset suffixes cloned from a genuinely played Prince cap.

No output files or emulator. Clones preserve the complete reached game,
actor, terrain, peripheral and resource state; only normal input differs.
These are linked checkpoint diagnostics, never natural pickup passes.
"""
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

import probe_prince_hidden_life_current_1123 as P

H,W,N,Engine=P.H,P.W,P.N,P.Engine
PREFIX_SHA='0a9900ba84aeb3be5ed255e0d3623210635cd70dcc8394ce7c3ea085b7d1ebd3'
CASES=(
    dict(name='baseline',pre=0,pre_controls=0,press=128,right_delay=0),
    dict(name='careful-Right-actual-idle-A',pre=65,pre_controls=1,press=129,right_delay=0,settle=True,donor_edge=True),
    dict(name='two-careful-Right-steps',pre=65,pre_controls=1,press=129,right_delay=0,settle=True,steps=2,donor_edge=True),
)
PRIOR_CASES={
    'prefix':'b6b6b79d61665a7d5189bef9d744152ba64031120ba6e1379e23038daeb0384b',
    'baseline':'e5a5ec189ac239d63d6f25f6f7b47e6a9bf7009cda877f452c50f3f7e72fdf9e',
    'A-plus-Right':'371f1ad66354569badf8229f5216c428a9cb32fcc39f37ff5d03f367c87a1486',
    'Right-one-control-early':'250c186f7af1e5ee64db16fa3604b8e3cdbc0a53cfb96ff7969c5405db3d3092',
    'Right-one-control-late':'f34ff6931e35f011ce857d61d2cbfb6f2bdf5ad595b0dde540125bc914ef4e28',
    'careful-step-SMB-foot-proxy-rejection':'49bfee5461b8d1d30a49f06b6bd6fe74934601793552727db1591c14b399d76c',
    'scope':'Ordinary linked checkpoint controls; none produced a1-UP. The last is an observer stop at actual idle943/112, not a donor admission failure.',
}
RESULTS={
    'ROM_SHA256':P.CURRENT,
    'prefix_controller':'0b0db1e06bb1435222f0e8492a485ca18eb4f4cb9f53ca713f36f1788a52908a',
    'prefix_receipt':'b6b6b79d61665a7d5189bef9d744152ba64031120ba6e1379e23038daeb0384b',
    'prefix_completed_Main_and_Prince':2019,
    'offset_controller':'380b7ef43b2a2c94744ea1bf309b6a0b09f9acfe72141a869ca4c32cb7aa343e',
    'offset_receipt':'58d7cdb931b9c8895dba2eeb79c00e0b46c6e62d3fb2d5913b8089583ff1e48b',
    'offset_completed_Main_and_Prince':168,
    'actual_idle_and_launch':[943,112],'launch_x_delta':6,
    'head_query':[1027,131,128,96],'head_native_speeds':[5,0],
    'native_foot_samples':[0,0],'original_feet_material':0,
    'health_at_launch_and_head':4,'terminal':[1052,176,3,2],
    'oneup_born':False,'native_head_writer_reached':False,
    'second_step_receipt':'ed9e1422e3aaf4b47cc28ceaf322ad3997efc338e6ca6c454b00b8c1ec5cb849',
    'second_step_idle':[973,176,4,2],
    'scope':'Ordinary inputs from an actually played cap; source admits the edge-frame jump despite empty feet; no physical/native or natural pickup pass claim',
}

BODY=r'''
local updates,controls,entries,returns,polls=0,0,0,0,0
local buttons,pendingMain,pendingWorker={},nil,nil
local stopped=false
local dynamic={}
local S={case=C.case.name,phase='pre',states={},heads={},admissions={},pre_start=0}
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function src(a)return emu.read(2*8192+a,emu.memType.nesWorkRam)end
local function r(n,i)return read(C.ram[n]+(i or 0))end
local function tile(x,y)return read(C.ram.Block_Buffer_1+((x//256)&1)*208+((y-32)//16)*16+((x&255)//16))end
local function state()
 local x=r('Player_X_Position')+256*r('Player_PageLoc');local y=r('Player_Y_Position')
 return{Main=returns,updates=updates,controls=controls,x=x,y=y,action=src(0x616),pose=src(0x617),mode=src(0x618),lock=src(0x6c0),facing=src(0x615),phase=src(0xa6),
  sourceX=src(0x60f)+256*src(0x610),sourceY=src(0x611),sourcePad=src(0x40a),foot=src(0x84)+256*src(0x85),hp=src(0x6cf),lives=r('NumberofLives'),
  ground=r('Player_State'),left=tile(x+2,144),right=tile(x+13,144),speed=r('Player_Y_Speed'),nativeInput=r('SavedJoypadBits')}
end
local function json(v)
 if v==nil then return'null'elseif type(v)=='string'then return string.format('%q',v)elseif type(v)~='table'then return tostring(v)end
 local a={};if#v>0 then for i,x in ipairs(v)do a[i]=json(x)end;return'['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
end
local function finish(why)
 if stopped then return end;stopped=true;buttons={}
 S.terminal=state();S.reason=why;S.pendingMain=pendingMain~=nil;S.pendingWorker=pendingWorker~=nil
 print('SMB_NATIVE_RECEIPT '..json({passed=false,reason=why,diagnostic=S,Main_entries=entries,Main_returns=returns,gameplay_seeds=0,source_checkpoint=true,outputs=0}))
 emu.stop(1)
end
local function guarded(fn)return function(...)if stopped then return end;local ok,e=pcall(fn,...);if not ok then finish(tostring(e))end end end
local function hook(n,fn)
 local h=C.hooks[n];emu.addMemoryCallback(guarded(function()
  local a=emu.convertAddress(h.pc);if not a or a.memType~=h.kind or a.address~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact reached '..n)end;fn(emu.getState())
 end),emu.callbackType.exec,h.pc)
end
local function mapping(pc)local a=emu.convertAddress(pc);return a and(a.memType..':'..a.address)or'cpu:'..pc end
local function returning(cpu,fn)
 local sp=cpu['cpu.sp'];local pc=(read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535
 local q={sp=(sp+2)&255,map=mapping(pc),fn=fn}
 if not dynamic[pc]then
  dynamic[pc]={};emu.addMemoryCallback(guarded(function()
   local cpu=emu.getState();local list=dynamic[pc]
   for i=#list,1,-1 do local t=list[i];if t.sp==cpu['cpu.sp']and t.map==mapping(pc)then table.remove(list,i);t.fn(cpu)end end
  end),emu.callbackType.exec,pc)
 end
 dynamic[pc][#dynamic[pc]+1]=q
end
local function setpad(p)buttons={right=p&1~=0,left=p&2~=0,up=p&8~=0,b=p&64~=0,a=p&128~=0}end
local function supported(s)return s.y>=111 and s.y<=114 and(s.left==16 or s.left==17 or s.right==16 or s.right==17)end
local function idle(s)return s.action==0 and s.mode==0 and s.pose==15 and s.lock==0 end
local function drive()
 local s=state();assert(r('SelectedCharacter')==38 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Same ordinary Prince')
 assert(s.hp>0 and s.lives==2,'Alive checkpoint continuation')
 if #S.states<36 and(S.lastKey~=s.x..':'..s.y..':'..s.action..':'..s.pose..':'..s.mode)then S.states[#S.states+1]=s;S.lastKey=s.x..':'..s.y..':'..s.action..':'..s.pose..':'..s.mode end
 for i=0,5 do
  if r('Enemy_Flag',i)==1 and r('Enemy_ID',i)==46 and r('PowerUpType',i)==3 then S.born=S.born or{state=s,slot=i,x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i),actorState=r('Enemy_State',i)}end
 end
 if S.born then finish('Real authored 1-UP birth observed; acquisition not yet claimed');return end
 if S.phase=='pre'then
  setpad(C.case.pre)
  if controls-S.pre_start>=C.case.pre_controls then
   S.pre_end=s
   if C.case.settle then S.phase='settle';setpad(0)else S.phase='press';S.request=s;setpad(C.case.press)end
  end
 elseif S.phase=='settle'then
  setpad(0)
  if idle(s)then
   S.settled=s;S.step_settles=S.step_settles or{};S.step_settles[#S.step_settles+1]=s
   S.native_foot_proxy=supported(s)
   if not supported(s)and not(C.case.donor_edge and s.y==112 and s.foot==144)then finish('Careful step did not settle at cap height');return end
   if #S.step_settles<(C.case.steps or 1)then S.phase='pre';S.pre_start=controls;setpad(C.case.pre)
   else S.phase='press';S.request=s;setpad(C.case.press)end
  end
 elseif S.phase=='press'then
  setpad(C.case.press)
  if s.action==3 or s.action==4 then S.launch=s;S.phase='flight';S.launch_control=controls;setpad(C.case.right_delay>0 and 128 or 1)end
  if not S.launch and s.y>140 then finish('Prelaunch input left the cap without admission');return end
 elseif S.phase=='flight'then
  setpad(controls-S.launch_control<C.case.right_delay and 128 or 1)
  if s.x>=1040 then setpad(0)end
  if updates>70 and idle(s)and s.y>=174 then finish('Landed after ordinary offset suffix');return end
 end
 if updates>=185 then finish('Bounded ordinary offset suffix')end
end
hook('Main',function(cpu)
 assert(not pendingMain);entries=entries+1;local sp=cpu['cpu.sp'];local pc=read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1
 assert(pc==C.hooks.Return0.pc or pc==C.hooks.Return1.pc);pendingMain={pc=pc,sp=(sp+2)&255}
end)
for i=0,1 do local n='Return'..i;hook(n,function(cpu)
 assert(pendingMain and pendingMain.pc==cpu['cpu.pc']and pendingMain.sp==cpu['cpu.sp']);pendingMain=nil;returns=returns+1;drive()
end)end
hook('Worker',function(cpu)
 assert(not pendingWorker);pendingWorker=true
 returning(cpu,function()pendingWorker=nil;updates=updates+1 end)
end)
hook('Control',function()controls=controls+1;S.first_control=S.first_control or state()end)
hook('Head',function(cpu)
 local s=state();if s.x<976 or s.x>1056 or cpu['cpu.y']~=C.headAdder or #S.heads>=64 then return end
 local q={state=s,headX=s.x+8,headY=(s.y+1)&255};S.heads[#S.heads+1]=q
 returning(cpu,function()q.tile=r('R3');q.row=(r('R2')+32)&255 end)
end)
hook('NativeHead',function(cpu)S.native_head=S.native_head or{state=state(),tile=cpu['cpu.a']}end)
hook('Feet',function(cpu)
 S.feet=S.feet or{};if#S.feet<16 then S.feet[#S.feet+1]={state=state(),material=cpu['cpu.a'],pc=cpu['cpu.pc'],sp=cpu['cpu.sp']}end
end)
emu.addEventCallback(guarded(function()polls=polls+1;emu.setInput(buttons,0)end),emu.eventType.inputPolled)
'''


def config(raw,case):
    P.authenticate(raw);b=dict(W.Symbols.bundle(),raw=raw);parts=P.Packet.extract(raw)[1]
    names='Player_X_Position Player_PageLoc Player_Y_Position Player_State Player_Y_Speed SavedJoypadBits Block_Buffer_1 SelectedCharacter CheatInvincible CheatStartLevel NumberofLives Enemy_Flag Enemy_ID PowerUpType Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_State R2 R3'.split()
    cfg=dict(case=case,ram={n:W.address(b,n)for n in names},hooks={},headAdder=raw[W.location(b,'BlockBufferAdderData')+6])
    def native(n,symbol,delta=0):
        pc,at=W.address(b,symbol)+delta,W.location(b,symbol)+delta
        cfg['hooks'][n]=dict(pc=pc,offset=at-16,kind=2,bytes=list(raw[at:at+8]))
    native('Main','GameLoop');native('Return0','IdleLoop',12);native('Return1','IdleLoop',30)
    native('Head','BlockBufferColli_Head');native('NativeHead','NativeRarePlayerHeadCollisionCore')
    for n,pc in(('Worker',0xb36e),('Control',0xabde),('Feet',0xad33)):
        cfg['hooks'][n]=dict(pc=pc,offset=3*8192+(pc&8191),kind=1,bytes=list(parts[0][pc-0xa000:pc-0xa000+8]))
    return cfg


def main():
    assert H(Path(P.__file__).read_bytes())==PREFIX_SHA
    raw=P.G.ROM.read_bytes();P.authenticate(raw);text=P.controller(raw,'cap')
    old="stockPhase('cap-fresh-A',128)"
    text=P.G.First.once(text,old,"final=s;finish(false,'Reached genuine idle cap for ordinary offset suffixes');return true")
    for case in CASES:P.Base.LuaRuntime().compile('local C='+P.G.Stock.value(config(raw,case))+'\n'+BODY)
    captured=[]
    def cold(image):m=P.cold(image);captured.append(m);return m
    def deny(*a,**k):raise AssertionError('Offset source search attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        with patch.object(Engine.J,'cold',cold),patch.object(Engine.J,'PIN',H(raw)):prefix=Engine.run(raw,2400,text=text)
        r=prefix['receipt'];assert r['reason']=='Reached genuine idle cap for ordinary offset suffixes'
        cap=r['natural_stock']['cap_ready'];assert(cap['x'],cap['y'],cap['action'],cap['hp'],cap['lives'])==(937,112,0,4,2)
        print('PRINCE_OFFSET_PREFIX '+json.dumps(dict(controller=H(text.encode()),receipt=prefix['receipt_SHA256'],passes=prefix['source_passes'],cap=cap),separators=(',',':')),flush=True)
        assert len(captured)==1;model=captured.pop();results=[]
        for case in CASES:
            program='local C='+P.G.Stock.value(config(raw,case))+'\n'+BODY;P.Base.LuaRuntime().compile(program)
            fork=N.fork(model)
            with patch.object(Engine.J,'cold',lambda image:fork),patch.object(Engine.J,'PIN',H(raw)):q=Engine.run(raw,220,text=program)
            result=q['receipt'].get('diagnostic',{});small={k:v for k,v in result.items()if k not in('states','heads','lastKey')}
            small['state_samples']=len(result.get('states',[]));small['heads']=[];seen=set()
            for head in result.get('heads',[]):
                s=head['state'];key=(head['headX'],head['headY'],head.get('row'),head.get('tile'),s['speed'])
                if key in seen:continue
                seen.add(key);small['heads'].append(head)
            row=dict(name=case['name'],controller=q['controller_SHA256'],receipt=q['receipt_SHA256'],passes=q['source_passes'],result=small);results.append(row)
            print('PRINCE_OFFSET_CASE '+json.dumps(row,separators=(',',':')),flush=True)
        print('PRINCE_OFFSET_SUMMARY '+json.dumps(dict(ROM=H(raw),prefix=prefix['receipt_SHA256'],cases=len(results),outputs=0,normal_input_only=True,linked_checkpoint=True,no_natural_pickup_pass_claim=True),separators=(',',':')),flush=True)


if __name__=='__main__':main()
