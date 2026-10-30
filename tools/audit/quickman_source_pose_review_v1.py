"""Replay the CX source renderer and compare every pixel of the menu pose."""
from pathlib import Path
import hashlib,json,sys
from PIL import Image
from py65.devices.mpu6502 import MPU

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/full-menu-quickman-art-v1'
ROM=Path('C:/NES/the stash/Rockman_CX-world44.spcs.bio.nes')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Bus:
    def __init__(self,b):self.b=b;self.ram=bytearray(32768);self.bank=0x1c;self.reg=6;self.events=[]
    def __getitem__(self,a):
        if isinstance(a,slice):return [self[i]for i in range(a.start or 0,a.stop,a.step or 1)]
        if a<0x8000:return self.ram[a]
        if a<0xa000:return self.b[16+self.bank*8192+a-0x8000]
        if a<0xc000:return self.b[16+0x15*8192+a-0xa000]
        return self.b[0x7c010+a-0xc000]
    def __setitem__(self,a,v):
        v&=255
        if a<0x8000:self.ram[a]=v
        elif a==0x8000:self.reg=v;self.events.append([a,v])
        elif a==0x8001:
            assert self.reg==6
            self.bank=v;self.events.append([a,v])
        else:raise AssertionError((a,v))

def main():
    b=ROM.read_bytes();assert sha(ROM)=='e04a4523e4ff0a0c7bfad1d30acedb9140c0972fa3be1c62e5d42a09664b5f6e'
    # Native upload record: nine pages from 16KB bank$13:$A900 to CHR$0000.
    assert b[0x1bd40:0x1bd44]==bytes([9,0xa9,9,0x13])
    chr=b[0x4e910:0x4f210];assert len(chr)==2304
    # Native player type0 standing script -> frame4 -> bank$14:$873C.
    assert b[0x39010]==0x73 and b[0x390d0]==0x8b
    assert b[0x38b83:0x38b88]==bytes([10,8,4,4,4])
    assert (b[0x39494],b[0x39894],b[0x39c94])==(0x3c,0x87,0x14)
    assert (b[0x2be10],b[0x2bf10])==(0xb4,0xaa)
    bus=Bus(b);bus.ram[0x420]=0xc0;bus.ram[0x460]=128;bus.ram[0x4a0]=128
    # A synthetic caller's return address; no source-ROM byte is changed.
    bus.ram[0x1fe]=0xfe;bus.ram[0x1ff]=0x7f
    m=MPU(memory=bus);m.pc=0xcd92;m.sp=0xfd
    steps=0
    while m.pc!=0x7fff:
        m.step();steps+=1;assert steps<10000
    assert bus.ram[6]==40 and bus.bank==0x1c
    oam=bytes(bus.ram[0x200:0x228]);cells=[list(oam[i:i+4])for i in range(0,40,4)]
    # RGB roles are the primary rip's original colors. Shape, geometry, tile
    # order, flip and palette-role bits come from the actual supplied ROM.
    palettes=[[(0,0,0),(0,0,0),(209,213,0),(255,0,160)],[(0,0,0),(0,0,0),(255,255,255),(236,238,78)]]
    canvas=Image.new('RGBA',(256,240))
    for y,tile,attr,x in reversed(cells):
        for yy in range(8):
            py=7-yy if attr&128 else yy
            for xx in range(8):
                px=7-xx if attr&64 else xx;at=tile*16
                v=((chr[at+py]>>(7-px))&1)|(((chr[at+py+8]>>(7-px))&1)<<1)
                if v:canvas.putpixel((x+xx,y+1+yy),palettes[attr&3][v]+(255,))
    body=canvas.crop(canvas.getbbox());reference=Image.open(OUT/'assets/quick-man-body.png').convert('RGBA')
    assert body.size==(24,24) and body.tobytes()==reference.tobytes()
    path=OUT/'offline/quick-man-native-source-pose.png';body.save(path)
    report=dict(status='ALL_379_OPAQUE_PIXELS_AND_OPACITY_MATCH_ACTUAL_ROM_RENDERER',ROM=str(ROM),ROM_sha256=sha(ROM),entry_PC='CD92',return_scope='Synthetic caller return at7FFF; sourceROM unchanged.',CPU_steps=steps,CPU_cycles=m.processorCycles,CHR_upload=dict(record_file_offset='1BD40',record_hex=b[0x1bd40:0x1bd44].hex(),CHR_file_offset='4E910',bytes=len(chr),sha256=hashlib.sha256(chr).hexdigest()),standing=dict(type=0,script_CPU_address='8B73',frame=4,frame_pointer_tables_CPU=['9480','9880','9C80'],frame_data_CPU='bank14:873C',frame_file_offset='2874C',frame_hex=b[0x2874c:0x28762].hex(),offset_index=0,offset_CPU='bank15:AAB4',offset_file='2AAC4'),actual_OAM=cells,mapper_writes=bus.events,output=str(path),output_sha256=sha(path),reference=str(OUT/'assets/quick-man-body.png'),reference_sha256=sha(OUT/'assets/quick-man-body.png'),opaque_pixels=sum(1 for a in body.getchannel('A').getdata()if a),palette_scope='Native attribute palette roles0/1 verified; original RGB colors taken from the primary original-game rip. Native palette installation path and abilities remain unverified.',no_native_emulator_launched=True)
    rp=OUT/'offline/source-pose-review.json';rp.write_text(json.dumps(report,indent=2)+'\n');print(rp);print(sha(rp));print('cycles',m.processorCycles,'steps',steps)
if __name__=='__main__':main()
