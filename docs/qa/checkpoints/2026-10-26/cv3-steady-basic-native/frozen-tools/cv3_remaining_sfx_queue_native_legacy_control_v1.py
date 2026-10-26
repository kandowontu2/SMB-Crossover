"""Prove existing1F adapter image order and whole hardware stream against50b and original."""
from pathlib import Path
import argparse,hashlib,json
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from cv3_remaining_sfx_complete_cpu_v1 import init
from cv3_dmc_complete_cpu_v1 import apu
from cv3_primary_sfx_source_v1 import Original,CV3
from verify_native_relocation import NesMPU
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def tick(q,labels):
 b=q.b;name='AudioUpdate';pc=address(b,name);bank=(location(b,name)-16)//8192;q.m.page((pc-0x8000)//8192,bank);q.m.writes=[];c=NesMPU(memory=q.m,pc=pc);c.sp=253;c.stPushWord(0x5aff);image=[];lo=labels[('Cv3MusicAndNoiseTick','Continue')];hi=labels[('Cv3MusicAndNoiseTick','End')];base=address(b,'GuestNativeApu')
 for _ in range(100000):
  if c.pc==0x5b00:return image,apu(q),c.processorCycles
  record=q.m.banks[2]==28 and lo<=c.pc<hi and q.get('Cv3NoiseActive')==1 and q.get('Cv3NoiseIndex')<=28;at=len(q.m.writes);c.step()
  if record:image.extend((0x4000+a-base,v)for a,v in q.m.writes[at:]if base<=a<base+16)
 raise AssertionError('Actual wholeAudioUpdate timeout')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);roms=[a.baseline,a.rom];bs=[load(r)for r in roms];labels=[qualified(r)for r in roms];cases=[]
 for mode in[0,1]:
  qs=[init(b,3)for b in bs]
  for q in qs:q.put(CrossoverBehaviorVersion=mode,Cv3AttackAge=8,Cv3AttackKind=1,Cv3Fresh=0,SavedJoypadBits=0,PlayerFacingDir=1);q.invoke('Cv3WeaponsGate');assert sum(q.get('Cv3ShotType',i)==6 for i in range(4))==1
  assert qs[0].get('AvAudioRequest')==26 and(qs[1].get('Cv3FxQueueHead')-qs[1].get('Cv3FxQueueTail'))&255==1;o=Original(CV3.read_bytes());o.call(0xe227);o.call(0xe25f,a=0x1f);rows=[]
  for frame in range(100):
   before=o.m[0x10d];o.m.trace=[];o.call(0xe24e);original=[(r['address'],r['value'])for r in o.m.trace];expected=sorted(original,key=lambda w:[0x400e,0x400f,0x400c].index(w[0]));results=[tick(q,l)for q,l in zip(qs,labels)];assert results[0][0]==results[1][0]==expected,('Declared unchanged adapter image',mode,frame,results[0][0],results[1][0],expected);assert results[0][1]==results[1][1],('Complete existing hardware stream differs',mode,frame,results[0][1],results[1][1])
   if before:assert[(at,v)for at,v in results[1][1]if at in[0x400c,0x400e,0x400f]]==sorted(original),('Exact original owned hardware/raw400F',mode,frame)
   assert(qs[0].get('Cv3NoiseActive'),qs[0].get('Cv3NoiseIndex'))==(qs[1].get('Cv3NoiseActive'),qs[1].get('Cv3NoiseIndex'));rows.append(dict(frame=frame,original_ordered_source=original,baseline_image=results[0][0],candidate_image=results[1][0],complete_hardware=results[1][1],source_before=before,baseline_cycles=results[0][2],candidate_cycles=results[1][2]))
  assert qs[0].get('Cv3NoiseActive')==qs[1].get('Cv3NoiseActive')==0;out=a.output/f'mode{mode}.json';out.write_text(json.dumps(rows,indent=2)+'\n');cases.append(dict(mode=mode,frames=100,path=str(out),sha256=sha(out),source_image_writes=sum(len(r['candidate_image'])for r in rows),last_source_emission=max(r['frame']for r in rows if r['candidate_image']),first_host_restore=28))
 result=dict(passed=True,native_executed=False,ROM_sha256=sha(a.rom),baseline_ROM_sha256=sha(a.baseline),source_ROM_sha256=sha(CV3),cases=cases,declared_adapter_image_order=[0x400e,0x400f,0x400c],original_image_order_equal=False,all_original_values_raw400F_and_complete_baseline_hardware_equal=True,scope='Actual primary release and whole assembledAudioUpdate. Existing1F retains its established buffered period/high/volume order; ORIGINAL volume/high/period ordering is intentionally NOT claimed. Exact original source emission values/lifetime and unchanged100-update hardware stream, including host restoration, proven in both modes. No native process or timing/adoption claim.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,native_executed=False,mode_cases=len(cases),last_source_frame=27,host_restore_frame=28),indent=2))
if __name__=='__main__':main()
