-- Authored render-time actor arenas. No CPU/ROM/state patches or traversal
-- claim. Restore the actor pool before the next native physics update.
local frame,index,depth=0,0,0
local pending,calls=nil,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,assert(pc))end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced firebar admission interrupts')end,emu.callbackType.exec,assert(pc))end
local cases={}
for slot=0,5 do for _,id in ipairs({0,0x1a,0x1b,0x22,0x23,255})do for _,flag in ipairs({0,1,128})do for _,parts in ipairs({0,1,12,13})do cases[#cases+1]={slot=slot,id=id,flag=flag,parts=parts}end end end end
local out=assert(io.open(OUTPUT..ROM_NAME..'-firebar-admission.csv','w'))
out:write('case,slot,id,flag,parts,helperCalls,bankRestored,exhaustedSlot\n')
emu.addMemoryCallback(function()
 if frame<600 or depth~=0 or r('CurrentBank')%128~=4 then return end
 assert(not pending,'Previous render admission completed')
 index=index+1;local q=cases[index]
 if not q then out:close();print('PASS '..#cases..' actual firebar render admission arenas: all6 slots, ID edges, inactive/duplicate/live flags, valid/invalid part counts, PRG restoration');emu.stop(0);return end
 pending=q;calls=0;q.bank=r('CurrentBankC')
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_ID',6,i);w('FirebarPartCount',0,i)end
 w('Enemy_ID',q.id,q.slot);w('Enemy_Flag',q.flag,q.slot);w('FirebarPartCount',q.parts,q.slot)
 for i=0,71 do w('FirebarPartX',80+i%12*8,i);w('FirebarPartY',80,i)end
end,emu.callbackType.exec,assert(L.WorldFirebarAdmission))
emu.addMemoryCallback(function()
 if pending and depth==0 and r('CurrentBank')%128==7 then calls=calls+1 end
end,emu.callbackType.exec,assert(L.DrawWorldFirebars))
emu.addMemoryCallback(function()
 if not pending or depth~=0 or r('CurrentBank')%128~=4 then return end
 local q=pending
 local primary=q.flag==1 and q.id>=0x1b and q.id<0x23 and q.parts>0 and q.parts<13
 assert(not primary or calls==1,'Every valid live owner retains native rendering')
 assert(calls<=1,'One native firebar pass per draw')
 if q.id<0x1b or q.id>=0x23 then assert(calls==0,'No eligible IDs avoid the redundant banked pass')end
 assert(r('CurrentBankC')==q.bank,'The player/data PRG window is preserved')
 assert(r('FirebarSlot')==255,'Exhausted native scratch slot is preserved')
 out:write(table.concat({index,q.slot,q.id,q.flag,q.parts,calls,1,r('FirebarSlot')},',')..'\n')
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_ID',6,i);w('FirebarPartCount',0,i)end
 pending=nil
end,emu.callbackType.exec,assert(L.WorldFirebarAdmissionDone))
emu.addEventCallback(function()emu.setInput({start=frame==60 or frame==240},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=550 and not pending then for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_ID',6,i)end end
 assert(frame<1600,'Bounded actual firebar admission matrix')
end,emu.eventType.endFrame)
