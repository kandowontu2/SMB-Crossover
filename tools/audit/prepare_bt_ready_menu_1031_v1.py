"""Source-built Battletoads admission experiment; no native/installation claim."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import traceback

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

P = R/'build/m3-cfbt-gfx-layout-v1'
O = R/'build/bt-ready-menu-1031-v1'
J = O/'joint'
EXPECTED = '79634f4581f223293a86d2bae28a0cc8ad05949a24f29695433b806eccf6a4b3'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding='utf-8', newline='\n')


def save(p, q):
    write(p, json.dumps(q, indent=2)+'\n')


def once(s, old, new):
    assert s.count(old) == 1, (old, s.count(old))
    return s.replace(old, new, 1)


MENU_NAME = '''; Real ready BT names. The original16-column field is fully replaced.
.proc BtQueueMenuName
  ldx VRAM_Buffer1_Offset
  lda #$23
  sta VRAM_Buffer1,x
  lda #$28
  sta VRAM_Buffer1+1,x
  lda #16
  sta VRAM_Buffer1+2,x
  lda FmGroups
  and #$20
  lsr
  tay
  lda #16
  sta R0
Copy:
  lda Names,y
  sta VRAM_Buffer1+3,x
  iny
  inx
  dec R0
  bne Copy
  inx
  inx
  inx
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
  rts
Names:
  .byte "      RASH      ","      ZITZ      "
.endproc
'''

STATUS = '''; Genuine status A0 continuation only; no writes on the A1/lives tail.
.export BtStatusName
BtStatusName:
 cmp #0
 bne BtStatusDone
 php
 txa
 pha
 tya
 pha
 ldy #0
 lda FmGroups
 and #$20
 beq BtStatusCopyStart
 ldy #7
BtStatusCopyStart:
 ldx #0
BtStatusCopy:
 lda BtStatusNames,y
 sta VRAM_Buffer1+11,x
 iny
 inx
 cpx #7
 bcc BtStatusCopy
 pla
 tay
 pla
 tax
 plp
 lda #0
BtStatusDone:
 rts
.include "inc/charmap.inc"
BtStatusNames:.byte "   RASH","   ZITZ"
'''


def main():
    assert not O.exists()
    stage = json.loads((P/'source-stage.json').read_text())
    assert stage['passed'] and stage['candidate'] == sha(P/'joint/candidate.nes') == EXPECTED
    for p, h in stage['bindings'].items():
        assert sha(p) == h, p
    O.mkdir()
    try:
        shutil.copytree(P/'joint', J)
        roots = [P/'joint', R/'build/m3-cfbt-source-join-v1/joint',
                 R/'build/bt-native-world-source-v2/joint',
                 R/'build/bt-current-cf-component-v2/joint']

        def rt(s):
            for root in roots:
                s = s.replace(str(root), str(J)).replace(root.as_posix(), J.as_posix())
            return s

        for p in J.rglob('*'):
            if p.is_file() and p.suffix in ['.s', '.inc', '.cfg']:
                write(p, rt(p.read_text(encoding='utf-8')))
        f = J/'src/full_roster_menu.s'
        s = once(f.read_text(), ' lda #9\n cpx #23\n beq Pending',
                 ' lda #9\n cpx #23\n beq Ready')
        write(f, s)
        f = J/'src/character_select.s'
        s = f.read_text()
        s = once(s, '  cmp #28\n  bcc FmNativeOtherPreview\n  farcall FmDrawDkPreview,jmp',
                 '  cmp #28\n  beq FmNativeDkPreview\n  cmp #32\n  bne FmNativeOtherPreview\nFmNativeDkPreview:\n  farcall FmDrawDkPreview,jmp')
        # All expanded paths used160; the original15 compare had no consumer.
        s = once(s, '  lda #152\n.if ::ENABLE_MMC5_EXPANDED\n  lda #160\n  ldx SelectedCharacter\n  cpx #15\n  bne :+\n  lda #160\n:\n.endif\n  sta Player_Y_Position',
                 '.if ::ENABLE_MMC5_EXPANDED\n  lda #160\n.else\n  lda #152\n.endif\n  sta Player_Y_Position')
        s = once(s, '.proc QueueSelectName\n.if ::ENABLE_MMC5_EXPANDED\n  farcall HuMenuName,jmp',
                 '.proc QueueSelectName\n.if ::ENABLE_MMC5_EXPANDED\n  lda SelectedCharacter\n  cmp #33\n  bne Foreign\n  jmp BtQueueMenuName\nForeign:\n  farcall HuMenuName,jmp')
        # Reuse menu-only NOP funding; all real target addresses are relinked.
        s = once(s, '  .res 3,$ea ; Existing21B Start identity block, all later PCs unchanged.\n', '')
        s = once(s, '  .res 9,$ea ; Genuine four-identity M3 cycle within existing span.\n', '')
        s = once(s, '.res $c8c-(*-CrossoverMenuInput),$ff',
                 MENU_NAME+'\n.assert *-CrossoverMenuInput<=$c8c,lderror,"BT menu stays within original PROTO_MENU"\n.res $c8c-(*-CrossoverMenuInput),$ff')
        write(f, s)
        f = J/'bt/api.s'
        s = once(f.read_text(), ' jmp BtUnavailable    ;30 status-name bridge pending',
                 ' jmp BtStatusName     ;30 actual native status continuation')
        s = once(s, '.segment "BT_CACHE_STATE"', STATUS+'\n.segment "BT_CACHE_STATE"')
        write(f, s)
        logs = []

        def run(name, cmd):
            guard = validate(cmd, J, cwd=R)
            z = subprocess.run(cmd, cwd=R, capture_output=True, text=True)
            p = O/(name+'.json')
            save(p, dict(command=cmd, output_guard=guard, returncode=z.returncode, stdout=z.stdout, stderr=z.stderr))
            logs.append(p)
            assert z.returncode == 0, (name, z.stderr)

        main_cmd = [rt(x) for x in json.loads((P/'main-build.json').read_text())['command']]
        run('main-build', main_cmd)
        for name in ['api', 'loader', 'stream']:
            cmd = [str(R/'tools/Windows/cc65/bin/ca65.exe'), '--cpu', '6502x', '-g', '-D', 'MAPPER_MMC5=1',
                   '-I', str(J/'bt'), '-I', str(J), '-I', str(R), '--create-full-dep', str(J/'bt'/(name+'.dep')),
                   '-o', str(J/'bt'/(name+'.o')), str(J/'bt'/(name+'.s'))]
            run(name+'-build', cmd)
        cmd = [rt(x) for x in json.loads((P/'final-link.json').read_text())['command']]
        for i, x in enumerate(cmd):
            p = Path(x)
            if p.suffix == '.o' and p.parent.name == 'bt' and p.stem in ['api', 'loader', 'stream']:
                cmd[i] = str(J/'bt'/p.name)
        run('initial-link', cmd)
        cache = (J/'sideoutputs/candidate/00-cache.bin').read_bytes()
        assert len(cache) == 8192 and cache[0x1fe0:0x1ff0] == bytes(16)
        cookie = bytes([167, 33, 1, 117])+hashlib.sha256(cache).digest()[:12]
        for n in ['cache.bin', 'stream.bin']:
            (J/'bt'/n).write_bytes(cache)
        (J/'bt/cookie.bin').write_bytes(cookie)
        for name in ['loader', 'stream']:
            run(name+'-final-build', json.loads((O/(name+'-build.json')).read_text())['command'])
        run('final-link', cmd)
        prepare(R, J/'candidate.nes')
        old, new = [scoped_load(p/'candidate.nes') for p in [P/'joint', J]]
        assert old['raw'][:16] == new['raw'][:16]
        for n in ['GameLoop', 'BtServiceVeneers', 'BtLoad', 'BtColdPortrait', 'BtColdColors', 'BtHostState', 'CfLoadIfCold', 'CfRetire', 'M3Movement', 'MbChrOffsets']:
            assert (address(old,n),location(old,n)) == (address(new,n),location(new,n)), n
        assert new['raw'][749223:749290] == bytes([234])*67
        for n in ['cf-stream.bin','cf-cookie.bin','bowser.bin','ram3.bin','code.bin','data.bin','ff-cookie.bin']:
            assert sha(J/n) == sha(P/'joint'/n), n
        assert location(new, 'BtStatusName')+70 < 0x1ee0
        paths = [Path(__file__), P/'source-stage.json', J/'candidate.nes', J/'candidate.dbg', J/'candidate.lbl',
                 J/'private.cfg', J/'src/character_select.s', J/'src/full_roster_menu.s', *logs,
                 *[J/'bt'/n for n in ['api.s','api.o','api.dep','loader.s','loader.o','loader.dep','stream.s','stream.o','stream.dep','cache.bin','stream.bin','cookie.bin']]]
        save(O/'source-stage.json', dict(source=True, native=False, installed=False, candidate=sha(J/'candidate.nes'), parent=EXPECTED,
             status='BT_READY_MENU_EXPERIMENT_SOURCE_CONTROLS_NATIVE_PENDING', BT_menu_ready=True, CF_pending=True,
             BT_cookie=cookie.hex(), shared_CF67_still_empty=True, remaining331_M3_bytes_untouched=True,
             changes=['Slot23 ready; Select toggles source Rash/Zitz identity.', 'Only DK/Arthur use the legacy portrait shortcut.',
                      'Full16-column Rash/Zitz menu text and authentic status continuation names.',
                      'Menu-only NOP/redundant Y-coordinate code funding; PROTO_MENU total footprint fixed.'],
             bindings={str(p.resolve()):sha(p) for p in paths}))
        print(json.dumps(dict(source=True, native=False, candidate=sha(J/'candidate.nes'), BT_cookie=cookie.hex(), joint=str(J))))
    except Exception as e:
        save(O/'negative.json', dict(passed=False, error=repr(e), traceback=traceback.format_exc()))
        raise


if __name__ == '__main__':
    main()
