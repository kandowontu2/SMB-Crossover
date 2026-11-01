"""Count each displayed body/platform observation independently along the route."""
from pathlib import Path
import json,sys
import prepare_thomas_native_platform_pixels_bounded_v2 as V
import prepare_thomas_native_bounded_v1 as T


def main():
    V.main()
    output=Path(sys.argv[sys.argv.index('--output')+1]).resolve();path=output/'controller.lua'
    text=path.read_text(encoding='utf-8')
    old='local function route()';assert text.count(old)==1
    text=text.replace(old,'local finalFrame=nil\n'+old,1)
    old='if#clears>=P.pipes then';assert text.count(old)==1
    text=text.replace(old,"""if#clears>=P.pipes then
   pad={};finalFrame=finalFrame or frame -- stop before the next gap
   if(counters.body_pixels or 0)>10 and(counters.platform_pixels or 0)>10 then
    finish(counters.defeat>0 and counters.source==counters.movement and counters.vectors>100,'Four pipe crossings with independently observed displayed body/platform pixels');return
   end""",1)
    old=" elseif phase=='game'then\n  if r('GameEngineSubroutine')";assert text.count(old)==1
    text=text.replace(old,""" elseif phase=='game'then
  if visible('game')then counters.body_pixels=(counters.body_pixels or 0)+1 end
  if platformVisible()then counters.platform_pixels=(counters.platform_pixels or 0)+1 end
  if finalFrame and frame-finalFrame>=90 then finish(false,'Endpoint pixel-observer deadline');return end
  if r('GameEngineSubroutine')""",1)
    path.write_text(text,encoding='utf-8',newline='\n')
    ready_path=output/'ready.json';ready=json.loads(ready_path.read_text())
    for p in [path,Path(V.__file__).resolve(),Path(__file__).resolve()]:ready['bindings'][str(p)]=T.sha(p)
    ready['scope']+=' Independent endFrame counters must each exceed10 displayed body/platform frames during the same four-pipe run; stop at endpoint and fail after90 additional frames if insufficient.'
    ready_path.write_text(json.dumps(ready,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
