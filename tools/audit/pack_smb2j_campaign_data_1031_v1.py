"""Build complete reachable donor-area catalogs and lossless cache carriers."""
from pathlib import Path
import collections
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/audit'))
from audit_smb2j_campaign_source_1031_v1 import disk_files, symbols, DONOR

O = R / 'build/smb2j-campaign-data-1031-v1'
A = R / 'build/smb2j-campaign-audit-1031-v1/source-audit.json'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest = lambda b: hashlib.sha256(b).hexdigest()


def encode(data):
    """LSB-first8-token groups; 1=literal, 0=12bit distance/4bit length."""
    out, cursor = bytearray(), 0
    positions = collections.defaultdict(collections.deque)
    while cursor < len(data):
        flag = len(out)
        out.append(0)
        for bit in range(8):
            if cursor == len(data):
                break
            best, distance = 0, 0
            key = bytes(data[cursor:cursor + 3])
            candidates = positions[key]
            while candidates and candidates[0] < cursor - 4096:
                candidates.popleft()
            for before in reversed(candidates):
                length = 0
                while length < 18 and cursor + length < len(data) and data[before + length] == data[cursor + length]:
                    length += 1
                if length > best:
                    best, distance = length, cursor - before
                    if length == 18:
                        break
            size = best if best >= 3 else 1
            if best >= 3:
                token = ((best - 3) << 12) | (distance - 1)
                out += token.to_bytes(2, 'little')
            else:
                out[flag] |= 1 << bit
                out.append(data[cursor])
            for at in range(cursor, cursor + size):
                positions[bytes(data[at:at + 3])].append(at)
            cursor += size
    return bytes(out)


def decode(data, expected):
    out, at = bytearray(), 0
    while len(out) < expected:
        flags = data[at]
        at += 1
        for bit in range(8):
            if len(out) == expected:
                break
            if flags >> bit & 1:
                out.append(data[at])
                at += 1
            else:
                word = int.from_bytes(data[at:at + 2], 'little')
                at += 2
                distance, length = (word & 4095) + 1, (word >> 12) + 3
                assert distance <= len(out)
                for _ in range(length):
                    out.append(out[-distance])
    assert len(out) == expected and at == len(data)
    return bytes(out)


