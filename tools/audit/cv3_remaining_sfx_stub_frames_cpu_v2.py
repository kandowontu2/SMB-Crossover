"""Every direct source frame: original image-store order and dynamic400F low3bits."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_audio_fallback_oc import qualified
from check_tmnt_render_oa import load,address
from cv3_dmc_complete_cpu_v1 import LaneArena
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 pa=argparse.ArgumentParser(description=__doc__);pa.add_argument('--rom',type=Path,required=True);pa.add_argument('--output',type=Path,required=True);a=pa.parse_args();a.output.mkdir(parents=True,exist_ok=False);parent=D/'cv3-remaining-decoder-v1/candidate.nes';old,new=load(parent),load(a.rom);table=json.loads((a.rom.parent/'pointer-translation.json').read_text());translation={r['old_PC']:r['new_PC']for r in table};decode=qualified(parent)[('Cv3FxService','Decode')];old['syms']['SourceFrameUnderTest']=dict(old['syms']['Cv3FxService'],name='"SourceFrameUnderTest"',val=hex(decode));newdecode=qualified(a.rom)[('Cv3FxService','Decode')];new['syms']['SourceFrameUnderTest']=dict(new['syms']['Cv3FxService'],name='"SourceFrameUnderTest"',val=hex(newdecode));cases=[]
 for rec,high,seed in itertools.product((r for r in table if not r.get('end')),range(8),[17,101]):
  qs=[LaneArena(b,5)for b in[old,new]]
  for q,pc in zip(qs,[rec['old_PC'],rec['new_PC']]):
   q.put(R0=pc&255,R1=pc>>8,Cv3FxSourceHigh=high)
   for name,count in[('GuestNativeApu',16),('GuestNativeDirty',16),('Cv3FxPulseApu',4)]:q.array(name,[(i*37+seed)&255 for i in range(count)])
   for i in[0,2,3]:q.set('Cv3NoiseApu',(i*53+seed)&255,i)
  cs=[qs[0].invoke('SourceFrameUnderTest')[0],qs[1].invoke('SourceFrameUnderTest')[0]]
  image={address(new,n)+i for n,count in[('GuestNativeApu',16),('GuestNativeDirty',16),('Cv3FxPulseApu',4)]for i in range(count)}|{address(new,'Cv3NoiseApu')+i for i in[0,2,3]}|{address(new,'Cv3FxSourceHigh')}
  writes=[[(at,v)for at,v in q.m.writes if at in image]for q in qs];assert writes[0]==writes[1],(rec,high,seed,writes)
  assert all(qs[0].m[i]==qs[1].m[i]for i in image)
  pointers=[q.get('R0')+256*q.get('R1')for q in qs];assert translation.get(pointers[0])==pointers[1],(rec,pointers)
  assert pointers==[rec['old_PC']+len(rec['original_ordered_writes'])*2+1,rec['new_PC']+rec['stub_bytes']]
  assert new['raw'][16+82*8192+rec['new_PC']-0xa000]in[0xa9,0x4c]
  cases.append(dict(event=rec['event'],voice=rec['voice'],frame=rec['frame'],prior_shared_high=high,image_seed=seed,ordered_source_image_stores=len(writes[0]),cycle_delta=cs[1].processorCycles-cs[0].processorCycles))
 assert len(cases)==4560
 r=dict(passed=True,accepted=False,ROM_sha256=sha(a.rom),held_ROM_sha256=sha(parent),actual_frames=285,all_dynamic_shared_high_values=8,independent_prior_images=2,assembled_frame_cases=len(cases),ordered_source_image_Dirty_High_writes_exact=True,logical_pointer_end_and_stride_exact=True,cycle_delta_range=[min(r['cycle_delta']for r in cases),max(r['cycle_delta']for r in cases)],scope='Each frame executes through actual Decode/JMP(R0), mappedA82 stub and writer/RTS; costs include the real new5-cycle indirect dispatch. Only helper-internal AXY/flags differ; outer wholeAudioUpdate ABI is separately compared. No source raw400F masking, additional RAM, native worker or cadence claim.')
 (a.output/'cases.json').write_text(json.dumps(cases,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
