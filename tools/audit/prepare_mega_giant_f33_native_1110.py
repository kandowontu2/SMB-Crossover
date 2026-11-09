"""Bind the controller-only Giant route to the exact current shared engine."""

import argparse
from pathlib import Path

import check_mega_giant_f33_1110 as Q
from nightly_patch_guard_v1 import check
from prepare_selected_native_packet_v1 import prepare, sha


ROOT = Q.R/'build/mega-giant-f33-1110'
BASE = Q.R/'build/shared-sparse-draw-native-1110/candidate.nes'
PROOF = ROOT/'proof-v2.json'
ROUTE = ROOT/'route-30-66-28-settle-timed-3300.json'
SOURCE = Q.R/'tools/playthroughs/mega_giant_host_1110.lua'
PROOF_SHA = '83f00077fdc924cd9ed049c2b04a0abeb648d611e364d0777bcf668b9c3ecb0c'
ROUTE_SHA = '2c25fdfe448d4c5c141a863cfdb2f8aff68bd78e0db7e5e60ff2a1d3eb9fbb5b'
ROM_SHA = 'd48a7454969ea71d8f7b91eb9709d7f19e9f44188577cbb1683152409f4cb61f'
RAM = '''SelectedCharacter MarioVariant OperMode OperMode_Task GameEngineSubroutine NumberofLives
WorldNumber LevelNumber Player_X_Position Player_PageLoc Player_Y_Position Player_X_Speed Player_Y_Speed Player_State
PlayerStatus TimerControl A_B_Buttons PreviousA_B_Buttons
ScreenLeft_X_Pos ScreenLeft_PageLoc Enemy_X_Position Enemy_PageLoc Enemy_Flag Enemy_ID Enemy_State
Enemy_Y_Position CrossoverTitleDrawn DisableScreenFlag CrossoverMenuState CrossoverMenuIndex
CheatStartLevel CheatInvincible'''.split()


def controller(digest=ROM_SHA):
    assert sha(PROOF)==PROOF_SHA and sha(ROUTE)==ROUTE_SHA
    assert sha(BASE)==Q.PIN
    for p in (PROOF,ROUTE):
        receipt = Q.read(p)
        assert receipt['passed'] and receipt['parent_SHA256']==Q.PIN
        assert receipt['expected_memory_only_SHA256']==ROM_SHA
        for name, bound_hash in receipt['bindings'].items():
            binding = BASE if Path(name)==Q.C.HOST and bound_hash==Q.PIN else Path(name)
            assert sha(binding)==bound_hash,name
    proof,route = Q.read(PROOF),Q.read(ROUTE)
    assert route['reason']=='active_1_2' and route['endpoint']['lives']==2
    b = Q.C.bundle(BASE.read_bytes())
    main,flag,draw = (Q.C.address(b,'GameLoop'),Q.C.address(b,'FlagpoleCollision'),
                      proof['render_symbols']['GiantDraw'])
    assert (main,flag,draw)==(0x82d9,0x9e47,0xa000)
    names = ','.join(f'{n}={Q.C.address(b,n)}' for n in RAM)
    config = f'local C={{rom="{digest}",main={main},flag={flag},draw={draw},ram={{{names}}}}}\n'
    return config+SOURCE.read_text(encoding='utf-8')


def compose_current(out, side_proof):
    nightly = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    side = Q.read(side_proof)
    assert side['passed'] and side['parent_SHA256'] == Q.PIN
    base = BASE.read_bytes()
    current = Q.install(base, side['patches'])
    assert check(nightly)['ROM_sha256'] == Q.G.digest(current) == side['expected_memory_only_SHA256']
    out.mkdir(exist_ok=True)
    _, image, patches, *_ = Q.compose(out, base)
    original = image['raw']
    assert Q.G.digest(original) == ROM_SHA and patches == Q.read(PROOF)['patches']
    assert not Q.overlap(patches, side['patches'])
    # Check actual cartridge bytes as well as the declared spans. Giant's CHR
    # data is composed from the donor and is not enumerated as PRG patches.
    for row in side['patches']:
        at = row['file_offset']
        n = len(bytes.fromhex(row['old_hex']))
        assert original[at:at+n] == base[at:at+n]
    candidate = Q.install(original, side['patches'])
    chr_start = 16 + 1024 * 1024
    changed_pages = [page for page in range(1024)
                     if candidate[chr_start + page * 1024:chr_start + (page + 1) * 1024]
                     != current[chr_start + page * 1024:chr_start + (page + 1) * 1024]]
    assert changed_pages == [*Q.G.ART, Q.G.ATLAS, Q.G.CODE]
    assert candidate[:16] == current[:16]
    rom = out / 'candidate.nes'
    if rom.exists():
        assert rom.read_bytes() == candidate
    else:
        rom.write_bytes(candidate)
    return rom, Q.G.digest(candidate)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--packet-name', default='native', choices=('native', 'native-route', 'native-clear', 'native-end'))
    mode = cli.add_mutually_exclusive_group()
    mode.add_argument('--rom',type=Path)
    mode.add_argument('--compose-current',type=Path,metavar='SIDE_PROOF')
    cli.add_argument('--expected-sha', help='Exact tested ROM digest for an explicit --rom launch.')
    cli.add_argument('--symbols-from', type=Path, help='Existing symbol carrier; never copied beside the ROM.')
    args = cli.parse_args()
    if (args.expected_sha or args.symbols_from) and args.rom is None:
        cli.error('--expected-sha and --symbols-from require --rom')
    if args.expected_sha and (len(args.expected_sha) != 64 or
                             any(c not in '0123456789abcdef' for c in args.expected_sha)):
        cli.error('--expected-sha must be a lowercase SHA-256 digest')
    out = args.output.resolve()
    assert out.is_relative_to(Q.R / 'build') and out != Q.R / 'build'
    if args.rom is None and args.compose_current is None:
        dest = args.output/'native-controller.lua'
        assert not dest.exists()
        dest.write_text(controller(),encoding='utf-8',newline='\n')
        print(dest,sha(dest),flush=True)
        return
    refs = {PROOF,ROUTE,SOURCE,Path(__file__),*map(Path,Q.read(PROOF)['bindings']),*map(Path,Q.read(ROUTE)['bindings'])}
    refs.discard(Q.C.HOST)
    refs.add(BASE)
    rom, digest = args.rom, args.expected_sha or ROM_SHA
    symbols = ((args.symbols_from.with_suffix('.lbl'), args.symbols_from.with_suffix('.dbg'))
               if args.symbols_from else None)
    if args.compose_current:
        side_proof = args.compose_current.resolve()
        rom, digest = compose_current(out, side_proof)
        out /= args.packet_name
        refs.add(side_proof)
        symbols = BASE.with_suffix('.lbl'), BASE.with_suffix('.dbg')
    prepare(out,rom,controller(digest),refs,expected=digest,timeout=240,allow_interactive=True,
            rom_symbols=symbols,
            scope='Private Giant exact variant9, sprite DMA/CHR, no cheat, controller-only flagpole and active 1-2.')


if __name__=='__main__':
    main()