def main():
    assert not O.exists()
    audit = json.loads(A.read_text())
    assert audit['passed'] and audit['assembled_disk_byte_exact']
    for name, expected in audit['bindings'].items():
        assert sha(name) == expected, name
    files, syms = disk_files(DONOR.read_bytes()), symbols()
    O.mkdir()
    profiles, links, catalog, carrier = [], [], [], bytearray()
    for profile in audit['profiles']:
        name, chain = profile['profile'], profile['original_load_order']
        image = bytearray(65536)
        for f in chain:
            q = files[f]
            image[q['load']:q['load'] + q['bytes']] = q['payload']
        labels = syms[profile['original_tables']]
        count = (labels['AreaDataHOffsets'] - labels['EnemyDataAddrs']) // 2
        assert count == (21 if name == 'worldsA-D' else 52)

        def area(pointer):
            kind, number = (pointer >> 5) & 3, pointer & 31
            result = dict(pointer=pointer & 127, kind=kind, number=number)
            for prefix, table, offsets in [('enemy', 'EnemyDataAddrs', 'EnemyAddrHOffsets'),
                                            ('terrain', 'AreaDataAddrs', 'AreaDataHOffsets')]:
                index = image[labels[offsets] + kind] + number
                assert index < count, (name, pointer, prefix, index)
                p = labels[table] + 2 * index
                start = int.from_bytes(image[p:p + 2], 'little')
                end = start + (2 if prefix == 'terrain' else 0)
                commands = []
                while image[end] != (253 if prefix == 'terrain' else 255):
                    size = 3 if prefix == 'enemy' and image[end] & 15 == 14 else 2
                    commands.append((end, bytes(image[end:end + size])))
                    end += size
                    assert end - start < 2048
                end += 1
                assert 0xc200 <= start < end <= 0xd2a0, (name, pointer, prefix, hex(start), hex(end))
                owners = [f for f in chain if files[f]['load'] <= start < files[f]['load'] + files[f]['bytes']]
                actual_owner = owners[-1]
                source_names = sorted(n for n, value in syms[actual_owner].items()
                                      if value == start and n.startswith('E_' if prefix == 'enemy' else 'L_'))
                assert source_names, (name, pointer, hex(start), actual_owner)
                result[prefix] = dict(start=start, end=end, bytes=end-start,
                                      sha256=digest(image[start:end]), labels=source_names,
                                      commands=[dict(address=a, bytes=list(b)) for a, b in commands])
            return result

        stages = [q for q in audit['routes'] if q['profile'] == name]
        queue = collections.deque((q['native_world'], q['area_pointer'] & 127) for q in stages)
        seen, source_areas = set(), {}
        while queue:
            world, pointer = queue.popleft()
            if (world, pointer) in seen:
                continue
            seen.add((world, pointer))
            q = source_areas.setdefault(pointer, area(pointer))
            for command in q['enemy']['commands']:
                b = command['bytes']
                if len(b) != 3:
                    continue
                link_world, destination, page = b[2] >> 5, b[1] & 127, b[2] & 31
                usable = link_world == world
                links.append(dict(profile=name, native_world=world, source=pointer,
                                  source_command=command['address'], destination=destination,
                                  entrance_page=page, original_world_filter=link_world, usable=usable))
                if usable:
                    queue.append((world, destination))
        for pointer, q in sorted(source_areas.items()):
            q.update(profile=name, native_worlds=sorted(w for w, p in seen if p == pointer))
            catalog.append(q)
        # Native pointer values stay intact in a private8KiB physical RAM page.
        # Runtime workers/cookie are intentionally absent from this data stage.
        cache = bytearray([255]) * 8192
        cache[0x200:0x12a0] = image[0xc200:0xd2a0]
        packed = encode(cache)
        assert decode(packed, 8192) == cache
        aligned = (len(carrier) + 255) & ~255
        carrier += bytes([255]) * (aligned - len(carrier)) + packed
        (O / (name + '.cache.bin')).write_bytes(cache)
        (O / (name + '.lzss')).write_bytes(packed)
        profiles.append(dict(name=name, original_files=chain,
                             raw_cache_bytes=8192, cache_sha256=digest(cache),
                             packed_bytes=len(packed), packed_sha256=digest(packed),
                             carrier_offset=aligned, original_table_count=count,
                             reachable_areas=len(source_areas), reachable_world_area_pairs=len(seen),
                             pointer_addresses={k: labels[k] for k in ['WorldAddrOffsets', 'AreaAddrOffsets', 'EnemyAddrHOffsets', 'EnemyDataAddrs', 'AreaDataHOffsets', 'AreaDataAddrs']}))
    (O / 'campaign-data.bin').write_bytes(carrier)
    catalog_path = O / 'catalog.json'
    catalog_path.write_text(json.dumps(dict(profiles=profiles, areas=catalog, links=links), indent=2) + '\n', encoding='utf-8', newline='\n')
    original_chr = files['SM2CHAR1']['payload']
    assert len(original_chr) == 8192
    (O / 'original-world-art.chr').write_bytes(original_chr)
    q = dict(passed=True, source_data_only=True, installed=False,
             campaign_complete=False, donor_sha256=sha(DONOR), profiles=profiles,
             worlds=13, numbered_levels=52, ordered_area_entries=58,
             reachable_profile_areas=len(catalog), reachable_world_area_pairs=sum(p['reachable_world_area_pairs'] for p in profiles),
             active_world_filtered_links=sum(p['usable'] for p in links), examined_links=len(links),
             packed_bytes=len(carrier), packed_pages=(len(carrier)+1023)//1024,
             original_art_bytes=8192, all_reachable_streams_original_byte_exact=True,
             limits=['Lossless data pack and active-world pipe-link closure, not a campaign implementation.',
                     'No resource grant, RAM/header change, loader, object parser, progression or native gameplay is adopted.'],
             bindings={str(p.resolve()): sha(p) for p in [Path(__file__), A, DONOR,
                        R/'tools/audit/audit_smb2j_campaign_source_1031_v1.py',
                        R/'build/smb2j-original-source-1031-v1/original/original.dbg',
                        *sorted(O.iterdir())]})
    (O / 'data-stage.json').write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k:v for k,v in q.items() if k not in ['bindings','profiles']}))


if __name__ == '__main__':
    main()
