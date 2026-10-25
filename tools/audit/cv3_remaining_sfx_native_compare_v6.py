"""Exact native pair census and original-CV3 raw per-voice stream oracle."""
from pathlib import Path
import argparse,collections,csv,hashlib,json
from cv3_primary_sfx_source_v1 import Original,CV3,CV3_SHA

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):return[{k:int(v)for k,v in r.items()}for r in csv.DictReader(p.open())]
def runlen(rs,key):
 best=now=0
 for r in rs:
  now=now+1 if r[key]==0 else 0;best=max(best,now)
 return best

def oracle(p,j):
 fx=rows(p/'source-voices.csv');ap=rows(p/'apu.csv');requests=rows(p/'requests.csv');byepoch=collections.defaultdict(list);rq=collections.defaultdict(list);mapping={26:0x1f,27:0x13,28:0x15,29:0x24,30:0x21,31:0x1e,32:0x2f}
 for r in ap:byepoch[r['audioEpoch']].append(r)
 for r in requests:
  if r['request']in mapping:rq[r['audioEpoch']+1].append(mapping[r['request']])
 o=Original(CV3.read_bytes());assert sha(CV3)==CV3_SHA;o.call(0xe227);checked=[];reset=False;c=j['cases'][0];profile=j['profile'];previous_paused=False;resume_replays=[]
 for r in fx:
  if not reset and(profile=='scene'and(r['wall']>c['sceneReturnWall']if c.get('sceneReturnWall')is not None else r['wall']>c['firstActionWall']+2)or profile=='death'and r['death']!=0):o.call(0xe227);reset=True
  for e in rq[r['audioEpoch']]:o.call(0xe25f,a=e)
  if r['paused']:previous_paused=True;continue
  resumed=previous_paused;previous_paused=False
  wanted=(o.m[0x10a],o.m[0x10d]);o.m.trace=[];o.call(0xe24e)
  for voice,regs in[(0,[0x4000,0x4001,0x4002,0x4003]),(1,[0x400c,0x400e,0x400f])]:
   if wanted[voice]:
    expected=sorted((x['address'],x['value'])for x in o.m.trace if x['address']in regs);actual=sorted((x['register'],x['value'])for x in byepoch[r['audioEpoch']]if x['register']in regs)
    if resumed:
     # Existing GuestAudioFinish invalidates GuestApuLast after4015 mute:
     # resume must restore held register images to reload length counters.
     # Check every extra raw write against original complete held APU state;
     # this is explicitly a common pause adapter replay, not a new source tick.
     assert all(pair in actual for pair in expected),(p.name,r['audioEpoch'],'Resume omitted original source store',actual,expected)
     assert all(value==o.m[reg]for reg,value in actual),(p.name,r['audioEpoch'],'Resume raw held-image mismatch',actual)
     resume_replays.append(dict(audioEpoch=r['audioEpoch'],voice=voice,original_new_stores=expected,common_held_image_replay=actual))
    else:assert actual==expected,(p.name,r['audioEpoch'],wanted,actual,expected)
    checked.append(dict(audioEpoch=r['audioEpoch'],voice=voice,originalID=wanted[voice],raw_register_writes=len(expected)))
  if j['event']!=0x1f and j['ROM_sha256']!=j.get('baseline_ROM_sha256'):
   # Legacy1F deliberately retains its fast-path representation; new source
   # IDs must match the actual executable original after its source tick.
   if r['owned']&0x0f or r['pulseID']or r['noiseID']:
    assert(r['pulseID'],r['noiseID'])==(o.m[0x10a],o.m[0x10d]),(p.name,r,(o.m[0x10a],o.m[0x10d]))
 return dict(original_ROM_sha256=CV3_SHA,original_full_raw_register_pairs=len(checked),raw_writes=sum(r['raw_register_writes']for r in checked),raw400F_unmasked=True,checked_updates=checked,reset_exercised=reset,explicit_common_pause_held_image_replays=resume_replays,common_hardware_mixer_register_flush_order_adaptation='Compare complete source raw stores per voice/update, sorted only by address because common hardware mixer flush order is ascending and original noise writes C/F/E. Values including all400F bits are exact. No waveform or bus-timing identity claim.')

