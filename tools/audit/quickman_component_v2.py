"""Generate a relocatable CX Quick Man engine component from actual opcodes."""
from pathlib import Path
import json,re,hashlib,subprocess,sys
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
R=Path(__file__).resolve().parents[2];O=R/'build/quickman-component-v2';ROM=Path('C:/NES/the stash/Rockman_CX-world44.spcs.bio.nes')
sys.path.insert(0,str(Path(__file__).parent))
from quickman_source_v1 import CoreBus
B=ROM.read_bytes();assert hashlib.sha256(B).hexdigest()=='e04a4523e4ff0a0c7bfad1d30acedb9140c0972fa3be1c62e5d42a09664b5f6e'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bank(a,current=0x3c):return current if a<0xa000 else 0x3d if a<0xc000 else 0x3e if a<0xe000 else 0x3f
def at(k):b,a=k;return 16+b*8192+(a-(0x8000 if b in[0x1e,0x1c,0x3c]else 0xa000 if b==0x3d else 0xc000 if b==0x3e else 0xe000))
def label(k):return f'CX_{k[0]:02X}_{k[1]:04X}'
def data_label(k):return f'DX_{k[0]:02X}_{k[1]:04X}'
EXTERNAL={0xcbc0:'QuickManWorldProbe',0xc02f:'QuickManSound',0xc968:'QuickManScrollStrip',0xec26:'QuickManContactBridge',0xc10b:'QuickManDeath',0xc07f:'QuickManYield',0xc000:'QuickManReturn',0xc001:'QuickManReturn',0xf859:'QuickManReturn',0xf8e8:'QuickManReturn'}
EXTERNAL[0xf137]='QuickManEffectSpawn'
DATA=[(0x3c,0x85b0,0x85b4),(0x3c,0x8783,0x879d),(0x3c,0x8906,0x8922),(0x3c,0x8a71,0x8a86),(0x3c,0x8b55,0x8b76),(0x3c,0x8ce3,0x8ce8),(0x3d,0xbdca,0xbdd0),(0x3e,0xd3c7,0xd3d4),(0x3e,0xd44c,0xd4dc),(0x3e,0xdcc7,0xdcdf),(0x3e,0xdd17,0xdd37)]
DATA.append((0x3f,0xf113,0xf11c))
DATA.extend([(0x1c,0x9300,0x9380),(0x1c,0x93c0,0x9440)])
DATA.append((0x3e,0xdaa5,0xdaaa))
STATE_TARGETS=[0x8506,0x8505,0x8538,0x8560,0x85b4,0x85e6,0x8609,0x85b4,0x85b4,0x86c5,0x86c5,0x8776,0xbe81]
def decode(k):
    b,a=k;m=MPU();start=at((b,0x8000 if b in[0x1e,0x1c,0x3c]else 0xa000 if b==0x3d else 0xc000 if b==0x3e else 0xe000));base=a-((at(k)-start));m.memory[base:base+8192]=B[start:start+8192];n,s=Disassembler(m).instruction_at(a);return n,s,m.disassemble[m.memory[a]][1],bytes(m.memory[a:a+n])
