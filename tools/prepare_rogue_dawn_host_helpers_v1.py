"""Independent exact-ID/input/context-B helpers; no shared integration/native."""
from pathlib import Path
import argparse,hashlib,itertools,json,re,subprocess,sys
from py65.devices.mpu6502 import MPU
import prepare_rogue_dawn_art_v1 as art
import rogue_dawn_map_v1 as ref
ROOT=Path(__file__).resolve().parents[1]

class Memory(bytearray):
    def __init__(self,data):super().__init__(data);self.reads=set();self.writes=set()
    def __getitem__(self,k):
        if isinstance(k,int):self.reads.add(k)
        return super().__getitem__(k)
    def __setitem__(self,k,v):
        if isinstance(k,int):self.writes.add(k)
        return super().__setitem__(k,v)

def call(m,pc,a=0,x=0,y=0,p=0x30):
    c=MPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,0xc0;c.stPushWord(0x5aff);m.reads.clear();m.writes.clear()
    for _ in range(1000):
        if c.pc==0x5b00:assert c.sp==0xc0;return c
        assert m[c.pc]!=0,('BRK',hex(c.pc));c.step()
    raise AssertionError(('timeout',hex(c.pc)))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--generate',action='store_true');p.add_argument('--output',type=Path,default=ROOT/'build/rogue-dawn-host-plan-v1/helpers-controls.json');a=p.parse_args();out=a.output.parent;out.mkdir(exist_ok=True,parents=True)
    raw=ref.ROM.read_bytes();assert ref.digest(raw)==ref.EXPECTED
    counts={};table=bytearray([255]*106);rows=[]
    for frame in art.BODY:
        for face in [0,1]:
            parts,_,_,_=art.native_render(raw,frame,face);count=4*len(parts)
            m=art.Memory(ref.cpu_image(raw,lower_bank=2));m[0x4b]=0;m[0x55]=1;m[0x300]=1;m[0x303]=frame;m[0x30d]=128;m[0x30e]=128;m[0x49]=2;m[0x6b]=face*16;m[0x5b]=0
            c=art.call(m,0xde4a);assert c.x==count
            if frame in counts:assert counts[frame]==count
            counts[frame]=count;table[frame]=count
            rows.append(dict(frame=frame,facing=face,source8x8_returnX=count,source_morph_acceleration_byte=raw[16+62*8192+0xcc0+count]))
    text='; Authenticated default1.21 body-only original8x8 returnX. Unsupported=$FF.\n; Actual decoder62:DE4A, virtual prior native cursor0; BOTH facings equal.\n; Source9271411a...61077. This is ROOT-approved explicit SMB adaptation B.\nRdHostBodyOnlyReturnX:\n'+''.join(' .byte '+','.join(f'${z:02x}'for z in table[j:j+16])+'\n'for j in range(0,106,16))
    inc=ROOT/'src/rogue_dawn_host_context.inc'
    if a.generate:inc.write_text(text,newline='\n')
    else:assert inc.read_text()==text
    (out/'helpers-wrapper.s').write_text('SelectedCharacter=$6002\nSavedJoypadBits=$DC\nRdMorphCooldown=$5C1B\nRdSourceAltPalette=$5C7D\n.include "rogue_dawn_host.s"\n')
    (out/'helpers.cfg').write_text('MEMORY { H:start=$A600,size=$1A00,bank=95,file=%O; }\nSEGMENTS { ROGUE_DAWN_HOST:load=H,type=ro; }\n')
    cc=ROOT/'tools/Windows/cc65/bin'
    subprocess.run([str(cc/'ca65.exe'),'-g','-I',str(ROOT/'src'),str(out/'helpers-wrapper.s'),'-o',str(out/'helpers.o')],check=True)
    subprocess.run([str(cc/'ld65.exe'),'-C',str(out/'helpers.cfg'),str(out/'helpers.o'),'-o',str(out/'helpers.bin'),'-Ln',str(out/'helpers.lbl'),'--dbgfile',str(out/'helpers.dbg')],check=True)
    syms={z[2]:int(z[1],16)for line in(out/'helpers.lbl').read_text().splitlines()if(z:=re.match(r'al ([\da-fA-F]+) \.(\S+)',line))};code=(out/'helpers.bin').read_bytes();m=Memory(bytes(65536));m[0xa600:0xa600+len(code)]=code
    overlays=set(range(0x5c00,0x5c80))|set(range(0x5fb0,0x5fb8));gates=0
    for char,variant in itertools.product(range(256),range(256)):
        m[0x6002]=char;m[0x5fee]=variant;c=call(m,syms['RdHostEnabled'],a=0x5a,x=0x37,y=0x91,p=0x71)
        assert bool(c.p&1)==(char==2 and variant==1)and(c.x,c.y)==(0x37,0x91);assert not m.reads&overlays and not m.writes&overlays;gates+=1
    foreign=0
    for char,variant,entry in itertools.product([0,1,2,3,8,20,21,23,255],[0,1,2,255],['RdHostInput','RdHostTickBefore','RdHostTickAfter','RdHostContextB']):
        if char==2 and variant==1:continue
        m[0x6002]=char;m[0x5fee]=variant;c=call(m,syms[entry]);assert not m.reads&overlays and not m.writes&overlays and not c.p&1;foreign+=1
    m[0x6002]=2;m[0x5fee]=1;inputs=0
    for old,new in itertools.product(range(0,256,17),range(256)):
        n=Memory(ref.cpu_image(raw,a_bank=3,lower_bank=2));n[1]=0;n[0x14]=old;n[0x18]=2;x=call(n,0xb024,a=new)
        m[0xdc]=new;m[0x5c29]=old;call(m,syms['RdHostInput'])
        assert[m[0x5c28],m[0x5c29],m[0x5c34]]==[n[0x12],n[0x14],n[0x16]],(old,new);inputs+=1
    contexts=0
    for frame,face,alt in itertools.product(range(256),[0,1,2],[0,1]):
        m[0x5c03]=frame;m[0x5c2c]=face;m[0x5c7d]=alt;c=call(m,syms['RdHostContextB'],y=0x91)
        admitted=bool(not alt and face<2 and(frame in counts or frame==247));assert bool(c.p&1)==admitted and c.y==0x91
        assert c.x==(counts.get(frame,0)if admitted else 0);contexts+=1
    ticks=0
    for cooldown,clock in itertools.product([0,1,2,8,255],[0,1,127,254,255]):
        m[0x5c1b]=cooldown;m[0x5c2e]=clock;call(m,syms['RdHostTickBefore']);assert m[0x5c1b]==max(0,cooldown-1)and m[0x5c2e]==clock
        call(m,syms['RdHostTickAfter']);assert m[0x5c2e]==(clock+1)&255;ticks+=1
    proof=dict(passed=True,native_run=False,complete_host_services=False,helper_bytes=len(code),entries={n:f'95:{v:04X}'for n,v in syms.items()if n.startswith('RdHost')},owner_cells=gates,foreign_no_overlay_read_write_cells=foreign,input_original_ROM_cells=inputs,context_admission_cells=contexts,timer_pairs=ticks,actual_body_only_rows=rows,source_input_boundary={'bank':3,'entry':'B024','return':'B050','source12_equals16':True,'bytes':raw[16+3*8192+0x1024:16+3*8192+0x1051].hex()},source_clock_and_cooldown_owners={'before':'62:C266..C27B (2A nonzero decrement)','after':'62:C0C5 INC2D','hurt_clock70':'Already decremented by actual action owner62:CE34; NEVER decrement it here.'},context_B='Approved deterministic SMB adaptation, not whole original draw ordering. Only real body-pose/facing decoder returnX at virtual original cursor0; F7=0. SourceD0CD still writes its literal-window value to0315/RdAcceleration.',limits=['No world collision, real enemy/weapon effects, BCD host damage or native integration is implemented by these helpers.','Standalone helper startsA600 but no complete RdHostDispatch exists yet; do not bind a native bridge to this partial image.','Input caller must run only once per active unpaused Main; not per physical poll/PPU or duplicate movement+weapons tick.'],bindings=[ref.binding(q)for q in [Path(__file__),ROOT/'src/rogue_dawn_host.s',inc,ref.ROM,out/'helpers.bin']])
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,helper_bytes=len(code),owner_cells=gates,foreign_cells=foreign,input_cells=inputs,context_cells=contexts,timer_pairs=ticks)))
if __name__=='__main__':main()
