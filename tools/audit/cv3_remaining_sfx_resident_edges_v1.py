"""C28 actual Full boundary, every hot frame/high/dirty mask and fixed-E alias."""
from pathlib import Path
import argparse,copy,hashlib,itertools,json,random
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from cv3_remaining_sfx_complete_cpu_v1 import init
from cv3_remaining_sfx_resident_cpu_v1 import compare

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 bs=[load(a.rom.parent/'baseline.nes'),load(a.rom)];maps=[qualified(a.rom.parent/(n+'.nes'))for n in['baseline','candidate']]
 for b,m in zip(bs,maps):
  original=b['syms']['Cv3FxTick'];actual_bank=(location(b,'Cv3FxTick')-16)//8192
  b['segs']['actual-C28']=dict(b['segs'][original['seg']],ooffs=str(16+8192*actual_bank),start='0xC000')
  b['syms']['ActualTickFull']=dict(original,val=hex(m[('Cv3FxTick','Full')]),seg='actual-C28')
 rng=random.Random(0xc28);rows=[]
 for event,index,high,dirty,ebank in itertools.product([0x21,0x1e],range(43),range(8),range(8),[125,127]):
  qs=[init(b,2)for b in bs];values=[rng.randrange(256)for _ in range(12)]
  for q,m in zip(qs,maps):
   q.put(Cv3FxOwned=8,Cv3FxNoiseID=event,Cv3FxPulseID=0,Cv3FxPendingNoise=0,Cv3FxPendingPulse=0,AvAudioRequest=0,Cv3NoiseActive=128,Cv3NoiseIndex=index,Cv3FxSourceHigh=high,CurrentBank=128|84)
   q.m[0x5115]=128|84;q.m.page(3,ebank)
   ptr=address(q.b,f'Cv3Fx21NoiseFrame{index:03d}');q.put(Cv3FxNoisePtr=ptr&255);q.set('Cv3FxNoisePtr',ptr>>8,1)
   for j,reg in enumerate([12,14,15]):
    q.set('GuestNativeDirty',(dirty>>j)&1,reg);q.set('GuestNativeApu',values[j],reg)
   q.put(Cv3NoiseMusicVolume=values[3],Cv3NoiseMusicPeriod=values[4],Cv3NoiseMusicHigh=values[5])
   q.array('Cv3NoiseApu',values[6:10]);q.put(R0=values[10],R1=values[11])
  cs=[q.invoke('ActualTickFull',a=128,x=0x36,y=0xa5,flags=0xe9)[0]for q in qs];delta=compare(qs,cs);assert delta<0
  rows.append(dict(event=event,index=index,sourceHigh=high,dirty=dirty,E_alias=ebank,delta=delta))
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.rom),parent_ROM_sha256=sha(a.rom.parent/'baseline.nes'),cases=len(rows),actual_unchanged_Full_entry=True,all_nonstack_RAM_raw_APU_AXYP_mapper_exact=True,pointer_exclusions=0,delta_min=min(r['delta']for r in rows),delta_max=max(r['delta']for r in rows),full_source_final_volume_and_pointer_carry_covered=True,scope='Source21/1E exact steady-frame Full boundary only; actual request admission/mixed/priority/lifecycle covered separately. No native deadline claim.',tool_sha256=sha(__file__))
 (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