def key(a,current=0x3c):return(bank(a,current),a)
def collect():
    work=[key(0x84ee),key(0xdcdf),key(0xcd23),key(0xdf31),key(0x8290,0x1e)];code={};ram=set();refs=set()
    while work:
        k=work.pop();b,a=k
        if a in EXTERNAL or k in code:continue
        if a==0xdf31:code[k]=(3,'JMP CX_1E_8290','abs',B[at(k):at(k)+11]);work.append((0x1e,0x8290));continue
        n,s,mode,raw=decode(k)
        assert s!='???',(k,raw.hex(),[(q,v[1])for q,v in code.items()if f'${a:04x}'in v[1]or q[0]==b and q[1]+v[0]==a])
        code[k]=(n,s,mode,raw);op=s.split()[0]
        nums=re.findall(r'\$([0-9a-f]+)',s);v=int(nums[0],16)if nums else None
        if op in ['JSR','JMP']and mode=='abs':
            work.append(key(v,b if b==0x1e else 0x3c))
            if op=='JSR':work.append((b,a+n))
        elif mode=='rel':
            known=None;back=a
            for _ in range(6):
                if any(z[2]=='rel'and z[1].endswith(f'${back:04x}')and q!=(b,a)for q,z in code.items()):break
                prev=[(q,z)for q,z in code.items()if q[0]==b and q[1]+z[0]==back]
                if len(prev)!=1:break
                q,z=prev[0];text=z[1];mn=text.split()[0]
                if mn in ['LDA','LDX','LDY']and z[2]=='imm'and op in['BEQ','BNE','BMI','BPL']:
                    value=int(text.split('$')[1],16);known={'BEQ':value==0,'BNE':value!=0,'BMI':bool(value&128),'BPL':not(value&128)}[op];break
                if mn in ['CLC','SEC']and op in['BCC','BCS']:known=(mn=='SEC')==(op=='BCS');break
                if mn not in ['STA','STX','STY','PHA','PHP','TXS','NOP','CLC','SEC','CLV','CLD','SED','SEI','CLI']:break
                back=q[1]
            if known is not False:work.append(key(v,b if b==0x1e else 0x3c))
            if known is not True:work.append((b,a+n))
        elif op=='JMP'and mode=='ind':
            if a==0x8502:work.extend(key(x)for x in STATE_TARGETS)
            elif a==0xda6c:work.append(key(0xda6f))
            else:raise AssertionError(('unknown indirect dispatch',k,s))
        elif op not in ['RTS','RTI','BRK']:work.append((b,a+n))
        if v is not None and mode not in ['imm','rel']and not(op in['JMP','JSR']and mode=='abs'):
            if v<0x8000:
                width=2 if mode in ['ind','iny','inx']else (10 if v==0x56 else 3 if v in[0x32,0x5a0,0x5a3]else 5 if v in[0x480,0x4c0,0x590,0x640,0x660,0x680,0x6a0,0x6c0,0x6e0]else 16 if v in[0x160,0x170]else 32)if mode in['zpx','zpy','abx','aby']else 1
                ram.update(range(v,v+width))
            else:refs.add((k,v))
    return code,ram,refs
def make_world():
    # Native data fixtures: 16px cells; terrain is not a movement implementation.
    grid=[[0]*64 for _ in range(16)]
    for y in range(12,16):grid[y]=[1]*64
    for y in range(4,12):grid[y][10]=1
    for x in range(4,9):grid[5][x]=1
    for x in range(6,9):grid[8][x]=1
    for y in range(8,12):grid[y][21]=1
    for y in range(12,16):
        for x in range(26,30):grid[y][x]=0
    stage=bytearray(8192);shapes={};records=[]
    for page in range(4):
        for sx in range(8):
            for sy in range(8):
                vals=tuple(grid[sy*2+dy][page*16+sx*2+dx]for dx,dy in[(0,0),(0,1),(1,0),(1,1)])
                if vals not in shapes:shapes[vals]=len(shapes);records.append(vals)
                stage[0x500+page*64+sx*8+sy]=shapes[vals]
    for i,vals in enumerate(records):stage[i*4:i*4+4]=bytes(v<<6 for v in vals)
    return grid,bytes(stage)
