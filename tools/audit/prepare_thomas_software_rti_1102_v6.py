"""Classify the actual96:DEC3 software RTI without consuming an NMI frame."""
from pathlib import Path
import hashlib
import json
from prepare_selected_native_packet_v1 import R, prepare, sha

O = R / 'build/bub-menu-candidate-1102-v2'
PIN = 'f5c30ceaa36894f3e814ef277081ecd9cf434a934c0f7b3f514c2291be0e1cfc'
TAIL = bytes.fromhex('a98048a94248ada17d4cc580')

BLOCK = r'''
local softwareFrames,softwarePosts,softwareEvents={},{},{}
counters.software_setup=0;counters.software_rti=0;counters.software_target=0
local function physical(pc,bank)
 local a=emu.convertAddress(pc)
 return a and a.memType==emu.memType.nesPrgRom and a.address//8192==bank
end
local function stackbyte(sp,i)return peek(0x100+((sp+i)&255))end
local function softwareEvent(kind,q)
 if#softwareEvents<16 then
  softwareEvents[#softwareEvents+1]={kind=kind,frame=frame,Main=updates,
   setup_sp=q.sp,status=q.status,return_pc=q.return_pc,old_C=q.old_C,
   outer_depth=q.outer_depth,phase=phase}
 end
end
local function vectorFail(reason)
 local s=emu.getState();local bytes={}
 for i=1,20 do bytes[#bytes+1]=stackbyte(s['cpu.sp'],i)end
 local f=assert(io.open(OUTPUT..'vector-classification.json','w'))
 f:write(json({reason=reason,frame=frame,Main=updates,phase=phase,
  cpu={pc=s['cpu.pc'],sp=s['cpu.sp'],a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y'],p=s['cpu.ps']},
  hardware_pending=isrs,software_pending=softwareFrames,post_pending=softwarePosts,
  software_events=softwareEvents,counters=counters,stack_above_SP=bytes}));f:close()
 assert(false,reason)
end
local function requireVector(ok,reason)if not ok then vectorFail(reason)end end
-- Actual foreign audio return:96:DEC3 pushes8042, then80C5/RTS consumes it
-- and executes the shared8043 RTI with the deliberately built P/B600 frame.
emu.addMemoryCallback(function()
 if not physical(0xdec3,96)or not(active()or lastMain or#isrs>0)then return end
 local s=emu.getState();local sp=s['cpu.sp']
 requireVector(#softwareFrames<8,'Bounded software RTI nesting')
 local q={sp=sp,status=stackbyte(sp,1),return_pc=stackbyte(sp,2)+256*stackbyte(sp,3),
  x=s['cpu.x'],y=s['cpu.y'],p=s['cpu.ps'],old_C=r('CurrentBankC'),smc=image(),outer_depth=#isrs}
 requireVector(q.return_pc==0xb600 and physical(0xb600,63),'Actual foreign audio software RTI destination63:B600')
 softwareFrames[#softwareFrames+1]=q;counters.software_setup=counters.software_setup+1
 requireVector(counters.software_setup<=2*frame+16,'Bounded actual software RTI count')
 softwareEvent('physical96:DEC3-setup',q)
end,emu.callbackType.exec,0xdec3)
emu.addMemoryCallback(function()
 if not physical(0xb600,63)or#softwarePosts==0 then return end
 local q=softwarePosts[#softwarePosts];local s=emu.getState()
 requireVector(s['cpu.sp']==((q.sp+3)&255),'Software RTI consumes exactly its three-byte frame')
 requireVector((s['cpu.ps']&0xef)==(q.status&0xef),'Software RTI restores its original P (B is not a CPU latch)')
 requireVector(s['cpu.a']==q.old_C and s['cpu.x']==q.x and s['cpu.y']==q.y and image()==q.smc,'Software RTI target AXYP/SMC contract')
 table.remove(softwarePosts);counters.software_target=counters.software_target+1
 softwareEvent('physical63:B600-after-software-RTI',q)
end,emu.callbackType.exec,0xb600)
for _,kind in ipairs({'NMI','IRQ'})do
 local entry=kind=='NMI'and L.NonMaskableInterrupt or L.IrqScrollSplit
 local leave=kind=='NMI'and L.NonMaskableInterrupt_RTI or L.IrqScrollSplit_RTI
 assert(entry and leave,'Explicit vector callback addresses')
 local bank=kind=='NMI'and 127 or 126
 emu.addMemoryCallback(function()
  if physical(entry,bank)and(active()or lastMain or#isrs>0)then
   local s=emu.getState();minSP=math.min(minSP,s['cpu.sp']);local t=isrs[#isrs]
   if t and t.kind==kind and t.sp==s['cpu.sp']then return end
   isrs[#isrs+1]={kind=kind,sp=s['cpu.sp'],smc=image(),a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y'],
    status=stackbyte(s['cpu.sp'],1),return_lo=stackbyte(s['cpu.sp'],2),return_hi=stackbyte(s['cpu.sp'],3)}
   counters[kind=='NMI'and'nmi'or'irq']=counters[kind=='NMI'and'nmi'or'irq']+1
  end
 end,emu.callbackType.exec,entry)
 emu.addMemoryCallback(function()
  if not physical(leave,bank)then return end
  local s=emu.getState();local soft=softwareFrames[#softwareFrames]
  if kind=='IRQ'and soft and soft.sp==s['cpu.sp']then
   requireVector(stackbyte(soft.sp,1)==soft.status and stackbyte(soft.sp,2)+256*stackbyte(soft.sp,3)==soft.return_pc,'Exact software RTI P/PC frame retained')
   local expectedP=(soft.p&0x7d)|(soft.old_C&0x80)|(soft.old_C==0 and 2 or 0)
   requireVector(s['cpu.a']==soft.old_C and s['cpu.x']==soft.x and s['cpu.y']==soft.y and s['cpu.ps']==expectedP and image()==soft.smc,'Source software RTI setup-to-opcode AXYP/SMC')
   requireVector(#isrs==soft.outer_depth,'Software RTI must not consume a hardware vector frame')
   table.remove(softwareFrames);softwarePosts[#softwarePosts+1]=soft
   counters.software_rti=counters.software_rti+1;softwareEvent('physical126:8043-software-RTI',soft)
   return
  end
  if#isrs>0 then local q=isrs[#isrs]
   if q.kind~=kind or q.sp~=s['cpu.sp']then vectorFail('Real vector stack balance')end
   assert(q.kind==kind and q.sp==s['cpu.sp'],'Real vector stack balance')
   if q.smc~=image()or q.a~=s['cpu.a']or q.x~=s['cpu.x']or q.y~=s['cpu.y']then vectorFail('Vector restores live registers/SMC')end
   assert(q.smc==image()and q.a==s['cpu.a']and q.x==s['cpu.x']and q.y==s['cpu.y'],'Vector restores live registers/SMC')
   requireVector(q.status==stackbyte(q.sp,1)and q.return_lo==stackbyte(q.sp,2)and q.return_hi==stackbyte(q.sp,3),'Hardware RTI original P/PC stack frame retained')
   table.remove(isrs);counters.vectors=counters.vectors+1
  end
 end,emu.callbackType.exec,leave)
end
'''


