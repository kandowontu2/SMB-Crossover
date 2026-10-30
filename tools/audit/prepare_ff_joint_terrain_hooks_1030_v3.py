"""Install genuine FF foot/wall selectors; expose post-BG API to common owner.

This is a source successor of frozen07cda, not a release or a readiness claim.
Resident ABI/PCs stay fixed. The foot worker publishes its own selected A before
any consumer, recovering three resident bytes without discarding live state.
"""
from pathlib import Path
import difflib, json, sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
import prepare_ff_joint_source_v1 as B
from prepare_ff_current_component_v2 import qualified
from finalize_ff_current_component_v3 import dependencies
from check_tmnt_render_oa import address, location
from prepare_cv3_dmc_mirror import prepare

P = R / 'build/ff-joint-full-render-v2'
O = R / 'build/ff-joint-terrain-hooks-1030-v3'
H = R / 'build/ff-joint-full-render-qualified-v1/handoff.json'


def replace(s, old, new):
    assert s.count(old) == 1, old
    return s.replace(old, new)


def main():
    assert not O.exists()
    files = B.validate(H, '33da4500485b1c1ebcf0613c95a01484740aec74f6267f87e0d07f3c2b66aa71')
    old = qualified(P / 'joint/candidate.nes')
    assert B.sha(P / 'joint/candidate.nes') == '07cda1d4b0812717334dc15e886f56474953e30b2cb2f6ddc5ecfd5ace52ea13'
    O.mkdir()
    d = O / 'joint'
    d.mkdir()
    for p in (P / 'joint').rglob('*'):
        if p.is_file() and p.suffix in ['.s', '.inc', '.cfg', '.bin', '.chr']:
            q = d / p.relative_to(P / 'joint')
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_bytes(p.read_bytes())
    changed = []

    def edit(rel, function):
        p = d / rel
        previous = p.read_text()
        current = function(previous)
        assert current != previous
        B.write(p, current)
        changed.append(rel)

    def feet(s):
        s = replace(s, '  cmp #CHARACTER_LINK\n  bcc FootNative\n  beq FootCold',
                    '  cmp #CHARACTER_LINK\n  beq FootCold')
        s = replace(s, '  cmp #26\n  beq FootCold\n  cmp #CHARACTER_DONKEY_KONG',
                    '  cmp #22\n  beq FootCold\n  cmp #26\n  beq FootCold\n  cmp #CHARACTER_DONKEY_KONG')
        s = replace(s, '  farcall DkHostFeetUnionRouter,jmp', '''  ; DkHostFeetUnionRouter first loads SelectedCharacter and publishes it.
  ; Incoming A/NZ die before use; its publication preserves the old SMC value.
  lda #<DkHostFeetUnionRouter
  sta FarcallJmpTarget_SMC+1
  lda #>DkHostFeetUnionRouter
  sta FarcallJmpTarget_SMC+2
  lda #.lobyte(.bank(DkHostFeetUnionRouter)|$80)
  jmp FarCallCommon''')
        return replace(s, '  .res 0,$ea\n  .assert *-CrossoverHeadProbe=63',
                       '  .res 1,$ea\n  .assert *-CrossoverHeadProbe=63')

    edit('src/characters.s', feet)

    def worker(s):
        s = replace(s, '.proc DkHostFeetUnionRouter\n lda SelectedCharacter\n cmp #26', '''.proc DkHostFeetUnionRouter
 lda SelectedCharacter
 sta SafecallA_SMC+1
 cmp #22
 beq FinalFantasy
 cmp #26''')
        s = replace(s, ' .assert *-DkHostFeetUnionRouter=33,error,"Existing DK host headroom33B"',
                    ' .assert *-DkHostFeetUnionRouter=40,error,"Own DK foot router40B"')
        # Keep the new cold call after the existing flag worker. Only that
        # own private worker moves; every call is reassembled from its symbol.
        return replace(s, '.assert *<=$c000,lderror,"Existing DK host1024B cap"', '''FinalFantasy:
 farcall FwSvcFeet,jmp
.assert *<=$c000,lderror,"Existing DK host1024B cap"''').replace(' beq FinalFantasy\n', ' beq ::DkFeetFinalFantasy\n').replace('FinalFantasy:\n farcall', '::DkFeetFinalFantasy:\n farcall')

    edit('src/donkey_kong_host.s', worker)
    edit('dk-component.s', lambda s: '.import FwSvcFeet\n' + s)

    def services(s):
        s = '.import FwHostFeet,FwHostWall,FwHostAfterTerrain\n.import BlockBufferColli_Feet,LmWallGate,HuLegacyPostBG\n.export FwSvcFeet,FwSvcWall,FwSvcAfterTerrain\n' + s
        return replace(s, 'FwSvcEnd:', '''; Native wall Guest entry already admitted engine8. Inactive/foreign calls
; retain the original LmWallGate, including all Mac/Link/RCR handling.
FWS_TYPED FwSvcFeet,FwHostFeet,BlockBufferColli_Feet
FWS_TYPED FwSvcWall,FwHostWall,LmWallGate
; Common owner installs this at the genuine post-terrain entry separately.
FWS_TYPED FwSvcAfterTerrain,FwHostAfterTerrain,HuLegacyPostBG
FwSvcEnd:''')

    edit('typed-services.s', services)
    edit('src/samus.s', lambda s: replace(s, '    farcall LmWallGate,jmp', '    farcall FwSvcWall,jmp'))
    edit('entrypoint.s', lambda s: '.import FwSvcWall\n.export LmWallGate\n' + s)
    edit('private.cfg', lambda s: replace(s, (P / 'joint/ram3.bin').as_posix(), (d / 'ram3.bin').as_posix()))

    before, after = str(P / 'joint'), str(d)
    for phase in sorted((P / 'joint').glob('*-build.json')):
        cmd = json.loads(phase.read_text())['command']
        B.run(d, [v.replace(before, after) for v in cmd], phase.stem)
    cmd = [v.replace(before, after) for v in json.loads((P / 'joint/final-link.json').read_text())['command']]
    B.run(d, cmd, 'final-link')
    prepare(R, d / 'candidate.nes')
    new = qualified(d / 'candidate.nes')
    assert (d / 'ram3.bin').read_bytes() == (P / 'joint/ram3.bin').read_bytes()
    allowed = []
    # FIXED is mirrored into bank126 and bank124 in this source cartridge.
    # Bind every actual mirror by exact old63B preimage; no assumed bank count.
    p = location(old, 'CrossoverHeadProbe')
    capsule = old['raw'][p:p + 63]
    mirrors = [i for i in range(16, 16 + 1048576) if old['raw'][i:i + 63] == capsule]
    assert mirrors and p in mirrors and len(mirrors) <= 4, mirrors
    allowed += [(i, i + 63, 'resident63B') for i in mirrors]
    p = location(old, 'SamusStopAtWall')
    # Native wall's exact source span ends at the next published bridge.
    z = p + address(old, 'SamusAfterBGCollisionBridge') - address(old, 'SamusStopAtWall')
    wall = old['raw'][p:z]
    wm = [i for i in range(16, 16 + 1048576) if old['raw'][i:i + len(wall)] == wall]
    assert wm and p in wm and len(wm) <= 4
    allowed += [(i, i + len(wall), 'wall_operand_only') for i in wm]
    allowed += [(location(old, 'DkHostFeetUnionRouter'), 16 + 66 * 8192, 'own_DK_tail'),
                (location(old, 'FwSvcEnd'), 16 + 62 * 8192 + 0x1690, 'own_FF_typed_tail')]
    # Rebind only the genuine existing own near JMP to the moved flag worker.
    p = location(old, 'DkHostSide')
    assert old['raw'][p] == new['raw'][p] == 0x4c
    assert int.from_bytes(old['raw'][p+1:p+3], 'little') == address(old, 'DkFlagSideGate')
    assert int.from_bytes(new['raw'][p+1:p+3], 'little') == address(new, 'DkFlagSideGate')
    allowed.append((p+1, p+3, 'own_DK_flag_JMP_operand'))
    diffs = [i for i, (a, b) in enumerate(zip(old['raw'], new['raw'])) if a != b]
    outside = [i for i in diffs if not any(a <= i < z for a, z, _ in allowed)]
    assert not outside, outside[:24]
    moved = {n: [s['val'], new['syms'].get(n, {}).get('val')]
             for n, s in old['syms'].items() if 'seg' in s and '::' not in n
             and new['syms'].get(n, {}).get('val') != s['val']}
    assert set(moved) == {'DkFlagSideGate', 'FwSvcEnd'}, moved
    assert address(new, 'DkFlagSideGate') - address(old, 'DkFlagSideGate') == 7
    assert address(new, 'FwSvcEnd') <= 0xb690
    patch = ''.join(''.join(difflib.unified_diff((P / 'joint' / rel).read_text().splitlines(True),
                       (d / rel).read_text().splitlines(True), fromfile=rel, tofile=rel)) for rel in changed)
    B.write(O / 'source-hooks.patch', patch)
    for dep in d.rglob('*.dep'):
        files.update(dependencies(dep))
    files.update(p for p in O.rglob('*') if p.is_file())
    files.update(Path(v) for v in cmd if v.endswith('.o'))
    files.add(Path(__file__))
    B.save(O / 'source-closure.json', dict(passed=True, native=False, admitted=False,
        candidate_sha256=B.sha(d / 'candidate.nes'), parent_sha256=B.sha(P / 'joint/candidate.nes'),
        changed_bytes=len(diffs), source_files=changed, own_public_entries_moved=moved,
        allowed_ranges=allowed, actual_foot_and_wall_selectors=True,
        after_terrain_API='FwSvcAfterTerrain (common hook not installed in this packet)',
        RAM3_cookie_payload_exact=True, A79_and_other_CHR_exact=True,
        limits=['CPU/state/ISR controls pending; no native/readiness claim.',
                'AfterTerrain common entry, flash/NewEnemy, palettes and audio remain separate integrations.'],
        bindings={str(p.resolve()): B.sha(p) for p in sorted(files)}))
    print('FF TERRAIN HOOKS', B.sha(d / 'candidate.nes'), flush=True)


if __name__ == '__main__':
    main()
