"""Private hurt-route/public ABI and full ordinary DMC owner differentials."""
from pathlib import Path
import argparse,hashlib,itertools,json
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import load,address,location
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def diff(qs,allow=()):
 excluded=set(range(0x100,0x200))|set(allow)
 changed=[at for at in range(0x8000)if at not in excluded and qs[0].m[at]!=qs[1].m[at]]
 assert not changed,[hex(at)for at in changed[:20]]
def regs(c):return(c.a,c.x,c.y,c.p&0xcf,c.sp)
def apu(q):return[(at,v)for at,v in q.m.writes if 0x4000<=at<=0x4017]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 old,new=load(a.prepared/'baseline.nes'),load(a.prepared/'candidate.nes');source=json.loads((a.source/'proof.json').read_text());cost=[];leaf=[]
 # Actual public DMC start, all legal typed requests and prior owner states.
 for char,variant,request,enable,owner,y in itertools.product((2,3,4,5,11,12),range(4),(21,22),(0,3,15,31),(0,1,2),(0,3,255)):
  qs=[Arena(b,char)for b in(old,new)]
  for q in qs:q.put(Cv3Variant=variant,GuestCombinedEnable=enable,BassDmcActive=owner)
  cs=[q.invoke('RemainingDmcStart',a=request,y=y)[0]for q in qs]
  desired=14 if(char,variant,request)==(5,1,22)else 13 if(char,variant,request)==(5,3,22)else 15
  assert qs[1].m[0x4010]==desired
  diff(qs,(0x4010,));assert regs(cs[0])==regs(cs[1])and qs[0].m.banks==qs[1].m.banks
  ow,nw=map(apu,qs);assert[(at,desired if at==0x4010 else v)for at,v in ow]==nw
  leaf.append(dict(character=char,variant=variant,request=request,enable=enable,prior_owner=owner,y=y,rate=desired));cost.append(cs[1].processorCycles-cs[0].processorCycles)
 (a.output/'public-start.json').write_text(json.dumps(leaf,separators=(',',':'))+'\n')
 # Real assembled injury owner: live/protected, enemies, modes, pending cues.
 injuries=[]
 for variant,mode,face,enemy,protected,pending in itertools.product((1,2,3),(0,1),(1,2),(0,45),(0,1),(0,21,26)):
  qs=[Arena(b,5)for b in(old,new)]
  for q in qs:
   q.put(Cv3Variant=variant,CrossoverBehaviorVersion=mode,PlayerFacingDir=face,ObjectOffset=0,Cv3Invul=protected,AvAudioRequest=pending)
   q.set('Cv3Health',64,variant-1);q.set('Enemy_ID',enemy)
  cs=[q.invoke('Cv3InjuryStartGate',a=0x55,x=0,y=3)[0]for q in qs]
  routed=variant in(1,3)and not protected
  assert qs[1].get('AvAudioRequest')==(22 if routed else qs[0].get('AvAudioRequest'))
  assert qs[1].get('Square1SoundQueue')==(0 if routed else qs[0].get('Square1SoundQueue'))
  diff(qs,[address(new,n)for n in('AvAudioRequest','Square1SoundQueue')]if routed else())
  assert regs(cs[0])==regs(cs[1])and qs[0].m.banks==qs[1].m.banks
  injuries.append(dict(variant=variant,mode=mode,face=face,enemy=enemy,protected=protected,pending=pending,routed=routed))
 (a.output/'injury-owner.json').write_text(json.dumps(injuries,separators=(',',':'))+'\n')
 # Exact original sample/rate normalized only for its relocated start address.
 routes=[]
 for variant,name in[(1,'Grant'),(3,'Alucard')]:
  q=Arena(new,5);q.put(Cv3Variant=variant,AreaMusicQueue=1);q.invoke('AudioUpdate')
  q.put(Cv3Invul=0,ObjectOffset=0);q.set('Cv3Health',64,variant-1);q.set('Enemy_ID',0)
  q.invoke('Cv3InjuryStartGate');assert q.get('AvAudioRequest')==22 and q.get('Square1SoundQueue')==0
  q.invoke('AudioUpdate');hw=apu(q);values={at:v for at,v in hw}
  original=next(r for r in source['source_injury']if r['character']==name)
  start=0xc000+64*values[0x4012];length=16*values[0x4013]+1
  payload=bytes(q.m[start:start+length]);assert hashlib.sha256(payload).hexdigest()==original['payload_sha256']
  assert values[0x4010]==original['rate']and values[0x4011]==0 and length==original['length']and q.get('BassDmcActive')==2
  routes.append(dict(character=name,variant=variant,request=22,rate=values[0x4010],relocated_start=start,length=length,payload_sha256=hashlib.sha256(payload).hexdigest(),APU_writes=hw))
 (a.output/'source-routes.json').write_text(json.dumps(routes,indent=2)+'\n')
 # All ordinary mixer/native paths, including every old typed effect. Only
 # the two intentional source-rate changes in request22 may differ.
 ordinary=0
 for char,variant,effect in itertools.product((3,4,5),range(4),range(27)):
  if char!=5 and variant:continue
  if effect==26 and(char,variant)!=(5,3):continue
  qs=[Arena(b,char)for b in(old,new)]
  for q in qs:q.put(Cv3Variant=variant,AreaMusicQueue=1)
  for tick in range(32):
   for q in qs:
    q.put(GamePauseStatus=int(tick in(16,17)),AvAudioRequest=effect if tick==8 else 0)
    if tick==20:q.m[0x4015]=15 # explicit ended-hardware control
   cs=[q.invoke('AudioUpdate')[0]for q in qs];desired=14 if(char,variant,effect)==(5,1,22)else 13 if(char,variant,effect)==(5,3,22)else 15
   ow,nw=map(apu,qs);assert[(at,desired if at==0x4010 and effect==22 else v)for at,v in ow]==nw,(char,variant,effect,tick)
   diff(qs,(0x4010,)if effect==22 else());assert regs(cs[0])==regs(cs[1])and qs[0].m.banks==qs[1].m.banks;ordinary+=1
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.prepared/'candidate.nes'),baseline_ROM_sha256=sha(a.prepared/'baseline.nes'),source_receipt_sha256=sha(a.source/'proof.json'),tool_sha256=sha(__file__),actual_public_DMC_start_cases=len(leaf),public_DMC_cycle_delta=[min(cost),max(cost)],actual_injury_owner_cases=len(injuries),actual_injury_to_source_APU_cases=len(routes),ordinary_full_AudioUpdate_cases=ordinary,public_final_AXY_flags_SP_exact=True,application_RAM_exact_except_intended_request_queue_rate=True,existing_DMC_samples_payload_location_length_exact=True,remaining='Source72 primary storage/priority, distinct Sypha75 payload/dispatch and native qualification remain incomplete.',scope='Actual assembled and original CPU source equality only; no native interrupts, DMC playback clocks, audible output or gameplay qualification.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
