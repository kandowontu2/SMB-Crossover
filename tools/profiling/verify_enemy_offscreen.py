"""Independent actual-ROM6502 differential for the ordinary-enemy shortcut.

This standalone unit interpreter may seed arbitrary CPU/RAM states; it never
modifies an NES emulator or supplies evidence of a controller level clear.
"""
from pathlib import Path
import argparse,hashlib,itertools,json,random,re
from py65.devices.mpu6502 import MPU

class NesMPU(MPU):
    # RP2A03 keeps D as a status flag but always uses binary ADC/SBC.
    def opADC(self,x):
        decimal=self.p&self.DECIMAL;self.p&=~self.DECIMAL
        super().opADC(x);self.p=(self.p&~self.DECIMAL)|decimal
    def opSBC(self,x):
        decimal=self.p&self.DECIMAL;self.p&=~self.DECIMAL
        super().opSBC(x);self.p=(self.p&~self.DECIMAL)|decimal

p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(path,entry):
    labels={m[2]:int(m[1],16)for line in path.with_suffix('.lbl').read_text().splitlines()if(m:=re.match(r'al ([0-9A-Fa-f]+) \.(\S+)$',line))}
    data=path.read_bytes();debug=path.with_suffix('.dbg').read_text();mem=[0]*65536
    for name in('CODE','OBJECT'):
        m=re.search(r'seg\s+[^\n]*name="'+name+r'",start=(0x[0-9A-Fa-f]+),[^\n]*ooffs=(\d+)',debug);assert m,name
        start=int(m[1],16);off=int(m[2]);mem[start:start+8192]=data[off:off+8192]
    cpu=NesMPU(memory=mem);return cpu,labels,labels[entry]
b,bl,be=load(a.before,'GetEnemyOffscreenBits');c,cl,ce=load(a.after,'NormalEnemyOffscreenBits')
names=('R0','R1','R2','R3','R4','R5','R6','R7','ObjectOffset','Enemy_OffscreenBits','ScreenEdge_X_Pos','ScreenEdge_PageLoc','SprObject_X_Position','SprObject_PageLoc','SprObject_Y_Position','SprObject_Y_HighPos')
assert all(bl[n]==cl[n]for n in names),'The caller RAM ABI must not move'
# Verify the exact ordinary-enemy caller targets the intended routine in each ROM.
for cpu,lab,target in((b,bl,be),(c,cl,ce)):
    call=lab['RunNormalEnemies']+5
    assert cpu.memory[call]==0x20 and cpu.memory[call+1]+256*cpu.memory[call+2]==target,'Actual native caller JSR'

def cases():
    # Dense horizontal edge/page matrix; actual independent camera widths.
    for slot,page,leftlow,width,rel,y in itertools.product(range(6),(0,1,127,255),(0,1,127,255),(0,1,23,24,127,239,255,256,511),(-257,-256,-255,-1,0,1,23,24,31,55,56,127,231,232,255,256,257,511),(32,184,223)):
        left=page*256+leftlow
        yield slot,left,(left+width)&65535,(left+rel)&65535,y,1
    # Every low Y, rejected high Y and representative interior/edge anchors.
    for slot,y,hi,rel in itertools.product(range(6),range(256),(0,1,2,127,128,255),(0,1,231,232)):
        left=0xff80 if y&1 else 0x007f
        yield slot,left,(left+255)&65535,(left+rel)&65535,y,hi
    # Every status byte and stack wrap, with unusual saved ObjectOffset values.
    for status,slot,rel in itertools.product(range(256),range(6),(1,231,232)):
        yield slot,0xff80,0x007f,(0xff80+rel)&65535,184,1,status
    # Foreign input slots must take the original path, including zp wrap X255.
    for slot,hi,y in itertools.product((6,7,15,63,127,128,254,255),(0,1,2,128,255),(0,31,32,184,223,224,255)):
        yield slot,0x01ff,0x02fe,0x027f,y,hi
    rng=random.Random(0x20233)
    for _ in range(10000):yield rng.randrange(256),rng.randrange(65536),rng.randrange(65536),rng.randrange(65536),rng.randrange(256),rng.randrange(256)

