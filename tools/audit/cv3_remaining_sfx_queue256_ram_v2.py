"""Pinned imported-driver/static alias inventory and actual all-menu music RAM accesses."""
from pathlib import Path
import argparse,hashlib,itertools,json,re
from check_tmnt_render_oa import load,address,Memory
from cv3_remaining_sfx_queue256_support_v1 import init
from cv3_dmc_complete_cpu_v1 import apu,regs
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Watch(Memory):
 def __getitem__(self,at):
  if getattr(self,'watching',False)and isinstance(at,int)and self.lo<=at<self.hi:self.upper_reads.append(at)
  return super().__getitem__(at)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);src=a.source/'src';driver=src/'audio/roster/castlevania.inc';refs=[];mentions=[]
 for line,t in enumerate(driver.read_text().splitlines(),1):
  if'RgAudioRam'not in t:continue
  m=re.search(r'RgAudioRam(?:([+-])\$([0-9a-f]+))?(?:,([xy]))?',t,re.I);assert m,t;offset=int(m[2],16)*(1 if m[1]=='+'else-1)if m[2]else 0;refs.append(dict(line=line,text=t.strip(),arbitrary_index_max=offset+(255 if m[3]else 0)))
 assert max(r['arbitrary_index_max']for r in refs)==142
 assert not any(re.search(r'\b(?:STA|STX|STY|INC|DEC|ASL|LSR|ROL|ROR)\s+\(',t,re.I)for t in driver.read_text().splitlines())
 for f in src.rglob('*'):
  if not f.is_file()or f.suffix not in['.s','.inc']:continue
  for line,t in enumerate(f.read_text().splitlines(),1):
   if any(n in t for n in ['RgAudioRam','RgContraRam','RgZeldaRam']):mentions.append(dict(path=f.relative_to(a.source).as_posix(),line=line,text=t.strip(),source_sha256=sha(f)))
 rows=[];total=0
 for area,event in[(1<<i,0)for i in range(7)]+[(0,1<<i)for i in range(7)]+[(128,0),(0,128)]:
  qs=[init(b,2)for _ in range(2)]
  for seed,q in enumerate(qs):
   m=Watch(b);list.__setitem__(m,slice(None),list(q.m));m.banks=list(q.m.banks);m.lo=address(b,'Cv3FxQueue');m.hi=m.lo+256;m.upper_reads=[];m.watching=False;q.m=m
   for i in range(256):q.set('Cv3FxQueue',(i*37+seed*113+19)&255,i)
   q.put(GuestAudioCharacter=255,RgAudioCharacter=255,Cv3FxQueueHead=0,Cv3FxQueueTail=0,AreaMusicQueue=area,EventMusicQueue=event)
  for frame in range(256):
   cs=[]
   for q in qs:
    q.m.upper_reads=[];q.m.watching=True;c,_=q.invoke('AudioUpdate');q.m.watching=False;cs.append(c)
    assert not q.m.upper_reads,('Imported/wrapper reads proposed upperRAM',area,event,frame,q.m.upper_reads)
    assert not any(q.m.lo<=at<q.m.hi for at,v in q.m.writes),('Imported/wrapper writes proposed upperRAM',area,event,frame)
    q.put(AreaMusicQueue=0,EventMusicQueue=0)
   assert apu(qs[0])==apu(qs[1])and regs(cs[0])==regs(cs[1])and qs[0].m.banks==qs[1].m.banks
   total+=2
  rows.append(dict(area_request=area,event_request=event,actual_whole_updates=512,arbitrary_upper_patterns=2,actual_upper_reads=0,actual_upper_writes=0,source_music_APU_AXYP_bank_independent_of_upper=True))
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.rom),imported_driver_sha256=sha(driver),all_direct_RAM_references=refs,max_direct_offset_for_any_byte_index=142,imported_indirect_stores=0,all_shared_RAM_wrapper_alias_mentions=mentions,actual_area_event_silence_profiles=rows,actual_whole_music_AudioUpdates=total,existing_storage=[address(b,'Cv3FxQueue'),address(b,'Cv3FxQueue')+256],logical_capacity=64,scope='Static direct read/write maximum and absence of any imported indirect store are exhaustive for the pinned CV1 source. Runtime indirect reads and complete cold wrappers are checked for every valid area/event/silence menu bit through256 updates under two arbitrary upper-RAM patterns; that finite dynamic coverage is not an unbounded proof of every future song phase. Contra/Zelda share only selected-family-exclusive RAM; MMC5 Parodius aliases use ExRAM, MMC3 else branch is unchanged. Producer cold-partial-write/NMI/reset proofs are separate.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['all_direct_RAM_references','all_shared_RAM_wrapper_alias_mentions','actual_area_event_silence_profiles']},indent=2))
if __name__=='__main__':main()
