"""Original-vs-compiled source physics/actions with actual host block lookup.

Controlled CPU arenas only; no native gameplay/PPU/NMI/campaign claim.
"""
import json,sys
from pathlib import Path
from py65.devices.mpu6502 import MPU
import dragon_power_reference_v1 as O
import dragon_power_component_v1 as B
import dragon_power_port_v1 as P
def invoke(m,pc,a=0,x=0,y=0,p=0x24):
 c=MPU(memory=m,pc=pc);c.a=a;c.x=x;c.y=y;c.p=p;c.sp=0xfd
 m[0x1fe]=255;m[0x1ff]=5
 for _ in range(30000):
  if c.pc==0x600:
   assert c.sp==255
   return c
  assert m[c.pc]!=0,('BRK',hex(c.pc));c.step()
 raise AssertionError(hex(c.pc))
def memory(code,s):
 r=B.HOST.with_suffix('.nes').read_bytes();m=bytearray(65536)
 for bank,cpu in [(126,0x8000),(86,0xa000),(85,0xc000),(127,0xe000)]:m[cpu:cpu+8192]=r[16+bank*8192:16+(bank+1)*8192]
 m[0xa800:0xa800+len(code)]=code
 m[s['SelectedCharacter']]=24
 return m
def loc(s,value):
 name=P.RAM[value]
 if '+'in name:n,k=name.split('+');return s[n]+int(k)
 return s[name]
def main():
 code,s=B.build();host=B.HOST.with_suffix('.nes').read_bytes();states=[];cost=[]
 # Choose an actual ordinary native solid (notbrick51/52 and notspecial hidden).
 solids=[i for i in range(256)if host[16+127*8192+s['MTileAttribute']-0xe000+i]&s['MTILE_SOLID']]
 ground=next(i for i in solids if i not in [0x23,0x26,0x51,0x52,0x5f,0x60,0xc2,0xc3])
 for pole in [0,1]:
  for policy in ['idle','walkR','walkL','jumpHold','jumpRelease','jumpReverse','punch','charge','airkick','crouch']:
   a=O.arena();a.ram[0x32]=pole;a.ram[0x3b]=3
   m=memory(code,s)
   # Actual native column/row layout for source arena floorY176.
   base=s['Block_Buffer_1']
   for row in range(144,208,16):
    for col in range(16):m[base+row+col]=ground
   for addr in P.RAM:
    if addr in [0,1]:continue
    m[loc(s,addr)]=a.ram[addr]
   for tick in range(90):
    held,fresh=0,0
    if policy=='walkR':held=128
    elif policy=='walkL':held=64
    elif policy.startswith('jump')or policy=='airkick':
     held=128 if policy!='jumpRelease'or tick<2 else 0
     if policy=='jumpReverse'and tick>=20:held=64
     if tick==0:held|=1;fresh=1
     if policy=='airkick'and tick==12:held|=2;fresh=2
    elif policy in ['punch','charge']:
     held=2;fresh=2 if tick==0 else 0
     if policy=='charge'and a.ram[0x2d]==8:fresh=1;held|=1
    elif policy=='crouch':held=32|(2 if tick>10 else 0)
    a.ram[0xdf]=held;a.ram[0xe0]=fresh
    m[s['DpHeld']]=held;m[s['DpFresh']]=fresh
    ca0=invoke(a,0xe82e)
    ca=invoke(a,0xec4d,a=ca0.a,x=ca0.x,y=ca0.y,p=ca0.p)
    cb=invoke(m,s['DpSourceFrame'])
    wrong=[]
    for addr in P.RAM:
     if addr in [0,1]:continue
     if a.ram[addr]!=m[loc(s,addr)]:wrong.append((hex(addr),P.RAM[addr],a.ram[addr],m[loc(s,addr)]))
    if wrong:raise AssertionError((policy,pole,tick,'state',wrong))
    expected=(ca.a,ca.x,ca.y,ca.p&0xcf)
    actual=(cb.a,cb.x,cb.y,cb.p&0xcf)
    assert actual==expected,(policy,pole,tick,'AXYP',expected,actual)
    oldptr=a.ram[0]|a.ram[1]<<8;newptr=m[s['R0']]|m[s['R1']]<<8
    assert newptr==s.get(f'DpN{oldptr:04X}',oldptr),(policy,tick,'genuinePtr',hex(oldptr),hex(newptr))
    cost.append([policy,pole,tick,ca0.processorCycles+ca.processorCycles+6,cb.processorCycles])
    # Source event output belongs to the caller; drain only after full update.
    assert m[s['DpCueOverflow']]==0
    m[s['DpCueCount']]=0
    a.ram[0x26]=(a.ram[0x26]+1)&255;m[s['DpClock']]=a.ram[0x26]
   states.append(dict(policy=policy,pole=pole,updates=90))
 proof=dict(status='PASS_SOURCE_CPU_ONLY',source=O.D.binding(O.D.ROM),parent=O.D.binding(B.HOST.with_suffix('.nes')),
   compiled=O.D.binding(B.OUT/'component.bin'),campaigns=states,full_mapped_state_and_AXYP_SP_cases=len(cost),
   genuine_pointer_translation_only=True,actual_host_block_helper=f'{s["GetBlockBufferAddr"]:04X}',native_solid=ground,
   min_delta=min(v[4]-v[3]for v in cost),max_delta=max(v[4]-v[3]for v in cost),costs=cost,
   limits='No sprites,PPU,NMI,IRQ,fullhostcaller/camera/gameplay proof yet; native scene-spawn and source audio event vector are explicit boundaries')
 p=B.OUT/'source-controls.json';p.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(proof=O.D.binding(p),cases=len(cost),delta=[proof['min_delta'],proof['max_delta']]),indent=2))
if __name__=='__main__':main()
