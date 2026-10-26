"""Offline selected-frame and telemetry review of one completed current route."""
from pathlib import Path
from collections import Counter
import argparse,csv,hashlib,json
from PIL import Image,ImageDraw
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open()))
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def active(x):return x['mode']=='1'and x['task']=='3'and x['engine']=='8'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 route=a.native/a.case;direct=a.native/(a.case+'-direct');m=json.loads((route/'manifest.json').read_text());d=json.loads((direct/'proof.json').read_text());assert m['result']['cleared']and m['result']['deaths']==0 and d['passed']
 trace=read(direct/'trace.csv');render=read(direct/'render.csv');working=[x for x in trace if active(x)and x['world']==x['level']=='0'];assert working
 mode=0 if m['config']['behavior']=='easy'else 1;assert {int(x['behaviorVersion'])for x in render if active(x)}=={mode}
 comparisons={}
 for n in ['inputs.csv','trace.csv','events.csv','render.csv','audio-events.csv','oam.csv','chr.csv','chr-commit.csv','scroll-writes.csv','stomp-events.csv','completed-loop-motion.csv']:
  comparisons[n]=dict(exact=(route/n).read_bytes()==(direct/n).read_bytes(),discovery_sha256=sha(route/n),replay_sha256=sha(direct/n))
 assert all(x['exact']for n,x in comparisons.items()if n!='events.csv'),comparisons
 entry=int(m['result']['stage_entries']['0-0'])
 old_events=read(route/'events.csv');new_events=read(direct/'events.csv')
 assert [x for x in old_events if int(x['frame'])>=entry]==[x for x in new_events if int(x['frame'])>=entry]
 comparisons['events.csv'].update(gameplay_suffix_exact=True,first_native_stage_frame=entry,
  discovery_pregame_rows=[x for x in old_events if int(x['frame'])<entry],replay_pregame_rows=[x for x in new_events if int(x['frame'])<entry],
  reason='Original live-menu selectionDone logger opens before fixed replay selectionDone; untouched pregame event rows retained. All gameplay rows compare literally.')
 transitions=[]
 for before,x in zip(trace,trace[1:]):
  if x['world']==before['world']=='0'and x['level']==before['level']=='0'and x['mode']=='1'and x['task']=='3'and x['power']!=before['power']:
   transitions.append(dict(frame=int(x['frame']),old=int(before['power']),new=int(x['power']),x=int(x['x']),y=int(x['y']),engine=int(x['engine'])))
 # Selected whole frames include route progress, source firing pose, tier/status
 # transitions and real destination control. These are samples, not full review.
 available={int(f.stem):f for f in(direct/'frames').glob('*.png')};nums=sorted(available);near=lambda n:min(nums,key=lambda v:abs(v-n))
 selected=[near(252),near(int(working[0]['frame']))]
 selected += [near(int(working[round(j*(len(working)-1)/7)]['frame']))for j in range(1,7)]
 firing=next((x for x in render if active(x)and int(x['shoot'])>0),None)
 selected.append(near(int(firing['frame']))if firing else near(int(working[len(working)//3]['frame'])))
 selected += [near(int(working[-1]['frame'])),near(nums[-1]-10),nums[-1]]
 interaction=[]
 for z in transitions[:2]:interaction += [near(z['frame']+v)for v in[-4,-1,0,1,60,100]]
 if not interaction:
  n=int(firing['frame'])if firing else int(working[len(working)//2]['frame']);interaction=[near(n+v)for v in[-5,-1,0,1,10,30,60,100]]
 bindings=[]
 for label,choice in [('overview',selected),('status-window',interaction)]:
  sheet=Image.new('RGB',(1024,260*((len(choice)+3)//4)),'#202020');draw=ImageDraw.Draw(sheet)
  for i,n in enumerate(choice):
   f=available[n];im=Image.open(f).convert('RGB');x,y=i%4*256,i//4*260;sheet.paste(im,(x,y+20));draw.text((x,y),a.case+' '+str(n),fill='white');bindings.append(dict(sheet=label,frame=n,path=str(f),sha256=sha(f)))
  sheet.save(a.output/(label+'-actual-PPU.png'))
 put(a.output/'selected-frames.json',bindings)
 sound=read(direct/'audio-events.csv');events=read(direct/'events.csv');stomps=json.loads((direct/'stomp-summary.json').read_text());motion=json.loads((direct/'completed-loop-motion.json').read_text())
 z=dict(passed=True,offline_only=True,agent_visual_review=False,identity=m['config']['name'],mode=m['config']['behavior'],actual_numeric_mode=mode,ROM_sha256=d['ROM_sha256'],
  result=d['result'],direct_PPU_frames=d['direct_frames'],comparisons=comparisons,completed_loop=motion,source_CHR_commit=d['body_chr'],
  numeric_modes_observed=sorted({int(x['behaviorVersion'])for x in render if active(x)}),stomps=stomps,
  power_status_values=sorted({int(x['power'])for x in working}),power_status_transitions=transitions,
  active_video_pose_rows={n:sum(int(x[n])!=0 for x in render if active(x))for n in['crouch','attack','shoot','wall','ceiling','hover','pitFlight']},
  request_store_events=[dict(name=k[0],value=k[1],stores=v)for k,v in sorted(Counter((x['event'],int(x['value']))for x in sound).items())],
  event_classes=dict(Counter(x['event']for x in events)),hardware_APU_write_count=sum(int(x['apuWrites'])for x in render),hardware_expansion_write_count=sum(int(x['expansionWrites'])for x in render),
  selected_whole_frame_samples=len(selected),selected_interaction_samples=len(interaction),selected_frame_bindings_sha256=sha(a.output/'selected-frames.json'),
  limits='Actual saved source/request/pose/status telemetry and selected actual wholePPU samples only. Power readback changes do not alone identify item owner/type. Sound request stores and perframe hardware activity are not audible/correct-source/duration proofs or distinct-use counts. No everyitem/weapon/SFX/physics/flicker/fidelity/60Hz/global completion claim.')
 put(a.output/'proof.json',z);print(json.dumps(dict(case=a.case,frames=d['direct_frames'],all_gameplay_comparison_files_exact=True,full_event_file_exact=comparisons['events.csv']['exact'],power_transitions=transitions,overview=str(a.output/'overview-actual-PPU.png'),window=str(a.output/'status-window-actual-PPU.png')),indent=2))
if __name__=='__main__':main()
