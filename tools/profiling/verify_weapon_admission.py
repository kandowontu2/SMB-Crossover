"""Actual whole ProcFireball_Bubble differential, explicit idle CPU/RAM cases."""
from pathlib import Path
import argparse,hashlib,importlib.util,itertools,json
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('native_unit',ROOT/'tools/audit/verify_native_relocation.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 b,B=native.load(a.before);c,C=native.load(a.after)
 assert all(C[n]==v for n,v in B.items() if v<0x8000 and n in C),'Unchanged native/SRAM ABI in this isolated change'
 ignored=set(range(0x100,0x200))|set(range(B['SMCCODE'],B['SMCCODE']+len(b.memory.smc)))
 stats={};count=0
 for char,power,timer,engine,now in itertools.product(range(13),range(3),range(2),(8,9,10,11),(0,1,3,16,32,63)):
  results=[];clocks=[]
  for cpu,L in ((b,B),(c,C)):
   cpu.memory[:0x8000]=[0]*0x8000
   cpu.memory[L['SMCCODE']:L['SMCCODE']+len(cpu.memory.smc)]=cpu.memory.smc
   cpu.memory.switch(0)
   for n,v in (('CurrentBank',128 if a.before.read_bytes()[6]>>4==5 else 0),('SelectedCharacter',char),('PlayerStatus',power),('TimerControl',timer),('GameEngineSubroutine',engine),('GuestBodyNow',now),('GuestBodyPrev',63-now),('FrameCounter',count&255),('Player_Y_HighPos',1),('Player_Y_Position',176),('Player_CollisionBits',3)):
    cpu.memory[L[n]]=v
   cpu.a,cpu.x,cpu.y,cpu.p=count&255,(count*13)&255,(count*29)&255,(count*73)&255
   cpu.sp=0xfd;cpu.stPushWord(0x7eff);cpu.pc=L['ProcFireball_Bubble'];cpu.processorCycles=0;steps=0
   while cpu.pc!=0x7f00:
    cpu.step();steps+=1;assert steps<20000,(count,char,power,timer,engine,hex(cpu.pc))
   results.append((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,tuple(v for i,v in enumerate(cpu.memory[:0x8000]) if i not in ignored)))
   clocks.append(cpu.processorCycles)
  assert results[0]==results[1],{'case':count,'character':char,'power':power,'timer':timer,'engine':engine,'now':now,'registers':[r[:5]for r in results],'first_memory_differences':[(hex(i),b.memory[i],c.memory[i]) for i in range(0x8000) if i not in ignored and b.memory[i]!=c.memory[i]][:10]}
  delta=clocks[1]-clocks[0];s=stats.setdefault(char,{'cases':0,'min_delta':10000,'max_delta':-10000});s['cases']+=1;s['min_delta']=min(s['min_delta'],delta);s['max_delta']=max(s['max_delta'],delta);count+=1
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 report={'result':'passed','cases':count,'before_sha256':sha(a.before),'after_sha256':sha(a.after),'script_sha256':sha(Path(__file__)),'scope':'Actual whole native caller, all13 IDs, all3 power states, timer0/1, engines8/9/10/11, six body contact dictionaries; idle shots/drops and no swimming','compared':'A/X/Y/allP/SP and all bytes below8000 except discarded stack/SMC code target scratch','stats':stats,'limits':['Explicit unit initialization, not controller route evidence.','No interrupts/PPU; active weapons/world contacts and swimming are covered by separate emulator/regression checks.']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS',count,'whole weapon caller cases',stats)


if __name__=='__main__':main()
