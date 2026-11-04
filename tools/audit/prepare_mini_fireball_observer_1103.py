"""Prepare (do not run) the explicit-fixture native Mini4x4 fireball replay."""
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
    ap.add_argument('--rom',type=Path,required=True)
    ap.add_argument('--labels',type=Path,action='append',required=True,
                    help='Repeat for final Mini kernel and fireball ld65 label files.')
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--fire-bank',type=int,default=89)
    args=ap.parse_args();rom=args.rom.resolve();out=args.output.resolve()
    raw=rom.read_bytes();image=bundle(raw);labels={}
    for p in args.labels:
        labels.update({name:int(pc,16)for pc,name in re.findall(r'^al ([\dA-Fa-f]+) \.(\w+)$',p.read_text(),re.M)})
    names=['SelectedCharacter','OperMode','OperMode_Task','GameEngineSubroutine',
           'CrossoverMenuState','CrossoverMenuIndex','MarioVariant','NumberofLives',
           'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos',
           'Player_State','Player_Y_Speed','PlayerStatus','PlayerFacingDir','Enemy_Flag',
           'CurrentOAMOffset','ScreenLeft_X_Pos','ScreenLeft_PageLoc']
    symbols={n:address(image,n)for n in names}
    symbols.update(Fireball_State=0x25,Fireball_State1=0x26,Fireball_X_Position=0x7c,
                   Fireball_PageLoc=0x63,Fireball_Y_Position=0xc4,Fireball_Y_HighPos=0xab,
                   Fireball_X_Speed=0x4d,Fireball_Y_Speed=0x95,FireballBouncingFlag=0x3a,
                   Fireball_BoundBoxCtrl=0x64c,FireballMetasprite=0x6e8,
                   FireballMetasprite1=0x6e9,GuestOamRotationActive=0x6c0b,RgOamRotation=0x6c08)
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
    assert extent==dict(width=4,height=4,opaque_pixels=16,left=0,top=0),extent
    config=dict(ROM_sha256=sha(rom),hooks=hooks,art=art,tile_extent=extent,
                fire_bank=args.fire_bank,spawn_left=-6,spawn_right=2,draw_x=6,draw_y=4,
                draw_limit=246,palette=[0x16,0x30,0x27],
                max_frames=4500,menu_variants=[1,5,6,2,3,4,7,8])
    source=Path(__file__).with_name('observe_mini_fireball_1103.lua')
    text='local MINI_FIREBALL_SYMBOLS='+lua(symbols)+'\nlocal MINI_FIREBALL_CONFIG='+lua(config)+'\n'+source.read_text()
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    refs=[Path(__file__),source,R/'src/reset.s',*args.labels]
    if out.exists():
        assert {p.name for p in out.iterdir()}<={'controller.lua','run.py','ready.json','fixture-contract.json'},'Only an unrun owned packet may be refreshed'
        contract=out/'fixture-contract.json'
        if contract.exists():
            assert json.loads(contract.read_text())['run']is False
            contract.unlink()
    prepare(out,rom,text,refs,expected=config['ROM_sha256'],timeout=180,allow_interactive=True,
            scope='Explicit native tier2/empty-actor fixture after actual cold Mini menu, Ready2, engine8, initial worldX40/floor. Real controller freshB/heldB/busy-slotB, left/right and Up. Native single slot, exact launch basis, ctrl8, movement/floor bounce/clipping,4x4 CHR967+2E0 slot5 and actual OAM DMA alongside Mini. At most4 PNGs/64files; no video or sequence. No earned flower, enemy kill, fullstage or controller-only claim. Prepared only; root owns sole Mesen queue.')
    (out/'fixture-contract.json').write_text(json.dumps(dict(prepared=True,run=False,
        ROM_sha256=config['ROM_sha256'],tile_extent=extent,script_RAM_writes=True,
        controller_only=False,earned_powerup_claim=False,enemy_kill_claim=False,
        fixture='One native PlayerStatus2 seed, clears enemy flags and both native fireball slots only after authentic cold Mini handoff; then real polled inputs.',
        hooks=hooks),indent=2)+'\n')


if __name__=='__main__':main()
