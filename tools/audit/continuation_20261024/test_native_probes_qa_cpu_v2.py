from pathlib import Path
import importlib.util,sys,json,hashlib,itertools,statistics
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'native-probes-qa-v2/cpu-v1';O.mkdir(exist_ok=False)
sys.path.insert(0,str(R/'tools/audit'));from check_tmnt_render_oa import load,Memory,address,location
from verify_native_relocation import NesMPU
old=load(D/'ryu-head-candidate-v5/candidate.nes');new=load(D/'native-probes-qa-v2/candidate.nes')
changes=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b];allowed=set()
for name,size in [('CrossoverHeadProbe',3),('CrossoverSourceSideProbe',28),('MegaManFullShotBank',55)]:
 a=location(old,name);assert location(new,name)==a;allowed.update(range(a,a+size))
assert set(changes)<=allowed and len(old['raw'])==len(new['raw'])
old_labels={q[2]:q[1]for line in (D/'ryu-head-candidate-v5/candidate.lbl').read_text().splitlines()if len(q:=line.split())==3}
new_labels={q[2]:q[1]for line in (D/'native-probes-qa-v2/candidate.lbl').read_text().splitlines()if len(q:=line.split())==3};assert all(new_labels[n]==v for n,v in old_labels.items())
excluded=set(range(0x100,0x200))|set(range(0x5114,0x5118))
for g in old['segs'].values():
 if g.get('name')=='"SMCCODE"':excluded.update(range(int(g['start'],0),int(g['start'],0)+int(g['size'],0)))
for name in ('safecall_a','SafecallA'):
 if name in old['syms']:excluded.add(address(old,name))
def invoke(b,name,case):
 x,y,page,probe,p,sp=case;m=Memory(b)
 for i in range(416):m[address(b,'Block_Buffer_1')+i]=[0,0,0x54,0xc1,0x24,0x26,0xc4,0x60][(i*17+x)%8]
 for n,v in dict(SelectedCharacter=1,Player_X_Position=x,Player_PageLoc=page,Player_Y_Position=y,Player_Y_HighPos=1,ScreenLeft_X_Pos=240,ScreenLeft_PageLoc=page,A_B_Buttons=128,PlayerStatus=2).items():m[address(b,n)]=v
 c=NesMPU(memory=m,pc=address(b,name));c.sp=sp;c.a=(x^y)&255;c.x=5;c.y=probe;c.p=p;c.stPushWord(0x5aff);m.writes=[]
 for _ in range(5000):
  if c.pc==0x5b00:break
  c.step()
 else:raise AssertionError(('CPU timeout',name,case,hex(c.pc),m.banks))
 return(c.a,c.x,c.y,c.p&0xcf,c.sp),{a:m[a]for a,v in m.writes if a not in excluded},c.processorCycles,m.banks
rows=[]
for i,case in enumerate(itertools.product((0,1,7,15,31,127,248,255),(0,16,31,32,65,125,208,239,255),(0,1,255),(0,7,14,21,28,35,42,49,56,63,70,77,83),(0x30,0x71,0xff),(0xdd,0xfd))):
 for name in ('CrossoverHeadProbe','CrossoverSourceSideProbe'):
  a=invoke(old,name,case);b=invoke(new,name,case);assert a[:2]==b[:2]and a[3]==b[3],(name,case,a,b)
  assert b[2]<a[2],(name,case,a[2],b[2]);rows.append((name,a[2],b[2]))
summary={n:dict(cases=sum(r[0]==n for r in rows),median_saved_cycles=statistics.median(a-b for k,a,b in rows if k==n),minimum_saved_cycles=min(a-b for k,a,b in rows if k==n),maximum_saved_cycles=max(a-b for k,a,b in rows if k==n))for n in ('CrossoverHeadProbe','CrossoverSourceSideProbe')}
q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),parent_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),changed_ROM_bytes=len(changes),changed_PRG_banks=sorted(set((p-16)//8192 for p in changes)),changes_only_in_original_resident_spans=True,all_preexisting_exported_labels_unchanged=True,cases=len(rows),exact='Actual A/X/Y/NV-DIZC/SP, application RAM writes and final bank mappings; only actual stack, shared farcall operand/bookkeeping and hardware bank-register writes excluded.',scopes=summary,scope='Assembled CPU query differential for Mega Man/Proto selector, authentic native block queries and mapper farcalls; no interrupts, timed traversal, damage/weapon, or whole-roster/source-fidelity admission here.')
(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q,indent=2))

