"""Remove only the held shot experiment from two frozen menu prototypes."""
from pathlib import Path
import argparse, difflib, hashlib, json, shutil, subprocess, sys, traceback
from check_tmnt_audio_fallback_oc import qualified
from link_pit_rygar_sophia_audit_cpu import scoped_load

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
ORIGINAL = D / 'current3cee-postdma-mask-v1/canonical-v2'
PUBLISHED = D / 'root-chip-hud-composed-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, data):
    Path(p).write_text(json.dumps(data, indent=2) + '\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True, exist_ok=False)
    original = ORIGINAL / 'source/src/protoman_legacy_shots.inc'
    original_hash = 'ad0241e8872468679f0cb33b7aa4c179e1bd185a3ae45905633f6d304027a73e'
    assert sha(original) == sha(PUBLISHED / 'source/src/protoman_legacy_shots.inc') == sha(R / 'src/protoman_legacy_shots.inc') == original_hash
    variants = [
        ('clean-menu', D / 'parodius-menu-budget-candidate-v5', 'c9b1e0c10698cee3b86c153cc27c0748b28ebe83b1df714fce4235ea4503807f'),
        ('clean-menu-irq', D / 'root-postdma-irq-arm-v3', '59a6088e2449401bc1ca47bffc15914ea79af5b36b0544a5f875bc43ff1d4ac6'),
    ]
    results = []
    try:
        for name, parent, expected_parent in variants:
            assert sha(parent / 'candidate.nes') == expected_parent
            manifest = json.loads((parent / 'source-manifest.json').read_text())
            out = a.output / name
            out.mkdir()
            source = out / 'source'
            for rel, expected in manifest.items():
                old, dest = parent / 'source' / rel, source / rel
                assert sha(old) == expected, rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(old, dest)
            shutil.copyfile(original, source / 'src/protoman_legacy_shots.inc')
            cfg = source / 'smb1base-mmc5-expanded.cfg'
            raw = cfg.read_bytes()
            newline = b'\r\n' if b'\r\n' in raw else b'\n'
            remove = b'    MM_PROTO_SHOT_MUX: load=X5_NEW_42,type=ro,start=$b9a8;' + newline
            assert raw.count(remove) == 1
            assert raw.count(b'    MENU_VRAM_BUDGET: load=X5_NEW_42,type=ro,start=$bb50,optional=yes;') == 1
            cfg.write_bytes(raw.replace(remove, b''))
            assert b'MM_PROTO_SHOT_MUX' not in cfg.read_bytes()
            changed = [rel for rel, expected in manifest.items() if sha(source / rel) != expected]
            assert sorted(changed) == ['smb1base-mmc5-expanded.cfg', 'src/protoman_legacy_shots.inc']
            put(out / 'source-manifest.json', {rel: sha(source / rel) for rel in manifest})
            patch = []
            for rel in sorted(changed):
                patch.extend(difflib.unified_diff((parent / 'source' / rel).read_text().splitlines(True),
                                                (source / rel).read_text().splitlines(True), fromfile='prototype/' + rel, tofile='clean/' + rel))
            (out / 'source.patch').write_text(''.join(patch))
            builds = []
            for mode in ['candidate', 'canonical', 'ordinary-mmc3', 'ordinary-mmc5']:
                command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'),
                           '--workspace', str(source), '--compiler', str(R / 'tools/Windows/cc65/bin/cl65.exe'),
                           '--output', str(out / (mode + '.nes'))]
                if mode.startswith('ordinary-'):
                    command += ['--flag-off', mode.split('-')[1]]
                z = subprocess.run(command, cwd=source, capture_output=True, text=True)
                put(out / (mode + '.launch.json'), dict(command=command, exit=z.returncode, stdout=z.stdout, stderr=z.stderr))
                assert z.returncode == 0, z.stdout + z.stderr
                expected = sha(out / 'candidate.nes') if mode in ['candidate','canonical'] else {
                    'ordinary-mmc3': 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb',
                    'ordinary-mmc5': 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833',
                }[mode]
                assert sha(out / (mode + '.nes')) == expected
                builds.append(dict(mode=mode, ROM_sha256=expected))
                if mode == 'candidate':
                    print(json.dumps(dict(variant=name, candidate_built=True, ROM_sha256=expected, qualification_complete=False)), flush=True)
            old, new = [scoped_load(q / 'candidate.nes') for q in [parent, out]]
            assert old['raw'][:16] == new['raw'][:16]
            assert old['raw'][16+128*8192:] == new['raw'][16+128*8192:]
            deltas = {}
            offsets = []
            for bank in range(128):
                left = old['raw'][16+bank*8192:16+(bank+1)*8192]
                right = new['raw'][16+bank*8192:16+(bank+1)*8192]
                count = sum(x != y for x,y in zip(left,right))
                if count:
                    deltas[bank] = count
                    offsets += [dict(bank=bank, offset=i, old=x, new=y) for i,(x,y) in enumerate(zip(left,right)) if x != y]
            assert deltas == {66:144}, deltas
            new_bank66 = new['raw'][16+66*8192:16+67*8192]
            original_bank66 = ORIGINAL.joinpath('candidate.nes').read_bytes()[16+66*8192:16+67*8192]
            assert new_bank66[0x3ea:0x3ed] == original_bank66[0x3ea:0x3ed] == bytes([0xbd,0x3b,0x60])
            assert new_bank66[0x19a8:0x1a35] == b'\xff'*141
            assert old['raw'][16+66*8192+0x1b50:16+67*8192] == new_bank66[0x1b50:]
            oq, nq = qualified(parent / 'candidate.nes'), qualified(out / 'candidate.nes')
            removed = {n:v for n,v in oq.items() if n not in nq}
            assert removed and all(n[0] == 'MmProtoShotMuxAdmission' for n in removed), removed
            moved = [(n,v,nq.get(n)) for n,v in oq.items() if n not in removed and nq.get(n) != v]
            assert not moved, moved[:15]
            assert all('MmProtoShotMuxAdmission' not in n for n in nq)
            put(out / 'removed-genuine-private-symbols.json', [dict(qualified_name=list(n), former_address=v) for n,v in sorted(removed.items())])
            put(out / 'exact-ROM-deltas.json', offsets)
            result = dict(passed=True,source_only=True,native_run=False,installed=False,
                parent_ROM_sha256=expected_parent,ROM_sha256=sha(out/'candidate.nes'),changed_source=changed,
                restored_original_source_sha256=original_hash,original_900_published3cee_and_default_source_exact=True,
                changed_PRG_bytes=deltas,header_CHR_RAM_other_PRG_and_all_retained_qualified_symbols_exact=True,
                retained_qualified_symbols=len(oq)-len(removed),removed_genuine_private_symbols=len(removed),
                MM_private_symbols_removed_without_aliases=True,BB50_menu_helper_bytes_and_declaration_pinned=True,
                original_ordinary_shots_reinstated=True,helper141bytes_restored_FF=True,builds=builds,
                source_manifest_sha256=sha(out/'source-manifest.json'),patch_sha256=sha(out/'source.patch'),
                tool_sha256=sha(__file__),limits='Clean build/layout only. Prior c9/59 menu/IRQ controls are not retagged; fresh exact-clean-pair CPU and native qualification remain separate. Experimental shot budget/fairness helper is absent; original shot visibility issue remains open.')
            put(out / 'proof.json', result)
            results.append(result)
            print(json.dumps(dict(variant=name,qualified=True,ROM_sha256=result['ROM_sha256'],retained_symbols=result['retained_qualified_symbols'],removed_private_symbols=len(removed))), flush=True)
        # The clean variants retain exactly the same IRQ-only relationship.
        a0,a1 = [a.output / x[0] / 'candidate.nes' for x in variants]
        d = {}
        for i,(x,y) in enumerate(zip(a0.read_bytes(),a1.read_bytes())):
            if x != y:
                bank=(i-16)//8192;d[bank]=d.get(bank,0)+1
        assert d == {125:30,127:30}, d
        put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,installed=False,
            variants=results,clean_pair_IRQ_only_delta=d,production_or_Git_or_settings_changes=False,tool_sha256=sha(__file__)))
    except BaseException as ex:
        put(a.output/'failure.json',dict(passed=False,native_run=False,error=repr(ex),traceback=traceback.format_exc(),completed_variants=results))
        (a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes())
        raise


if __name__ == '__main__':
    main()
