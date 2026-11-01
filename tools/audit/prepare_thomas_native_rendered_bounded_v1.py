"""Require the native route to retain its world palette and correct HUD owner."""
from pathlib import Path
import json
import sys
import prepare_thomas_native_bounded_v1 as T


def main():
    T.main()
    output=Path(sys.argv[sys.argv.index('--output')+1]).resolve()
    path=output/'controller.lua';text=path.read_text(encoding='utf-8')
    old='local function route()'
    assert text.count(old)==1
    text=text.replace(old,"local function route()\n if updates>8 then assert(ppu(0x3f00)==34,'Preserve native1-1 sky palette');assert(r('InvHudActive')==0,'Thomas must decline legacy Ryu inventory HUD')end",1)
    old='poses=poses,body_DMA=ui,';assert text.count(old)==1
    text=text.replace(old,"poses=poses,body_DMA=ui,background_palette=ppu(0x3f00),inventory_HUD=r('InvHudActive'),",1)
    path.write_text(text,encoding='utf-8',newline='\n')
    ready_path=output/'ready.json';ready=json.loads(ready_path.read_text())
    ready['bindings'][str(path)]=T.sha(path)
    ready['bindings'][str(Path(__file__).resolve())]=T.sha(__file__)
    ready['scope']+=' World1-1 sky palette and legacy inventory ownership asserted throughout.'
    ready_path.write_text(json.dumps(ready,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
