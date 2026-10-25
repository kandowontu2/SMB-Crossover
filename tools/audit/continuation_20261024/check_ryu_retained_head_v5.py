"""Assembled retained-body geometry and complete RP restore-tail contracts.

External native block effects and bbox construction are explicit RTS traps in
the geometry units. The real effects require separate native replay fixtures.
"""
from pathlib import Path
import sys,json,hashlib,itertools,time
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,Memory,address,location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU
oldpath=D/'food-candidate-v3/candidate.nes';newpath=D/'ryu-head-candidate-v5/candidate.nes'
O=D/'ryu-head-cpu-v5';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old,new=load(oldpath),load(newpath);qo,qn=qualified(oldpath),qualified(newpath)
changed=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
start=location(old,'RyuSourceHeadGate');size=int(old['syms']['RyuSourceHeadGate']['size'],0)
assert size==int(new['syms']['RyuSourceHeadGate']['size'],0)==771
assert all(start<=i<start+size for i in changed)
outside={k:(v,qn.get(k))for k,v in qo.items()if qn.get(k)!=v and k[:1]!=('RyuSourceHeadGate',)}
assert not outside,outside
def image(bundle):
 m=Memory(bundle);m.page(1,22);m[address(bundle,'CurrentBank')]=150
 return bytearray(m)
templates=[image(old),image(new)]
scratch=[address(old,'R0')+i for i in range(8)]+[address(old,n)for n in ['RgTempX','RgTempPage','RgTempY','RgTemp2','RgTemp3']]
tailcases=0
def tail(a,p,sp):
 global tailcases
 answers=[]
 for bundle,q,template in zip([old,new],[qo,qn],templates):
  m=template.copy();x=(a+3*p)&255;y=(17*a+7*p)&255
  values=[p,a,x,y]+[(i*37+a+p)&255 for i in range(13)]
  for i,v in enumerate(values):m[0x100+sp-i]=v
  m[0x100+sp+1]=0xef;m[0x100+sp+2]=0x7e
  c=NesMPU(memory=m,pc=q[('RyuSourceHeadGate','Handled')]);c.sp=sp-17;c.a=0x91;c.x=0x65;c.y=0xc3;c.p=0x24
  for _ in range(90):
   if c.pc==0x7ef0:break
   c.step()
  else:raise AssertionError(('Tail timeout',a,p,sp,hex(c.pc)))
  assert (c.a,c.x,c.y,c.sp)==(0,x,y,sp+2)
  assert c.p&0xcf==((p&0x4d)|2)
  for at,v in zip(scratch,values[4:]):assert m[at]==v
  untouched=template.copy()
  for at,v in zip(scratch,values[4:]):untouched[at]=v
  assert m[:0x100]==untouched[:0x100]and m[0x200:]==untouched[0x200:]
  answers.append((c.a,c.x,c.y,c.p&0xcf,c.sp,bytes(m[:0x100])+bytes(m[0x200:0x8000])))
 assert answers[0]==answers[1]
 tailcases+=1
for a in range(256):
 for p in range(256):tail(a,p,221)
for sp in range(17,254):
 for a,p in itertools.product([0,0x80,0xff],[0,0x28,0x9f,0xff]):tail(a,p,sp)
print(json.dumps(dict(tail_cases=tailcases,passed=True)),flush=True)

def execute(which,seed):
 bundle,q,template=[old,new][which],[qo,qn][which],templates[which]
 m=template.copy()
 for n,v in seed.items():m[q[(n,)]]=v&255
 m[0x1fe]=0xef;m[0x1ff]=0x7e
 c=NesMPU(memory=m,pc=q[('RyuSourceHeadGate',)]);c.sp=0xfd;c.a=seed['R3'];c.x=3;c.y=51;c.p=0xed
 calls=[]
 for _ in range(800):
  if c.pc==0x7ef0:break
  if c.pc in [q[('PlayerHeadCollision',)],q[('RyuPlatformBox',)]]:
   calls.append(('head'if c.pc==q[('PlayerHeadCollision',)]else'box',c.a,c.y))
   # Explicit unmodified effects are isolated from the scalar geometry unit.
   c.inst_0x60();continue
  c.step()
 else:raise AssertionError(('Gate timeout',hex(c.pc),seed))
 assert c.sp==255 and c.x==3 and c.y==51
 for at in scratch:assert m[at]==template[at]or any(q[(n,)]==at and m[at]==(v&255)for n,v in seed.items())
 return c,m,calls

seed0=dict(GameEngineSubroutine=8,SelectedCharacter=10,Player_State=1,Player_Y_HighPos=1,
 Player_PageLoc=7,Player_X_Position=96,Player_Y_Position=151,Player_Y_Speed=254,XgJumpUsed=1,
 RgAttack=6,RgAttackAge=8,RyuSourceBodyProfile=25,R2=112,R3=0x51,AreaType=1,
 MmVY=0,MmVX=0,RyWallSupported=0,RyWallOldHeight=0,RyWallWasGround=0)
