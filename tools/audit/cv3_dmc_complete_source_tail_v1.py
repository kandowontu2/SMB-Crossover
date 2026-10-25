"""Execute original CV3 completion and retain its authentic held-DAC rule."""
from pathlib import Path
import argparse,hashlib,json
from cv3_primary_sfx_source_v1 import Original,CV3,CV3_SHA,sha
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[];raw=CV3.read_bytes();assert sha(CV3)==CV3_SHA
 for sound in(0x72,0x74,0x75,0x76):
  o=Original(raw);o.call(0xe227);o.m.trace=[];o.call(0xe25f,a=sound);launch=list(o.m.trace);registers={r['address']:r['value']for r in launch};start=0xc000+registers[0x4012]*64;n=registers[0x4013]*16+1;payload=bytes(o.m[start:start+n]);level=registers[0x4011];levels=[]
  for v in payload:
   levels.append(level)
   for bit in range(8):
    if(v>>bit)&1:
     if level<=125:level+=2
    elif level>=2:level-=2
  list.__setitem__(o.m,0x4015,15);o.m.trace=[];o.call(0xe24e);end=list(o.m.trace);assert o.m[0x192]==0 and not any(r['address']==0x4011 for r in end)
  rows.append(dict(sound=sound,length=n,payload_sha256=hashlib.sha256(payload).hexdigest(),launch=launch,completion_APU=end,completion_priority=o.m[0x192],DAC_before_final_byte=levels[-1],last_byte=payload[-1],final_DAC=level))
 result=dict(original_ROM_sha256=CV3_SHA,source_completion_has_no_DAC_reset=True,rows=rows,scope='Actual original sound engine CPU completion with explicit hardware-done status. DAC bit decoding is from the exact source payload, not native waveform or DMA-clock qualification.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in('original_ROM_sha256','source_completion_has_no_DAC_reset','scope')},indent=2))
if __name__=='__main__':main()
