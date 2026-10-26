"""Diagnose the original failed pipe controller offline, without a native run.

Uses immutable native trace plus exact compiled contact/motion owners in an
explicit isolated empty-world/two-pipe-cell CPU arena. This is no area replay.
"""
from pathlib import Path
import argparse,csv,hashlib,json
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SHA='5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30'


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['native-run','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rom=a.native_run/'candidate.nes';assert sha(rom)==SHA
 b=scoped_load(rom);events=[json.loads(x)for x in (a.native_run/'lifecycle-events.jsonl').read_text().splitlines()]
 found=next(x for x in events if x['kind']=='natural-enterable-pipe-found')
 trace=[{k:int(v)for k,v in row.items()}for row in csv.DictReader((a.native_run/'trace.csv').open())]
 first=next(x for x in trace if x['frame']==found['ppu']['frame']-1)
 pipe_x,pipe_y=found['x'],found['top'];assert (pipe_x,pipe_y)==(912,144)
 rows=[];motions=[]
 def setup(x=920,y=136,camera=800,buttons=4):
  q=Arena(b,18)
  sx=x-camera+8;sy=y-24
  q.put(VvVariant=1,VvInitialized=0x76,VvLife=2,VvAlive=1,NumberofLives=2,VvNeedEntry=0,VvSpeed=0,
        PnInitialized=0x50,PnType=1,PnActive=128,PnDrawFlags=1,PnSkin=1,PnX=sx,PnY=sy,VvObjX=sx,VvObjY=sy,
        Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=y,ScreenLeft_X_Pos=camera&255,
        ScreenLeft_PageLoc=camera>>8,SavedJoypadBits=buttons,Up_Down_Buttons=buttons&12,ScrollLock=0)
  q.array('Block_Buffer_1',[0]*416)
  return q
 def putcell(q,x,y,v):q.set('Block_Buffer_1',v,(x//256%2)*208+((y-32)//16)*16+(x%256)//16)
 try:
  for y in [135,136,143,151,152]:
   for x in range(912,937):
    for buttons in [0,4]:
     q=setup(x,y,buttons=buttons);putcell(q,pipe_x,pipe_y,0x10);putcell(q,pipe_x+16,pipe_y,0x11)
     # Enter the real movement suffix AFTER native motion. This tests exact
     # point contact geometry without synthesizing motion to a desired result.
     q.invoke('VvMovement::MotionReady');entered=q.get('GameEngineSubroutine')==3
     expected=917<=x<=922 and 136<=y<=151 and buttons==4
     assert entered==expected,(x,y,buttons,entered,q.get('GameEngineSubroutine'))
     if entered:assert q.get('ChangeAreaTimer')==48 and q.get('DisableCollisionDet')==0
     rows.append(dict(x=x,y=y,buttons=buttons,entered=entered,engine=q.get('GameEngineSubroutine'),source_only_two_cell_arena=True))
  for buttons in [0,1,2]:
   q=setup(925,104,688,buttons);seq=[]
   for tick in range(20):
    before=q.get('Player_X_Position')+256*q.get('Player_PageLoc');cam=q.get('ScreenLeft_X_Pos')+256*q.get('ScreenLeft_PageLoc')
    q.invoke('VvMovement');q.invoke('VvScrollGate')
    after=q.get('Player_X_Position')+256*q.get('Player_PageLoc');newcam=q.get('ScreenLeft_X_Pos')+256*q.get('ScreenLeft_PageLoc')
    seq.append(dict(tick=tick,world_x=after,camera=newcam,world_step=after-before,camera_step=newcam-cam,screen_x=after-newcam,
                    native_screen_x=q.get('PnX'),native_fraction=q.get('PnXF')))
   motions.append(dict(buttons=buttons,start_world_x=925,start_camera=688,sequence=seq,source_only_empty_world=True))
 except Exception as ex:
  (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(ex),contacts=rows,motions=motions),indent=2)+'\n');raise
 assert first['x']>922 and first['x']-first['camera']==237
 assert not any(x['kind']in ['actual-native-pipe-request','actual-native-vertical-pipe-owner','actual-area-change']for x in events)
 left=motions[2]['sequence'];assert all(x['world_x']>=925 for x in left),'Source lead contradicted: initial Left could recover target'
 native_span=[x for x in trace if 1177<=x['frame']<=1219]
 (a.output/'contacts.json').write_text(json.dumps(rows,indent=2)+'\n');(a.output/'motions.json').write_text(json.dumps(motions,indent=2)+'\n')
 (a.output/'native-target-prefix.json').write_text(json.dumps(native_span,indent=2)+'\n')
 result=dict(passed=True,native_run=False,ROM_sha256=SHA,actual_native_pipe_found=found,preceding_trace=first,
             compiled_contact_cases=len(rows),compiled_motion_updates=60,exact_entry_playerX=[917,922],exact_entry_playerY=[136,151],
             actual_first_target_behind_entry_window=True,actual_native_pipe_requests=0,original_controller_failed=True,
             source_plan='Discover ahead while holding roughly screenX112 instead of driving to237. Align above pipe before entering x917..922, use the genuine native Left/autoscroll relationship to stall there and Down to enter. Discard an irrecoverably passed target rather than chase it indefinitely. A separately versioned controller still needs chronological source/mock checks and native reachability; no source game fix inferred.',
             limits='Explicit isolated CPU two-cell/empty-world setup, ordinary native motion speed0 and forced per-call button inputs. No full area parser/NMI/PPU/DMA/replay or Buffer2 overlap success. Actual old trace remains unchanged; this diagnoses its fixture policy.',
             files={f.name:sha(f)for f in a.output.glob('*.json')},
             bindings={str(f.resolve()):sha(f)for f in [Path(__file__),rom,rom.with_suffix('.dbg'),a.native_run/'trace.csv',a.native_run/'inputs.csv',a.native_run/'lifecycle-events.jsonl',a.native_run/'lifecycle-proof.json']})
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
