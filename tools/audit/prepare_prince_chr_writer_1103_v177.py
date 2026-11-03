"""Bind a finite last-writer observation to the unchanged native176 candidate."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
import build_storage_guard_v1 as G
O=R/'build/prince-chr-owner-1103-v177'
P=R/'build/prince-native-followup-1103-v176/native'


def main():
    G.preflight(private_root=O,reserved_bytes=100000,reserved_files=4,fresh=True)
    q=json.loads((P/'ready.json').read_text())
    for path,h in q['bindings'].items():assert sha(path)==h,path
    text=(P/'controller.lua').read_text()
    anchor='local dmaCount,drawReturns,metaCalls=0,0,0'
    assert text.count(anchor)==1
    text=text.replace(anchor,anchor+'''
local chr0Events,chrUpper={},0
local function chrEvent(address,value)
 if not sourceActive()or renderEvidence then return end
 require(#chr0Events<192,'Finite pre-snapshot CHR0 writer census')
 local s=emu.getState();local pc=s['cpu.pc'];local a=emu.convertAddress(pc)
 local am=emu.convertAddress(0xa000);local cm=emu.convertAddress(0xc000)
 chr0Events[#chr0Events+1]={address=address,value=value,upper=chrUpper,physical_page=address==0x5120 and value+256*chrUpper or nil,
  stamp=stamp(),writer_physical=a and a.address or nil,writer_memory=a and a.memType or nil,
  mapA=am and am.address or nil,mapC=cm and cm.address or nil,
  A=s['cpu.a'],X=s['cpu.x'],Y=s['cpu.y'],P=s['cpu.ps'],source_phase=ps(0xa6),source_frame=ps(0x617),
  CurrentCHRBank0=ram(0x147),X5ChrMode0=ram(0x73e0),ReloadCHRBank=ram(0x146),
  opcodes=bytes(pc,6),stack=bytes(0x100+((s['cpu.sp']+1)%256),math.min(20,255-s['cpu.sp']))}
end
emu.addMemoryCallback(function(a,v)chrUpper=v&3;chrEvent(a,v)end,emu.callbackType.write,0x5130)
for _,address in ipairs({0x147,0x73e0,0x5120})do emu.addMemoryCallback(chrEvent,emu.callbackType.write,address)end
''')
    old='captured_after_draw_and_DMA=true,DMA=q,parts=parts'
    assert text.count(old)==1
    text=text.replace(old,'captured_after_draw_and_DMA=true,CHR0_events=chr0Events,graphics_qualified=false,DMA=q,parts=parts')
    text=text.replace('Q.mode="Prince-render-turn176"','Q.mode="Prince-CHR0-writer177"')
    # First actual hardware image suffices for this finite writer trace.
    old="completePart();beginPart('right-short')"
    assert text.count(old)==1
    text=text.replace(old,"completePart();summary(true,'Finite actual CHR0 writer diagnostic complete; graphics not qualified');csv:close();finish()")
    assert 'emu.write'not in text
    refs={Path(__file__),P/'controller.lua',P/'ready.json',*map(Path,q['bindings'])}
    O.mkdir(exist_ok=True)
    prepare(O/'native',Path(q['ROM']),text,refs,expected=q['ROM_sha256'],timeout=240,allow_interactive=True,
            scope='Read-only unchanged6c9e. Same actual menu/cold/first8 and sourcephase/draw/DMA observer176. Neutral controller; stop after first completed source body/DMA/display snapshot. Finite at most192actual writes to CurrentCHRBank0/Mode0/5130/5120 with exactPC/physicalmap/SP/topstack, retained in render-evidence.json. Graphics remain unqualified; no repair/ROM mutation. Maximum2PNG; no perframe dumps.')


if __name__=='__main__':main()
