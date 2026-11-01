"""Check actual current terminal instructions, without inferring whole-bank ownership."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
O=R/'build/mario-tank-visible-host-1101-v5'
P=R/'build/karnov-native-platform-1101-v1/candidate.nes'
PIN='58e50db6ceead7c3706087c92d6e49014f05ff8b80b000be30c27b4e7dfa11f2'
def main():
 b=scoped_load(P);raw=b['raw'];assert hashlib.sha256(raw).hexdigest()==PIN
 rows=[]
 for name,bank,end in [('S2AcquireAudioImage',82,0xdfc2),('MaaReservation',66,0xb957),('RyuSourceBodyPlatformFinish',58,0xbfaa),('BassHeadAdmission',89,0xbfb0),('Cv3DmcBeforeCv1',28,0xdfb0)]:
  start=address(b,name);size=int(b['syms'][name]['size'],0);off=location(b,name)
  assert start+size==end and (off-16)//8192==bank
  m=MPU();m.memory[start:end]=raw[off:off+size];d=Disassembler(m)
  decoded={};pc=start
  while pc<end:
   n,text=d.instruction_at(pc);op=m.memory[pc];mn,mode=m.disassemble[op]
   assert mn!='???' and pc+n<=end
   decoded[pc]=(n,mn,mode,text);pc+=n
  todo=[start];seen=set();exits=[];calls=[];reads=[]
  while todo:
   pc=todo.pop()
   if pc in seen:continue
   assert pc in decoded,('fallthrough or misaligned branch',name,hex(pc))
   seen.add(pc);n,mn,mode,text=decoded[pc];nextpc=pc+n
   assert mode not in ['ind','iny','inx'],('unbounded indirect access',name,text)
   operand=m.memory[pc+1] if n>1 else None
   if n==3:operand|=m.memory[pc+2]<<8
   if mn in ['LDA','LDX','LDY','CMP','CPX','CPY','ORA','AND','EOR','ADC','SBC','BIT'] and mode in ['abs','abx','aby']:
    # These leaves read only native RAM, never any terminal ROM table.
    assert operand<0x8000,(name,text)
    reads.append(text)
   if mn=='RTS':exits.append([pc,'RTS']);continue
   if mn=='JMP':
    if start<=operand<end:todo.append(operand)
    else:exits.append([pc,operand])
    continue
   if mn=='JSR':calls.append([pc,operand])
   if mode=='rel':todo.append(nextpc+(operand if operand<128 else operand-256))
   todo.append(nextpc)
  assert seen==set(decoded),('unreachable bytes require separate review',name)
  rows.append(dict(name=name,bank=bank,half_open=[start,end],hex=raw[off:off+size].hex(),instructions=len(seen),exits=exits,calls=calls,RAM_reads=reads))
 result=dict(passed=True,ROM_sha256=PIN,leaves=rows,formal_grant=False,scope='Actual compiled terminal control-flow and local reader closure only. JSR callees are assumed to return under their existing contract. No full-bank pointer census, source-cap enforcement, lifecycle or playable admission claim.',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (O/'terminal-leaf-review.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(dict(passed=True,leaves=len(rows),instructions=sum(r['instructions']for r in rows))))
if __name__=='__main__':main()
