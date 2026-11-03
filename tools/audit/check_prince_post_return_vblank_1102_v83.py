"""Compare actual native interrupt runs after equal real VRAM queue drains."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_post_return_stack_1102_v80 as V
import check_prince_native_stack_1102_v72 as S
N,O=S.N,V.O


def drained_state(m):
 before=([bytes(z)for z in m.ram],bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:]);writes=len(m.ram_writes)
 c=N.NesMPU(memory=m,pc=0x5b00);c.a,c.x,c.y,c.p,c.sp=83,71,109,0x21,224;c.nmi()
 for _ in range(200000):
  if(c.pc,c.sp)==(0x5b00,224):break
  assert m[c.pc]!=0,('VBlank drain BRK',hex(c.pc));c.step()
 else:raise AssertionError('VBlank drain bound')
 assert(c.a,c.x,c.y,c.p&0xef)==(83,71,109,0x21)
 assert before==([bytes(z)for z in m.ram],bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:])and not m.ram_writes[writes:]
 return S.state(m)+(bytes(m.vram),)


def main():
 source=Path(V.__file__);text=source.read_text().replace('v80','v83')
 text=text.replace("try:env['main']()", "try:\n  env['state']=drained_state\n  env['main']()")
 marker=" env=dict(__file__"
 text=text.replace(marker," text=text.replace(\"cuts=sorted(ref['cuts']);minimum\",\"cuts=sorted(ref['cuts']);print('ISR cuts',name,len(cuts),flush=True);minimum\")\n"+marker)
 env=dict(__file__=str(Path(__file__)),__name__='prince_postreturn_vblank_v83',drained_state=drained_state);exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'native-stack-CPU-v83.json';q=json.loads(path.read_text());q.update(final_native_VRAM_and_queue_compared_after_equal_real_VBlank_drains=True,immediate_ISR_private_scratch_five_SMC_mapper_and_register_guards_unchanged=True,lag_NMI_native_VRAM_drain_negative_retained='post-return-boundary-v82.json')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,O/'post-return-boundary-v82.json',O/'post-return-foreign-CPU-v81.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
