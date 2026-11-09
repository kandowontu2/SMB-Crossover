"""Rebind the exact Thomas camera candidate with contact-gated controller recovery."""

import argparse
import json
from pathlib import Path

from prepare_selected_native_packet_v1 import R, prepare, sha


BASE=R/'build/helper-camera-native-1110/thomas'
PIN='5444f3e3bcb07c8314ba6f17b067f2e678eb4ec668786456e4f26d56ba8d75a2'
START='local stepProbes,lastStepProbe={},nil\nlocal function route()'
RETRY="""local stepProbes,lastStepProbe={},nil
local function retryBoard(reason)
 routeState='retry';runup=0;hop=0;previous=nil
 local key='lift_retry_'..reason
 counters[key]=(counters[key] or 0)+1
end
local function route()"""
OLD=""" if near then pad={down=true,b=updates%24<6}
 elseif routeState=='approach'then pad={right=true};if x>=lift-24 then routeState='wait';pad={}end
 elseif routeState=='wait'then pad={};if ly and ly>=188 and(not previous or ly>=previous)then routeState='runup';runup=0 end
 elseif routeState=='runup'then pad={right=true};runup=runup+1;if runup>=6 then routeState='hop';hop=0 end
 elseif routeState=='hop'then pad={right=true,up=hop<3};hop=hop+1;if x>=lift+14 then routeState='ride'end
 elseif routeState=='ride'then pad={};if py+32<=pipeTop-16 then routeState='cross';hop=0 end
 else pad={right=true,up=hop>=6 and hop<9};hop=hop+1 end"""
NEW=""" local boarded=slot~=nil and contact==slot
 local grounded=r('Player_State')==0
 if near then
  if not boarded and (routeState=='runup'or routeState=='hop')then retryBoard('combat')end
  pad={down=true,b=updates%24<6}
 elseif routeState=='retry'then
  pad={}
  if boarded and x>=lift+14 then routeState='ride'
  elseif grounded and x>lift-24 then pad={left=true}
  elseif grounded then routeState='wait';previous=nil end
 elseif routeState=='approach'then pad={right=true};if x>=lift-24 then routeState='wait';pad={}end
 elseif routeState=='wait'then pad={};if ly and ly>=188 and(not previous or ly>=previous)then routeState='runup';runup=0 end
 elseif routeState=='runup'then pad={right=true};runup=runup+1;if runup>=6 then routeState='hop';hop=0 end
 elseif routeState=='hop'then
  pad={right=true,up=hop<3};hop=hop+1
  if x>=lift+14 then
   if boarded then routeState='ride'
   else
    pad={}
    if grounded or hop>=64 then retryBoard('missed')end
   end
  elseif hop>=64 and not boarded then pad={};retryBoard('missed')end
 elseif routeState=='ride'then
  pad={}
  if boarded and py+32<=pipeTop-16 then routeState='cross';hop=0
  elseif grounded and not boarded then retryBoard('lost')end
 else pad={right=true,up=hop>=6 and hop<9};hop=hop+1 end"""


def transform(text):
    assert text.count(START)==1 and text.count(OLD)==1
    return text.replace(START,RETRY).replace(OLD,NEW)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    old_ready=BASE/'ready.json'
    ready=json.loads(old_ready.read_text())
    rom=Path(ready['ROM'])
    assert ready['ROM_sha256']==sha(rom)==PIN
    for path,digest in ready['bindings'].items():
        assert sha(Path(path))==digest,path
    controller=BASE/'controller.lua'
    scope=('Cold controller-only Thomas 1-1 into active 1-2. Six offscreen constructors, '
           'native support, assisted crossings, source art and real hardware vector checks. '
           'Combat or a missed board retries from the existing approach point. Same capture set.')
    prepare(args.output,rom,transform(controller.read_text()),[Path(__file__),old_ready,controller],
            expected=PIN,timeout=240,scope=scope,allow_interactive=True)
    out_ready=args.output/'ready.json'
    data=json.loads(out_ready.read_text())
    data['timeout']=ready['timeout']
    out_ready.write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':
    main()
