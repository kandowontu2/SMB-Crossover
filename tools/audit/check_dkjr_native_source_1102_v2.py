"""Independent donor/relocated phase, contact and typed rectangle proofs."""
from pathlib import Path
import collections,json,re,sys
import prepare_dkjr_native_source_1102_v2 as P
D=P.D;R=P.R;O=P.O


class Flat(list):pass


def main():
 lab={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'component.lbl').read_text(),re.M)};blob=(O/'component.bin').read_bytes();layout=json.loads((O/'layout.json').read_text());imports={pc:int(name,16)for name,pc in layout['imports'].items()};counts=collections.Counter();import_counts=collections.Counter();minimum_sp=255
 maps={int(n[6:],16):pc for n,pc in lab.items()if re.fullmatch('DData_[0-9a-f]{4}',n)}
 for original,length in layout['geometry_list_lengths'].items():
  original=int(original)
  for i in range(length):maps[original+i]=lab['DGeometry_%04x'%original]+i
 inverse={v:k for k,v in maps.items()}
 def translate(r,to_private):
  out=bytearray(r);mapping=maps if to_private else inverse
  for i in[2,0x91]:
   v=out[i]+256*out[i+1]
   if v in mapping:v=mapping[v];out[i]=v&255;out[i+1]=v>>8
  return out
 def native_call(m,entry,regs=(0,0,0,0x20),native_geometry=False):
  nonlocal minimum_sp
  c=D.T.NesMPU(memory=m,pc=entry);c.a,c.x,c.y,c.p=regs;c.sp=0xfd;c.stPushWord(0x5ffe);trace=collections.Counter()
  for _ in range(100000):
   if c.pc==0x5fff:break
   minimum_sp=min(minimum_sp,c.sp)
   for name in['DkjrInput','DkjrClock','DkjrMove','DkjrFruitHit','DkjrDefeatTick']:
    if c.pc==lab[name]:trace[name]+=1
   if c.pc in imports:
    imp=imports[c.pc];import_counts['%04X'%imp]+=1;q=D.T.NesMPU(memory=D.Bus(),pc=imp);q.memory[:2048]=translate(m[0xc000:0xc800],False);q.memory[0x100:0x200]=m[0x100:0x200]
    q.a,q.x,q.y,q.p,q.sp=c.a,c.x,c.y,c.p,c.sp;ret=m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1;D.until(q,ret&65535,limit=100000)
    m[0xc000:0xc800]=translate(q.memory[:2048],True);m[0x100:0x200]=q.memory[0x100:0x200];c.a,c.x,c.y,c.p,c.sp,c.pc=q.a,q.x,q.y,q.p,q.sp,q.pc
   else:assert m[c.pc]!=0,('BRK',hex(c.pc));c.step()
  else:raise AssertionError(('Component bound',hex(entry),hex(c.pc)))
  return (c.a,c.x,c.y,c.p,c.sp),trace
 def relocated(r,entry,regs=(0,0,0,0x20),geometry=None):
  m=Flat([0]*65536);m[0xa000:0xa000+len(blob)]=blob;m[0xc000:0xc800]=translate(r,True)
  native_call(m,lab['DkjrUseOriginalGeometry'])
  if geometry:
   for base,data in zip([0xc800,0xc840,0xc880],geometry):m[base:base+len(data)]=data
   z,_=native_call(m,lab['DkjrUseNativeGeometry']);assert z[3]&1
  got,trace=native_call(m,lab['D_%04x'%entry],regs,native_geometry=bool(geometry));return translate(m[0xc000:0xc800],False),got,trace,m
 def original(r,entry,regs,geometry):
  m=D.Bus();m[:2048]=r
  if geometry:
   for table,base,data in zip([0xc440,0xc448,0xc450],[0x700,0x740,0x780],geometry):
    m[base:base+len(data)]=data
    for i in range(4):list.__setitem__(m,table+2*i,base&255);list.__setitem__(m,table+2*i+1,base>>8)
  c=D.T.NesMPU(memory=m,pc=entry);z=D.T.run(c,entry,*regs,limit=100000);return c,z
 def compare(r,entry,regs=(0,0,0,0x20),cohort='source',geometry=None):
  # Both copies retain identical original RAM. Native-only context is a
  # declared extra measurement range; donor table substitution reads the
  # same source-format lists through original RAM700/740/780 fixtures.
  r=bytearray(r)
  if geometry:
   for base,data in zip([0x700,0x740,0x780],geometry):r[base:base+len(data)]=data
  q,z=original(r,entry,regs,geometry);out,got,trace,m=relocated(r,entry,regs,geometry)
  indices=list(range(256))+list(range(0x200,0x800));diff=[(i,q.memory[i],out[i])for i in indices if q.memory[i]!=out[i]]
  assert not diff,(cohort,hex(entry),diff[:12]);assert z[:3]==got[:3]and z[3]&0xef==got[3]&0xef and z[4]==got[4],(cohort,hex(entry),z,got)
  counts[cohort]+=1;return q,trace
 # Independent original reset/start trajectories reach phase and every
 # original terrain/contact leaf naturally. No donor import stand-in is
 # used for any of the newly recovered ranges.
 watched={0xcd91,0xd2fc,0xe893,0xe897,0xe89b,0xe89f};natural=0;states=set();jump_seed=None;vine_seed=None
 for name,controls in[('walk',[1]*100),('jump',[1]*48+[0x81]*14+[0]*55),('vine',[1]*48+[0x81]*9+[8]*50)]:
  c,_=D.active()
  def watch(q):
   if q.pc in watched:compare(bytes(q.memory[:2048]),q.pc,(q.a,q.x,q.y,q.p),'natural-'+name)
  for pad in controls:
   D.frame(c,pad,watch);natural+=1;states.add(c.memory[0x6b])
   if c.memory[0x6b]==3 and jump_seed is None:jump_seed=bytes(c.memory[:2048])
   if c.memory[0x6b]==2 and vine_seed is None:vine_seed=bytes(c.memory[:2048])
 assert jump_seed and vine_seed,(states,bool(jump_seed),bool(vine_seed))
 # Explicit air-input cases start from naturally earned jump/vine states;
 # falling is entered through the original detach routine.
 falling=D.T.NesMPU(memory=D.Bus(),pc=0);falling.memory[:2048]=vine_seed;D.T.run(falling,0xdad7);assert falling.memory[0x6b]==4
 phases=[]
 for seed in[jump_seed,bytes(falling.memory[:2048])]:
  for direction in[1,2,4,8]:
   r=bytearray(seed);r[0x14]=direction;r[0x15]=direction;before=r[0x54];original_state=r[0x6b];q,trace=compare(r,0xcd91,cohort='latched-air-phase')
   assert trace['DkjrInput']==0 and trace['DkjrMove']==1 and trace['DkjrClock']==1
   phases.append(dict(state=original_state,physical_input=direction,latched_direction_before=before,Input_calls=0,Move_calls=1,Clock_calls=1))
 active,_=D.active();r=bytearray(active.memory[:2048]);r[0x68]=1;r[0x69]=0;r[0x66]=0
 q,freeze=compare(r,0xcd91,cohort='original-fruit-hit-phase');assert freeze['DkjrFruitHit']==1 and not freeze['DkjrInput']and not freeze['DkjrMove']and not freeze['DkjrClock']
 r=bytearray(active.memory[:2048]);damage=D.T.NesMPU(memory=D.Bus(),pc=0);damage.memory[:2048]=r;D.T.run(damage,0xd405);q,death=compare(bytes(damage.memory[:2048]),0xcd91,cohort='original-defeat-phase');assert death['DkjrDefeatTick']==1 and not death['DkjrClock']and not death['DkjrMove']
 geometry_cases=0
 geometries=[([0,208,254,223],[64,32,64,207,96,32,96,207],[128,32,143,207]),([],[],[]),([16,96,47,111,64,160,95,175],[48,0,48,207,72,0,72,207],[0,0,15,239,144,32,159,207])]
 for floor,vines,walls in geometries:
  geometry=[bytes(values+[255])for values in[floor,vines,walls]]
  for stage in[1,2,3,4]:
   for x,y in[(40,80),(48,80),(64,191),(96,159),(128,64),(144,207)]:
    for entry in[0xe893,0xe897,0xe89b,0xe89f,0xe8a3]:
     for flags in[0x20,0xf1]:
      r=bytearray(active.memory[:2048]);r[0x4a]=stage;r[0x3e:0x42]=bytes([x,y,min(x+32,254),min(y+15,239)]);compare(r,entry,(0x57,7,9,flags),'typed-source-format-native-rectangles',geometry);geometry_cases+=1
 # Invalid list rejection does not partially publish new pointers.
 rejected=0
 for bad in['missing-FF','reversed-X','reversed-Y']:
  m=Flat([0]*65536);m[0xa000:0xa000+len(blob)]=blob;m[0xc8c0:0xc8d8]=bytes([0xa5])*24
  for base in[0xc800,0xc840,0xc880]:m[base]=255
  if bad=='missing-FF':m[0xc800:0xc840]=bytes(64)
  elif bad=='reversed-X':m[0xc800:0xc805]=[64,32,48,64,255]
  else:m[0xc800:0xc805]=[32,64,48,32,255]
  z,_=native_call(m,lab['DkjrUseNativeGeometry']);assert not z[3]&1 and m[0xc8c0:0xc8d8]==[0xa5]*24;rejected+=1
 out=dict(passed=True,native=False,ROM_written=False,component_SHA256=P.sha(blob),CPU_cases=sum(counts.values()),cohorts=dict(counts),natural_original_NMI_frames=natural,source_states_seen=sorted(states),latched_air_phase=phases,fruit_hit_branch=dict(FruitHit=1,Input=0,Move=0,Clock=0),defeat_branch=dict(DefeatTick=1,Move=0,Clock=0),typed_rectangle_cases=geometry_cases,invalid_list_rejections=rejected,minimum_CPU_SP=minimum_sp,remaining_imports_observed=dict(import_counts),resources=layout,bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),O/'component.bin',O/'component.s',O/'layout.json']},scope='Independent original instructions compare all original nonstackRAM, AXYP(B ignored),SP. Natural donor trajectories plus declared source-format rectangle fixtures. Untimed CPU only; native terrain/vine producer, fruit/enemy/UI imports, real mapper/NMI/IRQ and host ownership remain unimplemented.')
 (O/'CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,CPU_cases=out['CPU_cases'],cohorts=out['cohorts'],component_bytes=len(blob),typed_rectangle_cases=geometry_cases,latched_air_cases=len(phases),remaining_imports_observed=dict(import_counts))))


if __name__=='__main__':main()
