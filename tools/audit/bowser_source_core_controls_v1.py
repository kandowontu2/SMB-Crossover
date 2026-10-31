"""Original SMB3 6502 motion differential and actual assembled control loop."""
from pathlib import Path
import hashlib,itertools,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from verify_native_relocation import NesMPU
O=R/'build/bowser-source-core-v1';S=R/'build/smb3-original-source-match-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def call(mem,pc,a=0,x=0,y=0,p=0x30):
 c=NesMPU(memory=mem,pc=pc);c.a=a;c.x=x;c.y=y;c.p=p;c.sp=253;c.stPushWord(0x5aff);low=c.sp
 for i in range(10000):
  if c.pc==0x5b00:break
  assert mem[c.pc]!=0,('BRK',hex(c.pc));low=min(low,c.sp);c.step()
 else:raise AssertionError('bounded6502return')
 assert c.sp==253
 return c,low
def main():
 out=O/'controls.json';assert not out.exists();q=dict(passed=False,source=True,native=False,checks={})
 try:
  labels={n:int(v,16)for n,v in re.findall(r'^al ([0-9A-Fa-f]+) \.([^\s]+)$',(O/'arena.lbl').read_text(),re.M)}
  # Reverse regex groups from ld65 label format.
  labels={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.([^\s]+)$',(O/'arena.lbl').read_text(),re.M)}
  original={n:int(v,16)for n,v in re.findall(r'^(\w+)\s+= \$([\dA-F]+)$',(S/'smb3.fns').read_text(),re.M)}
  raw=(S/'smb3.nes').read_bytes();old=[0]*65536;new=[0]*65536;image=(O/'arena.bin').read_bytes();new[0x8000:0x8000+len(image)]=image
  for at,bank in [(0x8000,30),(0xa000,1),(0xc000,0),(0xe000,31)]:old[at:at+8192]=raw[16+bank*8192:16+(bank+1)*8192]
  assert raw[16:16+262144]==Path('C:/NES/Super Mario Bros. 3 (USA) (Rev 1).nes').read_bytes()[16:16+262144]
  pairs=[('Objects_XVel',0x6000),('Objects_XVelFrac',0x6004),('Objects_X',0x6008),('Objects_XHi',0x600c)]
  count=0;cycles=[];low=253
  for vel,frac,pos,page in itertools.product(range(256),[0,1,15,127,128,240,255],[0,1,15,127,255],[0,255]):
   slot=count&3;values=[vel,frac,pos,page]
   for (name,at),v in zip(pairs,values):old[original[name]+slot]=new[at+slot]=v
   old[original['Object_VelCarry']]=new[0x6010]=0x69
   a,l=call(old,original['Object_AddVelFrac'],x=slot,y=71,p=0x71)
   b,k=call(new,labels['Bw3AddVelFrac'],x=slot,y=71,p=0x71)
   expected=[old[original[name]+slot]for name,at in pairs]+[old[original['Object_VelCarry']]]
   actual=[new[at+slot]for name,at in pairs]+[new[0x6010]]
   assert expected==actual and(a.a,a.x,a.y,a.p)==(b.a,b.x,b.y,b.p),(values,expected,actual)
   low=min(low,l,k);count+=1;cycles.append([a.processorCycles,b.processorCycles])
  q['checks']['original4_4integrator']=dict(actual_original_source_pairs=count,all256velocities=True,position_page_fraction_edges=True,AXYP_SP_and_allfive_outputs_exact=True,minimum_SP=low,cycles_original=[min(r[0]for r in cycles),max(r[0]for r in cycles)],cycles_absolute_projection=[min(r[1]for r in cycles),max(r[1]for r in cycles)])
  flagrows=[]
  for flags,vel in itertools.product([48|i for i in range(256)if not i&48],[0,1,0x7f,0x80,0xa0,0xff]):
   for(name,at),v in zip(pairs,[vel,255,0,255]):old[original[name]]=new[at]=v
   a,l=call(old,original['Object_AddVelFrac'],p=flags);b,k=call(new,labels['Bw3AddVelFrac'],p=flags)
   assert(a.a,a.x,a.y,a.p)==(b.a,b.x,b.y,b.p)
   assert[old[original[n]]for n,a in pairs]+[old[original['Object_VelCarry']]]==[new[a]for n,a in pairs]+[new[0x6010]]
   flagrows.append([flags,vel])
  q['checks']['all64_live_flags']=dict(cases=len(flagrows),rows=flagrows)
  call(new,labels['Bw3Fresh']);new[0x6009]=176;new[0x6014]=1;rows=[]
  for tick in range(180):
   keys=(1 if tick<100 else 2)| (0x80 if 20<=tick<28 else 0)| (0x40 if tick<70 else 0)
   c,low=call(new,labels['Bw3Step'],a=keys)
   rows.append(dict(tick=tick,input=keys,x=new[0x6008]+new[0x600c]*256,y=new[0x6009]+new[0x600d]*256,vx=new[0x6000],vy=new[0x6001],ground=new[0x6014],face=new[0x6015],pose=new[0x6016],breath=new[0x6017],emit=new[0x6019],cycles=c.processorCycles))
  assert min(r['y']for r in rows)<176 and rows[-1]['ground']==1
  assert rows[90]['x']>rows[0]['x']and rows[170]['x']<rows[100]['x']
  assert sum(r['emit']for r in rows)==1 and next(r['tick']for r in rows if r['emit'])==46
  assert all(r['pose']in range(9)for r in rows)
  q['checks']['actual_assembled_controller_sequence']=dict(whole_steps=len(rows),rows=rows,original_breath3F_to10_emits_once=True,source_jump_gravity_integrator=True,callback_scope='Only abstract deterministic floor176; not actual SMB terrain/contact/gameplay proof.')
  q['measured']=dict(core_bytes=labels['BwCoreEnd']-labels['BwCoreStart'],art_metadata_bytes=labels['BwArtEnd']-labels['BwArtStart'],abstract_active_state_bytes=28,body_CHR_bytes=3072,SMB1_physics_implemented=False,actual_host_callbacks=False)
  q['passed']=True
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),O/'source-stage.json',O/'core.s',O/'arena.s',O/'arena.bin',O/'arena.lbl',S/'smb3.nes',S/'smb3.fns']}
 out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=q['passed'],error=q.get('error'),measured=q.get('measured'),path=str(out))),flush=True);assert q['passed']
if __name__=='__main__':main()
