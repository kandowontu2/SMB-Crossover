"""Read-only native-ROM ABI analysis; no replacement bytes or gameplay edits.

Runs the immutable resident helper in a standalone 6502 interpreter and checks
the proposed interior contract. This is an analytical unit probe, not NES route
or hardware-performance evidence. The prospective runtime gate is not emitted.
"""
from pathlib import Path
import argparse, hashlib, itertools, json, re
from py65.devices.mpu6502 import MPU

p=argparse.ArgumentParser();p.add_argument('rom',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
labels={m[2]:int(m[1],16)for line in a.rom.with_suffix('.lbl').read_text().splitlines()if(m:=re.match(r'al ([0-9A-Fa-f]+) \.(\S+)$',line))}
rom=a.rom.read_bytes();assert rom[:4]==b'NES\x1a';memory=[0]*65536
# MMC3 mode1 maps the native resident second-last physical bank at8000;
# consult the immutable linked debug segment rather than assuming bank0.
debug=a.rom.with_suffix('.dbg').read_text()
resident=re.search(r'seg\s+[^\n]*name="CODE",start=0x008000[^\n]*ooffs=(\d+)',debug)
assert resident,'Resident CODE ROM offset'
resident_offset=int(resident[1]);memory[0x8000:0xa000]=rom[resident_offset:resident_offset+0x2000]
cpu=MPU(memory=memory);sentinel=0x7f00
def put(n,v,i=0):memory[labels[n]+i]=v&255
def get(n,i=0):return memory[labels[n]+i]
fields=('R0','R1','R2','R3','R4','R5','R6','R7')
count=fast=0;cycles=[];examples=[];boundary_counts={}
# Actual screen edges are separately authored, including nonstandard widths;
# the predicate never infers Right from Left.
for slot,page,leftlow,width,relative,y,yhi,offset_other in itertools.product(range(6),(0,1,255),(0,31,127,255),(255,239,127),(-1,0,1,23,24,55,56,127,231,232,255,256),(0,31,32,184,223,224,255),(0,1,2),(False,True)):
 left=(page*256+leftlow)&65535;right=(left+width)&65535;world=(left+relative)&65535
 dxleft=(world-left)&65535;dxright=(right-world)&65535
 qualifies=(yhi==1 and 32<=y<=223 and 0<dxleft<256 and 24<=dxright<256)
 if not qualifies:continue
 for i,n in enumerate(fields):put(n,0xa0+i)
 objoffset=(5-slot)if offset_other else slot
 put('ObjectOffset',objoffset)
 put('ScreenEdge_X_Pos',left);put('ScreenEdge_PageLoc',left>>8)
 put('ScreenEdge_X_Pos',right,1);put('ScreenEdge_PageLoc',right>>8,1)
 put('SprObject_X_Position',world,slot+1);put('SprObject_PageLoc',world>>8,slot+1)
 put('SprObject_Y_Position',y,slot+1);put('SprObject_Y_HighPos',yhi,slot+1)
 put('Enemy_OffscreenBits',0xcc)
 cpu.pc=labels['GetEnemyOffscreenBits'];cpu.sp=0xfd;cpu.stPushWord(sentinel-1)
 cpu.a=0xe1;cpu.x=slot;cpu.y=0xe2;cpu.p=0xe5;cpu.processorCycles=0
 steps=0
 while cpu.pc!=sentinel:
  cpu.step();steps+=1
  assert steps<500,'Bounded resident helper'
 result={'A':cpu.a,'X':cpu.x,'Y':cpu.y,'C':cpu.p&1,'N':(cpu.p>>7)&1,'Z':(cpu.p>>1)&1,'V':(cpu.p>>6)&1,**{n:get(n)for n in fields},'offscreen':get('Enemy_OffscreenBits')}
 expected={'A':0,'X':objoffset,'Y':1,'C':0,'N':0,'Z':int(objoffset==0),'V':0,'R0':0,'R1':0xa1,'R2':0xa2,'R3':0xa3,'R4':slot+1,'R5':4,'R6':32,'R7':255-y,'offscreen':0}
 assert result==expected,{'slot':slot,'left':left,'right':right,'world':world,'y':y,'actual':result,'expected':expected}
 count+=1;cycles.append(cpu.processorCycles)
 k=str(relative);boundary_counts[k]=boundary_counts.get(k,0)+1
 if len(examples)<4:examples.append({'slot':slot,'left':left,'right':right,'world':world,'y':y,'native_cycles':cpu.processorCycles,'result':result})
out={'scope':'Read-only standalone native-ROM 6502 ABI analysis. No candidate runtime implementation, NES timing, or controller route claim.','rom':str(a.rom.resolve()),'rom_sha256':hashlib.sha256(rom).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'native_entry':hex(labels['GetEnemyOffscreenBits']),'passed_qualifying_calls':count,'native_cycles_without_caller_jsr':{'minimum':min(cycles),'maximum':max(cycles),'mean':sum(cycles)/len(cycles)},'relative_cases':boundary_counts,'candidate_predicate':'input X0..5; YHigh1; Y32..223; world-left16 in1..255; right-world16 in24..255; all other cases tailcall original unchanged','exact_public_result':{'A':0,'X':'ObjectOffset','Y':1,'C':0,'N':'bit7 of ObjectOffset','Z':'ObjectOffset == 0','V':0,'R0':0,'R1_R2_R3':'unchanged','R4':'inputSlot + 1','R5':4,'R6':32,'R7':'255 - EnemyY','shared_Enemy_OffscreenBits':0},'examples':examples,'limitations':['No runtime replacement emitted or measured.','Final flags include V for the verified NES binary-decimal-disabled helper path.','Stack contents below restored SP differ for any prospective replacement and are not a caller ABI.','Fallthrough cost estimate must be validated after any future implementation.']}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(count,'qualifying native ABI cases PASS',out['native_cycles_without_caller_jsr'])
