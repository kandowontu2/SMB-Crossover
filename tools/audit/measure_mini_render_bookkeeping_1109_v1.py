"""Source-funded native firebar/small-lift admission on current Mini."""
from collections import Counter
from itertools import product
from pathlib import Path
import json
import subprocess

import measure_mini_active_actor_1108_v1 as A

R, N = A.R, A.N
OUT = R/'build/mini-render-bookkeeping-1109-v1'
ROM = R/'build/mini-parser-lift-1109/candidate.nes'
PIN = 'a08d839b187fc6866a3fd3658200c2f26b8e3724b3b4de3b5e7d2a65702598d2'
SRC = R/'src/z2_platform_late_render.s'
LEGACY = R/'src/z2_platform_late_legacy.inc'
START, JOIN, BANK = 0xad01, 0xad5c, 71

NEW = '''
Z2LateWorldAdmission:
  ; A low ID cannot be a firebar or a native small platform. Preserve
  ; the original result of the first scan when all six IDs are low.
  ldx #5
LowIDs:
  lda Enemy_ID,x
  cmp #$1b
  bcs HighID
  dex
  bpl LowIDs
  stx FirebarSlot
  rts

  ; Resume the ordinary first scan at the first ID not yet ruled out.
HighID:
  cmp #$23
  bcc FoundFirebar
LegacyNext:
  dex
  bpl LegacyLoad
  stx FirebarSlot
  bmi Z2DrawLateSmallLifts
LegacyLoad:
  lda Enemy_ID,x
  cmp #$1b
  bcc LegacyNext
  bcs HighID
FoundFirebar:
  farcall DrawWorldFirebars
'''