count=accepted=rejected=0;cycles={'accepted':[],'rejected':[]};examples=[]
for spec in cases():
    slot,left,right,world,y,hi=spec[:6];status=spec[6]if len(spec)>6 else (count*73)&255
    objoffset=(slot,5-slot,0,5,127,128,255)[count%7]&255
    ram=[(i*73+count*17)&255 for i in range(2048)]
    def put(n,v,i=0):ram[bl[n]+i]=v&255
    put('ObjectOffset',objoffset)
    put('ScreenEdge_X_Pos',left);put('ScreenEdge_PageLoc',left>>8)
    put('ScreenEdge_X_Pos',right,1);put('ScreenEdge_PageLoc',right>>8,1)
    # Native indexed-zp instructions wrap the index for foreign slot255.
    for n,v in(('SprObject_X_Position',world),('SprObject_PageLoc',world>>8),('SprObject_Y_Position',y),('SprObject_Y_HighPos',hi)):
        ram[(bl[n]+((slot+1)&255))&255]=v&255
    outputs=[];timings=[]
    for cpu,entry in((b,be),(c,ce)):
        cpu.memory[:2048]=ram;cpu.a=(count*13)&255;cpu.x=slot;cpu.y=(count*29)&255;cpu.p=status
        cpu.sp=(0xfd,0x80,0x01,0xff,0x00)[count%5];cpu.stPushWord(0x7eff);cpu.pc=entry;cpu.processorCycles=0
        steps=0
        while cpu.pc!=0x7f00:
            cpu.step();steps+=1;assert steps<500,'Bounded native/candidate helper'
        outputs.append((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,tuple(cpu.memory[:256]),tuple(cpu.memory[512:2048])))
        timings.append(cpu.processorCycles)
    assert outputs[0]==outputs[1],{'case':count,'spec':spec,'objectOffset':objoffset,'status':status,'before_regs':outputs[0][:5],'after_regs':outputs[1][:5],'ram_first_mismatch':next((i for i,(x,z)in enumerate(zip(b.memory[:2048],c.memory[:2048]))if x!=z and not 256<=i<512),None)}
    # Read the actual positions after RAM alias setup for foreign slots.
    eligible=slot<6 and hi==1 and 32<=y<224 and 0<(world-left)&65535<256 and 24<=(right-world)&65535<256
    key='accepted'if eligible else'rejected';cycles[key].append((timings[0],timings[1]));accepted+=eligible;rejected+=not eligible;count+=1
    if len(examples)<6:examples.append({'spec':spec,'ObjectOffset':objoffset,'initialP':status,'before_cycles':timings[0],'after_cycles':timings[1]})
stats={k:{'cases':len(v),'before_mean':sum(x[0]for x in v)/len(v),'after_mean':sum(x[1]for x in v)/len(v),'delta_range':[min(x[1]-x[0]for x in v),max(x[1]-x[0]for x in v)]}for k,v in cycles.items()}
report={'scope':'Standalone actual-ROM RP2A03-equivalent6502 helper/caller-operand differential; not emulator gameplay traversal','before':str(a.before.resolve()),'after':str(a.after.resolve()),'before_sha256':sha(a.before),'after_sha256':sha(a.after),'script_sha256':sha(Path(__file__)),'cases':count,'all_equal':True,'accepted':accepted,'rejected':rejected,'compared':'A/X/Y/allP/SP plus all2048 native RAM bytes except discarded stack contents; includes R0..7 and shared offscreen byte','timing':stats,'examples':examples,'limitations':['No interrupts/PPU in standalone unit interpreter; real-emulator caller tests and gameplay canonical/DMA matrix are separate.','Stack contents below restoredSP may differ and are not part of callerABI.']}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(count,'actual-ROM cases PASS',stats)
