"""Require the moving platforms to display the original native tile pixels."""
from pathlib import Path
import json,sys
import prepare_thomas_native_rendered_bounded_v1 as V
import prepare_thomas_native_bounded_v1 as T


def main():
    V.main()
    output=Path(sys.argv[sys.argv.index('--output')+1]).resolve()
    joint=Path(sys.argv[sys.argv.index('--joint')+1]).resolve()
    stage=json.loads((joint/'source-stage.json').read_text())
    misc=T.R/'chr/mmc5/sprites_misc.chr'
    assert stage['native_platform_CHR_sha256']==T.sha(misc)
    path=output/'controller.lua';text=path.read_text(encoding='utf-8')
    old="if ui[stage]and frame-ui[stage].frame<16 then return end"
    assert text.count(old)==1
    text=text.replace(old,"if stage~='native_platform'and ui[stage]and frame-ui[stage].frame<16 then return end",1)
    old=" if not selected()then return end\n if phase=='browse'"
    new=""" if not selected()then return end
 if active()then
  -- The native renderer emits the six parts in this order; their physical
  -- window is now independent of the original Thomas pose's three windows.
  sample(page,{{90,2,0,16},{90,2,0,8},{90,2,0,0},{90,2,0,40},{90,2,0,32},{90,2,0,24}},'native_platform')
 end
 if phase=='browse'"""
    assert text.count(old)==1;text=text.replace(old,new,1)
    old='local function route()'
    new="""local function platformVisible()
 local q=ui.native_platform;if not q or frame-q.frame<1 or frame-q.frame>2 then return false end
 local screen=emu.getScreenBuffer();local colors={}
 for at,nes in pairs(q.expected)do
  local rgb=screen[at+1]&0xffffff
  if colors[nes]and colors[nes]~=rgb then return false end;colors[nes]=rgb
 end
 local distinct={};for _,rgb in pairs(colors)do distinct[rgb]=true end
 local count=0;for _ in pairs(distinct)do count=count+1 end
 return count>=2 and r('DisableScreenFlag')==0 and r('Mirror_PPUMASK')&24==24
end
local function route()"""
    assert text.count(old)==1;text=text.replace(old,new,1)
    old="if visible('game')then finish(counters.defeat"
    assert text.count(old)==1;text=text.replace(old,"if visible('game')and platformVisible()then finish(counters.defeat",1)
    path.write_text(text,encoding='utf-8',newline='\n')
    ready_path=output/'ready.json';ready=json.loads(ready_path.read_text())
    ready['bindings'][str(path)]=T.sha(path)
    ready['bindings'][str(misc)]=T.sha(misc)
    ready['bindings'][str(Path(V.__file__).resolve())]=T.sha(V.__file__)
    ready['bindings'][str(Path(__file__).resolve())]=T.sha(__file__)
    ready['scope']+=' Actual native miscellaneous-platform CHR/OAM/display pixels required at route completion.'
    ready_path.write_text(json.dumps(ready,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