def build(b):
    old = SRC.read_text().split('.segment "Z2_COLD"',1)[1].split(' RP_Save',1)[0]
    old = old.replace('.include "z2_platform_late_legacy.inc"', LEGACY.read_text())
    old = old.replace('.proc ', '').replace('.endproc', '')
    # Turn .proc headings into ordinary labels for an isolated link.
    for label in ('Z2LateWorldAdmission','Z2LateLegacyFirebarAdmission','Z2DrawLateSmallLifts'):
        old = old.replace('\n'+label+'\n', '\n'+label+':\n')
    old += '  php\n  pha\n  phx\n  tya\n  pha\n'
    late = old.split('\nZ2DrawLateSmallLifts:',1)[1].split('\nPresent:',1)[0]
    # On present the still-live saved P/A/X are the original RP_Save
    # frame's first three entries. Y has not changed during the scan.
    # The unchanged original body reloads X before its first use.
    new = NEW + 'Z2DrawLateSmallLifts:' + late + '\nPresent:\n  tya\n  pha\n'
    defs = ''.join(f'{name}=${A.address(b,name):04x}\n' for name in
                   ('Enemy_ID','Enemy_Flag','FirebarSlot','GuestOamRotationActive','DrawWorldFirebars'))
    defs += '''
.setcpu "6502"
.segment "SCAN"
.macro farcall target
  sta $016a
  lda #<target
  sta $016c
  lda #>target
  sta $016d
  lda #$87
  jsr $015a
.endmacro
.macro phx
  txa
  pha
.endmacro
.macro plx
  pla
  tax
.endmacro
'''
    result = []
    for tag,source in [('legacy',old),('single',new)]:
        stem = OUT/f'world-render-{tag}'
        src,cfg,obj,binary=(stem.with_suffix(ext) for ext in ('.s','.cfg','.o','.bin'))
        src.write_text(defs+source)
        cfg.write_text(f'MEMORY{{P:start=${START:04x},size=$100,file=%O;}}SEGMENTS{{SCAN:load=P,type=ro;}}\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',src,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
        obj.unlink()
        result.append(binary.read_bytes())
    return result


def init(m,slot,enemy,flag,owner,rotate):
    N.put(m,SelectedCharacter=owner,GuestOamRotationActive=rotate,RgOamRotation=248,
          CurrentOAMOffset=4,ObjectOffset=slot,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,
          ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,FrameCounter=3)
    b=m.bundle
    for name in ('Enemy_Flag','Enemy_ID','Enemy_State'):
        at=A.address(b,name)
        m[at:at+6]=bytes(6)
    for name,value in [('Enemy_ID',enemy),('Enemy_Flag',flag),('Enemy_State',0),('Enemy_X_Position',100),
                       ('Enemy_PageLoc',0),('Enemy_Y_Position',136),('Enemy_Y_HighPos',1),
                       ('FirebarSpinState_High',0),('FirebarSpinState_Low',0)]:
        m[A.address(b,name)+slot]=value
    if 0x1b<=enemy<0x23 and flag==1:
        N.invoke(m,'ProcFirebar',x=slot,y=0)
    m[0x200:0x300]=bytes((13*i+37)&255 for i in range(256))
    m.writes.clear()


def state(m, z):
    regs=tuple(z[k] for k in ('A','X','Y','P'))
    writes=[(a,v) for a,v in m.writes if 0x200<=a<0x300 or a in (0x5115,0x5116)]
    return regs,A.state(m),writes


def measure(images):
    seeds=[A.fixture(b,0,False,False) for b in images]
    direct=Counter()
    for enemy,flag,slot,owner,rotate in product([0,5,0x1a,0x1b,0x22,0x23,0x25,0x2a,0x2b,0x2c,0x2d,0xff],
            [0,1,2,0x80,0xff],[0,5],[0,4,41],[0,1]):
        outcomes=[]
        for seed in seeds:
            m=N.fork(seed)
            init(m,slot,enemy,flag,owner,rotate)
            z=N.invoke(m,'Z2LateWorldAdmission',x=7,y=12,a=137,p=0x71)
            outcomes.append((state(m,z),z['CPU']))
        a,b=outcomes
        assert a[0]==b[0], (enemy,flag,slot,owner,rotate,a[0][0],b[0][0],a[0][2][:10],b[0][2][:10])
        direct[enemy,a[1]-b[1]]+=1
    whole=[]
    for enemies,parse in product([0,2,5],[False,True]):
        pair=[A.fixture(b,enemies,False,parse) for b in images]
        costs=[]
        for epoch in range(2,22):
            outcomes=[]
            for m in pair:
                buttons=129 if 6<=epoch<18 else 0
                N.put(m,FrameCounter=epoch,SavedJoypadBits=buttons,SavedJoypad1Bits=buttons,
                      VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                m.writes.clear()
                z=N.invoke(m,'GameCoreRoutine',x=0,y=0)
                outcomes.append((state(m,z),z['CPU']))
            a,b=outcomes
            assert a[0]==b[0],(enemies,parse,epoch,a[0][0],b[0][0])
            costs.append([a[1],b[1],a[1]-b[1]])
        whole.append(dict(enemies=enemies,parser=parse,cycles=costs))
    return [[enemy,delta,num] for (enemy,delta),num in sorted(direct.items())],whole


def main():
    OUT.mkdir(exist_ok=True)
    raw=ROM.read_bytes()
    assert A.sha(raw)==PIN
    b=A.bundle(raw)
    old,new=build(b)
    at=16+BANK*8192+START-0xa000
    assert len(old)==JOIN-START and raw[at:at+len(old)]==old, (len(old),raw[at:at+len(old)].hex(),old.hex())
    print('Native source extents old/new',len(old),len(new),flush=True)
    assert len(new)<=len(old),(len(old),len(new))
    # The present path falls into the untouched original RP_Save body.
    new=new.ljust(len(old),b'\xea')
    image=raw[:at]+new+raw[at+len(old):]
    d,g=measure([b,A.bundle(image)])
    print('Direct',d,'GameCore',[(x['enemies'],x['parser'],sorted({q[2] for q in x['cycles']})) for x in g],flush=True)
    result=dict(passed=True,CPU_only=True,ROM_written=False,base_SHA256=PIN,
                memory_only_SHA256=A.sha(image),native_direct=d,whole_GameCore=g,
                patch=dict(physical_PRG=BANK,CPU_half_open=[START,JOIN],file_offset=at,old_hex=old.hex(),new_hex=new.hex()),
                scope='Reuses native legacy scan starting at the first high ID and keeps all actual firebar/lift drawing and OAM ordering. No added storage, bank or actor state. Actual vector proof separate.',
                bindings={str(p):A.sha(p.read_bytes()) for p in [Path(__file__),SRC,LEGACY,ROM]})
    (OUT/'measurement.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    main()
