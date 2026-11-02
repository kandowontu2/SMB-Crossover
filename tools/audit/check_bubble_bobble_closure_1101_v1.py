"""Instruction differentials on recovered donor code, with explicit bridge stubs."""
import collections,hashlib,json
import recover_bubble_bobble_source_1101_v1 as B
from py65.devices.mpu6502 import MPU

O=B.O;RET=0x300
SOUND=0xfa81;STUBS=[SOUND,0xc0a4,0xc470,0x8153,0x8156,0xee70,0xf01e,0x97c9]
manifest=json.loads((O/'source-closure.json').read_text());payload=(O/'donor-source.bin').read_bytes()
counts=collections.Counter();pcs=set();bridges=collections.Counter();digest=hashlib.sha256();max_steps=0
cycles=collections.defaultdict(list)


def pair():
 a=B.image(6);b=B.image(6);at=0
 for s in manifest['source_ranges']:
  b.memory[s['start']:s['end_exclusive']]=payload[at:at+s['bytes']];at+=s['bytes']
 for m in [a,b]:
  for p in STUBS:m.memory[p]=0x60
  m.memory[0x500:0x800]=[1]*768
  for x,y,ox,attr in [(0x2e,0,32,3),(0x42,8,208,0)]:
   m.memory[x]=3;m.memory[0x200+y:0x208+y]=[176,0,attr,ox,176,10,attr,ox+8]
  m.memory[0x45d]=2;m.memory[0x40a]=120;m.memory[0x463]=5;m.memory[0x454]=16
 return a,b


def put(p,at,data):
 if isinstance(data,int):data=[data]
 for m in p:m.memory[at:at+len(data)]=data


def run(p,pc,x=0,y=0,a=0,flags=0x30,stop=RET,tag='component'):
 global max_steps
 for m in p:m.pc=pc;m.x=x;m.y=y;m.a=a;m.p=flags;m.sp=255;m.stPushWord(RET-1)
 n=0;cycle_start=p[0].processorCycles
 while p[0].pc!=stop:
  m,z=p;assert(m.pc,m.a,m.x,m.y,m.p,m.sp)==(z.pc,z.a,z.x,z.y,z.p,z.sp)
  at=m.pc;assert at in STUBS or any(s['start']<=at<s['end_exclusive']for s in manifest['source_ranges']),(tag,hex(at))
  if at in STUBS:bridges[f'{at:04X}']+=1
  else:pcs.add(at)
  digest.update(at.to_bytes(2,'little'));digest.update(bytes([m.a,m.x,m.y,m.p,m.sp]))
  m.step();z.step();n+=1;assert n<20000,(tag,hex(m.pc))
 assert p[0].memory[:0x800]==p[1].memory[:0x800] and p[0].processorCycles==p[1].processorCycles,tag
 max_steps=max(max_steps,n);counts[tag]+=1;cycles[tag].append(p[0].processorCycles-cycle_start)
 return p[0]