def census(p,j):
 rs=rows(p/'cadence.csv');c=j['cases'][0];complete=rs[1:];return dict(actual_frames=c['frames'],actual_updates=j['updates'],actual_draws=j['draws'],recorded_rows=len(rs),recorded_updates=sum(r['updates']for r in rs),recorded_draws=sum(r['draws']for r in rs),skipped_draws=c['frames']-j['draws'],max_consecutive_recorded_no_draw=runlen(complete,'draws'),max_consecutive_recorded_no_update=runlen(complete,'updates'),initial_seed_partial_frame_excluded_from_longest_stall=True,final_update_completion_partial_frame_not_in_csv=True,inclusive_audio_min=min(c['audioCycles']),inclusive_audio_max=max(c['audioCycles']),inclusive_audio_total=sum(c['audioCycles']),inclusive_audio_calls=len(c['audioCycles']))

def main():
 pa=argparse.ArgumentParser(description=__doc__);pa.add_argument('--native',type=Path,nargs='+',required=True);pa.add_argument('--output',type=Path,required=True);a=pa.parse_args();a.output.mkdir(parents=True,exist_ok=False);runs=[];pairs=[];failed=[]
 for f in sorted(f for parent in a.native for f in parent.glob('*/native-proof.json')):
  j=json.loads(f.read_text());p=f.parent
  if not j['passed']or j['emulator_exit']!=0:failed.append(dict(path=str(p),proof_sha256=sha(f),status='Retained diagnostic, no qualification claim'));continue
  rec=dict(path=str(p),name=p.parent.name+'/'+p.name,proof_sha256=sha(f),ROM_sha256=j['ROM_sha256'],profile=j['profile'],mode=j['mode'],event=j['event'],census=census(p,j),guard_counts={k:j[k]for k in['nmis','irq_scroll_writes','min_sp','stack_writes','hardware_chr_checks','complete_dma_checks']},strict_completed_DMA=j.get('strict_completed_DMA'),actual_scene_owner=dict(returns=j['cases'][0].get('sceneResets',0),immediate_cancellations=j['cases'][0].get('sceneImmediate',0),return_wall=j['cases'][0].get('sceneReturnWall')),stream=oracle(p,j));runs.append(rec)
 byname={r['name']:r for r in runs}
 for candidate in runs:
  if not Path(candidate['name']).name.startswith('candidate-'):continue
  name=candidate['name'].replace('candidate-','baseline-',1)
  if name not in byname:continue
  baseline=byname[name];c,b=candidate['census'],baseline['census'];cr=rows(Path(candidate['path'])/'cadence.csv');br=rows(Path(baseline['path'])/'cadence.csv');cu=cd=bu=bd=0;prefix=[]
  for i in range(max(len(cr),len(br))):
   if i<len(cr):cu+=cr[i]['updates'];cd+=cr[i]['draws']
   if i<len(br):bu+=br[i]['updates'];bd+=br[i]['draws']
   if cu<bu or cd<bd:prefix.append(dict(offset=i,candidate_updates=cu,baseline_updates=bu,candidate_draws=cd,baseline_draws=bd))
  pairs.append(dict(candidate=candidate['name'],baseline=name,actual_frames_delta=c['actual_frames']-b['actual_frames'],actual_updates_delta=c['actual_updates']-b['actual_updates'],actual_draws_delta=c['actual_draws']-b['actual_draws'],skipped_draw_delta=c['skipped_draws']-b['skipped_draws'],longest_no_draw_delta=c['max_consecutive_recorded_no_draw']-b['max_consecutive_recorded_no_draw'],longest_no_update_delta=c['max_consecutive_recorded_no_update']-b['max_consecutive_recorded_no_update'],cumulative_prefix_deficits=prefix,scope='Individual frames/updates/draws/stalls and every cumulative prefix deficit retained; no aggregate erases a per-case loss. New effects compared with missing-cue negatives; idle/legacy1F are unchanged-work cadence controls.'))
 result=dict(passed=True,accepted=False,native_runs=len(runs),pairs=len(pairs),retained_failed_native=failed,runs=runs,paired_cadence=pairs,tool_sha256=sha(__file__),scope='Staged legal native ability/contact arenas, actual cold Easy/Hard options and physical controls. Exact-source value and per-voice update traces; native IRQ/NMI/SMC/bank/OAM/CHR/VRAM-owner guards as reported. Not fullcampaign/waveform or all-character acceptance; cadence review remains explicit.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,runs=len(runs),pairs=len(pairs),cadence=[{k:v for k,v in r.items()if k not in['scope','cumulative_prefix_deficits']}|{'prefix_deficits':len(r['cumulative_prefix_deficits'])}for r in pairs]),indent=2))
if __name__=='__main__':main()
