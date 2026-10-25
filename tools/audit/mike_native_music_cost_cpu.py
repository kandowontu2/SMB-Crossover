"""Matched CPU work of Mike's old fallback and private original native music.

One whole AudioUpdate per sample. CPU-only excludes raster, DMA, ISR time,
emulated hardware audio and completed gameplay updates/draws.
"""
from pathlib import Path
import argparse,hashlib,json
from mike_native_music_cpu import Run
from check_tmnt_render_oa import load

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['rom','baseline','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);bundles=[load(a.baseline),load(a.rom)];rows=[]
 for bit in range(7):
  cases=[]
  for b in bundles:
   r=Run(b)
   for n,v in dict(SelectedCharacter=16,OperMode=1,CrossoverBehaviorVersion=1,AreaMusicQueue=1<<bit,PlayerStatus=1,DisableScreenFlag=1).items():r.set(n,v)
   costs=[];minimum=255
   for i in range(601):costs.append(r.call('AudioUpdate',p=0x20));minimum=min(minimum,r.depth)
   cases.append(dict(init=costs[0],updates=600,mean=sum(costs[1:])/600,peak=max(costs[1:]),minimum_SP=minimum))
  row=dict(area_bit=bit,previous_Pit_fallback=cases[0],original_StarTropics_native=cases[1]);rows.append(row);print(row,flush=True)
 q=dict(passed=True,baseline_sha256=hashlib.sha256(a.baseline.read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows,native_emulator_launched=False,scope=__doc__)
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':main()
