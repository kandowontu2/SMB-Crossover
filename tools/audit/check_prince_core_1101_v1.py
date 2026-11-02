"""Instruction differentials against actual original Prince core/audio code."""
from pathlib import Path
import hashlib,itertools,json,random,sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/reference'))
import prince_original_cpu_1101_v1 as P
import recover_prince_core_1101_v1 as B
O=B.O


class Flat(list):pass


def original(ram,bank=5):
 c=P.machine();c.memory.switch(bank);list.__setitem__(c.memory,slice(0,2048),ram);return c


def main():
 step=P.T.NesMPU.step
 def tracked(c):
  c.original_stack_low=min(getattr(c,'original_stack_low',0xfd),c.sp)
  result=step(c);c.original_stack_low=min(c.original_stack_low,c.sp);return result
 P.T.NesMPU.step=tracked
 labels=P.T.labels(O/'prince-core.lbl');blob=(O/'prince-core.bin').read_bytes();codebytes=labels['PpCoreEnd']-0xa000
 seed=(O/'state-899.bin').read_bytes();rng=random.Random(0x5052494e);commands=set();audio={};cases=0;advances=0;fallcases=0;commandcases=0;inputcases=0;controlcases=0;costs=[];sequence_rows=[];chosen=set()
 relocs={}
 recovery=json.loads((O/'core-recovery.json').read_text())
 for v in recovery['dynamic_command_targets'].values():
  k=(v[0],int(v[1],16));relocs[k[1]]=labels[f'PpN_{k[0]}_{k[1]:04X}']
 callbacks={labels[n]:(k,n)for k,n in B.CALLBACKS.items()}
 def compiled(ram):
  c=P.T.NesMPU(memory=Flat([0]*65536),pc=0xa000);c.memory[0xa000:0xa000+len(blob)]=blob;c.memory[0xc000:0xc800]=ram
  for a in range(256):c.memory[a]=rng.randrange(256)
  return c
 def invoke(c,name,args):
  c.a,c.x,c.y,c.p=args;c.sp=0xfd;c.stPushWord(0x5ffe);c.pc=labels[name];n=0;start=c.processorCycles;nativeapu=[]
  while c.pc!=0x5fff:
   if c.pc in callbacks:
    (bank,target),tag=callbacks[c.pc]
    donor=original(bytes(c.memory[0xc000:0xc800]),bank if target<0xc000 else c.memory[0xc6d1])
    result=P.call(donor,target,a=c.a,x=c.x,y=c.y,p=c.p,limit=100000)
    for lo,hi in [(0,0x101+donor.original_stack_low),(512,2048)]:c.memory[0xc000+lo:0xc000+hi]=donor.memory[lo:hi]
    c.a,c.x,c.y,c.p=result[:4];c.pc=(c.stPopWord()+1)&65535;nativeapu+=donor.memory.apu
    audio[tag]=audio.get(tag,0)+1;continue
   c.step();n+=1;assert n<6000,('Compiled core bound',name,hex(c.pc))
  return(c.a,c.x,c.y,c.p,c.sp,c.processorCycles-start),nativeapu
 def equal(old,new,a,z,context):
  left=bytearray(old.memory[:2048]);right=bytes(new.memory[0xc000:0xc800])
  pointer=left[0x23]|left[0x24]<<8
  if pointer in relocs:
   dest=relocs[pointer];left[0x23]=dest&255;left[0x24]=dest>>8
  for lo,hi in [(0,0x101+old.original_stack_low),(512,2048)]:
   assert left[lo:hi]==right[lo:hi],(context,'RAM',[(hex(k),left[k],right[k])for k in range(lo,hi)if left[k]!=right[k]][:12])
  assert a[:3]==z[:3]and a[4]==z[4]and a[3]&0xef==z[3]&0xef,(context,'AXYPSP',a,z)
 for action,slot,facing in itertools.product(range(1,94),[0,14,28],[0,255]):
  ram=bytearray(seed);ram[0x69]=slot;ram[0x615+slot]=facing;ram[0x616+slot]=0
  old,new=original(ram),compiled(ram);zp=bytes(new.memory[:256]);args=(action,31,slot,0x21)
  a=P.call(old,0x8730,a=args[0],x=args[1],y=args[2],p=args[3]);z,apu=invoke(new,'PpSetAction',args);equal(old,new,a,z,('set',action,slot,facing));cases+=1
  frames=[];positions=[];seen_pointers=set()
  for tick in range(512):
   pointer=old.memory[0x613+slot]|old.memory[0x614+slot]<<8
   if pointer in seen_pointers:break
   assert 0x96ae<=pointer<0x9d93,('Animation pointer leaves exact recovered script range',action,slot,hex(pointer))
   seen_pointers.add(pointer)
   args=(85,slot,0,[0x20,0x21,0x61,0xa1][tick%4]);old.a,old.x,old.y,old.p=args;old.sp=0xfd;old.stPushWord(0x5ffe);old.pc=0xf158;old.memory.apu=[];n=0
   while old.pc!=0xf1a2:
    if old.pc==0xf16c:commands.add(256-old.a)
    assert old.memory[old.pc]!=0,('Original BRK',action,tick,old.memory.bank,hex(old.pc))
    old.step();n+=1;assert n<6000,('Original core bound',action,tick,hex(old.pc))
   # The recovered boundary replaces only the prefix ending before native
   # render projection. Complete its manufactured outer return for ABI parity.
   old.pc=(old.stPopWord()+1)&65535
   a=(old.a,old.x,old.y,old.p,old.sp,0)
   z,apu=invoke(new,'PpAdvanceActor',args);equal(old,new,a,z,('advance',action,slot,facing,tick))
   assert old.memory.apu==apu,('Actual native audio stream',action,slot,tick)
   assert bytes(new.memory[:256])==zp,'Host zero page mutated'
   assert bytes(new.memory[0x200:0x800])==bytes(0x600),'Host application RAM mutated'
   frames.append(old.memory[0x617+slot]);advances+=1;costs.append(z[5])
   positions.append([old.memory[0x60f+slot]|old.memory[0x610+slot]<<8,old.memory[0x611+slot]])
   if old.memory[0x60e+slot]==255:break
  else:raise AssertionError(('Action script did not reach a pointer cycle within512advances',action,slot,facing))
  if slot==0 and facing==0:sequence_rows.append(dict(action=action,frames=frames,x=old.memory[0x60f]|old.memory[0x610]<<8,y=old.memory[0x611],source_y_range=[min(v[1]for v in positions),max(v[1]for v in positions)],state=old.memory[0x618]))
 for command,slot,flags in itertools.product(range(1,16),[0,14,28],[0x20,0x21,0x61,0xa1]):
  bank,pc=recovery['dynamic_command_targets'][str(command)];pc=int(pc,16)
  ram=bytearray(seed);ram[0x69]=slot;ram[0x21:0x23]=bytes([0xaf,0x96]);ram[0x6d1]=5
  old,new=original(ram),compiled(ram);args=(85,slot,0,flags)
  a=P.call(old,pc,a=args[0],x=args[1],y=args[2],p=args[3],limit=100000)
  z,apu=invoke(new,f'PpN_{bank}_{pc:04X}',args);equal(old,new,a,z,('command',command,slot,flags))
  assert old.memory.apu==apu;commandcases+=1
 for state,face,velocity,fraction in itertools.product([0,1,2,3,4,15],[0,255],[0,1,8,27,255],[0,127,255]):
  ram=bytearray(seed);ram[0x618]=state;ram[0x615]=face;ram[0x4e2]=velocity;ram[0x4e1]=fraction;ram[0x6da]=3;ram[0x6db]=104;ram[0x6dd]=0
  old,new=original(ram),compiled(ram);args=(85,19,73,0x31)
  a=P.call(old,0x8133,a=args[0],x=args[1],y=args[2],p=args[3]);z,apu=invoke(new,'PpFall',args);equal(old,new,a,z,('fall',state,face,velocity,fraction));fallcases+=1
 for pad,face,demo,standing in itertools.product(range(256),[0,255],[0,1],[0,1]):
  ram=bytearray(seed);ram[0x40a]=pad;ram[0x615]=face;ram[0x735]=demo;ram[0x618]=standing;ram[0x51]=2
  old,new=original(ram),compiled(ram);args=(85,19,73,0x31)
  a=P.call(old,0x839f,a=args[0],x=args[1],y=args[2],p=args[3]);z,apu=invoke(new,'PpDecodeInput',args);equal(old,new,a,z,('input',pad,face,demo,standing));inputcases+=1
 pads=[0,1,2,4,8,0x80,0x40,0x81,0x41,9,5,0x88,0xc0]
 for pad,face,actorstate,frame in itertools.product(pads,[0,255],[0,1,2,3,4,5,6,15],[15,7,11,0x6a]):
  ram=bytearray(seed);ram[0x40a]=pad;ram[0x615]=face;ram[0x735]=0;ram[0x618]=actorstate;ram[0x617]=frame;ram[0x6d1]=5;ram[0x6dd]=0;ram[0x4f2]=0
  old,new=original(ram),compiled(ram);args=(85,19,73,0x31)
  old.a,old.x,old.y,old.p=args;old.sp=0xfd;old.stPushWord(0x5ffe);old.pc=0xeff2;n=0
  while old.pc!=0x5fff and not(old.pc==0xf090 and old.sp==0xfb):
   old.step();n+=1;assert n<20000,('Original controls bound',pad,face,actorstate,frame,hex(old.pc))
  if old.pc==0xf090:old.pc=(old.stPopWord()+1)&65535
  a=(old.a,old.x,old.y,old.p,old.sp,0)
  z,apu=invoke(new,'PpControls',args);equal(old,new,a,z,('controls',pad,face,actorstate,frame));controlcases+=1;chosen.add(old.memory[0x616])
  assert old.memory.apu==apu,('Control native audio',pad,face,actorstate,frame)
 q=dict(passed=True,donor_sha256=P.SHA,source_CPU_only=True,native=False,action_selection_cases=cases,animation_advances=advances,fall_cases=fallcases,direct_all15_command_cases=commandcases,input_decode_cases=inputcases,original_control_cases=controlcases,action_script_pointer_cycles_qualified=93,script_advances_bound_per_sequence=512,chosen_actions=sorted(chosen),commands_executed_in_sequences=sorted(commands),actual_original_environment_callbacks=audio,component_cycle_range=[min(costs),max(costs)],all_application_RAM_AXYP_SP_exact=True,comparison_relocation='Private scratch23/24 command targets normalized. Script pointers retain originalvalues. All2048originalRAM compared except actually reached stack-write interval tracked by minimumSP; lowstack-page application buffers are included. PhysicalN/V/D/I/Z/C exact; syntheticB ignored.',host_zero_page_preserved=True,host_nonstack_application_RAM_preserved=True,sequences=sequence_rows,limits=['Control prefix ends before original combat selectorF090; world/health/audio consumers remain declared native environment callbacks.','Animationprefix ends before original render projection. Fixture executes actual donor environment instructions, not terrain-return stubs.','Untimed sourceCPU oracle, not Mesen/nativehost/cadence/1-1 qualification.','Virtual A000..B7C1code/scripts and C000state are private fixture addresses, not granted host resources.'],bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(B.__file__),Path(P.__file__),O/'prince-core.s',O/'prince-core.bin',O/'prince-core.lbl',O/'state-899.bin']})
 (O/'core-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['sequences','bindings']}))


if __name__=='__main__':main()
