"""Retest Thomas's known first floor gap with the native trailing-foot window."""

import argparse
import json
from pathlib import Path

from prepare_selected_native_packet_v1 import R, prepare, sha


BASE=R/'build/helper-camera-thomas-recovery-1110'
PIN='5444f3e3bcb07c8314ba6f17b067f2e678eb4ec668786456e4f26d56ba8d75a2'


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def transform(text):
    text=once(text,'local maxX,maxCamera=0,0','local maxX,maxCamera=0,0\nlocal gapProbe={}')
    text=once(text,'poses=poses,body_DMA=ui,background_palette=',
              'poses=poses,body_DMA=ui,first_floor_gap=gapProbe,background_palette=')
    text=once(text,
              'Cold controller-only native run; original staged CHR/pixels, real interrupts and native moving-platform crossings.',
              'Cold controller-only native run; sampled original CHR/pixels, real interrupts and all native moving-platform crossings.')
    text=once(text,''' if active()then
  -- The native renderer emits the six parts in this order; their physical''',
              ''' if active()and target==1 and routeState=='ride' and not ui.platform_shot then
  -- Retain the first boarding snapshot without rescanning later DMAs.
  -- The native renderer emits the six parts in this order; their physical''')
    text=once(text," elseif active()and body then sample(page,body,'game')end",
              """ elseif active()and body and (not ui.game or frame%96==0 or
        (target==1 and routeState=='ride' and not ui.platform_shot))then
  sample(page,body,'game')
 end""")
    text=once(text,'''  pad={right=true}
  if r('Player_State')==0 then''',
              '''  pad={right=true}
  local grounded=r('Player_State')==0
  if gapProbe.trigger and x>=1360 and x<1450 then
   if not grounded and not gapProbe.airborne then
    gapProbe.airborne={frame=frame,Main=updates,x=x,y=py}
   elseif grounded and x>=1412 and gapProbe.airborne and not gapProbe.landing then
    gapProbe.landing={frame=frame,Main=updates,x=x,y=py}
   end
  end
  if grounded then''')
    text=once(text,'   if not support or foot then pad.up=updates%8<3 end',
              '''   local gap=x>=1350 and x<1424 and py==176
   local leftSupport,leftTile
   if gap then
    -- Thomas's native row0 feet are X+3 and X+12 at Y+32.
    -- At this 1376..1423 gap the trailing foot is supported through X1372.
    leftSupport,leftTile=solid(x+3,py+32)
    pad.up=x>=1370 and leftSupport and not support
   elseif not support or foot then pad.up=updates%8<3 end''')
    text=once(text,'''   end
  end
  if updates%10==0 then csv:write''',
              '''   end
   if gap and pad.up and not gapProbe.trigger then
    gapProbe.trigger={frame=frame,Main=updates,x=x,y=py,left_tile=leftTile,right_tile=supportTile}
   end
  end
  if updates%10==0 then csv:write''')
    return text


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    ready_path=BASE/'ready.json'
    controller=BASE/'controller.lua'
    failed_path=BASE/'capture/result.json'
    failed=json.loads(failed_path.read_text())
    ready=json.loads(ready_path.read_text())
    rom=Path(ready['ROM'])
    assert sha(rom)==ready['ROM_sha256']==failed['ROM_sha256']==PIN
    assert not failed['passed'] and failed['maximum_X']==1418 and failed['Main']==3090
    assert [q['pipe_X'] for q in failed['pipe_clears']]==[448,608,736,912]
    for path,digest in ready['bindings'].items():
        assert sha(Path(path))==digest,path
    scope=('Cold controller-only Thomas full 1-1 into active 1-2 with all six offscreen '
           'constructors, boardings and crossings. Keep real hardware/software interrupt '
           'assertions and sample original pixel data by phase. Retiming is limited to the '
           'X1376–1423 floor gap. Same capture set.')
    prepare(args.output,rom,transform(controller.read_text()),
            [Path(__file__),ready_path,controller,failed_path],expected=PIN,timeout=240,
            scope=scope,allow_interactive=True)
    output_ready=args.output/'ready.json'
    data=json.loads(output_ready.read_text())
    data['timeout']=ready['timeout']
    output_ready.write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':
    main()
