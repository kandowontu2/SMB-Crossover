"""Finite lifecycle source+full mixer oracle, raw register values never masked."""
from pathlib import Path
import argparse,csv,hashlib,json
from cv3_primary_sfx_source_v1 import Original,CV3
from cv3_remaining_sfx_queue_native_verify_v5 import cadence_metrics,compare_legacy_hardware
SOURCE_IDS={1:0x13,2:0x15,3:0x24,4:0x21,5:0x1e,6:0x1f,7:0x2f}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mixer_expected(z):
 assert z['owner']in['native','mixed']
 out=[]
 for i in range(16):
  if i in[9,13]:continue
  owner=8 if i//4==3 and z['mask']&8 and z['owner']=='mixed'else 0
  value=z['fx'][i]if owner else z['image'][i]
  dirty=z['fxDirty'][i]if owner else z['dirty'][i]
  transition=bool(z['owner']=='mixed'and i//4==3 and z['changed']&8)
  if value!=z['last'][i]or dirty or transition:out.append([0x4000+i,value])
 return out

def composed_source(life,events,images,legacy=False):
 o=Original(CV3.read_bytes());o.call(0xe227);rows=[];mix=[];steps=0
 by_epoch={}
 for r in images:by_epoch.setdefault(int(r['audioEpoch']),[]).append([int(r['address']),int(r['value'])])
 merged=sorted([(e['cpuCycle'],0,e)for e in events if e['kind']=='drain-return']+[(e['cpuCycle'],1,e)for e in life if e['kind']in['actual-music-init','source-tick-return','actual-mixer-flush']],key=lambda e:(e[0],e[1]))
 seen=set()
 for _,_,e in merged:
  kind=e['kind'];epoch=e['audioEpoch']
  if kind=='actual-music-init':o.call(0xe227)
  elif kind=='drain-return':
   for cue in e['cues']:
    if cue==8:
     # Port scene cancellation ends both private effect instruments. Preserve
     # the prior original register image/high bits; this is not a new sound.
     o.m[0x10a]=o.m[0x10d]=0
    else:assert cue in SOURCE_IDS;o.call(0xe25f,a=SOURCE_IDS[cue])
  elif kind=='source-tick-return':
   assert epoch not in seen;seen.add(epoch);before=[o.m[0x10a],o.m[0x10d]];o.m.trace=[];o.call(0xe24e)
   expected=[[r['address'],r['value']]for r in o.m.trace if before[0]and r['address']in[0x4000,0x4001,0x4002,0x4003]or before[1]and r['address']in[0x400c,0x400e,0x400f]]
   original=list(expected)
   if legacy and expected:expected=sorted(expected,key=lambda p:[0x400e,0x400f,0x400c].index(p[0]))
   actual=by_epoch.get(epoch,[]);assert actual==expected,('Complete ordered original source image/raw400F',epoch,actual,expected)
   rows.append(dict(audioEpoch=epoch,before=before,original_ordered=original,declared_adapter_order=expected,actual=actual));steps+=1
  else:
   expected=mixer_expected(e);actual=[]if e['hardware']=={}else e['hardware'];assert actual==expected,('Complete composed flush, incl resume replay/ordinary world ownership',epoch,e['hardware'],expected,e)
   mix.append(dict(audioEpoch=epoch,owner=e['owner'],mask=e['mask'],changed=e['changed'],expected=expected,actual=actual))
 assert set(by_epoch)<=seen,('Source image lacks a real tick owner',set(by_epoch)-seen)
 return dict(original_frames=steps,source_rows=rows,complete_flushes=mix)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fixture',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 cfg=json.loads((a.fixture/'configuration.json').read_text());prep=json.loads((a.fixture/'preparation.json').read_text());assert sha(a.fixture/'run.lua')==prep['script_sha256'];proof=json.loads((a.fixture/'proof.json').read_text());bp=json.loads((a.baseline/'proof.json').read_text());assert proof['passed']and bp['passed'];case=proof['cases'][0];assert case['modeReadback']==cfg['mode']
 life=[json.loads(s)for s in(a.fixture/'lifecycle.jsonl').read_text().splitlines()];events=[json.loads(s)for s in(a.fixture/'queue-owners.jsonl').read_text().splitlines()];images=list(csv.DictReader((a.fixture/'source-register-image.csv').open()));source=composed_source(life,events,images,cfg['expected_cue']==6)
 metrics=cadence_metrics(list(csv.DictReader((a.fixture/'cadence.csv').open())),list(csv.DictReader((a.baseline/'cadence.csv').open())));metrics['complete_game_totals']={n:{k:p[k]for k in['updates','draws']}for n,p in[('candidate',proof),('baseline',bp)]};metrics['passed']=metrics['passed']and proof['draws']>=bp['draws']
 legacy=compare_legacy_hardware(list(csv.DictReader((a.fixture/'apu.csv').open())),list(csv.DictReader((a.baseline/'apu.csv').open())))if cfg['expected_cue']==6 else None
 (a.output/'source-model.json').write_text(json.dumps(source,indent=2)+'\n');result=dict(passed=metrics['passed'],accepted=False,native_scope=cfg['cases'][0],ROM_sha256=prep['ROM_sha256'],source_original_ROM_sha256=sha(CV3),original_source_frames=source['original_frames'],complete_mixer_flushes=len(source['complete_flushes']),legacy1F_unchanged_complete_hardware_control=legacy,no_raw_register_value_masks=True,actual_mode_readback=case['modeReadback'],cadence=metrics,source_model_sha256=sha(a.output/'source-model.json'),tool_sha256=sha(__file__),scope='Only the bound finite lifecycle profile. Real consumer epochs feed authenticated original executable; mute freezes source, actual scene/music owner cancels. Every source-image byte and complete native/mixed flush is checked from prior image/last/dirty/world ownership, including resume replay and raw400F. Existing1F adapter order remains explicitly unchanged; complete hardware regression control. No waveform or full-campaign certification.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
