"""Small, read-only original RCR inspection; no emulator, download, or game edits."""
from pathlib import Path
import argparse, hashlib, json
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

ROOT = Path(__file__).resolve().parents[1]
NATIVE = Path('C:/NES/River City Ransom (USA).nes')

class NativeMemory(list):
    def __init__(self, raw):
        super().__init__([0]*65536)
        self.raw=raw; self.selector=0; self.writes=[]
        for page,bank in [(0,6),(1,7),(2,14),(3,15)]:
            self.page(page,bank)
    def page(self,page,bank):
        list.__setitem__(self,slice(0x8000+page*8192,0xa000+page*8192),self.raw[16+bank*8192:16+(bank+1)*8192])
    def __setitem__(self,key,value):
        if isinstance(key,int):
            self.writes.append((key,value))
            if key==0x8000:self.selector=value&7;return
            if key==0x8001:
                if self.selector in (6,7):self.page(self.selector-6,value)
                return
        list.__setitem__(self,key,value)

def call_native(memory,pc,x=0):
    cpu=MPU(memory=memory,pc=pc);cpu.x=x;cpu.sp=0xfd;cpu.stPushWord(0x5aff)
    for _ in range(15000):
        if cpu.pc==0x5b00:break
        cpu.step()
    else:raise AssertionError(('native call timeout',hex(cpu.pc)))
    assert cpu.sp==0xfd
    return cpu.processorCycles

def player_setup(raw,variant):
    """Execute actual stage player setup and reset sprite-CHR owner.

    The typed six-byte stage-position descriptor lives in scratch RAM. Native
    02:9D3B/9E6B initializes both real player actors, unlike the enemy-only
    09:B7FD constructor (graphics2/kinds82,83), which is deliberately not used.
    """
    assert variant in (0,1)
    memory=NativeMemory(raw);memory.page(0,2);memory.page(1,3)
    memory[0x2a]=0;memory[0x2b]=6
    memory[0x603:0x605]=[0x20,6]
    memory[0x620:0x626]=[128,0,112,0,128,112]
    call_native(memory,0x9d3b)
    assert memory[0xcb:0xcd]==[0,0] and memory[0x48:0x4a]==[0x80,0x81]
    call_native(memory,0xe2f7)
    memory[0x692]=3                 # Native full-brightness table E5D2[3]=30.
    call_native(memory,0xe3d5)
    assert memory[0x120:0x128]==[15,15,48,38,15,15,17,38]
    return memory

def native_pose(raw,pose,variant=0,face=1):
    """Execute the actual native ED0E renderer after genuine player setup."""
    memory=player_setup(raw,variant)
    for addr,value in {0x47:variant,0xd3+variant:pose|(0x80 if face==1 else 0),0x52d:252,
                       0x83+variant:128,0x8c+variant:0,0x9e+variant:112,0xa7+variant:0,0x520:0}.items():memory[addr]=value
    cycles=call_native(memory,0xed0e)
    used=memory[0x52d]
    return [list(memory[0x200+p:0x204+p]) for p in range(used+4,256,4)],cycles

def native_motion(raw):
    output=[]
    for direction in (0x40,0xc0):
        for speed in (12,28):
            memory=NativeMemory(raw)
            for addr,value in {0x47:0,0x30f:direction,0x316:speed,0x83:128,0x8c:1,0x9e:112}.items():memory[addr]=value
            rows=[]
            for _ in range(8):
                cpu=MPU(memory=memory,pc=0xd5e7);cpu.sp=0xfd;cpu.stPushWord(0x5aff)
                for _ in range(5000):
                    if cpu.pc==0x5b00:break
                    cpu.step()
                else:raise AssertionError('native movement timeout')
                rows.append(dict(x=memory[0x83]+256*memory[0x8c],fraction=memory[0x7a],cycles=cpu.processorCycles))
            output.append(dict(direction=direction,scalar=speed,rows=rows))
    return output

def native_pixels(raw,pose,variant=0,face=1):
    """Absolute rendered coordinates and original two-palette color classes."""
    chrdata=raw[16+131072:]
    # Genuine reset sprite-CHR owner; both player kinds share body pages.
    pages=player_setup(raw,variant)[0x521:0x525]
    data=b''.join(chrdata[p*1024:(p+1)*1024] for p in pages)
    parts,cycles=native_pose(raw,pose,variant,face)
    pixels={}
    for yy,tt,aa,xx in reversed(parts):
        source=tile(data,tt)
        for y in range(8):
            for x in range(8):
                v=source[7-y if aa&128 else y][7-x if aa&64 else x]
                if v:pixels[(xx+x-120,yy+y-96)]=1 if v==1 else (2 if v==3 else (4 if aa&1 else 3))
    return pixels,parts,cycles