def generate():
    out=O/'component';out.mkdir(parents=True,exist_ok=True);code,ram,refs=collect();ram.update([0x99,0x25,0x1c,0x6c0])
    # Keep native indexed aliases contiguous; imports are proposals, not leases.
    scratch=18;ram={a for a in ram if a>=scratch};groups=[]
    for a in sorted(ram):
        if groups and a==groups[-1][1]:groups[-1][1]+=1
        else:groups.append([a,a+1])
    mapping={};offset=0
    for lo,hi in groups:
        for a in range(lo,hi):mapping[a]=offset+a-lo
        offset+=hi-lo
    def mem(a):return f'QuickManScratch+${a:02X}'if a<scratch else f'QuickManState+${mapping[a]:03X}'
    data={}
    for b,lo,hi in DATA:
        for a in range(lo,hi):data[b,a]=f'${B[at((b,a))]:02X}'
    for i,target in enumerate(STATE_TARGETS):data[0x3c,0x8783+i]='>'+label(key(target));data[0x3c,0x8790+i]='<'+label(key(target))
    for a,prefix in[(0xdcc7,'<'),(0xdcd3,'>')]:data[0x3e,a]=prefix+label(key(0xda6f))
    data[0x3e,0xdd25]='<'+label(key(0xdf31));data[0x3e,0xdd35]='>'+label(key(0xdf31))
    types=sorted(set(B[0x7d3d7+i]+j for i in range(13)for j in range(2))|{0x7e,0x7f});scripts=[]
    for base_lo,base_hi,ids in[(0x9000,0x90c0,types),(0x9180,0x9240,[0xe])]:
        length=128 if base_lo==0x9000 else 16
        for i in range(length):data[0x1c,base_lo+i]='$00';data[0x1c,base_hi+i]='$00'
        for typ in ids:
            ptr=B[at((0x1c,base_lo+typ))]+256*B[at((0x1c,base_hi+typ))];a0=at((0x1c,ptr));n=B[a0]+3;assert n<67
            for j in range(n):data[0x1c,ptr+j]=f'${B[a0+j]:02X}'
            data[0x1c,base_lo+typ]='<'+data_label((0x1c,ptr));data[0x1c,base_hi+typ]='>'+data_label((0x1c,ptr));scripts.append(dict(table=f'{base_lo:04X}',type=typ,pointer=f'{ptr:04X}',bytes=n))
    lines=['; Generated from SHA256 '+sha(ROM),'.setcpu "6502"','.macpack longbranch','.import QuickManState','.importzp QuickManScratch','.import QuickManWorldProbe,QuickManSound,QuickManScrollStrip,QuickManProjectileContact,QuickManDeath,QuickManYield,QuickManEffectSpawn','.export QuickManTick,QuickManInit,QuickManAnimate,QuickManGetFrame,QuickManStateBytes,QuickManScratchBytes','.segment "QUICKMAN"',f'QuickManStateBytes={offset}',f'QuickManScratchBytes={scratch}']
    def emit(s):lines.append(s)
    emit('QuickManInit:');emit('lda #0');emit('ldy #0');emit('QmClearPages:')
    pages=offset//256
    for page in range(pages):emit(f'sta QuickManState+${page*256:03X},y')
    emit('iny');emit('bne QmClearPages')
    if offset%256:
        emit('ldy #0');emit('QmClearTail:');emit(f'sta QuickManState+${pages*256:03X},y');emit('iny');emit(f'cpy #${offset%256:02X}');emit('bne QmClearTail')
    defaults={0x15:3,0x2c:6,0x30:0x40,0x3b:0xdf,0x3c:4,0x42:0x40,0x99:40,0x9b:128,0xac:2,0x420:0xc0,0x460:80,0x4a0:181,0x6c0:40}
    for a,v in defaults.items():
        assert a in mapping or a<scratch,(hex(a),'init field omitted');emit(f'lda #${v:02X}');emit('sta '+mem(a))
    emit('rts');emit('QuickManTick:');emit('pha');emit('lda '+mem(0x23));emit('sta '+mem(0x25));emit('pla');emit('sta '+mem(0x23))
    for pc in[0xc095,0xc097,0xc099,0xc09b]:
        n,s,mode,raw=decode(key(pc));v=int(re.findall(r'\$([0-9a-f]+)',s)[0],16);emit(re.sub(r'\$[0-9a-f]+',mem(v),s))
    emit('jsr '+label(key(0x84ee)));emit('jsr '+label(key(0xdcdf)));emit('jsr QuickManAnimate');emit('inc '+mem(0x1c));emit('rts')
    emit('QuickManAnimate:');emit('ldx #4');emit('jmp '+label(key(0xcd23)));emit('QuickManReturn:');emit('rts')
    emit('QuickManGetFrame:');emit('lda '+mem(0x420)+',x');emit('bpl QmNoFrame');emit('ldy '+mem(0x400)+',x');emit('cpx #2');emit('bcs QmWeaponFrame')
    emit('lda DX_1C_9000,y');emit('sta '+mem(8));emit('lda DX_1C_90C0,y');emit('bne QmFramePointer')
    emit('QmWeaponFrame:');emit('lda DX_1C_9180,y');emit('sta '+mem(8));emit('lda DX_1C_9240,y')
    emit('QmFramePointer:');emit('sta '+mem(9));emit('ldy '+mem(0x6a0)+',x');emit('iny');emit('iny');emit('lda ('+mem(8)+'),y');emit('bne QmFrameReturn');emit('lsr '+mem(0x420)+',x');emit('QmNoFrame: lda #0');emit('QmFrameReturn: rts')
    emit('QuickManContactBridge:');emit('jsr QuickManProjectileContact');emit('ldx '+mem(0x2b));emit('lda '+mem(0x420)+',x');emit('bpl QmContactDone');emit('jmp ('+mem(8)+')');emit('QmContactDone:');emit('rts')
    for k,(n,s,mode,raw)in sorted(code.items()):
        emit(label(k)+':');emit('; CX '+f'{k[0]:02X}:{k[1]:04X} '+raw.hex())
        if k[1]==0xdf31:emit('jmp CX_1E_8290');continue
        op=s.split()[0];nums=re.findall(r'\$([0-9a-f]+)',s);v=int(nums[0],16)if nums else None
        if v is not None and mode not in ['imm']:
            if mode=='rel' or(op in['JSR','JMP']and mode=='abs'):
                dest=EXTERNAL.get(v,label(key(v,k[0]if k[0]==0x1e else 0x3c)));s=re.sub(r'\$[0-9a-f]+',dest,s)
                if mode=='rel':s={'BNE':'jne','BEQ':'jeq','BCC':'jcc','BCS':'jcs','BMI':'jmi','BPL':'jpl','BVC':'jvc','BVS':'jvs'}[op]+s[3:]
            elif v<0x8000:s=re.sub(r'\$[0-9a-f]+',mem(v),s)
            else:
                dk=(0x1c,v)if v in[0x9000,0x90c0,0x9180,0x9240,0x9300,0x93c0]else key(v,k[0]if k[0]==0x1e else 0x3c)
                assert dk in data,(k,s,'unmapped data');s=re.sub(r'\$[0-9a-f]+',data_label(dk),s)
        emit(s)
    for k,value in sorted(data.items()):emit(data_label(k)+': .byte '+value)
    (out/'component.s').write_text('\n'.join(lines)+'\n')
    manifest=dict(status='PRIVATE_RELOCATABLE_SOURCE_COMPONENT_NOT_HOST_LEASED',ROM_sha256=sha(ROM),source_instruction_nodes=len(code),source_instruction_bytes=sum(n for n,s,m,r in code.values()),state_bytes=offset,scratch_ZP_bytes=scratch,native_to_private_state={f'{a:04X}':i for a,i in mapping.items()},source_data_bytes=len(data),script_leaves=scripts,bank_adapter='NativeDF31 farcall becomes a direct JMP to copied bank1E:8290; native bank restore ends return. No source movement or projectile motion instructions replaced.',world_adapter='NativeCB9F rectangle contact prefix is retained. CBC0 is the host tile-data callback; native side/head/feet resolver stays in component.',callbacks=EXTERNAL,unsupported_contract='Source identity9B bit7 must stay set, weaponA9 must be0; APIs are Quick Man only. Host owns sound, death scenes, frame waits, PPU strips and projectile enemy contacts.',defaults={f'{a:04X}':v for a,v in defaults.items()})
    (out/'source-map.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':
    d=generate();print('instructions',d['source_instruction_nodes'],'bytes',d['source_instruction_bytes'],'state',d['state_bytes'],'ZP',d['scratch_ZP_bytes'])
