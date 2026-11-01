"""Validate displayed pixels at frame end, holding safely after the last pipe."""
from pathlib import Path
import json,sys
import prepare_thomas_native_platform_pixels_bounded_v2 as V
import prepare_thomas_native_bounded_v1 as T


def main():
    V.main()
    output=Path(sys.argv[sys.argv.index('--output')+1]).resolve();path=output/'controller.lua'
    text=path.read_text(encoding='utf-8')
    old='if#clears>=P.pipes then';assert text.count(old)==1
    text=text.replace(old,'if#clears>=P.pipes then\n   pad={} -- stop at the tested endpoint while awaiting displayed-frame validation',1)
    old=" elseif phase=='game'then\n  if r('GameEngineSubroutine')";assert text.count(old)==1
    text=text.replace(old,""" elseif phase=='game'then
  if#clears>=P.pipes and visible('game')and platformVisible()and not lastMain then
   finish(counters.defeat>0 and counters.source==counters.movement and counters.vectors>100,'Four native pipe crossings; displayed character/platform pixels validated at endFrame');return
  end
  if r('GameEngineSubroutine')""",1)
    path.write_text(text,encoding='utf-8',newline='\n')
    ready_path=output/'ready.json';ready=json.loads(ready_path.read_text())
    for p in [path,Path(V.__file__).resolve(),Path(__file__).resolve()]:ready['bindings'][str(p)]=T.sha(p)
    ready['scope']+=' Controller stops after the last pipe; endFrame validates complete displayed pixels instead of requiring coincidence with Main return.'
    ready_path.write_text(json.dumps(ready,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
