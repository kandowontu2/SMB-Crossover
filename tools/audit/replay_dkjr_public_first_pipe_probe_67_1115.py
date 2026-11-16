"""At most eight causal witnesses over unchanged public67/43b5 controls."""
from hashlib import sha256
import json
import recover_dkjr_current_identity_67_1115 as F
from check_ff_stdout_controller_source_1110 import LuaRuntime

BASE = '43b51e99c2e05c101a697f35bbf4a154deb6a3a3b4edf455f58bf586badb500d'


def one(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


DECL = '''local p1Counts={main_entries=0,main_returns=0,actual_carries=0,state_writes=0,polls=0}
local p1StateEvents,p1Carries,p1ReturnHooks={},{},{}
local p1FirstBad,p1FirstLoss,p1LastInput,p1Pending,p1LastPolled
'''

FUNCTIONS = '''local function p1Watching()
 return playing and index==1
end
local function p1Rects(offset)
 local rows={}
 for i=0,12,4 do
  if ram(2,offset+i)==255 then break end
  rows[#rows+1]={ram(2,offset+i),ram(2,offset+i+1),ram(2,offset+i+2),ram(2,offset+i+3)}
 end
 return rows
end
local function p1View(kind)
 local q=snapshot();q.kind=kind
 q.bits=bits;q.held=read(0xdc);q.source_held=ram(2,0x14);q.source_sample=ram(2,0x15)
 q.prior=ram(2,0x6c);q.source_y=ram(2,0x210);q.origin=ram(2,0x76);q.limit=ram(2,0x7b)
 q.age=ram(2,0x7e);q.fraction=ram(2,0x7f);q.acc=ram(2,0x82)+256*ram(2,0x83)
 q.impulse=ram(2,0x86)+256*ram(2,0x87);q.native_vy=read(0x8e)
 q.query_kind=ram(2,0x8db);q.query={ram(2,0x3e),ram(2,0x3f),ram(2,0x40),ram(2,0x41)}
 q.support=p1Rects(0x800);q.walls=p1Rects(0x880)
 q.bbox={read(0x658),read(0x659),read(0x65a),read(0x65b)}
 local b=births['416']
 if b then local s=b.slot;local at=0x65c+4*s
  q.helper={slot=s,flag=read(0x10+s),id=read(0x17+s),left=pos(0x76,0x5d,s),top=read(0xbe+s),
   vy=read(0x8f+s),passenger=read(0x566+s),bbox={read(at),read(at+1),read(at+2),read(at+3)}}
 end
 return q
end
local function p1Keep(rows,row,limit)
 if #rows>=limit then table.remove(rows,1)end
 rows[#rows+1]=row
end
'''

OBSERVERS = '''emu.addMemoryCallback(guarded('pipe1 Main entry',function()
 if not p1Watching()or not active()or not mapped(0xd65e,'nesWorkRam',2*8192+0x165e)then return end
 p1Counts.main_entries=p1Counts.main_entries+1
 local c=emu.getState();local sp=c['cpu.sp']
 local ret=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 p1Pending={pc=ret,sp=(sp+2)&255}
 if not p1ReturnHooks[ret]then
  p1ReturnHooks[ret]=true
  emu.addMemoryCallback(guarded('pipe1 Main return',function()
   local q=p1Pending;if not q or q.pc~=ret or emu.getState()['cpu.sp']~=q.sp then return end
   p1Pending=nil;p1Counts.main_returns=p1Counts.main_returns+1
   local last=p1Carries[#p1Carries]
   if phase=='cross'and not p1FirstLoss and last and updates-last.Main>1 and ram(2,0x6b)==4 then
    p1FirstLoss=p1View('first-original-fall-after-carry')
   end
  end),emu.callbackType.exec,ret)
 end
end),emu.callbackType.exec,0xd65e)
for _,pc in ipairs(P1_WRITERS)do
 local address=pc
 emu.addMemoryCallback(guarded('pipe1 source state writer',function()
  if not p1Watching()or not mapped(address,'nesWorkRam',3*8192+(address&8191))then return end
  p1Counts.state_writes=p1Counts.state_writes+1
  local c=emu.getState();local value=c['cpu.a']
  if value==5 and not p1FirstBad then
   local q=p1View('first-pending-source5-writer')
   q.writer_pc=address;q.writer_bank=3;q.pending_A=value;q.P=c['cpu.ps'];q.SP=c['cpu.sp']
   q.stack={};for i=1,8 do q.stack[i]=read(0x100+((c['cpu.sp']+i)&255))end
   p1FirstBad=q
  elseif phase=='cross'and value~=ram(2,0x6b)then
   local q=p1View('preceding-source-state-transition');q.writer_pc=address;q.pending_A=value;q.SP=c['cpu.sp']
   p1Keep(p1StateEvents,q,3)
  end
 end),emu.callbackType.exec,address)
end
emu.addMemoryCallback(guarded('pipe1 actual native carry',function()
 if not p1Watching()or not mapped(0xac29,'nesPrgRom',71*8192+0xc29)then return end
 local b=births['416'];local c=emu.getState()
 if not b or c['cpu.x']~=b.slot then return end
 p1Counts.actual_carries=p1Counts.actual_carries+1
 local q=p1View('actual-native-position');q.PC=0xac29;q.SP=c['cpu.sp'];q.A=c['cpu.a']
 p1Keep(p1Carries,q,2)
end),emu.callbackType.exec,0xac29)
'''

POLL = ''' if p1Watching()then
  p1Counts.polls=p1Counts.polls+1
  if p1LastPolled~=bits then p1LastInput=p1View('last-actual-poll-input-change');p1LastInput.previous_requested=p1LastPolled end
  p1LastPolled=bits
 end
'''

RECEIPT_OLD = 'events=events,'
RECEIPT_NEW = ('events=events,pipe1_counts=p1Counts,pipe1_first_source5=p1FirstBad,'
               'pipe1_preceding_transitions=p1StateEvents,pipe1_last_carries=p1Carries,'
               'pipe1_first_support_loss=p1FirstLoss,pipe1_last_input_change=p1LastInput,')


def controller(raw):
    _, payload = F.identity(raw)
    base = F.controller(raw, kind='delivered-public-67')
    assert sha256(base.encode()).hexdigest() == BASE
    writers = sorted(0xa000+i for i in range(0x1fde) if payload[i:i+3] == bytes.fromhex('8d6bc0'))
    assert writers and 0xa8dd in writers
    observers = OBSERVERS.replace('P1_WRITERS', '{'+','.join(str(pc) for pc in writers)+'}')
    text = one(base, 'local function finish(ok,why)', DECL+FUNCTIONS+'local function finish(ok,why)')
    text = one(text, "emu.addMemoryCallback(guarded('main',function()", observers+"emu.addMemoryCallback(guarded('main',function()")
    text = one(text, ' polls=polls+1\n', ' polls=polls+1\n'+POLL)
    text = one(text, RECEIPT_OLD, RECEIPT_NEW)
    restored = one(text, DECL+FUNCTIONS+'local function finish(ok,why)', 'local function finish(ok,why)')
    restored = one(restored, observers+"emu.addMemoryCallback(guarded('main',function()", "emu.addMemoryCallback(guarded('main',function()")
    restored = one(restored, ' polls=polls+1\n'+POLL, ' polls=polls+1\n')
    restored = one(restored, RECEIPT_NEW, RECEIPT_OLD)
    assert restored == base
    LuaRuntime().compile(text)
    return text


if __name__ == '__main__':
    raw = F.NIGHTLY.read_bytes()
    text = controller(raw)
    print('DKJR_PUBLIC_FIRST_PIPE_PROBE '+json.dumps(dict(
        passed=True, actual_ROM_SHA256=F.PIN, base_LF_SHA256=BASE,
        Lua_SHA256=sha256(text.encode()).hexdigest(),
        exact_controls_and_assertions_after_observer_removal=True,
        maximum_specific_witnesses=8, generic_per_Main_or_frame_snapshots=0,
        PNGs=0, outputs_written=0, game_writes=False, native_run=False), separators=(',', ':')), flush=True)
