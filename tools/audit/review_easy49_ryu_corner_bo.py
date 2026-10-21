"""Review immutable Ryu E evidence before the combined-layout integration."""
from pathlib import Path
import hashlib, importlib.util, json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
F = V / 'agent-lsr-ryu-corner-head-e'
P = V / 'root49-easy-advanced-union-ap'
H = V / 'root49-ryu-corner-review-bo'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    H.mkdir(exist_ok=False)
    retained_negative = V / 'root49-ryu-corner-review-bn/verifier-negative.json'
    retained_negative.write_text(json.dumps(dict(
        failed_script_sha256=sha(R / 'tools/audit/review_easy49_ryu_corner_bn.py'),
        failure='AssertionError at near PC48377/target40449: verifier required caller bank for a legal resident LOWCODE target.',
        correction='BO admits actual compiled LOWCODE/FIXED segments in their resident CPU slots; every opcode/operand and all other packet checks remain unchanged.',
        native_runtime_changed=False), indent=2) + '\n')
    pins = {
        F / 'implementation-freeze.json': 'ac4095308afe1256e708254a2b68423795e889b916b4d89c24fba41b23402878',
        F / 'review.json': '0770465ec0a3a9405c8e14b140dfc5866f8e23ea9b17d98f3dae1b988349e348',
        F / 'ordinary-review.json': '135738467265c5cad6b646c1f61208086415b1dc6e4a43473b7fb3f7be7e8fc3',
        F / 'provenance-addendum/receipt.json': '81b2f04dd11c70f24697a7011547b9dfcee24f0b1d832b4e541ae1282bffaee7',
        P / 'report.json': 'e1215e073905879a580fea13dfe55dad26d9fe11a0595bbe7fbfdf915a822b6e',
    }
    for path, digest in pins.items():
        assert sha(path) == digest, path
    frozen = json.loads((F / 'implementation-freeze.json').read_text())
    assert all(sha(F / n) == h for n, h in frozen['files'].items())
    receipts = json.loads((F / 'receipt-hashes.json').read_text())
    assert all(sha(F / n) == h for n, h in receipts.items())
    parent = json.loads((P / 'report.json').read_text())['source_hashes']
    after = json.loads((F / 'source-catalog.json').read_text())
    assert len(parent) == 428 and len(after) == 429
    assert all(sha(P / 'source' / n) == h for n, h in parent.items())
    assert all(sha(F / 'source' / n) == h for n, h in after.items())
    review = json.loads((F / 'review.json').read_text())
    changes = sorted(n for n, h in after.items() if parent.get(n) != h)
    assert changes == sorted(review['changed_parent_files'] + review['new_files'])
    for n in changes:
        assert sha(F / 'overlay' / n) == after[n] == frozen['overlay_after_sha256'][n]
    assert set(review['raw_parent_sha256']) == set(changes)
    assert all(parent.get(n) == h for n, h in review['raw_parent_sha256'].items())
    provenance = json.loads((F / 'provenance-addendum/receipt.json').read_text())
    old_core = F / 'provenance-addendum' / provenance['retained_source_path']
    assert sha(old_core) == provenance['recovered_original_core_sha256']
    for name, digest in provenance['bindings'].items():
        path = R / name
        assert sha(path) == digest
        binding = json.loads(path.read_text())
        assert provenance['recovered_original_core_sha256'] in json.dumps(binding)
    spec = importlib.util.spec_from_file_location('ryu_bn_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = []
    for mapper in ['mmc3', 'mmc5']:
        old = module.Image(P / 'source/build' / ('smb-crossover-' + mapper + '.nes'))
        new = module.Image(F / 'source/build' / ('smb-crossover-' + mapper + '.nes'))
        assert sha(new.path) == frozen['ROMs'][mapper]
        assert new.ram == old.ram and len(new.raw) == len(old.raw)
        assert new.raw[:16] == old.raw[:16] and new.raw[524304:] == old.raw[524304:]
        originals = {x['name']: x for x in old.segs.values()}
        current = {x['name']: x for x in new.segs.values()}
        deltas = {name: current[name]['size'] - item['size'] for name, item in originals.items()
                  if current[name]['size'] != item['size']}
        assert deltas == {'ROSTER': 23}
        assert set(current) - set(originals) == {'RYU_COLD'}
        cold = current['RYU_COLD']
        assert cold['size'] == 497 and (cold['ooffs'] - 16) // 8192 == 25
        assert old.raw[cold['ooffs']:cold['ooffs'] + 497] == bytes([255]) * 497
        audio = {}
        for name, item in originals.items():
            if item.get('type') != 'ro' or not ('AUDIO' in name or 'DPCM' in name):
                continue
            now = current[name]
            assert all(now[k] == item[k] for k in ['start', 'size', 'ooffs'])
            assert new.raw[now['ooffs']:now['ooffs'] + now['size']] == old.raw[item['ooffs']:item['ooffs'] + item['size']]
            audio[name] = item['size']
        # Independently check the compiled local control references reported by
        # the packet. The only out-of-ROM call is the mapper's known RAM bridge.
        compiled = next(x for x in review['builds'] if x['mapper'] == mapper)
        checked = 0
        for scope in compiled['closure']:
            bank = scope['physical_bank']
            for ref in scope['near_references']:
                pc = int(ref['PC'], 16)
                opcode = int(ref['opcode'], 16)
                target = int(ref['target'], 16)
                segments = [s for s in new.segs.values() if s.get('type') == 'ro'
                            and s['start'] <= pc < s['start'] + s['size']
                            and (s['ooffs'] + pc - s['start'] - 16) // 8192 == bank]
                assert len(segments) == 1, (scope['name'], pc, bank)
                segment = segments[0]
                off = segment['ooffs'] + pc - segment['start']
                assert new.raw[off] == opcode and int.from_bytes(new.raw[off + 1:off + 3], 'little') == target
                if target >= 32768:
                    resident = any(s['name'] in ['LOWCODE', 'FIXED']
                                   and s['start'] <= target < s['start'] + s['size']
                                   and (s['ooffs'] + target - s['start'] - 16) // 8192 in ref['label_target_physical_banks']
                                   for s in new.segs.values())
                    assert bank in ref['label_target_physical_banks'] or resident, (pc, target)
                else:
                    assert ref['FarCallCommon_RAM']
                checked += 1
        rows.append(dict(mapper=mapper, ROM_sha256=sha(new.path), RAM_header_CHR_size_exact=True,
                         old_RO_audio_addresses_bytes_exact=audio, segment_deltas=deltas,
                         RYU_COLD_bytes=497, physical_bank=25, cold_occupies_old_FF_only=True,
                         actual_compiled_near_references_checked=checked))
    ordinary = json.loads((F / 'ordinary-review.json').read_text())
    assert ordinary['results']['discovery'] == ordinary['results']['fixed']
    assert ordinary['results']['fixed']['frames'] == 9787 and ordinary['results']['fixed']['failure'] == 'death'
    assert len(ordinary['nine_streams']) == 9 and all(x['literal'] for x in ordinary['nine_streams'].values())
    report = dict(status='REVIEWED_FROZEN_SCOPED_RYU_E_FOR_COMBINED_INTEGRATION',
                  script_sha256=sha(__file__), source_files_checked=429, frozen_packet_files_checked=len(frozen['files']),
                  native_receipt_files_checked=len(receipts), source_changes=changes, builds=rows,
                  native_evidence='168 unique candidate controls plus452 inherited cases pass. Repeated168 nativeVY checks are not additional unique arenas. Old AP control92 assertions/map includes15 setup and15 helper-coverage assertions.',
                  ordinary='Live/fixed native negative9787 and all9 CSVs exact; incident9760 source response proved. Not a completed route.',
                  qualifications=review['qualifications'],
                  next='Merge after BILL_COLD in final shared bank25, rebind actual physical sites and run integration checks; adapt ordinary Ryu controls.',
                  references=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p)) for p in pins],
                  BN_host_negative_sha256=sha(retained_negative),
                  main_changed=False, accepted_release=False, goal_complete=False)
    target = H / 'report.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(target), flush=True)


if __name__ == '__main__':
    main()
