"""Prepare (do not run) the explicit-fixture native Mini two4x4 fireball replay."""
import argparse
import json
from pathlib import Path
import re
import sys

from check_tmnt_render_oa import location
from observe_chip_committed_write import lua
from prepare_mini_mario_native_power_1103_v56 import address,bundle
from prepare_selected_native_packet_v1 import R,prepare,sha


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom',type=Path)
    ap.add_argument('--labels',type=Path,action='append',
                    help='Repeat for final Mini kernel and fireball ld65 label files.')
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--donor-art',type=Path,help='Exact GBC art integration manifest for this ROM.')
    ap.add_argument('--fire-bank',type=int,default=89)
    ap.add_argument('--spawn-bank',type=int,action='append',
                    help='Source attack constructor banks; defaults to owned bank89/91.')
    ap.add_argument('--syntax-only',action='store_true',help='Compile Lua syntax only; prepare no packet and bind no ROM.')
    args=ap.parse_args();out=args.output.resolve()
    source=Path(__file__).with_name('observe_mini_fireball_1103.lua')
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    syntax=LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')
    if args.syntax_only:
        assert syntax(source.read_text())
        out.mkdir(exist_ok=True)
        (out/'two-slot-observer-syntax.json').write_text(json.dumps(dict(
            passed=True,syntax_only=True,packet_prepared=False,ROM_bound=False,
            pool_slots=2,max_PNGs=3,Lua_SHA256=sha(source),generator_SHA256=sha(Path(__file__))),indent=2)+'\n')
        print(json.dumps(dict(passed=True,syntax_only=True,packet_prepared=False)))
        return
    assert args.rom and args.labels,'A candidate ROM and final label files are required for a native packet'
    rom=args.rom.resolve()
    raw=rom.read_bytes();image=bundle(raw);labels={}
    for p in args.labels:
        labels.update({name:int(pc,16)for pc,name in re.findall(r'^al ([\dA-Fa-f]+) \.(\w+)$',p.read_text(),re.M)})
    names=['SelectedCharacter','OperMode','OperMode_Task','GameEngineSubroutine',
           'CrossoverMenuState','CrossoverMenuIndex','MarioVariant','NumberofLives',
           'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos',
           'Player_State','Player_Y_Speed','PlayerStatus','PlayerFacingDir','Enemy_Flag',
           'CurrentOAMOffset','ScreenLeft_X_Pos','ScreenLeft_PageLoc','Enemy_ID','Enemy_State',
           'Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed',
           'Enemy_MovingDir','Enemy_BoundBoxCtrl']
    symbols={n:address(image,n)for n in names}
    symbols.update(Fireball_State=0x25,Fireball_State1=0x26,Fireball_X_Position=0x7c,
                   Fireball_PageLoc=0x63,Fireball_Y_Position=0xc4,Fireball_Y_HighPos=0xab,
                   Fireball_X_Speed=0x4d,Fireball_Y_Speed=0x95,FireballBouncingFlag=0x3a,
                   Fireball_BoundBoxCtrl=0x64c,FireballMetasprite=0x6e8,
                   FireballMetasprite1=0x6e9,GuestOamRotationActive=0x6c0b,RgOamRotation=0x6c08,FrameCounter=0x0e,
                   NmiSkipped=0x013a)
    def hook(name,pc,bank):
        at=16+bank*8192+(pc&8191)
        return dict(name=name,pc=pc,physical=bank*8192+(pc&8191),
                    memory='nesPrgRom',bytes=list(raw[at:at+4]))
    hooks={}
    for name in ['GameCoreRoutine','FireballObjCore']:
        pc=address(image,name);bank=(location(image,name)-16)//8192
        hooks[name]=hook(name,pc,bank)
    hooks['MiniFireballDraw']=hook('MiniFireballDraw',labels['MiniFireballDraw'],args.fire_bank)
    art=list(raw[1048592+967*1024+0x2e0:1048592+967*1024+0x300])
    opaque=[]
    for tile in range(2):
        for y in range(8):
            for x in range(8):
                bit=7-x;value=((art[tile*16+y]>>bit)&1)|(((art[tile*16+8+y]>>bit)&1)<<1)
                if value:opaque.append((x,y+tile*8))
    extent=dict(width=max(x for x,y in opaque)-min(x for x,y in opaque)+1,
                height=max(y for x,y in opaque)-min(y for x,y in opaque)+1,
                opaque_pixels=len(opaque),left=min(x for x,y in opaque),top=min(y for x,y in opaque))
    expected = dict(width=6,height=6,opaque_pixels=23,left=1,top=1) if args.donor_art else dict(width=4,height=4,opaque_pixels=16,left=0,top=0)
    assert extent == expected,extent
    config=dict(ROM_sha256=sha(rom),hooks=hooks,art=art,tile_extent=extent,
                fire_bank=args.fire_bank,spawn_banks={n:True for n in(args.spawn_bank or[89,91])},
                pool_slots=2,spawn_left=-6,spawn_right=2,draw_x=6,draw_y=4,
                draw_limit=246,palette=[0x16,0x30,0x27],
                max_frames=4500,menu_variants=[1,5,6,2,3,4,7,8])
    refs=[Path(__file__),source,R/'src/reset.s',*args.labels]
    if args.donor_art:
        report=json.loads(args.donor_art.read_text())
        assert report['passed'] and report['candidate_SHA256']==sha(rom)
        if 'native_draw_address' in report:
            # Watch the wrapper on every render pass, including an empty pool.
            # The direct renderer is entered only while a shot is active.
            pc=0xd239
            wrapper=1048592+967*1024+(pc&0x3ff)
            assert raw[wrapper:wrapper+3]==bytes.fromhex('4c45d4')
            hooks['MiniFireballDraw']=dict(name='MiniFireballDraw',pc=pc,physical=2*8192+(pc&8191),
                                           memory='nesWorkRam',bytes=list(raw[wrapper:wrapper+4]))
        for row in report['frames'].values():
            offset=1048592+967*1024+row['CHR_offset']
            assert raw[offset:offset+32].hex()==row['bytes']
        config.update(donor_frames={name:dict(tile=row['tile'],offset=row['CHR_offset'],data=list(bytes.fromhex(row['bytes'])))
                                    for name,row in report['frames'].items()},
                      draw_x=4,draw_y=2,phase_ram=report['phase_RAM'],palette=report['palette'])
        refs.append(args.donor_art)
    text='local MINI_FIREBALL_SYMBOLS='+lua(symbols)+'\nlocal MINI_FIREBALL_CONFIG='+lua(config)+'\n'+source.read_text()
    assert syntax(text)
    if out.exists():
        assert {p.name for p in out.iterdir()}<={'controller.lua','run.py','ready.json','fixture-contract.json'},'Only an unrun owned packet may be refreshed'
        contract=out/'fixture-contract.json'
        if contract.exists():
            assert json.loads(contract.read_text())['run']is False
            contract.unlink()
    prepare(out,rom,text,refs,expected=config['ROM_sha256'],timeout=180,allow_interactive=True,
            scope='Cold Mini menu then explicit fire-tier fixture. Real B edges, two native actors, third-shot rejection, bounce, clipping and independent hardware OAM/CHR/palette in both directions and Up. In donor-art mode a staged Goomba exercises the native impact and both donor impact frames. Reports physical cadence. No earned flower or full-stage claim. Three PNG cap.')
    (out/'fixture-contract.json').write_text(json.dumps(dict(prepared=True,run=False,
        ROM_sha256=config['ROM_sha256'],tile_extent=extent,script_RAM_writes=True,
        pool_slots=2,max_PNGs=3,phase_cadence_reported=True,cadence_zero_enforced=False,
        controller_only=False,earned_powerup_claim=False,enemy_kill_claim=False,
        fixture='One native PlayerStatus2 seed, clears enemy flags and both native fireball slots only after authentic cold Mini handoff; then real polled inputs.',
        hooks=hooks),indent=2)+'\n')


if __name__=='__main__':main()
