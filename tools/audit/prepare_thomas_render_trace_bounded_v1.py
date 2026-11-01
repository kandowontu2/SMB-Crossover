"""Short read-only palette/HUD diagnostic for the native Thomas rendering defect."""
from pathlib import Path
import json
import sys
import prepare_thomas_native_bounded_v1 as T


def main():
    T.main()
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    target = output / 'controller.lua'
    text = target.read_text(encoding='utf-8')
    changes = [
        ("local phase,done='title',false", "local phase,done='title',false\nlocal paletteTrace,uiTrace={},{}"),
        ('poses=poses,body_DMA=ui,', "poses=poses,body_DMA=ui,palette_writes=paletteTrace,UI_entries=uiTrace,background_palette=ppu(0x3f00),inventory_HUD=r('InvHudActive'),"),
        ('local function route()', '''emu.addMemoryCallback(function(_,value)
 if phase~='launch'and phase~='game'then return end
 local s=emu.getState();local at=s['ppu.videoRamAddr']&0x3fff
 if at>=0x3f00 and at<0x4000 and#paletteTrace<80 then
  local stack={};for i=1,16 do stack[#stack+1]=peek(0x100+((s['cpu.sp']+i)&255))end
  paletteTrace[#paletteTrace+1]={frame=frame,Main=updates,address=at,value=value,pc=s['cpu.pc'],bank=r('CurrentBank'),C=r('CurrentBankC'),SP=s['cpu.sp'],stack=stack}
 end
end,emu.callbackType.write,0x2007)
for _,name in ipairs({'InventorySupported','InventoryHud','InventoryUiTick','ThWorld','HuNativeWorldPalette'})do
 emu.addMemoryCallback(function()
  if phase=='launch'or phase=='game'then
   local expected=B[name]and(B[name]|128)
   if expected and raw(L[name])==expected and#uiTrace<40 then
    local s=emu.getState();uiTrace[#uiTrace+1]={name=name,frame=frame,Main=updates,A=s['cpu.a'],Y=s['cpu.y'],sky=ppu(0x3f00),bank=r('CurrentBank')}
   end
  end
 end,emu.callbackType.exec,assert(L[name],name))
end
local function route()'''),
        ("elseif phase=='game'then\n  if r('GameEngineSubroutine')", "elseif phase=='game'then\n  if updates>=40 and not lastMain then finish(true,'Short palette/HUD diagnostic only');return end\n  if r('GameEngineSubroutine')"),
    ]
    for old, new in changes:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    target.write_text(text, encoding='utf-8', newline='\n')
    ready_path = output / 'ready.json'
    ready = json.loads(ready_path.read_text())
    ready['timeout'] = 90
    ready['scope'] = 'Short palette/HUD diagnostic only; not route admission.'
    ready['bindings'][str(target)] = T.sha(target)
    ready['bindings'][str(Path(__file__).resolve())] = T.sha(__file__)
    ready_path.write_text(json.dumps(ready, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
