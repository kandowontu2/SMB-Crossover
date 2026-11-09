"""Reach the donor side sweep from native GameLoop and the parsed 1-1 pipe."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

from check_mega_giant_geometry_1110_v1 import M, R, ROM, HOST_PIN, SOURCE as GEOMETRY, address, bundle, sha
from check_mega_giant_crush_1110_v1 import SOURCE as CRUSH, FIXTURE, RETURN
from check_mega_giant_ppu_mapping_1110_v1 import frame, start_stage
from prepare_mini_side_alias_1108 import compare_memory


SWEEP=R/'tools/reference/mega_giant_mario_sweep_1110_v1.s'
INGRESS=0x9b5b
PATCH_BANK=126


def assemble(out,b):
    text=CRUSH.read_text()
    names=[name for line in text.splitlines() if line.startswith('.import')
           for name in line.split(' ',1)[1].split(', ')]
    names.extend(('PlayerFacingDir','DisableCollisionDet'))
    defines=''.join(f'{n}=${address(b,n):04x}\n' for n in names)
    text=defines+SWEEP.read_text()+re.sub(r'^\.import(?:zp)? .*\n','',text,flags=re.M)+GEOMETRY.read_text()
    assert address(b,'PlayerBGCollision')==INGRESS
    with tempfile.TemporaryDirectory(prefix='sweep-',dir=out) as folder:
        work=Path(folder)
        cfg,asm,obj,raw=(work/('sweep.'+ext) for ext in ('cfg','s','o','bin'))
        cfg.write_text('MEMORY { CODE:start=$5b80,size=$300,file=%O; } '
                       'SEGMENTS { GIANT_SWEEP:load=CODE,type=ro; GIANT_CRUSH:load=CODE,type=ro; '
                       'GIANT:load=CODE,type=ro; }\n')
        asm.write_text(text)
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',asm,'-o',obj],check=True)
        asm.unlink()
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',raw],check=True)
        return raw.read_bytes()


def world_x(m):
    return M.get(m,'Player_X_Position')+256*M.get(m,'Player_PageLoc')


def cell(x,y):
    col=(x//16)&31
    return 0x300+(0xd0 if col>=16 else 0)+(col&15)+(y&0xf0)-32


def reach_pipe(b):
    m,_=start_stage(b)
    jump=0
    jumped=False
    for f in range(250):
        x=world_x(m)
        if x>=417:
            break
        if not jumped and x>=264:
            jump=35
            jumped=True
        frame(m,65+(128 if jump else 0))
        jump=max(0,jump-1)
        m.writes.clear()
        m.ram_writes.clear()
        m.ppu_log.clear()
    assert f==173 and x==417 and M.get(m,'Player_Y_Position')==118
    assert bytes(m[cell(x,y)] for x,y in ((448,0xb0),(448,0xc0),(464,0xb0),(464,0xc0)))==bytes.fromhex('12141315')
    return m,f


def fixed_frame(m,variant,keys):
    M.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,NmiDisable=255)
    cpu=M.NesMPU(memory=m,pc=address(m.bundle,'GameLoop'))
    cpu.p,cpu.sp=0x31,252
    cpu.stPushWord(RETURN-1)
    ingress=None
    return_state=None
    native_crush_calls=0
    minimum_sp=cpu.sp
    min_crush_sp=cpu.sp
    for _ in range(55000):
        if cpu.pc==RETURN:
            break
        if m.rawtags[0]==254 and cpu.pc==INGRESS:
            assert ingress is None
            ingress=(cpu.sp,cpu.a,cpu.x,cpu.y,cpu.p,world_x(m),M.get(m,'Player_Y_Position'))
            M.put(m,MarioVariant=variant)
        if ingress is not None and return_state is None:
            min_crush_sp=min(min_crush_sp,cpu.sp)
            if cpu.pc==0xbe8b and m.rawtags[1]==137:
                native_crush_calls+=1
        if m.rawtags[0]==254 and cpu.pc==INGRESS+3:
            return_state=(cpu.sp,cpu.a,cpu.x,cpu.y,cpu.p&0xef)
            M.put(m,MarioVariant=0)
        minimum_sp=min(minimum_sp,cpu.sp)
        assert m[cpu.pc],('GameLoop BRK',hex(cpu.pc),m.rawtags)
        cpu.step()
    else:
        raise AssertionError(('Fixed GameLoop bound',hex(cpu.pc)))
    assert cpu.sp==252 and ingress and return_state
    return dict(ingress=list(ingress),return_state=list(return_state),native_effect_calls=native_crush_calls,
                frame_cycles=cpu.processorCycles,minimum_SP=minimum_sp,minimum_sweep_SP=min_crush_sp)


def place(m,x,face):
    M.put(m,Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=176,Player_Y_HighPos=1,
          Player_Y_Speed=0,Player_X_Speed=0,Player_X_MoveForce=0,Player_Y_MoveForce=0,
          Player_State=0,PlayerFacingDir=face,VRAM_Buffer1_Offset=0)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert sha(ROM)==HOST_PIN
    b=bundle(ROM.read_bytes())
    seed,setup_frames=reach_pipe(b)
    code=assemble(args.output,b)
    at=16+PATCH_BANK*8192+(INGRESS&8191)
    raw=b['raw']
    assert raw[at:at+3]==bytes.fromhex('ad1907')
    patched=raw[:at]+bytes.fromhex('20805b')+raw[at+3:]
    fork=M.fork(seed)
    fork.bundle=dict(fork.bundle,raw=patched)
    fork.raw_page(0,254)
    fork[FIXTURE:FIXTURE+len(code)]=code
    seed[FIXTURE:FIXTURE+len(code)]=code
    foreign=[]
    positive=[]

    for x,face,keys in ((417,1,0),(434,1,0),(417,2,0),(417,1,1)):
        old,new=M.fork(seed),M.fork(fork)
        for m in (old,new):
            place(m,x,face)
        a,z=fixed_frame(old,0,keys),fixed_frame(new,0,keys)
        assert a['return_state']==z['return_state']
        assert not a['native_effect_calls'] and not z['native_effect_calls']
        compare_memory(old,new)
        foreign.append(dict(x=x,face=face,keys=keys,fixture_added_cycles=z['frame_cycles']-a['frame_cycles']))

    for x,tile_x in ((417,448),(434,464)):
        new=M.fork(fork)
        place(new,x,1)
        targets=[cell(tile_x,y) for y in (176,192)]
        before=bytes(new[at] for at in targets)
        z=fixed_frame(new,9,0)
        pending=bytes(new[at] for at in targets)
        assert z['ingress'][5:]==[x,176]
        assert z['native_effect_calls']==2 and pending==b'\x23\x23',(x,before.hex(),pending.hex(),z)
        M.consume(new)
        for updates in range(12):
            after=bytes(new[at] for at in targets)
            if after==b'\0\0':
                break
            frame(new)
        else:
            raise AssertionError((x,before.hex(),pending.hex(),after.hex(),z))
        positive.append(dict(world_x=x,tile_world_x=tile_x,source_probes=[39,43],
                             before=before.hex(),pending=pending.hex(),after=after.hex(),
                             native_commit_updates=updates,**z))

    q=dict(passed=True,ROM_written=False,source_CPU_only=True,host_SHA256=HOST_PIN,
           old_entry=dict(bank=PATCH_BANK,pc=INGRESS,preimage='ad1907'),
           real_host_setup_frames=setup_frames,private_fixture=FIXTURE,assembled_bytes=len(code),
           assembled_SHA256=hashlib.sha256(code).hexdigest(),positive=positive,foreign=foreign,
           scope='Actual cold title, stock controller and native parser to the first pipe, then seeded grounded '
                 'pose for two full native GameLoop updates. Both source side-effect cells erase on each actual '
                 'donor X coordinate. The private identity exists only within the reached collision call. '
                 'Full donor sweep groups, motion/gap/end-level route, executable placement, IRQ and menu remain open.',
           bindings={str(p):sha(p) for p in (Path(__file__),SWEEP,CRUSH,GEOMETRY,ROM)})
    (args.output/'pipe-ingress-proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assembled_bytes=len(code),positive=positive,foreign=foreign)))


if __name__=='__main__':
    main()
