"""Stage a same-address Proto injury recovery repair from accepted OE sources."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / 'build/checkpoints/tmnt-hud-probes-oe'
OUT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-proto-hurt-of')


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--label', required=True); a = p.parse_args()
    assert a.label and all(c.isalnum() or c in '-_' for c in a.label)
    out = OUT / a.label; out.mkdir(parents=True, exist_ok=False)
    m = json.loads((PARENT / 'manifest.json').read_text())
    assert sha(PARENT / 'source.zip') == m['source_zip_sha256']
    source = out / 'source'
    with zipfile.ZipFile(PARENT / 'source.zip') as z:
        assert z.testzip() is None
        assert all((source / n).resolve().is_relative_to(source.resolve()) for n in z.namelist())
        z.extractall(source)
    assert all(sha(source / n) == h for n, h in m['source_files'].items())
    changed = {}
    def edit(name, before, after):
        path = source / name; text = path.read_text(); assert text.count(before) == 1
        digest = sha(path); path.write_text(text.replace(before, after))
        changed[name] = dict(before=changed.get(name,{}).get('before',digest), after=sha(path))
    path=source/'src/megaman_injury.s';text=path.read_text()
    start=text.index('.proc MegaManHurtEnd\n');end=text.index('.endproc',start)
    original=text[start:end]
    wrapper='''.proc MegaManHurtEnd
.if ::ENABLE_MMC5_EXPANDED
  farcall ProtoHurtEndCore
  jmp MegaManHurtReturned
::MmRecoveryDrawGate:
  lda PlayerChrBank
  sec
  sbc #MM_HURT_BODY_BANK
  lsr
  bne RecoveryDrawReturn
  farcall ProtoRecoveryDrawCore
RecoveryDrawReturn:
  plp
Done:
  lda #0
  rts
  .assert *-MegaManHurtEnd=52,error,"Keep original recovery span/Done label"
.else
'''+original.split('\n',1)[1]+'.endif\n'
    edit('src/megaman_injury.s',original,wrapper)
    edit('src/megaman_injury.s', '.proc MegaManHurtDraw\n  lda GuestHurtTicks\n  jeq Done\n',
         '.proc MegaManHurtDraw\n  lda GuestHurtTicks\n.if ::ENABLE_MMC5_EXPANDED\n::MmRecoveryDrawBranch:\n  php\n  beq MmRecoveryDrawGate\n  plp\n  nop\n.else\n  jeq Done\n.endif\n')
    path = source / 'src/protoman_hurt_end.s'; assert not path.exists()
    path.write_text((ROOT / 'tools/reference/proto_hurt_end_of.s').read_text())
    changed['src/protoman_hurt_end.s'] = dict(before=None, after=sha(path))
    edit('src/entrypoint.s', '\n.include "mac_visible_side.s"\n',
         '\n.include "mac_visible_side.s"\n.include "protoman_hurt_end.s"\n')
    edit('smb1base-mmc5-expanded.cfg', '    PROTO_MENU: load=X5_NEW_42,type=ro;\n',
         '    PROTO_MENU: load=X5_NEW_42,type=ro;\n    PROTO_HURT_END: load=X5_NEW_42,type=ro;\n')
    result = subprocess.run([sys.executable, str(source / 'tools/build_mmc5_expanded.py'),
        '--workspace', str(source), '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
        '--output', str(out / 'candidate.nes')], cwd=source, capture_output=True, text=True)
    (out / 'build.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, (result.stdout + result.stderr)[-3000:]
    old = (PARENT / 'candidate.nes').read_bytes(); new = (out / 'candidate.nes').read_bytes()
    banks = [b for b in range(128) if old[16+b*8192:16+(b+1)*8192] != new[16+b*8192:16+(b+1)*8192]]
    assert banks == [10, 66] and old[16+1048576:] == new[16+1048576:]
    q = dict(passed=True, ROM_sha256=sha(out / 'candidate.nes'), parent_ROM_sha256=m['rom_sha256'],
             source_changes=changed, changed_PRG_banks=banks, CHR_unchanged=True,
             live_source_unchanged=True, scope='Staged only. CPU/interrupt/native reproduction and fresh route acceptance pending.')
    (out / 'preparation.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q, indent=2))


if __name__ == '__main__': main()
