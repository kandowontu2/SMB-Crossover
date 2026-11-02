"""Bounded actual interrupt-hook sequence; preserve Thomas vector parity checks."""
from pathlib import Path
import hashlib
from prepare_selected_native_packet_v1 import R, prepare, sha

O = R / 'build/bub-menu-candidate-1102-v2'
PIN = 'f5c30ceaa36894f3e814ef277081ecd9cf434a934c0f7b3f514c2291be0e1cfc'

BLOCK = r'''
local vectorSequence,vectorSequenceCount,vectorWritten={},0,false
local function vectorEvent(event,kind,pc,bankAccepted,gateAccepted)
 local s=emu.getState();local a=emu.convertAddress(pc)
 vectorSequenceCount=vectorSequenceCount+1
 local t={sequence=vectorSequenceCount,event=event,kind=kind,hook_pc=pc,cpu_pc=s['cpu.pc'],
  sp=s['cpu.sp'],a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y'],frame=frame,Main=updates,
  phase=phase,active=active(),last_Main=lastMain~=nil,depth=#isrs,
  converted_address=a and a.address or -1,converted_memType=a and a.memType or -1,
  converted_bank=a and a.address//8192 or -1,opcode=peek(pc),
  bank_accepted=bankAccepted,gate_accepted=gateAccepted}
 if #isrs>0 then t.saved_kind=isrs[#isrs].kind;t.saved_sp=isrs[#isrs].sp end
 if #vectorSequence==128 then table.remove(vectorSequence,1)end
 vectorSequence[#vectorSequence+1]=t
end
local function vectorWrite(reason)
 if vectorWritten then return end;vectorWritten=true
 local s=emu.getState();local bytes={}
 for i=1,20 do local a=0x100+((s['cpu.sp']+i)&255);bytes[#bytes+1]={address=a,value=peek(a)}end
 local f=assert(io.open(OUTPUT..'vector-sequence.json','w'))
 f:write(json({reason=reason,ROM_sha256=P.sha256,frame=frame,Main=updates,
  phase=phase,sequence_count=vectorSequenceCount,events=vectorSequence,
  pending=isrs,stack_above_SP=bytes,controller_only=true,ROM_changed=false,
  diagnostic_only=true,full_stage=false}));f:close()
end
for _,kind in ipairs({'NMI','IRQ'})do
 local entry=kind=='NMI'and L.NonMaskableInterrupt or L.IrqScrollSplit
 local leave=kind=='NMI'and L.NonMaskableInterrupt_RTI or L.IrqScrollSplit_RTI
 assert(entry and leave,'Explicit vector callback addresses')
 local function vectorBank(pc)local a=emu.convertAddress(pc);return a and a.memType==emu.memType.nesPrgRom and a.address//8192==(kind=='NMI'and 127 or 126)end
 emu.addMemoryCallback(function()
  local bankAccepted=vectorBank(entry);local gateAccepted=active()or lastMain~=nil or#isrs>0
  vectorEvent('entry-hook',kind,entry,bankAccepted,gateAccepted)
  if bankAccepted and gateAccepted then
   local s=emu.getState();minSP=math.min(minSP,s['cpu.sp']);local t=isrs[#isrs]
   if t and t.kind==kind and t.sp==s['cpu.sp']then
    vectorEvent('entry-duplicate-suppressed',kind,entry,true,true);return
   end
   isrs[#isrs+1]={kind=kind,sp=s['cpu.sp'],smc=image(),a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y']}
   counters[kind=='NMI'and'nmi'or'irq']=counters[kind=='NMI'and'nmi'or'irq']+1
   vectorEvent('entry-pushed',kind,entry,true,true)
  end
 end,emu.callbackType.exec,entry)
 emu.addMemoryCallback(function()
  local bankAccepted=vectorBank(leave)
  vectorEvent('leave-hook',kind,leave,bankAccepted,#isrs>0)
  if bankAccepted and #isrs>0 then
   local q=isrs[#isrs];local s=emu.getState()
   if q.kind~=kind or q.sp~=s['cpu.sp'] then vectorWrite('Real vector stack balance')end
   assert(q.kind==kind and q.sp==s['cpu.sp'],'Real vector stack balance')
   if q.smc~=image()or q.a~=s['cpu.a']or q.x~=s['cpu.x']or q.y~=s['cpu.y']then vectorWrite('Vector restores live registers/SMC')end
   assert(q.smc==image()and q.a==s['cpu.a']and q.x==s['cpu.x']and q.y==s['cpu.y'],'Vector restores live registers/SMC')
   table.remove(isrs);counters.vectors=counters.vectors+1
   vectorEvent('leave-popped',kind,leave,true,true)
  end
 end,emu.callbackType.exec,leave)
 -- Trace only: observing the instruction after the entry PHA can reveal an
 -- emulator callback omitted at the vector's very first instruction.
 emu.addMemoryCallback(function()
  vectorEvent('entry-plus-one-sentinel',kind,entry+1,vectorBank(entry+1),active()or lastMain~=nil or#isrs>0)
 end,emu.callbackType.exec,entry+1)
end
'''


def main():
    source = R / 'build/thomas-full11-1102-v1/native-vector-trace/controller.lua'
    rom = R / 'build/wwf-helper-stable-1102-v2/candidate2.nes'
    assert sha(rom) == PIN
    raw = rom.read_bytes()
    irq = 16 + 126 * 8192
    nmi = 16 + 127 * 8192
    assert raw[irq:irq+3] == bytes.fromhex('488a48')
    assert raw[irq+0x40:irq+0x44] == bytes.fromhex('68aa6840')
    assert raw[nmi+0x33c:nmi+0x341] == bytes.fromhex('488a489848')
    assert raw[nmi+0x40a:nmi+0x410] == bytes.fromhex('68a868aa6840')
    assert raw[nmi+0x1ffa:nmi+0x2000:4] == bytes([0x3c,0])
    old = source.read_text()
    start = old.index("for _,kind in ipairs({'NMI','IRQ'})do")
    end = old.index("emu.addMemoryCallback(function()if active()then assert", start)
    text = old[:start] + BLOCK + old[end:]
    for assertion in [
        "assert(q.kind==kind and q.sp==s['cpu.sp'],'Real vector stack balance')",
        "assert(q.smc==image()and q.a==s['cpu.a']and q.x==s['cpu.x']and q.y==s['cpu.y'],'Vector restores live registers/SMC')",
    ]:
        assert old.count(assertion) == text.count(assertion) == 1
    assert old.split("emu.addEventCallback(function()\n if done then return end;local b={}",1)[1] == \
           text.split("emu.addEventCallback(function()\n if done then return end;local b={}",1)[1]
    # Do not run a full route solely to diagnose interrupt bookkeeping.
    text += r'''
emu.addEventCallback(function()
 if not done and updates>=8 and not lastMain then
  vectorWrite('Eight actual Main returns with strict vector parity intact')
  done=true;csv:close();print('PASS bounded vector sequence diagnostic; fullstage unqualified');emu.stop()
 end
end,emu.eventType.endFrame)
'''
    prepare(O/'native-thomas-vector-sequence',rom,text,[Path(__file__),source],
        expected=PIN,timeout=120,allow_interactive=True,
        scope='Readonly current f5 Thomas vector diagnostic. Unchanged cold/menu/earlyroute inputs and exact stack/AXY/SMC parity assertions. Last128 actual CPU hook events include unfiltered physical translations/admission/depth and entry+1 sentinels; firstmismatch writes one small JSON beforeassert. Stops after8 actualMain returns if no mismatch. No ROM/fullstage/install claim.')
    print('Producer SHA256 '+hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
