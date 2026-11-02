"""Qualify source contact closure and local branches against donor CPU."""
from pathlib import Path
import hashlib,json
import recover_prince_landing_1102_v3 as B
R,O=B.R,B.O


def main():
 p=R/'tools/audit/check_prince_landing_1102_v3.py';s=p.read_text()
 changes={
  'landing-recovery.json':'contact-recovery.json',
  'landing-core':'contact-core',
  'landing-CPU.json':'contact-CPU.json',
  'recover_prince_landing_1102_v3.py':'recover_prince_contact_1102_v4.py',
 }
 for old,new in changes.items():assert old in s,old;s=s.replace(old,new)
 extra='''
 contactcases=0;fallcontactcases=0
 for action,face,y,mode,pad,flags in itertools.product([0,1,3,4,7,10,18,23,47,68],[0,255],[32,64,128,191],range(6),[0,8,129],[0x20,0x61]):
  ram=bytearray(seed);ram[0x616]=action;ram[0x615]=face;ram[0x611]=y;ram[0x618]=mode;ram[0x40a]=pad;ram[0x6d1]=5;ram[0x6dd]=0
  old,new=original(ram),compiled(ram);args=(85,19,73,flags)
  a=P.call(old,0xd17a,a=args[0],x=args[1],y=args[2],p=args[3],limit=100000)
  z,apu=invoke(new,'PpTerrainContact',args);equal(old,new,a,z,('original postphysics contact',action,face,y,mode,pad,flags))
  assert old.memory.apu==apu;contactcases+=1
 for action,y,face,count,hold,flags,latched in itertools.product([7,10,18,21,23,24,25,68],[32,63,64,95,96,127,128,159,160,191],[0,255],[0,5,6],[0,64,128,192],[0x20,0x61],[0,1]):
  ram=bytearray(seed);ram[0x616]=action;ram[0x611]=y;ram[0x615]=face;ram[0x6c6]=count;ram[0x40a]=hold;ram[0x4c9]=latched;ram[0x617]=0x69;ram[0x6d1]=5
  old,new=original(ram),compiled(ram);args=(85,19,73,flags)
  a=P.call(old,0xf882,a=args[0],x=args[1],y=args[2],p=args[3],limit=100000)
  z,apu=invoke(new,'PpFallContact',args);equal(old,new,a,z,('original ledge contact after branch relaxation',action,y,face,count,hold,flags,latched))
  assert old.memory.apu==apu;fallcontactcases+=1
'''
 s=s.replace(" changes={\n", " extra+=EXTRA\n changes={\n",1)
 s=s.replace("original_landing_cases=landingcases,original_HP_cases=hpcases,", "original_landing_cases=landingcases,original_HP_cases=hpcases,original_postphysics_cases=contactcases,original_ledge_cases=fallcontactcases,")
 env=dict(__file__=str(p),__name__='prince_contact_qualification',EXTRA=extra)
 exec(compile(s,str(p),'exec'),env);env['main']()
 out=O/'contact-CPU.json';q=json.loads(out.read_text())
 q['full_original_postphysics_contact_source_included']=True
 q['branch_relaxation_preserves_original_CPU_state']=True
 q['wrapper_SHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 out.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
