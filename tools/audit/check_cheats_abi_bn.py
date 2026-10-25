"""Compiled CPU parity of rare cleanup, damage gate and all starting levels."""
from pathlib import Path
import ast,hashlib,itertools,json
from py65.devices.mpu6502 import MPU
R=Path(__file__).resolve().parents[2];O=R/'build/verification/cheats-abi-br';assert not O.exists();O.mkdir()
source=R/'tools/audit/check_score_abi_at.py'
tree=ast.parse(source.read_text())
nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in('labels','segment','Bus')]
ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),ns)
labels,segment,Bus=(ns[n]for n in('labels','segment','Bus'))
def finish(cpu,mem,limit=400):
 cpu.sp=0xe0;stop=0x5d00;mem.ram[0x1e1]=(stop-1)&255;mem.ram[0x1e2]=(stop-1)>>8
 steps=0
 while cpu.pc!=stop:
  cpu.step();steps+=1;assert steps<limit
 assert cpu.sp==0xe2
 return steps,cpu.processorCycles
results=[]
for mapper in('mmc3','mmc5'):
 stem=R/'build'/f'smb-crossover-{mapper}';raw=stem.with_suffix('.nes').read_bytes();L=labels(stem.with_suffix('.lbl'));smc=segment(stem.with_suffix('.dbg'),'SMCCODE')
 before=R/'build/checkpoints/score-popup-location-az/build'/f'smb-crossover-{mapper}'
 old=before.with_suffix('.nes').read_bytes();oldL=labels(before.with_suffix('.lbl'));oldsmc=segment(before.with_suffix('.dbg'),'SMCCODE')
 total=0;cost=[]
 patterns=([0]*6,[6]*6,[0x17]*6,[6,0x17,6,0x33,6,6],[0,1,2,3,4,5],[255,0,255,0,255,0])
 for selector,p,target,ids in itertools.product(range(0x40,0x48)if mapper=='mmc3'else[0],(0,1,0x40,0x41,0x44,0xc1),(0,6,0x17,0x33,255),patterns):
  observations=[]
  for rom,syms,sm in((old,oldL,oldsmc),(raw,L,smc)):
   mem=Bus(rom,syms,sm,mapper,selector)
   for i,id in enumerate(ids):
    mem.put('Enemy_ID',id,i)
    for n in('Enemy_Flag','EnemyMetasprite','EnemyVerticalFlip'):mem.put(n,(i*37+17)&255,i)
   cpu=MPU(memory=mem,pc=syms['KillEnemies']);cpu.a=target;cpu.x=0xa5;cpu.y=0x5a;cpu.p=p
   steps,cycles=finish(cpu,mem)
   observations.append(dict(reg=(cpu.a,cpu.x,cpu.y,cpu.p&0xcf,cpu.sp),
    fields=tuple(mem.get(n,i)for n in('Enemy_ID','Enemy_Flag','EnemyMetasprite','EnemyVerticalFlip')for i in range(6)),
    scratch=bytes(mem.ram[:8]),bank=mem.a,bankC=mem.c,selector=mem.selector,shadow=mem.get('BankShadow')if mapper=='mmc3'else 0,cycles=cycles))
  z,w=observations;assert all(z[k]==w[k]for k in z if k!='cycles'),(mapper,selector,p,target,ids,z,w)
  cost.append(w['cycles']-z['cycles']);total+=1
 gate=0
 for injury,enabled,p in itertools.product(range(256),(0,1),(0,0x41,0xc5)):
  mem=Bus(raw,L,smc,mapper,0x43);mem.put('InjuryTimer',injury);mem.put('CheatInvincible',enabled)
  cpu=MPU(memory=mem,pc=L['CheatsInjuryTimer']);cpu.a=0xa5;cpu.x=0x57;cpu.y=0x84;cpu.p=p
  finish(cpu,mem)
  v=injury|enabled;nz=(2 if v==0 else 0)|(v&128)
  assert(cpu.a,cpu.x,cpu.y)==(v,0x57,0x84)and(cpu.p&0x4d)==(p&0x4d)and(cpu.p&0x82)==nz
  gate+=1
 levels=0
 areas=((0,1,3,4),(0,1,3,4),(0,1,2,3),(0,1,3,4),(0,1,2,3),(0,1,2,3),(0,1,3,4),(0,1,2,3))
 for value,cont,enabled in itertools.product(range(32),(0,0x80),(False,True)):
  mem=Bus(raw,L,smc,mapper,0x40);mem.a=0x14;mem.put('CurrentBank',0x14|(0x80 if mapper=='mmc5'else 0));mem.put('CheatStartLevel',value|(32 if enabled else 0));mem.put('CrossoverContinue',cont)
  names=('WorldNumber','OffScr_WorldNumber','LevelNumber','OffScr_LevelNumber','AreaNumber','OffScr_AreaNumber','HalfwayPage','OffScr_HalfwayPage','AltEntranceControl')
  for n in names:mem.put(n,0xa5)
  cpu=MPU(memory=mem,pc=L['CheatsApplyStartingLevel']);finish(cpu,mem)
  if not enabled:assert all(mem.get(n)==0xa5 for n in names)and mem.get('CrossoverContinue')==cont
  else:
   world,level=divmod(value,4);wanted=(world,world,level,level,areas[world][level],areas[world][level],0,0,0)
   assert tuple(mem.get(n)for n in names)==wanted and mem.get('CrossoverContinue')==0
  levels+=1
 results.append(dict(mapper=mapper,ROM_sha256=hashlib.sha256(raw).hexdigest(),cleanup_cases=total,cleanup_registers_flags_slots_scratch_stack_mapper_exact=True,cleanup_extra_cycles_min=min(cost),cleanup_extra_cycles_max=max(cost),damage_gate_cases=gate,level_mapping_and_continue_cases=levels))
report=dict(passed=True,results=results,test_model_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),scope='Compiled instructions and mapper-aware memory. Separate native controller/arena evidence is required; no interrupt-injection claim. Damage-gate call adds16 cycles only when native injury is attempted; normal non-contact gameplay has no added instructions.',goal_complete=False)
(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