def cpu_contract(raw):
    import check_hogan_current_bounded_v1 as N
    from link_pit_rygar_sophia_audit_cpu import scoped_load
    from check_tmnt_render_oa import address
    b = scoped_load(R/'build/wwf-death-1102-v2/candidate.nes')
    b['raw'] = raw
    rows = []
    for status, old_c in [(0xb0,2),(0x75,3),(0xff,2),(0x20,3)]:
        m=N.fresh(b);m.raw_page(1,191);m.raw_page(2,224)
        m[address(b,'CurrentBankC')]=old_c
        m[0x1f1:0x1f4]=[status,0,0xb6]
        smc=bytes(m[0x15a:0x17b])
        c=N.NesMPU(memory=m,pc=0xdec3);c.sp=240;c.a=7;c.x=19;c.y=31;c.p=0x61
        pcs=[]
        for i in range(16):
            if c.pc==0xb600:break
            pcs.append(c.pc);c.step()
        else:raise AssertionError('Bounded software RTI tail')
        assert c.sp==243 and(c.p&0xef)==(status&0xef)
        assert(c.a,c.x,c.y)==(old_c,19,31)and bytes(m[0x15a:0x17b])==smc
        assert m.rawtags[1]==191 and m.rawtags[2]==old_c
        rows.append(dict(status=status,old_C=old_c,final_SP=c.sp,final_P=c.p,
                         actual_PCs=pcs,AXY_SMC_preserved=True))
    return rows


