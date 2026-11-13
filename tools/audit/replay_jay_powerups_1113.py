"""Minimal controller-only Jay first-block negative or earned-pickup replay."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_jay_powerups_current_1113 as Current
from run_stdout_mesen_1110 import R, run


def controller(raw, *, expect='missing'):
    assert expect in ('missing', 'earned')
    if expect == 'missing':
        assert sha256(raw).hexdigest() == Current.PIN
    else:
        import compose_jay_head_bridge_1113 as Bridge
        assert sha256(raw).hexdigest() == Bridge.CANDIDATE_PIN
    template = r'''local sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'))
local expected='EXPECT_VALUE'
local frame,main,epoch,pad,opening=0,0,0,0,0
local game,done,pending,mainReturn=false,false,nil,nil
local phase,phaseEpoch='opening',0
local attempts,landings,air,minimum=0,0,false,255
local heads,births,collections,trace={},{},{},{}
local registered={}
local function r(a)return emu.read(a,emu.memType.nesDebug)end
local function state()
 return {x=r(0x75)+256*r(0x5c),y=r(0xbd),motion=r(0x1e),dy=r(0x8e),lives=r(0x75f),engine=r(0x0f),
  hp=r(0x5f30),maximum=r(0x5f31),tier=r(0x5f32),status=r(0x75b),frame=frame,main=main,epoch=epoch}
end
local function actor(i)
 return {slot=i,flag=r(0x10+i),id=r(0x17+i),kind=r(0x34+i),state=r(0x1f+i),
  x=r(0x76+i)+256*r(0x5d+i),y=r(0xbe+i),private=r(0x7d62+i),owner=r(0x7d6e+i)}
end
local function json(v)
 local t=type(v)
 if t=='string'then return '"'..v:gsub('[%z\1-\31\\"]',function(c)return string.format('\\u%04x',string.byte(c))end)..'"'end
 if t=='number'or t=='boolean'then return tostring(v)end
 assert(t=='table');local out={}
 if #v>0 then for _,x in ipairs(v)do out[#out+1]=json(x)end;return '['..table.concat(out,',')..']'end
 for k,x in pairs(v)do out[#out+1]=json(tostring(k))..':'..json(x)end
 table.sort(out);return '{'..table.concat(out,',')..'}'
end
local function finish(ok,why)
 if done then return end
 done=true;pad=0
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=sha,controller_only=true,expect=expected,
  terminal=state(),head_calls=heads,births=births,collections=collections,attempts=attempts,landings=landings,
  minimum_y=minimum,block=r(0x445),trace=trace}))
 emu.stop(ok and 0 or 1)
end
local function guard(name,fn)
 return function(...)
  if done then return end
  local ok,why=pcall(fn,...);if not ok then finish(false,name..' '..tostring(why))end
 end
end
local function mapped(pc)
 local q=emu.convertAddress(pc)
 return q and q.memType==emu.memType.nesPrgRom and q.address==126*8192+(pc&8191)
end
local function ret(c)
 local sp=c['cpu.sp']
 return r(256+((sp+1)&255))+256*r(256+((sp+2)&255))+1,(sp+2)&255
end
local function exec(pc,name,fn)emu.addMemoryCallback(guard(name,fn),emu.callbackType.exec,pc)end
local function phaseTo(nextPhase)phase,phaseEpoch=nextPhase,epoch end
local function drive()
 if not game then return end
 local s=state()
 assert(r(0x6002)==16 and r(0x730b)&96==32,'Jay identity')
 assert(r(0x764)==0 and r(0x761)==0 and r(0x7ffb)==0 and r(0x7ffc)==0,'1-1 cheats off')
 assert(s.lives==2 and s.engine~=11 and epoch<1400,'Alive bounded route')
 for bank=2,3 do
  local h={};for i=0x1fe0,0x1fef do h[#h+1]=string.format('%02x',emu.read(bank*8192+i,emu.memType.nesWorkRam))end
  assert(table.concat(h)=='a810200a8071b239e4a3bcb6a1eae213','Authenticated Jay cold header')
 end
 if opening<60 then
  pad=opening<4 and 0 or opening<36 and 1 or opening<52 and 129 or 1
  opening=opening+1;return
 elseif phase=='opening'then phaseTo('approach')end
 local item=nil;local near=false
 for i=0,5 do
  local a=actor(i)
  if a.flag~=0 then
   if a.id==46 then item=a;if #births==0 then births[1]={actor=a,player=s}end end
   if a.id<21 and a.state&32==0 and a.x>s.x and a.x-s.x<100 and math.abs(a.y-s.y)<30 then near=true end
  end
 end
 local shot=near and epoch%12<2 and 64 or 0
 if phase=='approach'and s.x>=332 and s.motion==0 then phaseTo('park')end
 if phase=='park'and epoch-phaseEpoch>=8 then phaseTo('jump')end
 if phase=='jump'then
  minimum=math.min(minimum,s.y)
  if s.motion==1 and not air then attempts=attempts+1;air=true end
  if s.motion==0 and air then landings=landings+1;air=false end
  if #trace<48 and(attempts<=1 or s.y==minimum)then trace[#trace+1]=s end
 end
 if #collections>0 and epoch-collections[1].epoch>=8 then
  assert(expected=='earned'and #heads>0 and #births>0,'Natural reveal and collection')
  assert(s.maximum==4 and s.hp==8 and s.status==0,'Current inherited heart grant')
  finish(true,'Jay revealed and collected the authored first pickup');return
 end
 if landings>=5 then
  assert(expected=='missing'and #heads==0 and #births==0 and #collections==0 and r(0x445)==0xc1,'Five blocked jumps preserve authored block')
  finish(true,'Reproduced original ceiling stop before native block reveal');return
 end
 if item then
  pad=(s.x<item.x-8 and 1 or s.x>item.x+4 and 2 or 0)+shot
  if s.motion==0 and item.state&128~=0 then pad=pad|128 end
 elseif phase=='approach'then pad=1+shot
 elseif phase=='park'then pad=shot
 else pad=((epoch-phaseEpoch)%64<18 and 128 or 0)+shot end
 epoch=epoch+1
end
local function pause(n)for _=1,n do coroutine.yield()end end
local function press(b)pad=b;pause(4);pad=0;pause(8)end
local function wait(fn)for _=1,1000 do if fn()then return end;coroutine.yield()end;error('Menu bound')end
local boot=coroutine.create(function()
 wait(function()return frame>=70 and r(0x6004)==1 and r(0x775)==0 end)
 press(16);wait(function()return r(0x7307)==2 and r(0x775)==0 end)
 press(4);for _=1,7 do press(1)end;press(32)
 assert(r(0x7309)==15 and r(0x6002)==16 and r(0x730b)&96==32,'Jay Select alternate')
 press(16);wait(function()return r(0x771)==1 and r(0x773)==3 and r(0x0f)==8 end)
 game=true;drive();while not done do coroutine.yield()end
end)
exec(0x82d9,'Main entry',function()
 if not mapped(0x82d9)then return end
 assert(not mainReturn,'Synchronous Main');local pc,sp=ret(emu.getState());mainReturn={pc,sp}
end)
for _,pc in ipairs({0x82be,0x82d0})do exec(pc,'Main return',function()
 if mainReturn and mapped(pc)and mainReturn[1]==pc and mainReturn[2]==emu.getState()['cpu.sp']then mainReturn=nil;main=main+1;drive()end
end)end
exec(0x9ef5,'Head effect',function()
 if game and mapped(0x9ef5)then heads[#heads+1]={tile=emu.getState()['cpu.a'],player=state()}end
end)
exec(0x9b28,'Collector',function()
 if not game or not mapped(0x9b28)then return end
 local c=emu.getState();local pc,sp=ret(c);pending={pc=pc,sp=sp,item=actor(c['cpu.x']),player=state(),sound=0}
 if not registered[pc]then
  registered[pc]=true
  exec(pc,'Collector return',function()
   local c=emu.getState();local q=pending
   if not q or q.pc~=pc or q.sp~=c['cpu.sp']then return end
   pending=nil;assert(r(0x10+q.item.slot)==0 and q.sound>0,'Native erasure and sound')
   q.epoch=epoch;q.after=state();collections[#collections+1]=q
  end)
 end
end)
emu.addMemoryCallback(guard('Pickup sound',function(_,value)if pending and value==32 then pending.sound=pending.sound+1 end end),emu.callbackType.write,0x104)
emu.addEventCallback(guard('Input poll',function()
 emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,up=pad&8~=0,start=pad&16~=0,select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard('Physical frame',function()
 frame=frame+1;assert(frame<7000,'Physical bound');local ok,why=coroutine.resume(boot);assert(ok,why)
end),emu.eventType.endFrame)
'''
    result = template.replace('EXPECT_VALUE', expect)
    if expect == 'missing':
        return result
    result = result.replace(Current.COOKIE.hex(),Bridge.NEW_COOKIE.hex())
    state_tail = 'status=r(0x75b),frame=frame,main=main,epoch=epoch}'
    assert result.count(state_tail) == 1
    result = result.replace(state_tail,'status=r(0x75b),frame=frame,main=main,epoch=epoch,\n  source_flags=emu.read(2*8192+0x12,emu.memType.nesWorkRam),source_control=emu.read(2*8192+0x13,emu.memType.nesWorkRam)}')
    before = ''' if item then
  pad=(s.x<item.x-8 and 1 or s.x>item.x+4 and 2 or 0)+shot
  if s.motion==0 and item.state&128~=0 then pad=pad|128 end
 elseif phase=='approach'then pad=1+shot
 elseif phase=='park'then pad=shot
 else pad=((epoch-phaseEpoch)%64<18 and 128 or 0)+shot end'''
    after = ''' if item and(phase=='approach'or phase=='park'or phase=='jump')then phaseTo('pipe-approach')end
 if item and phase=='pipe-approach'then
  pad=1+shot
  if s.x>=400 and s.motion==0 then phaseTo('pipe-jump');pad=pad|128 end
 elseif item and phase=='pipe-jump'then
  pad=(s.x<426 and 1 or 2)+shot
  if epoch-phaseEpoch<12 then pad=pad|128 end
  if s.motion==0 and s.y==144 then phaseTo('pipe-turn');pad=0 end
 elseif item and phase=='pipe-turn'then
  pad=shot
  if epoch-phaseEpoch>=1 and s.source_flags&4==0 and s.source_control&0x38==0 then
   if s.source_flags&2~=0 then phaseTo('collect-jump');pad=130+shot
   else phaseTo('pipe-face');pad=2+shot end
  end
 elseif item and phase=='pipe-face'then
  pad=2+shot
  if epoch-phaseEpoch>=4 and s.source_flags&4==0 and s.source_control&0x38==0 then phaseTo('pipe-runup')end
 elseif item and phase=='pipe-runup'then
  pad=2+shot
  if epoch-phaseEpoch>=1 and s.source_flags&4==0 then phaseTo('collect-jump');pad=pad|128 end
 elseif item and phase=='collect-jump'then
  pad=(s.x>item.x and 2 or 0)+shot
  if epoch-phaseEpoch<18 then pad=pad|128 end
 elseif phase=='approach'then pad=1+shot
 elseif phase=='park'then pad=shot
 elseif phase=='jump'then pad=((epoch-phaseEpoch)%64<18 and 128 or 0)+shot
 else pad=0 end'''
    assert result.count(before) == 1
    result = result.replace(before,after)
    old = "pending=nil;assert(r(0x10+q.item.slot)==0 and q.sound>0,'Native erasure and sound')"
    new = old+"\n   assert(q.item.state==128 and q.item.private==129 and q.item.owner==16,'Mature authored Jay heart')\n   assert(q.player.hp==6 and q.player.maximum==3 and state().hp==8 and state().maximum==4,'Original inherited health grant')"
    assert result.count(old) == 1
    return result.replace(old,new)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=Current.ROM)
    parser.add_argument('--output', type=Path, default=R/'build/jay-powerups-native-1113')
    parser.add_argument('--expect', choices=('missing', 'earned'), default='missing')
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    raw = args.rom.read_bytes()
    text = controller(raw, expect=args.expect)
    if args.check_only:
        import check_ff_stdout_controller_source_1110 as Mock
        assert Mock.LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
        print(json.dumps(dict(compiles=True, ROM_SHA256=sha256(raw).hexdigest(), output_files=0,
                              script_SHA256=sha256(text.encode()).hexdigest())), flush=True)
        return
    args.output.mkdir(exist_ok=True)
    script = args.output/'controller.lua'
    script.write_text(text, encoding='utf-8', newline='\n')
    if args.prepare_only:
        print(json.dumps(dict(prepared=True, script=str(script), script_SHA256=sha256(script.read_bytes()).hexdigest(), output_files=1)), flush=True)
        return
    result = run(script, args.rom, args.output/'capture', sha256(raw).hexdigest(), 180)
    print(json.dumps({key: result[key] for key in ('passed', 'receipt_SHA256', 'script_SHA256', 'receipt')}), flush=True)
    assert result['passed']


if __name__ == '__main__':
    main()
