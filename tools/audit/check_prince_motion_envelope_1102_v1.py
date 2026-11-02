"""Original script and genuine pose projection trajectory, not actorY alone."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prince_original_cpu_1101_v1 as P
from recover_prince_core_1101_v1 import O


def main():
 art=json.loads((O/'source-art.json').read_text());poses={(q['source_frame'],q['source_facing']):q for q in art['poses']}
 seed=(O/'state-899.bin').read_bytes();rows=[]
 for action in [1,3,4,7,8,10,14,17,18,28,42,58,68]:
  for face in [0,255]:
   c=P.machine();list.__setitem__(c.memory,slice(0,2048),seed)
   c.memory[0x69]=0;c.memory[0x615]=face;c.memory.switch(5)
   P.call(c,0x8730,a=action,y=0);seen=set();trace=[]
   for tick in range(512):
    ptr=c.memory[0x613]|c.memory[0x614]<<8
    if ptr in seen:break
    seen.add(ptr);c.a=85;c.x=0;c.y=0;c.p=0x21;c.sp=253;c.stPushWord(0x5ffe);c.pc=0xf158
    for _ in range(10000):
     if c.pc==0xf1a2:break
     assert c.memory[c.pc]!=0;c.step()
    else:raise AssertionError('Original animation advance bound')
    frame=c.memory[0x617];ay=c.memory[0x611];ax=c.memory[0x60f]|c.memory[0x610]<<8
    if frame:
     pose=poses[frame,c.memory[0x615]];delta=pose['source_projection_geometry']['native_06F1_minus_anchor_y'];delta=delta if delta<128 else delta-256
     trace.append(dict(update=tick,frame=frame,actor_X=ax,actor_Y=ay,physical_projected_bottom=ay+delta,projection_bottom_delta=delta,pose_top=ay+min(p['y']for p in pose['parts_8x16'])))
    c.pc=(c.stPopWord()+1)&65535
    if c.memory[0x60e]==255:break
   baseline=seed[0x611]+poses[15,face]['source_projection_geometry']['native_06F1_minus_anchor_y']
   rows.append(dict(action=action,initial_facing=face,initial_physical_bottom=baseline,actor_Y_range=[min(v['actor_Y']for v in trace),max(v['actor_Y']for v in trace)],physical_bottom_range=[min(v['physical_projected_bottom']for v in trace),max(v['physical_projected_bottom']for v in trace)],physical_bottom_peak_rise=baseline-min(v['physical_projected_bottom']for v in trace),trace=trace))
 q=dict(passed=True,source_CPU_only=True,native_host=False,donor_sha256=P.SHA,source_actions=13,both_facings=True,source_projection_authority='Original bank4 B3B7 reads frame vertical offset; B3C5 adds logical actorY and B3F1 adds3 to publish06F1. Actual source8x8 renderer/uploader art packet supplies that exact per-frame delta. ActorY alone is not physical body/foot motion.',rows=rows,scope='Actual original93-program interpreter subset with genuine donor world/audio consumers. Directed source action selections, not controller-earned native obstacles. Projection metadata was independently executed/decoded against original pixels. No invented jump curve or native1-1/helper claim.',bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[Path(__file__),Path(P.__file__),O/'state-899.bin',O/'source-art.json']})
 (O/'motion-envelope.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['rows','bindings']}));print(json.dumps([{k:v for k,v in row.items()if k!='trace'}for row in rows]))


if __name__=='__main__':main()
