"""Read-only cheat-option diagnostic of the remaining E037 cold target.

This factory never runs Mesen or writes outputs. Its real title/options
opening is not source-qualified: the existing bus lacks a vblank clock.
"""
from hashlib import sha256
import argparse
import json

import compose_smb2_postbg_mirror_1113 as C

PIN=C.CANDIDATE
BASE_SHA='5804ddb027a6b2956dae8fd155184a4a521a59e7fd784689d95db240fd8bfe4f'
LUA_SHA='eb9ae28a623d58d75b5795e3620643c7e2b945a047e75df46ae3fbd9bec6102b'


def once(text,before,after):
    assert text.count(before)==1,before
    return text.replace(before,after,1)


def bindings(raw):
    assert sha256(raw).hexdigest()==PIN
    b=dict(C.W.Symbols.bundle(),raw=raw)
    fields={n:C.W.address(b,n)for n in ('CheatInvincible','CheatStartLevel','CrossoverOptionsFocus',
             'CrossoverMenuState','GuestHurtKind','CurrentBank','CurrentBankC')}
    assert fields['CheatInvincible']==0x7ffb and fields['GuestHurtKind']==0x6f1c
    windows=[]
    def bind(name,bank,pc,code):
        at=bank*8192+(pc&8191)
        assert raw[16+at:16+at+len(code)]==code,(name,bank,hex(pc))
        windows.append(dict(name=name,pc=pc,bank=bank,offset=at,hex=code.hex()))
    canonical=bytes.fromhex('ad1c6f0dfb7ff0128d6a01a9f58d6c01a9bd8d6d01a9cf4c5a018d6a01a9218d6c01a9ad8d6d01a9bf4c5a01ea')
    for bank in(119,120,125,127):
        code=bytearray(canonical)
        if bank in(119,120):code[0xe037-0xe02b]=0xde
        bind('game_gate_'+str(bank),bank,0xe02b,bytes(code))
    bind('real_low_caller',126,0x83a1,bytes.fromhex('202be0'))
    bind('obsolete_UI_tail',79,0xbdde,bytes.fromhex('8d6c01a9aa8d6d01a9bf8d620168684c6101'))
    bind('canonical_game_cold',79,0xbdf5,bytes.fromhex('0848ad0260c918f01fc902d02f'))
    for name in('CrossoverMenuInput','CheatsMenuInput','CheatsSixInput'):
        pc,at=C.W.address(b,name),C.W.location(b,name)
        assert raw[at:at+16]==b['raw'][at:at+16]
        bind(name,(at-16)//8192,pc,raw[at:at+16])
    for name,pc,code in(('DMC_alias_select',0xbb93,'8d1751'),('DMC_start',0xbb9c,'8d1540'),
                         ('DMC_stop',0xbb78,'8d1540')):
        bind(name,74,pc,bytes.fromhex(code))
    return fields,windows


OPENING=r'''
 assert(read(coldFields.CheatInvincible)==0 and read(coldFields.CheatStartLevel)==0,'Fresh cold cheat defaults')
 coldMenu('title-defaults')
 press(4);assert(read(coldFields.CrossoverOptionsFocus)==1,'Real title Down chooses Options')
 press(16);wait(function()return r('CrossoverMenuState')==4 and r('DisableScreenFlag')==0 end)
 assert(read(coldFields.CrossoverOptionsFocus)==0,'Options opens first row');coldMenu('options')
 press(4);press(4);assert(read(coldFields.CrossoverOptionsFocus)==2,'Two ordinary Down presses choose Cheats')
 press(128);wait(function()return r('CrossoverMenuState')==6 and r('DisableScreenFlag')==0 end)
 assert(read(coldFields.CrossoverOptionsFocus)==0,'Cheats opens Invincible row');coldMenu('cheats-before')
 press(128);assert(read(coldFields.CheatInvincible)==1,'Actual menu enables only Invincible bit0')
 assert(read(coldFields.CheatStartLevel)==0,'Starting level untouched');coldMenu('invincible-enabled')
 press(64);wait(function()return r('CrossoverMenuState')==4 and r('DisableScreenFlag')==0 end)
 assert(read(coldFields.CrossoverOptionsFocus)==2,'B returns to Cheats parent row');coldMenu('options-return')
 press(64);wait(function()return r('CrossoverMenuState')==0 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 assert(read(coldFields.CheatInvincible)==1 and read(coldFields.CrossoverOptionsFocus)==0,'Rebuilt title retains only UI-earned Invincible')
 coldMenu('title-return')
'''


OBSERVER=r'''
local function coldMapped(pc,bank)
 local a=emu.convertAddress(pc);return a and a.memType==emu.memType.nesPrgRom and a.address==bank*8192+(pc&8191)
end
local function coldBank(pc)
 local a=emu.convertAddress(pc);return a and a.memType==emu.memType.nesPrgRom and a.address//8192 or -1
end
local function coldSnapshot(kind)
 local c=emu.getState();local sp=c['cpu.sp']
 return{kind=kind,frame=frames,Main=updates,cycle=c['cpu.cycleCount'],pc=c['cpu.pc'],sp=sp,
  a=c['cpu.a'],x=c['cpu.x'],y=c['cpu.y'],bank=coldBank(c['cpu.pc']),resident=coldBank(0xe02b),
  bankA=read(coldFields.CurrentBank),bankC=read(coldFields.CurrentBankC),engine=r('GameEngineSubroutine'),
  world=r('WorldNumber'),level=r('LevelNumber'),cheat=read(coldFields.CheatInvincible),hurt=read(coldFields.GuestHurtKind),
  status4015=read(0x4015),bytesRemaining=c['apu.dmc.bytesRemaining'],
  literal_target=read(0xe037)+256*read(0xe03c),literal_bank=read(0xe041),
  smc_target=read(0x16c)+256*read(0x16d),stack_return=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535}
end
local function coldRecord(q)
 if coldTrace.count>=64 then coldTrace.dropped=coldTrace.dropped+1;return end
 coldTrace.count=coldTrace.count+1;coldTrace.events[tostring(coldTrace.count)]=q
end
coldMenu=function(label)
 local q=coldSnapshot('menu');q.label=label;q.menu=r('CrossoverMenuState');q.focus=read(coldFields.CrossoverOptionsFocus)
 q.start_level=read(coldFields.CheatStartLevel);coldRecord(q)
end
local token,sequence=nil,0
local retained,returnHooks={},{}
local canonicalDetails,aliasDetails=0,0
local function count(name)coldTrace.calls[name]=(coldTrace.calls[name]or 0)+1 end
local function fresh(t)
 if not game or not t or t.Main~=updates then return false end
 local c=emu.getState();return c['cpu.cycleCount']>=t.cycle and c['cpu.cycleCount']-t.cycle<=120000 and frames-t.frame<=4
end
local function log(t,q)
 if not t.keep then return end
 q.token=t.id;q.stage=t.stage;q.entry_Main=t.Main;q.entry_sp=t.sp;q.caller_return=t.ret
 q.target=t.target;q.rawbank=t.rawbank;q.target_seen=t.seen or false;q.resident_return=t.returned or false
 q.farcall_return=t.farcall_return;coldRecord(q)
end
emu.addMemoryCallback(guard(function()
 if not game then return end
 local bank=coldBank(0xe02b);if bank~=119 and bank~=120 and bank~=125 and bank~=127 then return end
 local q=coldSnapshot('game_gate_entry');sequence=sequence+1;count('entries')
 if q.stack_return~=0x83a4 or not coldMapped(0x83a4,126)then count('unexpected_caller_stack');return end
 local old=bank==119 or bank==120
 local keep=old and aliasDetails<4 or not old and canonicalDetails<1
 if keep then if old then aliasDetails=aliasDetails+1 else canonicalDetails=canonicalDetails+1 end end
 token={id=sequence,Main=updates,cycle=q.cycle,frame=frames,sp=q.sp,ret=q.stack_return,stage='entry',keep=keep}
 if keep then retained[#retained+1]=token;log(token,q)end
 if not returnHooks[token.ret]then
  local pc=token.ret;returnHooks[pc]=true
  emu.addMemoryCallback(guard(function()
   local t=token;if not fresh(t)or pc~=t.ret or not coldMapped(pc,126)then return end
   if emu.getState()['cpu.sp']~=(t.sp+2)&255 then return end
   t.returned=true;count('resident_returns');log(t,coldSnapshot('game_gate_caller_return'));t.stage='returned'
  end),emu.callbackType.exec,pc)
 end
end),emu.callbackType.exec,0xe02b)
emu.addMemoryCallback(guard(function()
 local t=token;if not fresh(t)or t.stage~='entry'or emu.getState()['cpu.sp']~=t.sp then return end
 t.stage='cold';count('cold_branches')
end),emu.callbackType.exec,0xe033)
emu.addMemoryCallback(guard(function()
 local t=token;if not fresh(t)or t.stage~='cold'then return end
 local q=coldSnapshot('game_gate_tail');if q.sp~=t.sp then return end
 t.target=q.smc_target;t.rawbank=q.a
 if t.rawbank~=207 or(t.target~=0xbdde and t.target~=0xbdf5)then log(t,q);count('unexpected_producer');return end
 t.stage='tail';count('matched_tail')
end),emu.callbackType.exec,0xe042)
emu.addMemoryCallback(guard(function()
 local t=token;if not fresh(t)or t.stage~='tail'then return end
 local q=coldSnapshot('gateway');if q.sp~=t.sp or q.a~=t.rawbank or q.smc_target~=t.target then return end
 t.stage='gateway';count('matched_gateway')
end),emu.callbackType.exec,0x15a)
emu.addMemoryCallback(guard(function()
 local t=token;if not fresh(t)or t.stage~='gateway'then return end
 local q=coldSnapshot('game_gate_SMC')
 if q.sp~=(t.sp-1)&255 or q.smc_target~=t.target or not coldMapped(t.target,79)then return end
 t.stage='SMC';count('matched_SMC');log(t,q)
end),emu.callbackType.exec,0x16b)
for _,point in ipairs({{pc=0xbdde,name='obsolete_UI_tail'},{pc=0xbdf5,name='canonical_game_cold'}})do
 emu.addMemoryCallback(guard(function()
  local t=token;if not fresh(t)or t.stage~='SMC'or t.target~=point.pc or not coldMapped(point.pc,79)then return end
  local q=coldSnapshot(point.name);if q.sp~=(t.sp-3)&255 or q.stack_return~=0x16e then return end
  t.stage='target';t.seen=true;count(point.name);log(t,q)
 end),emu.callbackType.exec,point.pc)
end
emu.addMemoryCallback(guard(function()
 local t=token;if not fresh(t)or t.stage~='target'then return end
 local q=coldSnapshot('farcall_return');if q.sp~=(t.sp-1)&255 then return end
 t.farcall_return={cycle=q.cycle,sp=q.sp,bankA=q.bankA};t.stage='farcall_return';count('farcall_returns')
end),emu.callbackType.exec,0x16e)
coldAfterMain=function()
 for _,t in ipairs(retained)do if updates>t.Main then log(t,coldSnapshot('next_Main_outcome'))end end
 retained={};token=nil
end
local audioSeen={};local audioRecords=0
for _,p in ipairs({{pc=0xbb96,name='after_alias_select'},{pc=0xbb9f,name='after_DMC_start'},{pc=0xbb7b,name='after_DMC_stop'}})do
 emu.addMemoryCallback(guard(function()
  if not game or not coldMapped(p.pc,74)then return end
  local q=coldSnapshot(p.name)
  local key=p.name..':'..q.resident..':'..(q.status4015&16)..':'..tostring(q.bytesRemaining)..':'..q.level
  if audioSeen[key]then return end;audioSeen[key]=true;count('DMC_interest_changes')
  if audioRecords<12 then audioRecords=audioRecords+1;coldRecord(q)end
 end),emu.callbackType.exec,p.pc)
end
for _,w in ipairs(coldWindows)do for i=1,#w.hex,2 do
 assert(emu.read(w.offset+(i-1)//2,emu.memType.nesPrgRom)==tonumber(w.hex:sub(i,i+1),16),'Exact current UI/cold-gate preimage')
end end
'''


def controller(raw):
    assert sha256(raw).hexdigest()==PIN
    parent=C.inverse(raw)
    base=C.Owner.base_controller(parent)
    assert base.count(C.PIN)==1
    base=base.replace(C.PIN,PIN)
    assert sha256(base.encode()).hexdigest()==BASE_SHA
    fields,windows=bindings(raw)
    declaration='local coldFields='+C.Owner.lua(fields)+'\nlocal coldWindows='+C.Owner.lua(windows)+'\n'
    declaration+='local coldTrace={events={},count=0,dropped=0,calls={},cheat_option_diagnostic=true,standard_stage_qualification=false}\nlocal coldMenu,coldAfterMain\n'
    text=once(base,'local function finish(ok,why)',declaration+'local function finish(ok,why)')
    text=once(text,'controller_only=true,physical_frames=',
              'controller_only=true,cheat_option_diagnostic=true,standard_stage_qualification=false,cold_gate=coldTrace,physical_frames=')
    opening=" press(16);wait(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)"
    text=once(text,opening,OPENING+opening)
    text=once(text,'local function drive()\n',"local function drive()\n assert(read(coldFields.CheatInvincible)==1,'Retain only UI-enabled Invincible; no other cheats')\n")
    text=once(text,'pending[#pending]=nil;updates=updates+1',
              'pending[#pending]=nil;updates=updates+1;if coldAfterMain then coldAfterMain()end')
    old_reason="'SMB2/Doki clears non-shortcut1-1 then25 grounded quiet underground1-2 updates'"
    new_reason="'Cheat-option diagnostic completes ordinary Luigi route; not standard stage qualification'"
    text=once(text,old_reason,new_reason)
    text+='\n'+OBSERVER
    restored=text[:-len('\n'+OBSERVER)]
    restored=restored.replace(new_reason,old_reason,1).replace(declaration,'',1)
    restored=restored.replace('controller_only=true,cheat_option_diagnostic=true,standard_stage_qualification=false,cold_gate=coldTrace,physical_frames=',
                              'controller_only=true,physical_frames=',1)
    restored=restored.replace(OPENING+opening,opening,1)
    restored=restored.replace("local function drive()\n assert(read(coldFields.CheatInvincible)==1,'Retain only UI-enabled Invincible; no other cheats')\n",'local function drive()\n',1)
    restored=restored.replace(';updates=updates+1;if coldAfterMain then coldAfterMain()end',';updates=updates+1',1)
    assert restored==base,'Original ordinary route/full-stage assertions changed'
    C.Owner.Terrain.Frozen.Flag.Root.Base.LuaRuntime().compile(text)
    assert all(word not in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA
    return text


def reset_probe(raw,limit=50000):
    """Observe the existing bus's genuine RESET-vector limitation; no grants."""
    assert sha256(raw).hexdigest()==PIN
    b=dict(C.W.Symbols.bundle(),raw=raw);m=C.W.ControllerBus(b)
    cpu=C.N.NesMPU(memory=m,pc=None);recent=[]
    for i in range(limit):
        if i>=limit-10:recent.append(cpu.pc)
        cpu.step()
    assert cpu.pc in(0xe29c,0xe29f)and m[0x2002]==0
    return dict(source_opening_qualified=False,instructions=limit,PC=cpu.pc,
                last_PC=recent,status2002=m[0x2002],maps=m.rawtags,
                limitation='Existing bus returns PPUSTATUS0 without a video/APU clock; RESET waits at E29C/E29F before title/input. No status override or cheat seed is applied.',
                outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reset-probe',action='store_true');args=p.parse_args()
    raw=C.Owner.NIGHTLY.read_bytes()
    q=reset_probe(raw)if args.reset_probe else dict(ROM_SHA256=PIN,controller_SHA256=sha256(controller(raw).encode()).hexdigest(),
        ordinary_route_SHA256=BASE_SHA,cheat_option_diagnostic=True,standard_stage_qualification=False,
        source_opening_qualified=False,passive_record_cap=64,outputs=0,Mesen_run=False)
    print(json.dumps(q,separators=(',',':')),flush=True)
