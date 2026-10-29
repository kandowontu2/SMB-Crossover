"""Generate original SMB2 instructions/data into the approved raw25 overlay.

No shared integration edits. Terrain/room-object boundaries are named host
callbacks; source control, fractions, collision response, lifting and throw
instructions retain their genuine original instruction boundaries.
"""
from pathlib import Path
import hashlib
import json
import re
from py65.devices.mpu6502 import MPU

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT.parent/'mario in kid icarus/vendor/smb2'
ROM = Path('C:/NES/Super Mario Bros. 2 (USA).nes')
SHA = '41300bc4942a8a4f9b53148b404dd5cae3dd708ebdd9b617888d290a51a83e43'
OUT = ROOT/'build/smb2-roster-component-v1'


def digest(b): return hashlib.sha256(b).hexdigest()
def binding(p):
    p = Path(p); b = p.read_bytes()
    return dict(path=str(p.resolve()), bytes=len(b), sha256=digest(b))


def labels():
    result = {}
    for p in (REF/'bin').glob('native.nes.*.nl'):
        for line in p.read_text().splitlines():
            m = re.match(r'\$([0-9a-fA-F]+)#([^#]+)#', line)
            if m: result[m[2]] = int(m[1], 16)
    return result


def original(pair=0):
    raw = ROM.read_bytes(); assert digest(raw) == SHA
    m = bytearray(65536)
    m[0x8000:0xc000] = raw[16+pair*16384:16+(pair+1)*16384]
    m[0xc000:] = raw[16+7*16384:16+8*16384]
    return m


EXTERNAL_NAMES = {
    'PlayerTileCollision_CheckCherryAndClimbable': 'S2WorldInteraction',
    'TileBehavior_CheckJar': 'S2GroundInteraction',
    'PlayerTileCollision_CheckQuicksand': 'S2QuicksandBoundary',
    'PlayerTileCollision_HurtPlayer': 'S2TerrainHurt',
    'sub_BANK0_924F': 'S2NativeTileProbe', 'LoadCharacterCHRBanks':'S2ChrReloadBoundary'}
ENTRY_NAMES = ['HandlePlayerState_Normal', 'HandlePlayerState_Lifting',
    'PlayerStartJump', 'PlayerGravity', 'ApplyPlayerPhysicsY', 'PlayerWalkJumpAnim',
    'HandlePlayerState_ChangingSize']
DATA = {0x8ac0:14, 0x8c18:2, 0x8d26:4, 0x8d2a:2, 0x8d62:10,
    0x8d6c:3, 0x8db2:8, 0x8dba:4, 0x8dbe:2, 0x8ee8:8,
    0x8ef0:8, 0x8ef8:2, 0x9062:3, 0x9311:5, 0xf000:12,
    0xf64e:12, 0xf011:44, 0xf055:44, 0x8bec:5}


def graph():
    m = original(); l = labels(); cpu = MPU(memory=m)
    external = {l[n]:v for n,v in EXTERNAL_NAMES.items()}
    todo = [l[n] for n in ENTRY_NAMES]; code = {}; addresses = set()
    while todo:
        pc = todo.pop()
        if pc in code or pc in external: continue
        assert 0x8a41 <= pc < 0x8ac2 or 0x8bf1 <= pc < 0x9074 or 0x9312 <= pc < 0x934f, hex(pc)
        ins, mode = cpu.disassemble[m[pc]]
        n = {'imp':1,'acc':1,'imm':2,'zpg':2,'zpx':2,'zpy':2,'inx':2,'iny':2,
             'rel':2,'abs':3,'abx':3,'aby':3,'ind':3}[mode]
        code[pc] = (ins,mode,n)
        if n > 1 and mode not in ['imm','rel']:
            target = m[pc+1] | (m[pc+2]<<8 if n == 3 else 0)
            if ins in ['JSR','JMP']:
                assert mode == 'abs', (pc,mode)
                if target not in external: todo.append(target)
            elif target < 0x8000: addresses.add(target)
            else: assert any(a <= target < a+b for a,b in DATA.items()), (hex(pc),hex(target))
        if mode == 'rel': todo.append((pc+2+(m[pc+1] if m[pc+1]<128 else m[pc+1]-256))&65535)
        if ins not in ['RTS','RTI','JMP']: todo.append(pc+n)
    return m,l,external,code,addresses


