"""Independent sampled-cell oracle for the added side row and unchanged ABI."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,Memory,address,location
from verify_native_relocation import NesMPU
def run(b,x,y,seq,crouch,index,kind,flags):
 m=Memory(b);bank=(location(b,'TnSideDispatch')-16)//8192;m.page(1,bank);m[address(b,'CurrentBank')]=bank|128
 seed=dict(SelectedCharacter=19,GameEngineSubroutine=8,Player_X_Position=x,Player_PageLoc=1,Player_Y_Position=y,Player_Y_HighPos=1,
  TnSeq=seq,RgCrouch=crouch,R0=2 if index<5 else 1,R1=0x34,R2=0x77,R3=0x88,R4=0x99,R5=0xaa,R6=0xbb,R7=0xcc)
 for n,v in seed.items():m[address(b,n)]=v
 top=2 if seq==0x87 else 5 if crouch else -8;bottom=14 if seq==0x87 else 27 if crouch else 24
 high=((y+top)&0xf0)-32;low=((y+bottom)&0xf0)-32;mid=high+16
 px=x+(2 if index<5 else 13);page=1+(px//256);col=px%256//16;base=address(b,'Block_Buffer_1'if page%2==0 else'Block_Buffer_2')+col
 rows=[high]if kind==1 else[mid]if kind==2 else[low]if kind==3 else[high,mid,low]if kind==4 else[]
 tiles={row:0xc0 for row in rows if 0<=row<=192}
 for row,value in tiles.items():m[base+row]=value
 expect=tiles.get(high if index%2 else low,0)
 if not expect and index%2 and seq!=0x87 and high<192:expect=tiles.get(mid,0)
 c=NesMPU(memory=m,pc=address(b,'TnSideDispatch'));c.a=0x56;c.x=0;c.y=index;c.p=flags;c.sp=0xfd;m[0x1fe]=255;m[0x1ff]=0x7e;m.writes=[]
 for _ in range(5000):
  if c.pc==0x7f00:break
  c.step()
 else:raise AssertionError('Side probe timed out')
 assert m[address(b,'Player_X_Position')]==x and m[address(b,'Player_PageLoc')]==1 and m[address(b,'Player_Y_Position')]==y
 return c,m,expect
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom);cases=novel=0
 for x,y,pose,index,kind,flags in itertools.product([0,1,14,15,127,159,240,254,255],[48,64,127,144,150,151,152,160,176,208,224],[(0x80,0),(0x83,1),(0x87,0)],[3,4,5,6],range(5),[0x30,0x71]):
  seq,crouch=pose;c,m,want=run(new,x,y,seq,crouch,index,kind,flags);d,n,_=run(old,x,y,seq,crouch,index,kind,flags)
  assert c.a==want,(x,y,pose,index,kind,c.a,want)
  if c.a==d.a:
   excluded=set(range(256,512));assert(c.a,c.x,c.y,c.p&0xcf,c.sp)==(d.a,d.x,d.y,d.p&0xcf,d.sp),(x,y,pose,index,kind,'ABI')
   assert all(m[i]==n[i]for i in range(32768)if i not in excluded),(x,y,pose,index,kind,'RAM')
  else:
   assert d.a==0 and c.a==0xc0 and index%2 and seq!=0x87;novel+=1
  cases+=1
 q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),cell_oracle_cases=cases,formerly_missed_thin_cells=novel,
  scope='Independent upper/middle/lower cell geometry, standing/crouch/roll, both sides, page wrap, all tested height phases and flags. Existing-result ABI/RAM exact excluding discarded stack; every body origin restored. Native contact/replay/performance separate.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q),flush=True)
if __name__=='__main__':main()
