"""Freeze reviewed real-controller/actor source feasibility; no native certification."""
from pathlib import Path
import argparse,hashlib,json
from check_tmnt_render_oa import load,address,location

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[]
 for profile,mode in[('mixed',0),('mixed',1),('priority',1),('death',0),('death',1)]:
  path=a.root/'actors-cpu-v5'/(profile+'-mode'+str(mode)+'.json');h=json.loads(path.read_text());owners=[(r,e)for r in h for e in r['events']]
  if profile=='mixed':
   casts=[(r,e)for r,e in owners if e['owner']=='Cv3FxProducerFast'];assert len(casts)==1 and casts[0][1]['A']==2 and casts[0][0]['frame']==12
   for owner,frame,rate,start,length in[('Cv3DmcPrimaryQueue',26,15,197,68),('Cv3DmcFullInjuryQueue',27,14,252,12)]:
    r,e=next((r,e)for r,e in owners if e['owner']==owner and r['frame']==frame);assert e['owned']&8 and r['noise']==0x15 and r['owned']&8
    assert all([at,v]in r['APU']for at,v in[(0x4010,rate),(0x4012,start),(0x4013,length),(0x4015,31)])
   assert h[27]['health']==60 and all(e['owner']!='KillPlayer'for r,e in owners)
  elif profile=='priority':
   pickup=[(r,e)for r,e in owners if e['owner']=='Cv3CollectPickupGate'];assert len(pickup)==1 and pickup[0][0]['frame']==32 and pickup[0][0]['sub']==3
   casts=[(r['frame'],e['A'])for r,e in owners if e['owner']=='Cv3FxProducerFast'];assert casts==[(16,4)]*3+[(48,5)]*3;assert h[48]['noise']==0x21
  else:
   bats=[r['frame']for r,e in owners if e['owner']=='Cv3FxBatEnter'];kills=[(r,e)for r,e in owners if e['owner']=='KillPlayer'];assert bats==[4]and len(kills)==1 and kills[0][0]['frame']==20 and kills[0][1]['owned']==9 and kills[0][0]['health']==0
  rows.append(dict(profile=profile,mode=mode,path=str(path),sha256=sha(path),frames=len(h),passed=True))
 pipe=a.root/'pipe-cpu-v1/proof.json';z=json.loads(pipe.read_text());assert z['passed']and z['ROM_sha256']==sha(a.rom)and len(z['cases'])==2
 for r in z['cases']:assert r['genuine_movement']['bat']==1 and r['genuine_BG_pipe_collision']['sub']==3 and r['real_VerticalPipeEntry_updates']==48 and r['source_owned_before_area_load']==9
 b=load(a.rom);off=location(b,'E_GroundArea6');assert b['raw'][off:off+3]==bytes([0x1e,0xc2,0])
 negatives=[]
 for path,reason in[('actors-cpu-v2','Ice legitimately freezes approaching enemy; no natural injury proved.'),('actors-cpu-v4','Flame only retains pulse by second primary; cannot claim requested noise overlap.')]:
  ps=sorted((a.root/path).glob('*.json'));assert ps;negatives.append(dict(path=str(a.root/path),reason=reason,files={str(p):sha(p)for p in ps}))
 r=dict(passed=True,native_executed=False,ROM_sha256=sha(a.rom),cases=rows,pipe=dict(path=str(pipe),sha256=sha(pipe)),authentic_original_pipe_destination=dict(symbol='E_GroundArea6',PC=address(b,'E_GroundArea6'),bytes=[30,194,0]),retained_insufficient_drafts=negatives,tool_sha256=sha(__file__),scope='Source/CPU feasibility only: actual GameCore/controller bits and natural seeded actor contact/pickup; only inputs/frame clock advance afterseed. Isolated authentic pipe geometry plus genuine collision/48entry updates. No physical DMC reads, Mesen, PPU/native cadence, actual Start menu, full loader, or campaign coverage claim.')
 (a.output/'proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