def ram_map(addresses, l):
    # Keep original +10 axis indexing and player-before-object array ABI.
    aliases = {}; occupied = set()
    for native, host, name in [(0x28,0x5c00,'S2X'),(0x32,0x5c0a,'S2Y'),
        (0x14,0x5c10,'S2Page'),(0x1e,0x5c1a,'S2YPage'),
        (0x3c,0x5c20,'S2VX'),(0x46,0x5c2a,'S2VY'),
        (0x407,0x5c30,'S2XF'),(0x411,0x5c3a,'S2YF'),
        (0x4cb,0x5c40,'S2AX'),(0x4d5,0x5c4a,'S2AY')]:
        for i in range(4):
            aliases[native+i] = (name+('' if not i else '+'+str(i)),host+i)
            occupied.add(host+i)
    for i in range(23):
        aliases[0x546+i] = ('S2Stats'+('' if not i else '+'+str(i)),0x5c50+i)
        occupied.add(0x5c50+i)
    # Source PickupSpeedAnimation-2 is read only with proven native Y2..7.
    aliases[0x544] = ('S2Stats-2',0x5c4e)
    names = {0:'S2Math0',1:'S2Math1',7:'S2ProbeDirection',8:'S2ProbeOffset',
        0xa:'S2Conveyor',0xc:'S2Ice',0xe:'S2Spikes',0x10:'S2Clock',0x12:'S2Source12',
        0x50:'S2State',0x5a:'S2Collision',0x6e:'S2MovementDir',0x82:'S2Timer',
        0x84:'S2WalkTimer',0x85:'S2Hurt',0x6f6:'S2Size',0x8f:'S2NativeCharacter',0x99:'S2Air',0x9a:'S2Duck',
        0x9b:'S2WalkFrame',0x9c:'S2Holding',0x9d:'S2Face',0xc7:'S2Animation',
        0xec:'S2Horizontal',0xf5:'S2Fresh',0xf7:'S2Held',0x428:'S2ScreenX',
        0x429:'S2SourceScreenX',0x42d:'S2HeldIndex',0x4b2:'S2Carpet',
        0x4c9:'S2Float',0x4ca:'S2Charge',0x4df:'S2Quicksand',
        0x4e0:'S2Star',0x601:'S2DpcmRequest',0x602:'S2Sfx1',0x604:'S2Sfx2',
        0x624:'S2Slippery',0x635:'S2Tileset'}
    arrays = [(0x51,'S2ObjectState'),(0x90,'S2ObjectType'),
              (0xa8,'S2ObjectLift'),(0x42f,'S2ObjectProjectile'),
              (l['ObjectHitbox'],'S2ObjectHitbox')]
    free = lambda n: next(a for a in range(0x5c00,0x5c81-n)
        if not set(range(a,a+n))&occupied)
    for native,name in arrays:
        a = free(3)
        for i in range(3):
            aliases[native+i] = (name+('' if not i else '+'+str(i)),a+i)
            occupied.add(a+i)
    for native in sorted(addresses):
        if native in aliases: continue
        a = free(1); occupied.add(a)
        aliases[native] = (names[native],a)
    # Explicit private host fields use remaining genuinely unassigned bytes.
    extras = {}
    for name in ['S2Previous','S2Hurt','S2Size',
        'S2ObjectFacing0','S2ObjectFacing1','S2ObjectFacing2','S2ObjectHost0',
        'S2ObjectHost1','S2ObjectHost2','S2Math2','S2HeadX','S2HeadPage','S2HeadY']:
        if any(alias==name for alias,host in aliases.values()):continue
        a = free(1); occupied.add(a); extras[name] = a
    assert max(occupied) <= 0x5c7f
    return aliases,extras,occupied


