"""Read-only exact fixed-DPCM capacity and original CV3 injury/priority proof."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,address,location
from cv3_primary_sfx_source_v1 import Original,CV3,CV3_SHA,authenticate
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 b=load(a.rom);raw=CV3.read_bytes();assert sha(CV3)==CV3_SHA
 ref=ROOT/'build/player-guide-agent/cv3-private/reference/source/code/playerStateProcessing_b1c.s'
 auth=authenticate(raw,ref,28,[(0x20b,0x214),(0x294,0x298)])
 occupied=[]
 for s in b['segs'].values():
  if'ooffs'in s and(int(s['ooffs'],0)-16)//8192==127 and int(s['size'],0)and s['name']!='"BASS_DPCM"':occupied.append((int(s['start'],0),int(s['start'],0)+int(s['size'],0),s['name']))
 target={}
 for n in('BassWaterDpcm','AvDmcLinkTakeDamage','AvDmcSimonTakeDamage'):
  lo,hi=location(b,n),location(b,n+'End');target[n]=b['raw'][lo:hi];occupied.append((address(b,n),address(b,n+'End'),n))
 cursor=0xe000;gaps=[]
 for lo,hi,n in sorted(occupied):
  assert lo>=cursor,(hex(lo),hex(cursor),n)
  if lo>cursor:gaps.append(dict(start=cursor,end=lo,length=lo-cursor))
  cursor=hi
 if cursor<0x10000:gaps.append(dict(start=cursor,end=0x10000,length=0x10000-cursor))
 sources=[]
 for enum,name,event,rate in[(0,'Simon',0x73,15),(1,'Sypha',0x75,15),(2,'Grant',0x74,14),(3,'Alucard',0x76,13)]:
  o=Original(raw);o.call(0xe227);o.m[0x54e]=enum;o.call(0x820b,stop=0xe25f);assert o.c.a==event
  o.m.trace=[];o.call(0xe25f,a=event)
  regs={r['address']:r['value']for r in o.m.trace};assert regs[0x4010]==rate and regs[0x4011]==0
  start=0xc000+64*regs[0x4012];length=16*regs[0x4013]+1;payload=bytes(o.m[start:start+length])
  f=a.output/f'{name.lower()}-injury.dmc';f.write_bytes(payload)
  sources.append(dict(character=name,original_enum=enum,event=event,rate=rate,DAC=0,source_start=start,length=length,payload_sha256=sha(f),reuse_labels=[n for n,data in target.items()if data==payload],launch_writes=o.m.trace))
 priority=[]
 for current,request in itertools.product(range(14),(0x72,0x74,0x75,0x76)):
  o=Original(raw);o.call(0xe227);o.m[0x192]=current;o.m[0x4015]=31;o.m.trace=[];o.call(0xe25f,a=request)
  launched=any(r['address']==0x4012 for r in o.m.trace);expected=current<5 or request-0x6d>=current;assert launched==expected
  priority.append(dict(current=current,request=request,launched=launched,new_priority=o.m[0x192]))
 (a.output/'original-priority.json').write_text(json.dumps(priority,indent=2)+'\n')
 freebanks=[]
 for bank in range(128):
  segs=[s for s in b['segs'].values()if'ooffs'in s and int(s['size'],0)and(int(s['ooffs'],0)-16)//8192<=bank<=(int(s['ooffs'],0)+int(s['size'],0)-17)//8192]
  if not segs and set(b['raw'][16+bank*8192:16+(bank+1)*8192])<={255}:freebanks.append(bank)
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.rom),original_ROM_sha256=CV3_SHA,tool_sha256=sha(__file__),original_callsite_authenticated_bytes=sum(len(bytes.fromhex(q['hex']))for q in auth),fixed_occupied=sorted(occupied),fixed_gaps=gaps,fixed_free_bytes=sum(q['length']for q in gaps),largest_contiguous_gap=max(q['length']for q in gaps),aligned_sample_starts={str(size):[at for q in gaps for at in range((q['start']+63)&~63,q['end']-size+1,64)]for size in(193,1089)},source_injury=sources,original_priority_cases=len(priority),fully_unoccupied_FF_banks=freebanks,scope='Read-only capacity and actual original CPU requests/launch writes. Alternate fixed-bank mirroring/owner is an architectural plan, not implemented or native-qualified.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in('source_injury','fixed_occupied')},indent=2))
if __name__=='__main__':main()
