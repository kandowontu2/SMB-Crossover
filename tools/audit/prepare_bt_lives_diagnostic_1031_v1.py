"""Retain a failing native BT palette/load trace; never qualifies admission."""
from pathlib import Path
import hashlib
import json

R=Path(__file__).resolve().parents[2]
P=R/'build/bt-ready-native-1031-v2/rash'
O=R/'build/bt-lives-diagnostic-1031-v1/rash'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    q=json.loads((P/'ready.json').read_text())
    for p,h in q['bindings'].items():assert sha(p)==h,p
    text=(P/'controller.lua').read_text()
    old="assert(r('SelectedCharacter')==P.raw,'Launched ready raw owner');assert(renderedUI.lives,'Actual visible lives scene before control');"
    assert old in text;text=text.replace(old,"assert(r('SelectedCharacter')==P.raw,'Launched raw owner for failed diagnostic');")
    text=text.replace("assert(sourceFresh>=1,'Genuine BT construction');",'')
    text=text.replace("if not renderedUI.lives and stableUI('lives')then shot('lives')end", "if age==30 then shot('lives-unqualified')end")
    start=text.index("  if age>=360 and not main then finish(")
    end=text.index('\n',start)
    text=text[:start]+"  if age>=90 and not main then finish(false,'DIAGNOSTIC ONLY: native lifecycle/palette trace');return end"+text[end:]
    insert="""
local diagnostic=assert(io.open(OUTPUT..'native-lifecycle.csv','w'))
diagnostic:write('frame,phase,event,A,X,Y,bankA,bankC,mode,task,screenTask,engine,busy,nmiDisable,mask,queue,P0,P1,cookie\\n')
local function note(event)
 local s=emu.getState();local p0,p1={},{}
 for i=1,3 do p0[i]=ppu(0x3f10+i);p1[i]=ppu(0x3f14+i)end
 diagnostic:write(table.concat({frame,phase,event,s['cpu.a'],s['cpu.x'],s['cpu.y'],r('CurrentBank'),r('CurrentBankC'),r('OperMode'),r('OperMode_Task'),r('ScreenRoutineTask'),r('GameEngineSubroutine'),r('FamilyMainCommit'),r('NmiDisable'),r('Mirror_PPUMASK'),r('VRAM_Buffer1_Offset'),table.concat(p0,':'),table.concat(p1,':'),emu.read(0xdfe0,emu.memType.nesDebug)},',')..'\\n');diagnostic:flush()
end
for _,name in ipairs({'SetupIntermediate','GetPlayerColors','BtColdColors','BtAcquire','BtLoad','BtConstruct','WriteGameText','BtStatusName','BtMovement','BtCoreStep','BtColdPortrait'})do
 emu.addMemoryCallback(function()
  local guest=name=='BtConstruct'or name=='BtStatusName'or name=='BtMovement'or name=='BtCoreStep'
  if guest and r('CurrentBank')==3 or not guest and bank(L[name])==B[name]then note(name)end
 end,emu.callbackType.exec,assert(L[name],name))
end
emu.addMemoryCallback(function()if phase=='launch'and age<60 then note('DMA')end end,emu.callbackType.write,0x4014)
"""
    at=text.index('local function stableUI(stage)')
    text=text[:at]+insert+'\n'+text[at:]
    O.mkdir(parents=True)
    (O/'controller.lua').write_text(text,encoding='utf-8',newline='\n')
    (O/'run.py').write_text((P/'run.py').read_text(),encoding='utf-8',newline='\n')
    q.update(scope='DIAGNOSTIC ONLY. Same controller through first90gameframes; trace actual load/lives palette calls. Always fails and must never qualify admission.',diagnostic_only=True)
    q['bindings'].update({str(p.resolve()):sha(p)for p in[Path(__file__),P/'ready.json',O/'controller.lua',O/'run.py']})
    (O/'ready.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(prepared=True,diagnostic_only=True,ready=str(O/'ready.json'),sha256=sha(O/'ready.json'))))


if __name__=='__main__':main()
