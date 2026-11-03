"""Full original battle control/strike/incoming instruction differentials."""
from collections import Counter
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import recover_prince_core_1101_v1 as B
P,O=B.P,B.O


def main():
 recovery=json.loads((O/'contact-recovery.json').read_text());q=json.loads((O/'combat-tail-recovery-v34.json').read_text());assert q['closed']and q['original_PC_assembly_exact']
 for name,digest in q['bindings'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,name
 lab=P.T.labels(O/'contact-core.lbl');new=P.T.labels(O/'combat-tail-v34.lbl');core=bytearray((O/'contact-core.bin').read_bytes());extra=(O/'combat-tail-v34.bin').read_bytes();seed=(O/'state-899.bin').read_bytes()
 # Only two emitted absolute operands implement the intentional old F090
 # cutoff. Retarget those exact original edges; do not run battle controls
 # after original early-return/death/locked-action paths.
 old=bytes([0x4c,lab['PpControlComplete']&255,lab['PpControlComplete']>>8]);retarget=[]
 for name,delta in [('PpN_7_F044',2),('PpN_7_F08D',3)]:
  at=lab[name]-0xa000+delta;assert core[at:at+3]==old,(name,core[at:at+3].hex());core[at+1:at+3]=new['PpCombatControls'].to_bytes(2,'little');retarget.append(dict(source=name,CPU=0xa000+at,old=old.hex(),new=bytes(core[at:at+3]).hex()))
 callbacks={lab[n]:(k[0],int(k[1],16),n)for n,k in recovery['declared_original_environment_boundaries'].items()}
 callbacks.update({0x5100:(7,0xd6ce,'OriginalSfx'),0x5110:(6,0xaa13,'OriginalRawSfx'),0x5120:(7,0xd487,'OriginalLandingAlign')})
 reloc={}
 for row in recovery['dynamic_command_targets'].values():
  bank,pc=row[0],int(row[1],16);reloc[pc]=lab[f'PpN_{bank}_{pc:04X}']
 counts=Counter();events=Counter();cost=[];changed=set();outcomes=Counter();minsp=253
 def compare(kind,pc,root,ram,args):
  nonlocal minsp
  d=P.machine();d.memory.switch(4 if 0xa000<=pc<0xc000 else 5);list.__setitem__(d.memory,slice(0,2048),ram);out=P.call(d,pc,a=args[0],x=args[1],y=args[2],p=args[3],limit=50000)
  m=[0]*65536;m[0xa000:0xa000+len(core)]=core;m[0x4000:0x4000+len(extra)]=extra;m[0xc000:0xc800]=ram
  c=P.T.NesMPU(memory=m,pc=root);c.a,c.x,c.y,c.p=args;c.sp=253;c.stPushWord(0x5ffe)
  for _ in range(50000):
   if c.pc==0x5fff:break
   minsp=min(minsp,c.sp)
   if c.pc in callbacks:
    bank,target,name=callbacks[c.pc];env=P.machine();env.memory.switch(bank if target<0xc000 else m[0xc6d1]);list.__setitem__(env.memory,slice(0,2048),m[0xc000:0xc800])
    result=P.call(env,target,a=c.a,x=c.x,y=c.y,p=c.p,limit=100000)
    m[0xc000:0xc100]=env.memory[:256];m[0xc200:0xc800]=env.memory[512:2048];c.a,c.x,c.y,c.p=result[:4];c.pc=(c.stPopWord()+1)&65535;events[name]+=1;continue
   assert m[c.pc]!=0,('Battle component BRK',kind,hex(c.pc),args);c.step()
  else:raise AssertionError(('Battle component bound',kind,hex(c.pc),args))
  left=bytearray(d.memory[:2048]);pointer=int.from_bytes(left[0x23:0x25],'little')
  if pointer in reloc:left[0x23:0x25]=reloc[pointer].to_bytes(2,'little')
  diff=[(hex(i),left[i],m[0xc000+i])for i in itertools.chain(range(256),range(512,2048))if left[i]!=m[0xc000+i]]
  assert not diff,('Original battle RAM',kind,args,ram[0x6ee],ram[0x616],ram[0x617],diff[:12])
  assert out[:3]==(c.a,c.x,c.y)and out[3]&0xef==c.p&0xef and out[4]==c.sp,('Original battle AXYP/SP',kind,out,(c.a,c.x,c.y,c.p,c.sp))
  assert not any(m[:256])and not any(m[512:2048]);counts[kind]+=1;cost.append(c.processorCycles);outcomes[(kind,m[0xc6cf],m[0xc6d0],m[0xc616],m[0xc624])]+=1
  changed.update(i for i in range(2048)if not 0x100<=i<0x200 and ram[i]!=d.memory[i])
 for sword,action,pad,dx,dy,flags in itertools.product([0,1,2],[0,56,58,74],[0,1,2,8,128,129,130,136],[16,32,64,105],[-30,0,30],[0x20,0x61]):
  ram=bytearray(seed);ram[0x69]=0;ram[0x2c]=3;ram[0x6cf]=5;ram[0x6d0]=1;ram[0x6ee]=sword;ram[0x6e0]=1;ram[0x401]=0;ram[0x6de]=0;ram[0x616]=action;ram[0x615]=255;ram[0x623]=0;ram[0x61d:0x61f]=(160+dx).to_bytes(2,'little');ram[0x61f]=(128+dy)&255;ram[0x40a]=pad;ram[0x617]=170 if action==74 else 171
  compare('full_controls',0xeff2,lab['PpControls'],ram,(83,71,0,flags))
 for target,hp,sword,action,pose,flags in itertools.product([0,14],range(6),[0,1,2],[0,62,69,74],[15,170],[0x20,0x61]):
  ram=bytearray(seed);ram[0x69]=0;ram[0x6cf]=5;ram[0x6d0]=1;ram[0x6cf+(target!=0)]=hp;ram[0x6ee]=sword;ram[0x616+target]=action;ram[0x617+target]=pose;ram[0x70]=0
  compare('incoming',0xacfa,new['PpOriginalIncoming'],ram,(83,71,target,flags))
 for striker,action,pose,defender,flags in itertools.product([0,14],[0,69,74],[153,154],[0,62,69,74],[0x20,0x61]):
  target=striker^14;ram=bytearray(seed);ram[0x69]=0;ram[0x6cf]=5;ram[0x6d0]=1;ram[0x6ee]=2;ram[0x616+striker]=action;ram[0x617+striker]=pose;ram[0x616+target]=defender;ram[0x70]=0
  compare('strike',0xacd6,new['PpOriginalStrike'],ram,(83,71,striker,flags))
 result=dict(passed=True,source_CPU_only=True,native_emulator=False,ROM_written=False,hardware_placement_granted=False,donor_SHA256=P.SHA,original_instruction_bytes=q['original_instruction_bytes'],original_instruction_boundaries=q['original_instruction_boundaries'],original_PC_assembly_exact=True,component_bytes=len(extra),original_differential_cases=dict(counts),complete_original_application_RAM_AXYP_SP_exact=True,host_ZP_preserved=True,component_CPU_excluding_actual_environment_ports=[min(cost),max(cost)],minimum_SP=minsp,original_environment_calls=dict(events),exact_old_control_edges_retargeted=retarget,source_written_bytes=sorted(changed),outcome_count=len(outcomes),original_combat_contract='Source6EE0/1 unarmed/sheathing incoming damage uses five8710 calls then death85; mode2 uses oneHP E95A reaction74. OriginalDBB9 clears actions at playerpose170. Source A-choice/attackadmission/parry/frame154/targetswap and guard branches execute original instructions.',remaining=['Actual native enemy proxy import/export and source predicate binding.','Quiet rawAA13 event continuation proof, native hitbox/terrain/palette/death/public routing and live placement.','Bounded cold image/physical fit, source/native reader/constructor/ISR closure and root grants before native.'],scope='Full original battle component with authentic original audio/world environment ports. All303original instructions and existing source core execute; no native enemy outcome or gameplay is seeded/claimed.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'combat-tail-recovery-v34.json',O/'combat-tail-v34.bin',O/'contact-core.bin',O/'contact-recovery.json',O/'contact-continuation-negative-v33.json']})
 (O/'combat-tail-CPU-v36.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['bindings','source_written_bytes']}))


if __name__=='__main__':main()
