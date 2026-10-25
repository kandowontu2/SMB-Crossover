from pathlib import Path
import hashlib,itertools,json,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,Memory,address,location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU
A=R/'build/checkpoints/native-items-px/candidate.nes';B=D/'wave-candidate-v1/candidate.nes';a,b=load(A),load(B);qa,qb=qualified(A),qualified(B)
assert all(qb.get(k)==v for k,v in qa.items())and set(qb)==set(qa),'Every old qualified symbol and constant exact'
diff=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y];assert len(diff)==2
assert {(a['raw'][i],b['raw'][i])for i in diff}=={(1,255),(255,1)}
assert a['raw'][16+1048576:]==b['raw'][16+1048576:]
start=qa[('KbWeapons','NotReturn')];end=qa[('KbWeapons','Move')];bank=(location(b,'KbWeapons')-16)//8192
cycles=set();cases=0
for slot,kind,age,flags in itertools.product(range(3),range(15),range(256),[0x30,0x71,0x39,0xee]):
 outputs=[]
 for bundle in [a,b]:
  m=Memory(bundle);m.page(1,bank);m[address(bundle,'CurrentBank')]=bank|128
  m[address(bundle,'KbShotKind')+slot]=kind;m[address(bundle,'KbShotAge')+slot]=age;m[address(bundle,'KbShotVYHi')+slot]=37
  c=NesMPU(memory=m,pc=start);c.x=slot;c.y=71;c.a=85;c.p=flags;c.sp=0xed
  for _ in range(30):
   if c.pc==end:break
   c.step()
  else:raise AssertionError(('Wave span timeout',kind,age))
  outputs.append((c,m))
 (c,m),(d,n)=outputs;assert c.processorCycles==d.processorCycles and c.sp==d.sp and c.x==d.x and c.y==d.y
 if kind==8:
  expect=1 if age&8 else 255
  assert n[address(b,'KbShotVYHi')+slot]==expect and m[address(a,'KbShotVYHi')+slot]==(255 if age&8 else 1)
  assert(c.p&0x4d)==(d.p&0x4d)
 else:assert(c.a,c.p,bytes(m[:0x100])+bytes(m[0x200:0x8000]))==(d.a,d.p,bytes(n[:0x100])+bytes(n[0x200:0x8000]))
 cycles.add(c.processorCycles);cases+=1
paths={}
for startY in [196,132]:
 old=new=startY;values=[];old_values=[]
 for age in range(1,90):
  old+=-1 if age&8 else 1;new+=1 if age&8 else-1;values.append(new);old_values.append(old)
 if startY==196:assert max(values)+9<=207 and min(values)-14>=160 and max(values)+8<208
 paths[str(startY)]=dict(min=min(values),max=max(values),old_max=max(old_values),new_final=new)
q=dict(passed=True,ROM_sha256=hashlib.sha256(B.read_bytes()).hexdigest(),parent_ROM_sha256=hashlib.sha256(A.read_bytes()).hexdigest(),qualified_symbols_exact=len(qa),changed_ROM_bytes=2,changed_file_offsets=diff,changed_PRG_bank=bank,CHR_changes=0,instruction_addresses_unchanged=True,native_motion_span_cases=cases,all_span_CPU_cycles_exact=True,non_wave_register_and_RAM_outputs_exact=True,ground_and_air_paths=paths,scope='Only two immediate vertical-direction constants change. Native age1..89 trajectory and source effect lower extent show ground wave stays above the floor. Target availability, all copy attack outcomes and rendered pixels are separate native gates.')
(D/'wave-static-v1.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))