def main():
 # Controller semantics are independent of the hand-authored dispatch labels.
 for actor,oy in [(0x2e,0),(0x42,8)]:
  for fresh in range(256):
   held=((fresh*73)^0xa5)&255;p=pair();put(p,0xf5+bool(oy),fresh);put(p,0xf7+bool(oy),held)
   m=run(p,0xd1a0,x=actor,y=0xf5+bool(oy),tag='input')
   assert m.memory[actor+1]==((fresh&0xc0)>>2)|((fresh&3)<<2)|(held&0xc3)
 # Stock ascent table, source direction carry, both identities and speed flags.
 jump=[]
 for actor,oy in [(0x2e,0),(0x42,8)]:
  for direction in [0,1,2,3]:
   for speed in [0,1]:
    p=pair();put(p,actor+1,0x20|direction);put(p,actor+2,speed);put(p,0x1f,0)
    run(p,0xd365,x=actor,y=oy,tag='jump_start');assert p[0].memory[actor+4]==28 and p[0].memory[actor+5]==direction
    ys=[]
    for frame in range(28):
     put(p,0x1f,frame);run(p,0xd386,x=actor,y=oy,tag='jump_ascent');ys.append(p[0].memory[0x200+oy])
    assert ys[-1]==133 and p[0].memory[actor+3]==2,(actor,direction,speed,ys[-1],p[0].memory[actor+3])
    jump.append(dict(actor='Bub'if actor==0x2e else'Bob',direction=direction,speed_flag=speed,ascent_updates=28,rise=176-ys[-1],final_x=p[0].memory[0x203+oy]))
 # Fresh-B requests, saturation, fast-shot candy, identity bit and original timing.
 motion=[]
 for actor,oy in [(0x2e,0),(0x42,8)]:
  for direction in [1,2]:
   for fast in [0,1]:
    p=pair();put(p,0x461,1);put(p,actor+1,direction);put(p,actor+2,fast);put(p,0x203+oy,100);put(p,0x207+oy,108)
    put(p,0x780,[0]*128)
    for frame in range(30):
     put(p,0x1f,frame);put(p,0x28,3-frame%3);run(p,0xd1e7,x=actor,y=oy,tag='player_flat')
    expected=100+(30*(1+fast)-fast if direction==1 else -30*(1+fast))
    assert p[0].memory[0x203+oy]==expected and p[0].memory[0x200+oy]==176,(actor,direction,fast,expected,p[0].memory[0x203+oy],p[0].memory[0x200+oy],p[0].memory[actor:actor+10])
    motion.append(dict(actor=actor,direction=direction,speed_flag=fast,updates=30,dx=expected-100))
 for actor in [0x2e,0x42]:
  for upgrade in range(8):
   for timer in range(28):
    p=pair();put(p,actor+8,timer);put(p,actor+2,upgrade);put(p,0x464,1)
    m=run(p,0xd530,x=actor,tag='shot_request')
    assert m.memory[actor+8]==(timer if timer else 12 if upgrade&4 else 25)
    assert m.memory[0x464]==(1 if timer else 1|(0x80 if actor==0x2e else 0x40))
 # Actual source scheduler handles requests and grows an empty bubble through24 updates.
 spawn=[]
 for request in [0x80,0x40,0xc0]:
  p=pair();put(p,0x464,request)
  for frame in range(24):
   put(p,0x1f,frame);run(p,0xd887,stop=0xd8fd,tag='bubble_scheduler')
  active=[(x,p[0].memory[x])for x in range(0x88,0xc4,4)if p[0].memory[x]]
  assert len(active)==(2 if request==0xc0 else 1) and all(state==2 for x,state in active)
  spawn.append(dict(request=request,active=len(active),states=[v for x,v in active],sprites=list(p[0].memory[0x288:0x298])))
 # Saturated original pool is bounded at15 slots; request cleanup never grows it.
 p=pair()
 for i,x in enumerate(range(0x88,0xc4,4)):
  put(p,x,[2,200,3,8]);put(p,0x288+i*8,[48,0x26,3,64+i*8,48,0x28,3,72+i*8])
 put(p,0x464,0xc0);run(p,0xd887,stop=0xd8fd,tag='bubble_capacity')
 capacity=[]
 for frame in range(3):
  if frame:run(p,0xd887,stop=0xd8fd,tag='bubble_capacity')
  capacity.append(dict(active=sum(bool(p[0].memory[x])for x in range(0x88,0xc4,4)),pending=p[0].memory[0x464]))
 assert capacity==[dict(active=14,pending=192),dict(active=14,pending=64),dict(active=15,pending=0)],capacity
 # Native enemy mirrors must be trapped, not killed: exact donor DE99 flags/timer.
 traps=[]
 for owner in [0,3]:
  for delta in range(14):
   for immune in [0,8,16]:
    p=pair();put(p,0x88,[1,0,0,8]);put(p,0x288,[100,0x20,owner,100,100,0x20,owner,108]);put(p,0x68,[1,0,immune,0]);put(p,0x210,[100,0x40,0,100+delta,100,0x42,0,108+delta])
    m=run(p,0xda00,x=0x88,y=0x88,tag='trap_contact');hit=delta<12 and immune==0
    assert bool(m.memory[0x6a]&16)==(hit or immune==16)
    assert m.memory[0x88]==(0 if hit else 1)
    if hit:assert m.memory[0x413]==120 and m.memory[0x6a]&1==bool(owner)
    traps.append(int(hit))
 # Empty bubble contact pop, nearby pop chaining and original trapped-enemy pop flag.
 p=pair();put(p,0x200,[100,0,3,100,100,10,3,108]);put(p,0x88,[2,100,3,8]);put(p,0x288,[100,0x26,3,100,100,0x28,3,108]);put(p,0x8c,[2,100,3,8]);put(p,0x290,[100,0x26,3,112,100,0x28,3,120]);put(p,0x68,[1,0,16,0]);put(p,0x210,[100,0,0,112,100,0,0,120]);put(p,0x413,120)
 run(p,0xdc55,x=0x88,y=0x88,tag='pop_contact');assert p[0].memory[0x88]==4
 run(p,0xdd6d,tag='pop_chain');assert p[0].memory[0x88]==5 and p[0].memory[0x8c]==4 and p[0].memory[0x6b]==4
 run(p,0xdd6d,tag='pop_chain');run(p,0xdd6d,tag='pop_chain')
 assert p[0].memory[0x8c]==5 and p[0].memory[0x6b]==5
 put(p,0x26,0x68);run(p,0x9528,x=0x68,y=0x10,tag='trapped_pop');assert p[0].memory[0x6a]&24==24
 # Actual trapped-enemy timeout clears trap and enters original escape path.
 p=pair();put(p,0x68,[1,0,16,0]);put(p,0x210,[100,0,0,100,100,0,0,108]);put(p,0x413,1);put(p,0x26,0x68)
 run(p,0x9528,x=0x68,y=0x10,stop=0x9603,tag='trap_timeout')
 assert not p[0].memory[0x6a]&16 and p[0].memory[0x69]==0x8c and p[0].memory[0x6b]==0x80
 # Empty bubble normal->warning->burst and exact three-step burst animation.
 p=pair();put(p,0x88,[2,1,3,8]);put(p,0x288,[64,0x26,3,100,64,0x28,3,108])
 run(p,0xdb7f,x=0x88,y=0x88,tag='bubble_age');assert p[0].memory[0x88]==3 and p[0].memory[0x89]==180
 put(p,0x89,1);run(p,0xdb7f,x=0x88,y=0x88,tag='bubble_age');assert p[0].memory[0x88]==5
 for frame in [0,4,8]:
  put(p,0x1f,frame);run(p,0xda81,x=0x88,y=0x88,tag='bubble_burst')
 assert p[0].memory[0x88:0x8c]==[0]*4 and p[0].memory[0x288]==0xf4
 # A below-player bubble sets the source support bit; held A starts the same jump.
 ride=[]
 for actor,oy in [(0x2e,0),(0x42,8)]:
  p=pair();put(p,actor+3,2);put(p,actor+1,0x80);put(p,0x200+oy,[100,0,3,100,100,10,3,108]);put(p,0x88,[2,100,3,8]);put(p,0x288,[112,0x26,3,100,112,0x28,3,108])
  run(p,0xdc55,x=0x88,y=0x88,tag='bubble_support');assert p[0].memory[actor+9]
  run(p,0xd2c1,x=actor,y=oy,tag='bubble_ride');assert p[0].memory[actor+3]==1 and p[0].memory[actor+4]==28
  ride.append(dict(actor=actor,jump_restarted=True))
 # Every source animation pose in both facings; native8x16 retains2 body sprites.
 poses=[];allowed=set(range(0,0x30,2))|{0x27}
 for actor,oy in [(0x2e,0),(0x42,8)]:
  for pose in range(23):
   for facing in [0,64]:
    p=pair();put(p,0x202+oy,(3 if actor==0x2e else 0)|facing)
    run(p,0xd693 if pose<=10 or pose==22 else 0xd6af,x=actor,y=oy,a=pose,tag='animation')
    packet=list(p[0].memory[0x200+oy:0x208+oy]);assert packet[1]in allowed and packet[5]in allowed
    poses.append(dict(actor=actor,pose=pose,facing=facing,OAM=packet))
 q=dict(passed=True,ROM_sha256=B.PIN,source_sha256=manifest['source_sha256'],exact_instruction_lockstep=True,call_counts=dict(counts),cycle_ranges={k:dict(min=min(v),max=max(v),mean=round(sum(v)/len(v),2))for k,v in cycles.items()},calls=sum(counts.values()),unique_source_PCs=len(pcs),trace_sha256=digest.hexdigest(),max_steps_per_call=max_steps,bridges=dict(bridges),jump=jump,motion=motion,spawning=spawn,capacity=capacity,trap_contact_cases=len(traps),actual_traps=sum(traps),pop_chain_and_enemy_pop=True,source_trap_timeout=True,source_bubble_age_burst=True,bubble_riding=ride,poses=poses,host_allocation=False,scope='Exact source slices against original ROM in a6502 CPU fixture. No native host, banked transport, ISR, terrain adapter, original main/NMI scheduler or emulator validation. Sound/score/UI/special mode/stage bubble spawn/enemy renderer are explicit RTS imports. Normal bubble core, trap/pop chain and source bubble support execute actual donor instructions.')
 (O/'CPU-closure.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','calls','unique_source_PCs','max_steps_per_call','trap_contact_cases','actual_traps','host_allocation']}))


if __name__=='__main__':main()
