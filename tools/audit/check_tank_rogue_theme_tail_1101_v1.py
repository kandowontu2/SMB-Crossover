"""Verify the compiled theme producer and six-byte final audio table."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as M
from check_tank_terminal_leaves_1101_v1 import O,P,PIN
def main():
 b=scoped_load(P);raw=b['raw'];assert hashlib.sha256(raw).hexdigest()==PIN
 m=M.fresh(b);table=location(b,'NormalFlags');pc=address(b,'NormalFlags')
 assert pc==0xbfbe and (table-16)//8192==62
 assert raw[table:table+6]==bytes([16,1,8,64,16,128])
 area=location(b,'CommitContext::AreaTheme');world=location(b,'CommitContext::WorldTheme')
 assert raw[area:area+4]==bytes([4,0,2,5]) and raw[world:world+8]==bytes([1,0,3,1,0,3,1,0])
 calls=0;outputs=set()
 for a,w,old,q in itertools.product(range(4),range(8),range(256),[0,15]):
  M.put(m,AreaType=a,WorldNumber=w,RdsTheme=old,AreaMusicQueue=q)
  M.invoke(m,'CommitContext')
  result=M.get(m,'RdsTheme');expected=raw[world+w]if a==1 else raw[area+a]
  assert result==expected and 0<=result<6
  outputs.add(result);calls+=1
 # Execute the exact compiled indexed read, with every produced theme.
 site=address(b,'RdsAudioFrame::FontDone')+5
 off=location(b,'RdsAudioFrame::FontDone')+5
 assert raw[off:off+6]==bytes.fromhex('ae5a70bdbebf')
 reads=[]
 for theme in sorted(outputs):
  m.raw_page(1,190);M.put(m,CurrentBank=190,RdsTheme=theme)
  c=NesMPU(memory=m,pc=site);c.step();c.step()
  assert c.a==raw[table+theme] and c.pc==site+6
  reads.append(pc+c.x)
 result=dict(passed=True,ROM_sha256=PIN,producer_cases=calls,legal_AreaType=[0,3],legal_SMB1_WorldNumber=[0,7],arbitrary_old_theme_tested=True,produced_themes=sorted(outputs),actual_indexed_reads=reads,final_table_half_open=[pc,pc+6],formal_grant=False,scope='Theme producer and final indexed table only. Does not establish all writer paths or support for future expanded world numbering.',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (O/'Rogue-theme-tail.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(dict(passed=True,producer_cases=calls,themes=sorted(outputs))))
if __name__=='__main__':main()
