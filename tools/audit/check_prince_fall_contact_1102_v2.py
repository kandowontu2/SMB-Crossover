"""Requalify original core plus expanded falling ledge-catch instructions."""
from pathlib import Path
from types import SimpleNamespace
import hashlib,json
import recover_prince_core_1101_v1 as B
R,O=B.R,B.O


def main():
 recovery=json.loads((O/'fall-contact-recovery.json').read_text())
 callbacks={(v[0],int(v[1],16)):n for n,v in recovery['declared_original_environment_boundaries'].items()}
 proxy=SimpleNamespace(O=O,CALLBACKS=callbacks,__file__=str(R/'tools/audit/recover_prince_fall_contact_1102_v2.py'))
 p=R/'tools/audit/check_prince_core_1101_v1.py';source=p.read_text()
 extra='''
 fallcontactcases=0
 for action,y,face,count,hold,flags,latched in itertools.product([7,10,18,21,23,24,25,68],[32,63,64,95,96,127,128,159,160,191],[0,255],[0,5,6],[0,64,128,192],[0x20,0x61],[0,1]):
  ram=bytearray(seed);ram[0x616]=action;ram[0x611]=y;ram[0x615]=face;ram[0x6c6]=count;ram[0x40a]=hold;ram[0x4c9]=latched;ram[0x617]=0x69;ram[0x6d1]=5
  old,new=original(ram),compiled(ram);args=(85,19,73,flags)
  a=P.call(old,0xf882,a=args[0],x=args[1],y=args[2],p=args[3],limit=100000)
  z,apu=invoke(new,'PpFallContact',args);equal(old,new,a,z,('expanded original falling ledge contact',action,y,face,count,hold,flags,latched))
  assert old.memory.apu==apu;fallcontactcases+=1
'''
 changes={
  'import recover_prince_core_1101_v1 as B':'B=PROXY',
  "O/'prince-core":"O/'fall-contact-core",
  "O/'core-recovery.json'":"O/'fall-contact-recovery.json'",
  "O/'core-CPU.json'":"O/'fall-contact-CPU.json'",
  ' q=dict(passed=True,donor_sha256=P.SHA':extra.lstrip('\n')+' q=dict(passed=True,expanded_original_fall_contact_cases=fallcontactcases,donor_sha256=P.SHA',
  'Virtual A000..B7C1code/scripts and C000state are private fixture addresses, not granted host resources.':'Flat CPU fixture A000..B9C1 and C000state follow granted conditional windows; this test does not exercise mapped host integration.',
 }
 for old,new in changes.items():assert old in source,old;source=source.replace(old,new)
 env=dict(__file__=str(p),__name__='prince_expanded_contact_check',PROXY=proxy)
 exec(compile(source,str(p),'exec'),env);env['main']()
 q=json.loads((O/'fall-contact-CPU.json').read_text())
 q['expanded_original_ledge_catch_source_included']=True
 q['wrapper_SHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 (O/'fall-contact-CPU.json').write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
