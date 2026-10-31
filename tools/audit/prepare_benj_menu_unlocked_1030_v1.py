"""Private Toad/Peach menu and body-palette integration; native checks pending."""
from pathlib import Path
import json
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
import prepare_functional_roster_visuals58_v1 as B
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load, address, location
P = R / 'build/benj-current-host-1030-v5'
O = R / 'build/benj-menu-unlocked-1030-v3'
J = O / 'joint'


def once(t, a, b):
    assert t.count(a) == 1, (a, t.count(a))
    return t.replace(a, b)


def main():
    assert not O.exists()
    h = json.loads(B.read(P / 'source-stage.json'))
    B.bound(h)
    assert h['candidate'] == 'c7b0d3ee3b1ce4b9b4550984e9692482bdefa2f49a85654e264685ce4a8de251'
    shutil.copytree(P / 'joint', J)
    def rt(s):
        return s.replace(str(P / 'joint'), str(J)).replace((P / 'joint').as_posix(), J.as_posix())
    for p in J.rglob('*'):
        if p.is_file() and p.suffix in ['.s', '.inc', '.cfg']:
            B.write(p, rt(B.read(p)))
    # The unjoined stomp/ceiling prototypes stay in the frozen v5 archive.
    # Their reserved bytes now fund the actual body palette callback. Native
    # SMB contacts remain authoritative in this first playable WIP.
    p = J / 'peach_float_core.s'
    s = B.read(p)
    s = s[:s.index('; F793..F7AC:')] + '.endscope\n' + '''
.proc BmColors
 farcall X5GetPlayerColors
 php
 pha
 lda SelectedCharacter
 bne Done
 lda MarioVariant
 cmp #5
 bcc Done
 cmp #7
 bcs Done
 phx
 phy
 lda MarioVariant
 ldy #0
 cmp #5
 beq Row
 ldy #3
Row:
 ldx VRAM_Buffer1_Offset
 lda Colors,y
 sta VRAM_Buffer1-3,x
 lda Colors+1,y
 sta VRAM_Buffer1-2,x
 lda Colors+2,y
 sta VRAM_Buffer1-1,x
 ply
 plx
Done:
 pla
 plp
 rts
Colors:.byte $16,$30,$27,$0f,$36,$17
.endproc
'''
    B.write(p, s)
    # Verify normal palette roles against actual donor-generated PPU memory,
    # not guessed RGBs or an unrelated game's palettes.
    donor = R / 'build/benj-donor-peach-discovery-1030-v3/ppu.bin'
    v = donor.read_bytes()
    assert v[0x3f19:0x3f1c] == bytes.fromhex('163027')
    assert v[0x3f1d:0x3f20] == bytes.fromhex('0f3617')
    for p in [J / 'src/new_roster_dispatch.s', J / 'union.s']:
        s = B.read(p)
        for a, b in [('<X5GetPlayerColors', '<BmColors'), ('>X5GetPlayerColors', '>BmColors'),
                     ('.bank(X5GetPlayerColors)', '.bank(BmColors)')]:
            assert a in s
            s = s.replace(a, b)
        B.write(p, s)
    B.write(J / 'entrypoint.s', B.read(J / 'entrypoint.s') + '\n.export BmColors\n')
    B.write(J / 'union_imports.inc', B.read(J / 'union_imports.inc') + '\n.import BmColors\n')
    p = J / 'src/kamikaze_mario.s'
    s = B.read(p)
    a, b = s.index('.proc KmNextVariant\n'), s.index('.endproc', s.index('.proc KmNextVariant\n'))
    s = s[:a] + '''.proc KmNextVariant
 ldx MarioVariant
 cpx #7
 bcc Valid
 ldx #4
Valid:lda Cycle,x
 sta MarioVariant
 rts
Cycle:.byte 1,5,3,4,0,6,2
 .res 9,$ea
''' + s[b:]
    s = once(s, ' KmMarioName:\n', ''' KmMarioName:
  cmp #5
  bcc OldName
  cmp #7
  bcs Foreign
  pla
  plp
  jmp BmName
OldName:
''')
    s = once(s, 'KmMenuEnd:', '''.proc BmName
 lda MarioVariant
 sec
 sbc #5
 asl
 asl
 asl
 asl
 clc
 adc #<Names
 sta R2
 lda #>Names
 adc #0
 sta R3
 lda #0
 jmp NrQueueSelectName::NamePage
Names:.byte "     TOAD       ","     PEACH      "
.endproc
KmMenuEnd:''')
    B.write(p, s)
    p = J / 'src/full_roster_menu.s'
    s = B.read(p)
    a, b = s.index(' inc MarioVariant\n'), s.index('NotMario:\n', s.index('.proc FmToggle'))
    assert a < b and 'cmp #5' in s[a:b]
    s = s[:a] + ' farcall KmNextVariant\n jmp Yes\n' + s[b:]
    s = once(s, '.res 0,$ea\n.endproc', '.res 2,$ea\n.assert *-FmToggle=278,lderror,"Preserve Select entry span"\n.endproc')
    B.write(p, s)
    recipes = []
    for label in ['main-build', 'union-build']:
        c = [rt(x) for x in json.loads(B.read(P / (label + '.json')))['command']]
        recipes.append((label, c))
    link = [rt(x) for x in json.loads(B.read(P / 'final-link.json'))['command']]
    recipes.append(('final-link', link))
    B.write(O / 'output-preflight.json', json.dumps([dict(step=n, validation=validate(c, J, cwd=R)) for n, c in recipes], indent=2) + '\n')
    for n, c in recipes:
        validate(c, J, cwd=R)
        z = subprocess.run(c, cwd=R, capture_output=True, text=True)
        B.write(O / (n + '.json'), json.dumps(dict(command=c, returncode=z.returncode, stdout=z.stdout, stderr=z.stderr), indent=2) + '\n')
        assert z.returncode == 0, (n, z.stderr)
    from prepare_cv3_dmc_mirror import prepare
    prepare(R, J / 'candidate.nes')
    old, new = [load(p / 'candidate.nes') for p in [P / 'joint', J]]
    for n in ['KmGraphics', 'KmSelect', 'KmPortrait', 'KmCoreEnd', 'KmNextVariant', 'KmQueueName', 'FmToggle', 'FmQueueName']:
        assert address(old, n) == address(new, n), n
    assert new['raw'][:16] == old['raw'][:16] and new['raw'][16 + 128 * 8192:] == old['raw'][16 + 128 * 8192:]
    d = dict(status='PRIVATE_BENJ_MENU_PALETTE_ADMISSION_SOURCE_CONTROLS_PENDING', source=True,
        candidate=B.sha(J / 'candidate.nes'), parent=h['candidate'], joint=str(J), native=False,
        installed=False, enabled_if_qualified=64, cycle=[0,1,5,6,2,3,4],
        source_normal_palette=dict(Toad=[22,48,39], Peach=[15,54,23]),
        partial_behavior='Original float vertical/ground/head-support producer integrated; native SMB enemy/platform contacts retained. Original special float contact consumers deferred.',
        palette_limits='Normal source role rows authenticated; original fire/star/area-specific palette progression not fully qualified.',
        bindings={str(p):B.sha(p) for p in [Path(__file__), P/'source-stage.json', donor,
          J/'candidate.nes', J/'candidate.dbg', J/'candidate.lbl', O/'output-preflight.json']})
    B.write(O / 'source-stage.json', json.dumps(d, indent=2) + '\n')
    print(json.dumps({k:v for k,v in d.items()if k!='bindings'}, indent=2))


if __name__ == '__main__':
    main()
