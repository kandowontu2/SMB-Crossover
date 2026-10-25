"""Full source admission/mixed/world/release fallback versus2e, including cycle gate."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load
from cv3_remaining_sfx_complete_cpu_v1 import init,sound,EVENTS
from cv3_remaining_sfx_resident_cpu_v1 import compare

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);bs=[load(a.rom.parent/(n+'.nes'))for n in['baseline','candidate']];rows=[]
 for event,age,request in itertools.product(EVENTS,[0,1,5,12,16,27,42,63,88],list(EVENTS)+['world21','world22','ordinary5','scene','music']):
  qs=[init(b)for b in bs]
  for q in qs:
   sound(q,event)
   for _ in range(age):q.invoke('AudioUpdate')
   if isinstance(request,int):sound(q,request)
   elif request=='scene':q.invoke('Cv3NoiseSceneReset')
   elif request=='music':q.put(AreaMusicQueue=2)
   else:q.put(AvAudioRequest={'world21':21,'world22':22,'ordinary5':5}[request])
  cs=[q.invoke('AudioUpdate')[0]for q in qs];delta=compare(qs,cs);rows.append(dict(current=event,age=age,incoming=request,delta=delta));assert delta<=0,rows[-1]
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.rom),held2e_ROM_sha256=sha(a.rom.parent/'baseline.nes'),whole_updates=len(rows),all_nonstack_RAM_raw_APU_AXYP_mapper_exact=True,pointer_exclusions=0,cycle_delta_min=min(r['delta']for r in rows),cycle_delta_max=max(r['delta']for r in rows),actual_spawn_scene_music_and_common_request_owners=True,scope='Actual assembled wholeAudioUpdate after native source releases, continued phases and ordinary-world requests; source/CPU only, no physical-frame/cadence claim.',tool_sha256=sha(__file__))
 (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
