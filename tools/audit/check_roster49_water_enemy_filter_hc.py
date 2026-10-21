"""Compiled exact-span batch admission and native rejection implication."""
from pathlib import Path
import collections,hashlib,importlib.util,itertools,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-water-enemy-filter-gy'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=J/'compiled-review-hc.json';assert not out.exists()
 assert sha(J/'build-review-ha.json')=='6eedbf9da2b36e9c77fae68200d63b4308c611af1511becb0bf6a197900144d6'
 p=V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py';s=importlib.util.spec_from_file_location('enemy_hc_model',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 class CPU(m.q.core.NesMPU):
  cycletime=list(m.q.core.NesMPU.cycletime);cycletime[0xce]=6
 groups=[]
 for mapper in ['mmc3','mmc5']:
  images=[m.q.Image(V/'root49-lag-combined-i/source/build'/f'smb-crossover-{mapper}.nes'),m.q.Image(J/'source/build'/f'smb-crossover-{mapper}.nes')];L=images[0].ram;assert L==images[1].ram
  def ix(n,i=0):
   a=L[n]+i;return a if a<2048 else a-0x6000+2048
  counter=ix('SsEnemies');cases=[]
  for flag,state,kind,offscreen in itertools.product([0,1,127,128,255],[0,1,2,31,32,33,255],range(64),[0,1,128,255]):
   rows=[(0,0,0,0)]*6;rows[len(cases)%6]=(flag,state,kind,offscreen);cases.append(rows)
  for mask in range(64):cases.append([(1,0,(6 if i%2 else 0x2d),0 if mask&(1<<i)else 1)for i in range(6)])
  counts=collections.Counter();cost=collections.Counter();digest=hashlib.sha256()
  for number,rows in enumerate(cases):
   raw=bytearray((i*31+number)&255 for i in range(10240));raw[counter]=0
   for slot,row in enumerate(rows):
    for n,v in zip(['Enemy_Flag','Enemy_State','Enemy_ID','EnemyOffscrBitsMasked'],row):raw[ix(n,slot)]=v
   expected=[];outputs=[]
   for filtered,image in enumerate(images):
    expected.append(sum(0<flag<128 and not state&32 and(kind<21 or kind in[45,51])and(not filtered or offscreen==0)for flag,state,kind,offscreen in rows))
    mem=m.Bus(image,raw,{0x8000:62,0xa000:60,0xc000:13,0xe000:63},());cpu=CPU(memory=mem);cpu.a=number&255;cpu.x=5;cpu.y=number*7&255;cpu.p=number*13&0xcf;cpu.sp=0xed;cpu.pc=image.hook('EnemyCandidates','SpecialWeapons')['address'];cpu.processorCycles=0
    stop=images[0].hook('EnemyNext','SpecialWeapons')['address']+6;steps=0
    while cpu.pc!=stop:
     mem.pc=cpu.pc;mem.op=mem.data[cpu.pc];cpu.step();steps+=1;assert steps<200
    result=mem.ram();assert result[counter]==expected[-1],(mapper,number,filtered,result[counter],expected[-1])
    assert all(a==b for i,(a,b)in enumerate(zip(raw,result))if i!=counter)
    outputs.append(dict(regs=[cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc],ram=result,cycles=cpu.processorCycles,banks=mem.banks,selector=mem.selector,ports=mem.ports))
   for key in ['regs','banks','selector','ports']:assert outputs[0][key]==outputs[1][key],(mapper,number,key)
   # Every removed candidate has the exact unchanged native rejection byte.
   if expected[1]==0:
    for flag,state,kind,offscreen in rows:
     if 0<flag<128 and not state&32 and(kind<21 or kind in[45,51]):assert offscreen!=0
   counts['changed_to_empty'if expected[0]and not expected[1]else'conservative_nonempty'if expected[1]else'empty']+=1
   cost[outputs[0]['cycles']-outputs[1]['cycles']]+=1;digest.update(bytes(outputs[1]['regs'][:5]));digest.update(outputs[1]['ram'])
  groups.append(dict(mapper=mapper,cases=len(cases),classes=counts,scan_cycle_savings_histogram=dict(cost),digest=digest.hexdigest()));print(mapper,len(cases),dict(counts),flush=True)
 out.write_text(json.dumps(dict(status='PASS_COMPILED_BATCH_COUNTER_ABI_AND_NO_FALSE_EMPTY_NATIVE_ELIGIBILITY',script_sha256=sha(__file__),build_review_sha256=sha(J/'build-review-ha.json'),groups=groups,compared='Exact AXYP/SP/continuation, all10240RAM except the intentionally refined SsEnemies counter, banks/selector/ports. Every changed-to-empty actor has exact unchanged native offscreen rejection. All64 native kinds, five flag states, seven states, four offscreen bytes; rotating real six slot positions plus all64 six-actor offscreen masks.',limits=['Authored compiled isolated scan only, not natural route/whole-game/ISR or source collision certification. Native effect/transition checks and actual eligible-enemy profiles remain separate.','Only pre-existing native reject is hoisted; no projectile/enemy/damage/collision geometry is changed. Mixed special-batch state and scratch liveness still require actual native review.'],main_changed=False,goal_complete=False),indent=2)+'\n',encoding='utf-8');print('COMPILED',sha(out),flush=True)
if __name__=='__main__':main()
