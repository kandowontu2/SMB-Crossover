"""Passive bounded pipe5 observer from frozen d9a text; no ROM required."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from check_ff_stdout_controller_source_1110 import LuaRuntime

BASE='d9a13fe9158332ddf15ef19228c2cc613d20d8313b6b34a0b0932153027734f6'
ROM='e98df463b9376105af9fa699e7e34b1d93fe95b4550e35a1558afdaa9f17cd47'
LUA_PIN='46f1a1418137eadf4b0d162cdbb9f3b7c47da7187cbf77d75e89ff025131fa1f'

def once(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new)

DECLARATIONS='''local p5Trace,p5Tokens,p5Completed,p5ReturnHooks={},{},{},{}
local p5Sequence,p5Counts={host=0,main=0,worker=0},{drive=0,drive_inside_host=0,drive_inside_main=0,drive_inside_worker=0,polls=0,polls_inside_host=0,polls_inside_main=0,polls_inside_worker=0}
local p5FirstInjury,p5FirstPendingDecision,p5FirstSupportLoss,p5Terrain,p5LastNativePosition
local p5HadNativeSupport,p5Scanned=false,false
'''

FUNCTIONS=r'''local function p5Watching()
 return phase:sub(1,5)=='pipe5'
end
local function p5Rects(offset)
 local rows={}
 for i=0,12,4 do
  if ram(2,offset+i)==255 then break end
  rows[#rows+1]={ram(2,offset+i),ram(2,offset+i+1),ram(2,offset+i+2),ram(2,offset+i+3)}
 end
 return rows
end
local function p5View(kind)
 local row=snapshot();row.kind=kind
 row.bits=bits;row.native_held=read(0xdc);row.original_held=ram(2,0x14);row.original_sample=ram(2,0x15)
 row.original_direction=ram(2,0x54);row.original_facing=ram(2,0x6d);row.prior=ram(2,0x6c)
 row.source_y=ram(2,0x210);row.fall_origin=ram(2,0x76);row.fall_limit=ram(2,0x7b);row.native_vy=read(0x8e)
 row.host_pending=p5Tokens.host;row.main_pending=p5Tokens.main;row.worker_pending=p5Tokens.worker
 row.last_host_return=p5Completed.host;row.last_main_return=p5Completed.main;row.last_worker_return=p5Completed.worker
 row.query_kind=ram(2,0x8db);row.query_rect={ram(2,0x3e),ram(2,0x3f),ram(2,0x40),ram(2,0x41)}
 row.support_rects=p5Rects(0x800);row.wall_rects=p5Rects(0x880)
 row.player_bbox={read(0x658),read(0x659),read(0x65a),read(0x65b)}
 local birth=births['2640']
 if birth then
  local slot=birth.slot;local at=0x65c+4*slot
  row.helper={slot=slot,left=pos(0x76,0x5d,slot),top=read(0xbe+slot),speed=read(0x8f+slot),force=read(0xa0+slot),
   flag=read(0x10+slot),id=read(0x17+slot),passenger=read(0x566+slot),bbox={read(at),read(at+1),read(at+2),read(at+3)}}
 end
 row.last_actual_native_position=p5LastNativePosition
 return row
end
local function p5Keep(row)
 if not p5Terrain then
  p5Terrain={left=2544,top=144,columns=10,rows=5,tiles={}}
  for y=144,208,16 do for wx=2544,2688,16 do
   p5Terrain.tiles[#p5Terrain.tiles+1]=read(0x300+((wx>>8)&1)*208+((y-32)//16)*16+((wx>>4)&15))
  end end
 end
 if #p5Trace>=32 then table.remove(p5Trace,9)end
 p5Trace[#p5Trace+1]=row
 if p5HadNativeSupport and not p5FirstSupportLoss and row.source==4 and
  p5LastNativePosition and updates-p5LastNativePosition.Main>1 then p5FirstSupportLoss=row end
end
local function p5Decision(before)
 if not before then return end
 p5Counts.drive=p5Counts.drive+1
 if before.host_pending then p5Counts.drive_inside_host=p5Counts.drive_inside_host+1 end
 if before.main_pending then p5Counts.drive_inside_main=p5Counts.drive_inside_main+1 end
 if before.worker_pending then p5Counts.drive_inside_worker=p5Counts.drive_inside_worker+1 end
 local row=p5View('drive-decision');row.before_bits=before.bits;row.before_phase=before.phase
 row.decision_inside_host=before.host_pending~=nil;row.decision_inside_main=before.main_pending~=nil;row.decision_inside_worker=before.worker_pending~=nil
 if (row.decision_inside_host or row.decision_inside_main)and not p5FirstPendingDecision then p5FirstPendingDecision=row end
 if before.bits~=bits or before.phase~=phase or updates%8==0 then p5Keep(row)end
end
'''

OBSERVERS=r'''local function p5Follow(label,pc,bank,kind)
 kind=kind or'nesWorkRam'
 emu.addMemoryCallback(guarded('pipe5 '..label..' entry',function()
  if not active()or not mapped(pc,kind,bank*8192+(pc&8191))then return end
  p5Sequence[label]=p5Sequence[label]+1
  local c=emu.getState();local sp=c['cpu.sp']
  local ret=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
  p5Tokens[label]={token=p5Sequence[label],Main=updates,entry_pc=pc,entry_sp=sp,return_pc=ret,return_sp=(sp+2)&255}
  local key=label..':'..ret
  if not p5ReturnHooks[key]then
   p5ReturnHooks[key]=true
   emu.addMemoryCallback(guarded('pipe5 '..label..' return',function()
    local pending=p5Tokens[label];if not pending then return end
    local q=emu.getState()
    if q['cpu.pc']~=pending.return_pc or q['cpu.sp']~=pending.return_sp then return end
    p5Completed[label]={token=pending.token,Main=updates,pc=q['cpu.pc'],sp=q['cpu.sp']}
    p5Tokens[label]=nil
    if p5Watching()and updates%8==0 then p5Keep(p5View(label..'-return'))end
   end),emu.callbackType.exec,ret)
  end
 end),emu.callbackType.exec,pc)
end
p5Follow('main',0xd65e,2)
p5Follow('worker',0xa2e8,3)
p5Follow('host',0x839a,126,'nesPrgRom')
emu.addMemoryCallback(guarded('pipe5 source stores',function()
 if p5Scanned or not active()or not mapped(0xd65e,'nesWorkRam',2*8192+0x165e)then return end
 p5Scanned=true
 for _,span in ipairs({{3,0xa000,0xbfdd},{2,0xd000,0xd7fd}})do
  local bank=span[1]
  for pc=span[2],span[3]do
   local offset=pc&8191
   if ram(bank,offset)==0x8d and ram(bank,offset+1)==0x6b and ram(bank,offset+2)==0xc0 then
    local address=pc;local owner=bank
    emu.addMemoryCallback(guarded('pipe5 original source5 writer',function()
     if not p5Watching()or p5FirstInjury or not mapped(address,'nesWorkRam',owner*8192+(address&8191))then return end
     local c=emu.getState();if c['cpu.a']~=5 then return end
     local row=p5View('first-source5-writer');row.writer_pc=address;row.writer_bank=owner;row.pending_A=c['cpu.a']
     p5FirstInjury=row;p5Keep(row)
    end),emu.callbackType.exec,address)
   end
  end
 end
end),emu.callbackType.exec,0xd65e)
emu.addMemoryCallback(guarded('pipe5 actual native support',function()
 if not p5Watching()or not mapped(0xac18,'nesPrgRom',71*8192+0xc18)then return end
 local birth=births['2640'];local c=emu.getState()
 if not birth or c['cpu.x']~=birth.slot then return end
 p5HadNativeSupport=true
 p5LastNativePosition={Main=updates,frame=frame,slot=c['cpu.x'],pending_y=c['cpu.a'],x=x(),top=read(0xbe+c['cpu.x']),passenger=read(0x566+c['cpu.x'])}
 if updates%8==0 then p5Keep(p5View('actual-native-position'))end
end),emu.callbackType.exec,0xac18)
'''

def from_text(original):
    assert isinstance(original,str)and sha256(original.encode()).hexdigest()==BASE
    assert original.count(ROM)==1
    text=DECLARATIONS+original
    text=once(text,'local function drive()\n',FUNCTIONS+'local function drive()\n')
    wrapper='''local p5OriginalDrive=drive
drive=function()
 local before=p5Watching()and p5View('before-drive')or nil
 p5OriginalDrive()
 if before then p5Decision(before)end
end
'''
    text=once(text,'local function wait(pred)',wrapper+'local function wait(pred)')
    text=once(text,"emu.addMemoryCallback(guarded('main',function()",OBSERVERS+"emu.addMemoryCallback(guarded('main',function()")
    poll=''' if p5Watching()then
  p5Counts.polls=p5Counts.polls+1
  if p5Tokens.host then p5Counts.polls_inside_host=p5Counts.polls_inside_host+1 end
  if p5Tokens.main then p5Counts.polls_inside_main=p5Counts.polls_inside_main+1 end
  if p5Tokens.worker then p5Counts.polls_inside_worker=p5Counts.polls_inside_worker+1 end
  if polls%8==0 then p5Keep(p5View('input-poll'))end
 end
'''
    text=once(text,' polls=polls+1\n',' polls=polls+1\n'+poll)
    receipt='events=events,pipe5_trace=p5Trace,pipe5_counts=p5Counts,pipe5_first_injury=p5FirstInjury,pipe5_first_pending_decision=p5FirstPendingDecision,pipe5_first_support_loss=p5FirstSupportLoss,pipe5_terrain=p5Terrain,'
    text=once(text,'events=events,',receipt)
    restored=text[len(DECLARATIONS):]
    for before,after in((FUNCTIONS+'local function drive()\n','local function drive()\n'),
        (wrapper+'local function wait(pred)','local function wait(pred)'),
        (OBSERVERS+"emu.addMemoryCallback(guarded('main',function()","emu.addMemoryCallback(guarded('main',function()"),
        (' polls=polls+1\n'+poll,' polls=polls+1\n'),(receipt,'events=events,')):
        restored=once(restored,before,after)
    assert restored==original,'Passive observer changed a control or assertion'
    LuaRuntime().compile(text)
    if LUA_PIN is not None:assert sha256(text.encode()).hexdigest()==LUA_PIN
    return text

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--from-text',type=Path);args=ap.parse_args()
    if args.from_text:base=args.from_text.read_text().replace('\r\n','\n')
    else:
        import compose_dkjr_oneway_current_1114 as Current
        import replay_dkjr_oneway_grounded12_1114 as Ground
        current=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
        raw,private,_=Current.source_projection(current,kind='hidden-421')
        base=Ground.strengthen(Current.source_controller(raw,private=private))
    text=from_text(base)
    print('DKJR_PIPE5_OBSERVER '+json.dumps(dict(ROM_SHA256=ROM,base_Lua_SHA256=BASE,
        observer_Lua_SHA256=sha256(text.encode()).hexdigest(),maximum_trace_rows=32,
        separate_first_injury_pending_decision_and_support_loss=True,
        actual_Main_and_original_Move_return_PC_SP_tokens=True,all_controls_and_assertions_exact=True,
        source_or_native_writes=False,outputs_written=0),separators=(',',':')),flush=True)
