"""Original landing and HP instruction differentials, plus prior core cases."""
from pathlib import Path
from types import SimpleNamespace
import hashlib,json
import recover_prince_core_1101_v1 as B
R,O=B.R,B.O


def main():
 recovery=json.loads((O/'landing-recovery.json').read_text())
 callbacks={(v[0],int(v[1],16)):n for n,v in recovery['declared_original_environment_boundaries'].items()}
 proxy=SimpleNamespace(O=O,CALLBACKS=callbacks,__file__=str(R/'tools/audit/recover_prince_landing_1102_v3.py'))
 p=R/'tools/audit/check_prince_core_1101_v1.py';source=p.read_text()
 extra='''
 landingcases=0;hpcases=0
 for action,y,velocity,age,hp,flags in itertools.product([0,7,11,18,21,23,45,68],[63,64,127,128,191],[0,8,27],[0,2,3,6,7],[0,1,3],[0x20,0x61]):
  ram=bytearray(seed);ram[0x616]=action;ram[0x611]=y;ram[0x4e2]=velocity;ram[0x6c6]=age;ram[0x6cf]=hp;ram[0x6d1]=5
  old,new=original(ram),compiled(ram);args=(85,19,73,flags)
  a=P.call(old,0xd427,a=args[0],x=args[1],y=args[2],p=args[3],limit=100000)
  z,apu=invoke(new,'PpLanding',args);equal(old,new,a,z,('original landing',action,y,velocity,age,hp,flags))
  assert old.memory.apu==apu;landingcases+=1
 for name,pc in [('PpLoseHP',0x8574),('PpCombatLoseHP',0x8710)]:
  for hp,other,slot,flags in itertools.product(range(8),[0,1,3],[0,1,14,255],[0x20,0x21,0x61,0xa1]):
   ram=bytearray(seed);ram[0x6cf]=hp;ram[0x6d0]=other;ram[0x6d2]=0;ram[0x6dc]=0
   old,new=original(ram),compiled(ram);args=(85,19,slot,flags)
   a=P.call(old,pc,a=args[0],x=args[1],y=args[2],p=args[3],limit=100000)
   z,apu=invoke(new,name,args);equal(old,new,a,z,('original HP leaf',name,hp,other,slot,flags))
   assert old.memory.apu==apu;hpcases+=1
'''
 changes={
  'import recover_prince_core_1101_v1 as B':'B=PROXY',
  "O/'prince-core":"O/'landing-core",
  "O/'core-recovery.json'":"O/'landing-recovery.json'",
  "O/'core-CPU.json'":"O/'landing-CPU.json'",
  ' q=dict(passed=True,donor_sha256=P.SHA':extra.lstrip('\n')+' q=dict(passed=True,original_landing_cases=landingcases,original_HP_cases=hpcases,donor_sha256=P.SHA',
  'Virtual A000..B7C1code/scripts and C000state are private fixture addresses, not granted host resources.':'Flat CPU fixture uses conditional granted code/state windows; this test does not exercise mapped host integration.',
 }
 for old,new in changes.items():assert old in source,old;source=source.replace(old,new)
 env=dict(__file__=str(p),__name__='prince_original_landing_check',PROXY=proxy)
 exec(compile(source,str(p),'exec'),env);env['main']()
 out=O/'landing-CPU.json';q=json.loads(out.read_text())
 q['original_landing_and_HP_source_included']=True
 q['wrapper_SHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 out.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