geometry=ordinary=negative=0
cycles=[]
for tile,offset,fy,vy,age in itertools.product([0x51,0xc1,0xc4],range(-4,4),[0,1,0x7fff,0x8000,0xffff],[-294912,-131072,-8192],[0,1,2,8]):
 seed=dict(seed0,R3=tile,Player_Y_Position=153+offset,RgAttackAge=age,
  MmYFraction=fy&255,**{'MmYFraction+1':fy>>8})
 # Labels with indexed suffixes are materialized as numeric RAM addresses below.
 seed.pop('MmYFraction+1');seed['MmVY']=vy&255
 expanded={k:v for k,v in seed.items()}
 # execute supports indexed seeds through freshly installed qualified aliases.
 for q in [qo,qn]:
  q[('FY_HI',)]=q[('MmYFraction',)]+1;q[('VY_MID',)]=q[('MmVY',)]+1;q[('VY_HI',)]=q[('MmVY',)]+2
 expanded.update(FY_HI=fy>>8,VY_MID=(vy>>8)&255,VY_HI=(vy>>16)&255,Player_Y_Speed=(vy>>16)&255)
 oldc,oldm,oldcalls=execute(0,expanded);c,m,calls=execute(1,expanded)
 cur=((153+offset)<<16)+fy;previous=cur-vy
 crossing=cur+7*65536<=160*65536 and previous+(7 if age>=2 else 5)*65536>=160*65536
 if crossing:
  assert c.a==0 and m[qn[('Player_Y_Position',)]]==153
  assert [m[qn[('MmVY',)]] ,m[qn[('MmVY',)]+1],m[qn[('MmVY',)]+2]]==[0x55,0xd5,0]
  assert m[qn[('Player_Y_Speed',)]]==0
  head=[x for x in calls if x[0]=='head'];assert len(head)==(0 if tile==0xc4 else 1)
  assert len([x for x in calls if x[0]=='box'])==1
  assert m[qn[('Player_X_Position',)]]==96 and m[qn[('Player_PageLoc',)]]==7
  geometry+=1
 elif cur+7*65536>160*65536:
  assert c.a==0 and not calls and m[qn[('Player_Y_Position',)]]==153+offset
  geometry+=1
 else:
  assert not calls and c.a==tile
 # The unchanged ordinary-air path must keep all external behavior.
 if age==8:
  expanded['RgAttack']=0
  a,am,ac=execute(0,expanded);b,bm,bc=execute(1,expanded)
  assert (a.a,a.x,a.y,a.p&0xcf,a.sp,bytes(am[:0x100])+bytes(am[0x200:0x8000]),ac)==(b.a,b.x,b.y,b.p&0xcf,b.sp,bytes(bm[:0x100])+bytes(bm[0x200:0x8000]),bc)
  ordinary+=1
for field,values in [('RyuSourceBodyProfile',[0,16,27]),('Player_State',[0,2,3]),('XgJumpUsed',[0]),('RgCrouch',[1]),('CrouchingFlag',[4]),('SwimmingFlag',[1]),('MmUnderwater',[1]),('XgWall',[1]),('XgWallLock',[1]),('RyPlatformSlot',[1]),('RyWallResolved',[1]),('AvSlash',[1]),('GuestHurtTicks',[1]),('AreaType',[0])]:
 for v in values:
  seed=dict(seed0,**{field:v},FY_HI=0,VY_MID=0,VY_HI=254)
  a,am,ac=execute(0,seed);b,bm,bc=execute(1,seed)
  assert (a.a,a.x,a.y,a.p&0xcf,a.sp,bytes(am[:0x100])+bytes(am[0x200:0x8000]),ac)==(b.a,b.x,b.y,b.p&0xcf,b.sp,bytes(bm[:0x100])+bytes(bm[0x200:0x8000]),bc)
  negative+=1
report=dict(passed=True,baseline_sha256=sha(oldpath),candidate_sha256=sha(newpath),changed_ROM_bytes=len(changed),changed_banks=sorted(set((i-16)//8192 for i in changed)),all_changed_bytes_inside_head_gate=True,old_qualified_symbols_outside_helper_fixed=True,restore_cases=tailcases,geometry_cases=geometry,ordinary_differential_cases=ordinary,negative_differential_cases=negative,
 scope='Assembled source25 retained-air scalar head crossings and restore-tail isolation. All legal nonoverflow snapshot SPs17..253, all256 A/P values at one SP, boundary A/P across every legal SP. Full instruction execution; native block effects and bbox calls are isolated RTS traps in geometry units. Separate native contacts, interrupt/bank guards, and complete physical replay required. No campaign/other retained pose/source-perfect claim.')
(O/'proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