def main():
    OUT.mkdir(exist_ok=True)
    m,l,external,code,addresses = graph()
    try:
        aliases,extras,occupied = ram_map(addresses,l)
    except StopIteration:
        first=OUT/'first-RAM-fit-negative.txt'
        if not first.exists(): first.write_text('Original unoptimized draft retained all native fields plus redundant host XY/last-export/temp copies; >128 bytes, StopIteration before any source output. No spill or new RAM was used.\n')
        raise
    base_aliases = {name:host for native,(name,host) in aliases.items() if '+' not in name and '-' not in name}
    state = ['; Source-only SMB2 raw25 component. Every overlay read needs exact owner.',
        '.ifndef __SMB2_ROSTER_STATE_INC','__SMB2_ROSTER_STATE_INC=1',
        '.ifndef CHARACTER_SMB2_ROSTER','CHARACTER_SMB2_ROSTER=25','.endif',
        '.ifndef S2_FIRST_CHR','S2_FIRST_CHR=796','.endif','S2Variant=$5fe3',
        'S2Health=$5f98','S2MaxHealth=$5f99','S2Vegetables=$5f9a','S2Ready=$5f9b',
        'S2Life=$5f9c','S2Area=$5f9d','S2World=$5f9e','S2PaletteAck=$5f9f']
    for n,a in sorted((base_aliases|extras).items(),key=lambda x:x[1]): state.append(f'{n}=${a:04x}')
    state += ['.export '+','.join(base_aliases|extras),'.endif']
    (ROOT/'src/smb2_roster_state.inc').write_text('\n'.join(state)+'\n')
    lines = ['; Genuine original SMB2 USA instructions, ROM SHA'+SHA,
        '; World/terrain interfaces are explicit named host callbacks.',
        '.pushseg','.segment "PARODIUS_BELLS"','S2NativeStart:']
    branch = {'BCC':'jcc','BCS':'jcs','BEQ':'jeq','BNE':'jne','BMI':'jmi','BPL':'jpl','BVC':'jvc','BVS':'jvs'}
    for pc,(ins,mode,n) in sorted(code.items()):
        operand = ''; op = ins.lower()
        if mode == 'rel':
            target = (pc+2+(m[pc+1] if m[pc+1]<128 else m[pc+1]-256))&65535
            operand = 'S2N'+f'{target:04X}'; op = branch[ins]
        elif mode == 'imm': operand = f'#${m[pc+1]:02x}'
        elif mode == 'acc': operand = 'a'
        elif mode != 'imp':
            target = m[pc+1] | (m[pc+2]<<8 if n == 3 else 0)
            if ins in ['JSR','JMP']: operand = external.get(target,'S2N'+f'{target:04X}')
            elif target < 0x8000: operand = aliases[target][0]
            else:
                a = next(a for a,b in DATA.items() if a <= target < a+b)
                operand = 'S2D'+f'{a:04X}'+('+'+str(target-a) if target != a else '')
            if mode in ['zpx','abx']: operand += ',x'
            elif mode in ['zpy','aby']: operand += ',y'
            elif mode == 'iny': operand = '('+operand+'),y'
            elif mode == 'inx': operand = '('+operand+',x)'
        lines += [f'S2N{pc:04X}: {op} {operand}'.rstrip()+f' ;0:{pc:04X} '+m[pc:pc+n].hex()]
        if pc+n in external and ins not in ['RTS','RTI','JMP']:
            lines.append(' jmp '+external[pc+n]+' ; actual original fallthrough boundary')
    for a,n in DATA.items():
        lines += [f'S2D{a:04X}: .byte '+','.join(f'${v:02x}' for v in m[a:a+n])]
    lines += ['S2NativeEnd:', '.export '+','.join('S2N'+f'{l[n]:04X}' for n in ENTRY_NAMES), '.popseg']
    native = ROOT/'src/smb2_roster_native.inc'; native.write_text('\n'.join(lines)+'\n')
    report = dict(status='GENERATED_PRIVATE_SOURCE_NO_BUILD_OR_NATIVE',
        original=binding(ROM),instructions=len(code),original_instruction_bytes=sum(n for _,_,n in code.values()),
        entries={n:f'{l[n]:04X}' for n in ENTRY_NAMES},external_boundaries={f'{p:04X}':v for p,v in external.items()},
        RAM=[dict(original=f'{p:04X}',host=f'{a:04X}',alias=n) for p,(n,a) in sorted(aliases.items())],
        extra_RAM={n:f'{a:04X}' for n,a in extras.items()},active_bytes_occupied=len(occupied),
        unused_active_bytes=[f'{a:04X}' for a in range(0x5c00,0x5c80) if a not in occupied],
        source_inputs=[binding(REF/p) for p in ['src/prg-0-1.asm','src/ram.asm']],
        outputs=[binding(native),binding(ROOT/'src/smb2_roster_state.inc')],tool=binding(__file__))
    out = OUT/'native-projection.json'; out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(output=binding(out),instructions=len(code),active_bytes=len(occupied)),indent=2))


if __name__ == '__main__': main()