def pose_gallery(raw):
    from PIL import Image,ImageDraw
    colors={1:(0,0,0),2:(248,120,88),3:(255,255,255),4:(0,120,248)}
    result=Image.new('RGB',(16*64,8*90),(100,100,100));d=ImageDraw.Draw(result)
    for variant in range(2):
        for pose in range(64):
            pixels,_,_=native_pixels(raw,pose,variant)
            im=Image.new('RGB',(48,48),(170,170,170))
            for (x,y),v in pixels.items():
                if -8<=x<40 and -8<=y<40:im.putpixel((x+8,y+8),colors[v])
            x=(pose%16)*64;y=((pose//16)+4*variant)*90
            result.paste(im.resize((64,64)),(x,y));d.text((x,y+66),f'{variant}:{pose:02X}',fill='white')
    result.save(ROOT/'chr/characters/river-city-native-poses.png')

def tile(raw,index):
    data=raw[index*16:index*16+16]
    return [[((data[y]>>(7-x))&1)|(((data[y+8]>>(7-x))&1)<<1) for x in range(8)] for y in range(8)]

def preview_native(raw):
    from PIL import Image,ImageDraw
    chrdata=raw[16+131072:]
    poses,_=native_pose(raw,0)
    result=Image.new('RGB',(16*64,2*90),(64,64,64));d=ImageDraw.Draw(result)
    colors=[[(0,0,0,0),(0,0,0,255),(255,121,90,255),(255,255,255,255)],[(0,0,0,0),(0,0,0,255),(0,89,255,255),(255,255,255,255)]]
    for bank in range(32):
        im=Image.new('RGBA',(40,40))
        for yy,tt,aa,xx in reversed(poses):
            pixels=tile(chrdata[bank*4096:(bank+1)*4096],tt)
            for y in range(8):
                for x in range(8):
                    v=pixels[7-y if aa&128 else y][7-x if aa&64 else x]
                    if v:
                        dx,dy=xx-108+x,yy-90+y
                        if 0<=dx<40 and 0<=dy<40:im.putpixel((dx,dy),colors[aa&1][v])
        x=(bank%16)*64;y=(bank//16)*90;result.paste(im.resize((64,64)),(x,y),im.resize((64,64)));d.text((x,y+66),str(bank),fill='white')
    result.save(ROOT/'chr/characters/river-city-native-inspect.png')

def disassemble(raw, bank, start, pc, count):
    memory = [0] * 65536
    memory[start:start + 8192] = raw[16 + bank * 8192:16 + (bank + 1) * 8192]
    decoder = Disassembler(MPU(memory=memory))
    result = []
    for _ in range(count):
        size, text = decoder.instruction_at(pc)
        result.append(f'{bank:02X}:{pc:04X} {bytes(memory[pc:pc+size]).hex(" "):8} {text}')
        pc += size
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bank', type=lambda s:int(s,0), default=15)
    parser.add_argument('--start', type=lambda s:int(s,0), default=0xe000)
    parser.add_argument('--pc', type=lambda s:int(s,0), default=0xec90)
    parser.add_argument('--count', type=int, default=140)
    parser.add_argument('--poses',action='store_true')
    parser.add_argument('--preview',action='store_true')
    parser.add_argument('--gallery',action='store_true')
    parser.add_argument('--motion',action='store_true')
    args = parser.parse_args()
    raw = NATIVE.read_bytes()
    assert len(raw) == 262160 and raw[:8] == bytes.fromhex('4e45531a08104008')
    assert hashlib.sha256(raw).hexdigest() == '276c1a1a37685717c0d808490100874a949ea79b68bdef0fcaeeab4586a72f62'
    if args.preview:
        preview_native(raw);return
    if args.gallery:
        pose_gallery(raw);return
    if args.motion:
        print(json.dumps(native_motion(raw),indent=2));return
    if args.poses:
        for pose in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x29,0x2a]:
            print(hex(pose),native_pose(raw,pose,0)[0],native_pose(raw,pose,1)[0])
        return
    print('\n'.join(disassemble(raw,args.bank,args.start,args.pc,args.count)))

if __name__ == '__main__':
    main()
