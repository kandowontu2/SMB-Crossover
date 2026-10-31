"""Observe native early/late lives raster; diagnostic exit cannot admit ROM."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2]
P=R/'build/bt-visible-native-1031-v2/rash'
O=R/'build/bt-lives-scroll-diagnostic-1031-v1/rash'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    q=json.loads((P/'ready.json').read_text())
    for p,h in q['bindings'].items():assert sha(p)==h,p
    s=(P/'controller.lua').read_text()
    marker=" elseif phase=='launch'then\n"
    assert s.count(marker)==1
    s=s.replace(marker,marker+"  if age==80 then shot('lives-late');finish(false,'DIAGNOSTIC ONLY: early/late lives raster');return end\n")
    marker="emu.addEventCallback(function()\n if done then return end;local b={}"
    extra="""
local raster=assert(io.open(OUTPUT..'raster.csv','w'))
raster:write('frame,age,event,address,value,line,dot,PC,bankA,bankC,HorizontalScroll,VerticalScroll,PPUCTRL,PPUMASK\\n')
local rasterCount=0
local function rasterEvent(kind,address,value)
 if phase~='launch'or age>80 then return end
 rasterCount=rasterCount+1;assert(rasterCount<30000,'Bounded raster trace')
 local z=emu.getState()
 raster:write(table.concat({frame,age,kind,address,value,z['ppu.scanline'],z['ppu.cycle'],z['cpu.pc'],r('CurrentBank'),r('CurrentBankC'),r('HorizontalScroll'),r('VerticalScroll'),r('Mirror_PPUCTRL'),r('Mirror_PPUMASK')},',')..'\\n');raster:flush()
end
for _,a in ipairs({0x2000,0x2001,0x2005,0x2006,0x2007})do
 emu.addMemoryCallback(function(_,v)rasterEvent('write',a,v)end,emu.callbackType.write,a)
end
emu.addMemoryCallback(function()rasterEvent('status-read',0x2002,0)end,emu.callbackType.read,0x2002)
emu.addMemoryCallback(function(_,v)
 if phase=='launch'and age==40 then
  local z={};for k,x in pairs(emu.getState())do if type(k)=='string'and k:sub(1,4)=='ppu.'then z[k]=x end end
  local f=assert(io.open(OUTPUT..'PPU-state.json','w'));f:write(json(z));f:close()
 end
end,emu.callbackType.write,0x4014)
"""
    assert marker in s;s=s.replace(marker,extra+'\n'+marker)
    O.mkdir(parents=True)
    (O/'controller.lua').write_text(s,encoding='utf-8',newline='\n')
    (O/'run.py').write_text((P/'run.py').read_text(),encoding='utf-8',newline='\n')
    q.update(diagnostic_only=True,scope='Always exit1 diagnostic: preserve controller inputs through lives age80, early/late images and exactPPU port write timing. No admission claim.')
    q['bindings'].update({str(p.resolve()):sha(p)for p in[Path(__file__),P/'ready.json',O/'controller.lua',O/'run.py']})
    (O/'ready.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(prepared=True,diagnostic_only=True,ready=str(O/'ready.json'),sha256=sha(O/'ready.json'))))


if __name__=='__main__':main()