def main():
    source=R/'build/thomas-full11-1102-v1/native-vector-trace/controller.lua'
    rom=R/'build/wwf-helper-stable-1102-v2/candidate2.nes'
    assert sha(rom)==PIN
    raw=rom.read_bytes();offset=16+96*8192+0x1ec3
    assert raw[offset:offset+len(TAIL)]==TAIL
    assert raw[16+126*8192+0x43]==0x40
    rows=cpu_contract(raw)
    old=source.read_text()
    start=old.index("for _,kind in ipairs({'NMI','IRQ'})do")
    end=old.index("emu.addMemoryCallback(function()if active()then assert",start)
    text=old[:start]+BLOCK+old[end:]
    for a in ["assert(q.kind==kind and q.sp==s['cpu.sp'],'Real vector stack balance')",
              "assert(q.smc==image()and q.a==s['cpu.a']and q.x==s['cpu.x']and q.y==s['cpu.y'],'Vector restores live registers/SMC')"]:
        assert old.count(a)==text.count(a)==1
    controls="emu.addEventCallback(function()\n if done then return end;local b={}"
    assert old.split(controls,1)[1]==text.split(controls,1)[1]
    marker=" if done then return end;done=true;shot('endpoint');csv:close()"
    assert text.count(marker)==1
    text=text.replace(marker," if done then return end\n if ok then assert(counters.software_rti>0 and counters.software_target>0,'Positive actual qualified software RTI path');assert(counters.nmi>0 and counters.irq>0 and counters.vectors>0,'Positive genuine hardware NMI/IRQ parity')end\n done=true;shot('endpoint');csv:close()")
    text=text.replace("No RAM writes, full1-1, audio, every upgrade or60Hz claim.","No RAM writes; full1-1 attempt with separately qualified software/hardware RTI paths. Audio waveform/every upgrade/60Hz unqualified.")
    receipt=O/'thomas-software-rti-CPU-v6.json'
    assert not receipt.exists()
    receipt.write_text(json.dumps(dict(passed=True,ROM_SHA256=PIN,ROM_changed=False,
        source=source.as_posix(),source_SHA256=sha(source),producer_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        original_shared_RTI_opcode=0x8043,setup_physical_bank=96,setup_PC=0xdec3,
        target_physical_bank=63,target_PC=0xb600,source_setup_bytes=TAIL.hex(),
        synthetic_original_tail_cases=rows,native_run=False,
        scope='Actual current ROM9-instruction software setup/map/RTS/RTI path consumes P/B600 frame, preservesXY/SMC and lands63:B600. Fixture establishes the observer contract; native positive setup/opcode/target and hardwarevector parity remain required.'),indent=2)+'\n')
    prepare(O/'native-thomas-software-rti',rom,text,[Path(__file__),source,receipt],
        expected=PIN,timeout=240,allow_interactive=True,
        scope='Unchanged currentf5 Thomas full1-1 controller. Exact physically qualified96:DEC3 setup/126:8043softwareRTI/63:B600postreturn checksP/PC/SP/AXY/SMC without poppinghardwareNMI. GenuinehardwareNMI/IRQ retainalloriginalparity assertions plusP/PCframeguards; positiveactualcountsrequired. No ROM/gameplay/install change.')


if __name__=='__main__':
    main()
