"""Inventory the exact local SMB2J disk and its unmodified source rebuild."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

R = Path(__file__).resolve().parents[2]
S = R / 'build/smb2j-original-source-1031-v1'
O = R / 'build/smb2j-campaign-audit-1031-v1'
DONOR = Path('C:/NES/fds/Super Mario Bros. 2 (Japan) (En).fds')
EXPECTED = 'ff8afb9ae6b705b4e51dbcb193dcebadf4c049800a71003d3a45052648e52eda'
COMMIT = '9c40114626ecd07f13e16d5e67e217b98482d7af'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest = lambda b: hashlib.sha256(b).hexdigest()


def save(name, data):
    (O / name).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')


def disk_files(raw):
    assert len(raw) == 65500 and raw.startswith(b'\x01*NINTENDO-HVC*\x01')
    assert raw[56] == 2 and raw[57] == 8
    cursor, files = 58, {}
    for i in range(8):
        assert raw[cursor] == 3 and raw[cursor + 1] == i
        name = raw[cursor + 3:cursor + 11].decode('ascii').rstrip()
        address = int.from_bytes(raw[cursor + 11:cursor + 13], 'little')
        length = int.from_bytes(raw[cursor + 13:cursor + 15], 'little')
        kind = raw[cursor + 15]
        assert raw[cursor + 16] == 4
        offset = cursor + 17
        files[name] = dict(name=name, file_id=raw[cursor + 2], load=address,
                           bytes=length, type=kind, disk_offset=offset,
                           sha256=digest(raw[offset:offset + length]),
                           payload=raw[offset:offset + length])
        cursor = offset + length
    assert set(raw[cursor:]) <= {0}
    return files


def symbols():
    scopes, syms = {}, []
    for line in (S / 'original/original.dbg').read_text().splitlines():
        if '\t' not in line:
            continue
        kind, text = line.split('\t', 1)
        fields = {k: v.strip('"') for k, v in re.findall(r'(\w+)=("[^"]*"|[^,]+)', text)}
        if kind == 'scope':
            scopes[fields['id']] = fields.get('name', '')
        if kind == 'sym' and fields.get('type') == 'lab' and 'val' in fields:
            syms.append(fields)
    result = {}
    for sym in syms:
        scope = scopes.get(sym.get('scope'), '')
        if scope.startswith('FILE_SM2'):
            result.setdefault(scope[5:], {})[sym['name']] = int(sym['val'], 0)
    return result


def main():
    assert not O.exists()
    O.mkdir()
    assert sha(DONOR) == sha(S / 'original/original.fds') == EXPECTED
    actual = subprocess.check_output(['git', '-C', str(S / 'upstream'), 'rev-parse', 'HEAD'], text=True).strip()
    assert actual == COMMIT
    files, sym = disk_files(DONOR.read_bytes()), symbols()
    for name in ['sm2main.asm', 'sm2data2.asm', 'sm2data3.asm', 'sm2data4.asm', 'fdswrap.asm']:
        assert sha(S / 'original' / name) == sha(S / 'upstream' / name)
    profiles = [
        ('worlds1-4', ['SM2MAIN'], 'SM2MAIN', list(range(4)), ['1', '2', '3', '4']),
        ('worlds5-8', ['SM2MAIN', 'SM2DATA2'], 'SM2MAIN', list(range(4, 8)), ['5', '6', '7', '8']),
        ('world9', ['SM2MAIN', 'SM2DATA2', 'SM2DATA3'], 'SM2MAIN', [8], ['9']),
        ('worldsA-D', ['SM2MAIN', 'SM2DATA4'], 'SM2DATA4', list(range(4)), ['A', 'B', 'C', 'D']),
    ]
    route_rows, profile_rows = [], []
    for profile, chain, tables, indices, worlds in profiles:
        image = bytearray(65536)
        for name in chain:
            f = files[name]
            image[f['load']:f['load'] + f['bytes']] = f['payload']
        labels = sym[tables]

        def owner(address):
            return next(name for name in reversed(chain)
                        if files[name]['load'] <= address < files[name]['load'] + files[name]['bytes'])

        def named(address, prefix):
            source = owner(address)
            names = sorted(n for n, a in sym[source].items() if a == address and n.startswith(prefix))
            return dict(address=address, source=source, labels=names)

        def stream(address, enemy):
            cursor, records = address + (0 if enemy else 2), []
            while image[cursor] != (255 if enemy else 253):
                size = 3 if enemy and image[cursor] & 15 == 14 else 2
                records.append(bytes(image[cursor:cursor + size]))
                cursor += size
                assert cursor - address < 2048, (profile, address)
            raw = bytes(image[address:cursor + 1])
            return dict(bytes=len(raw), sha256=digest(raw), records=len(records),
                        area_links=[list(r) for r in records if len(r) == 3] if enemy else [],
                        header=list(raw[:2]) if not enemy else [])

        area_base, world_base = labels['AreaAddrOffsets'], labels['WorldAddrOffsets']
        for index, world in zip(indices, worlds):
            offset = image[world_base + index]
            stop = image[world_base + index + 1] if index < (3 if tables == 'SM2DATA4' else 8) else (18 if tables == 'SM2DATA4' else 40)
            assert 4 <= stop - offset <= 5, (profile, world, offset, stop)
            for area in range(stop - offset):
                pointer = image[area_base + offset + area]
                kind, number = (pointer >> 5) & 3, pointer & 31
                pointers = []
                for table, offsets, prefix in [('EnemyDataAddrs', 'EnemyAddrHOffsets', 'E_'),
                                                ('AreaDataAddrs', 'AreaDataHOffsets', 'L_')]:
                    slot = image[labels[offsets] + kind] + number
                    at = labels[table] + slot * 2
                    address = int.from_bytes(image[at:at + 2], 'little')
                    named_ptr = named(address, prefix)
                    assert named_ptr['labels'], (profile, world, area, named_ptr)
                    named_ptr.update(stream(address, prefix == 'E_'))
                    pointers.append(named_ptr)
                route_rows.append(dict(profile=profile, world=world, native_world=index,
                                       hard_world=tables == 'SM2DATA4', area=area,
                                       area_pointer=pointer, area_type=kind,
                                       enemy=pointers[0], terrain=pointers[1]))
        profile_rows.append(dict(profile=profile, original_load_order=chain,
                                 original_tables=tables, active_image_sha256=digest(image)))
    assert len(route_rows) == 58
    # FDS files contain distinct world overlays. World9 intentionally retains
    # DATA2 bytes below C5D0; treating the disk as one flat PRG loses these.
    inputs = [Path(__file__), DONOR, S / 'original/original.fds', S / 'original/original.dbg',
              S / 'original/original.lbl', S / 'assemble.json', S / 'link.json']
    inputs += [p for p in (S / 'original').iterdir() if p.suffix.lower() in ['.asm', '.chr']]
    inputs += [R / 'build/bt-p2-cf-menu-source-1031-v2/main-build.json',
               R / 'build/contra-force-world-chr-publisher-1031-v1/joint/candidate.nes']
    source = dict(passed=True, source_only=True, installed=False, campaign_implemented=False,
                  donor_sha256=EXPECTED, assembled_disk_byte_exact=True, compared_bytes=65500,
                  upstream='https://github.com/threecreepio/smb2j-disassembly', upstream_commit=COMMIT,
                  source_credit='doppelganger; ca65 adaptation by threecreepio',
                  disk_files=[{k: v for k, v in f.items() if k != 'payload'} for f in files.values()],
                  profiles=profile_rows, world_count=13, numbered_levels=52,
                  ordered_world_area_entries_including_pipe_intros=58, routes=route_rows,
                  current_host_SMB2J_feature_flag=0,
                  original_world9_retains_DATA2_prefix=True,
                  coverage='Exact source reconstruction and table/stream inventory only; no new campaign/menu, transformed level data, full bonus-area closure, native gameplay or feature-equivalence claim.',
                  bindings={str(p.resolve()): sha(p) for p in inputs})
    save('source-audit.json', source)
    print(json.dumps(dict(source=True, byte_exact=True, world_count=13,
                          route_count=len(route_rows), installed=False, output=str(O / 'source-audit.json'))))


if __name__ == '__main__':
    main()
