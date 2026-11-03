"""Private, zero-growth Prince OAM-header backing on an explicit five-owner ROM.

Returns a memory image only. Never restores the historical four-owner manager,
publishes menu admission, or writes a ROM. All generated files belong to O.
"""
from pathlib import Path
import argparse, hashlib, json, re, subprocess, sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit')]
import prepare_prince_body_backing_1103_v180 as OLD
import measure_prince_lzdict_1102_v9 as CODEC
import build_storage_guard_v1 as STORAGE

O = R / 'build/prince-pose-reservation-1103-v185'
PARENT = R / 'build/mini-mario-end-candidate-root-1103-v49/mini-end.nes'
PIN = 'ca90e8be125c55e7ae12413964ecf766c9b890525751ea1e0ad6ce225613f4db'
FIT = R / 'build/mini-mario-owner-1103-v15/owner-fit-v15.json'
V = OLD.V
digest = lambda data: hashlib.sha256(data).hexdigest()
sha = lambda path: digest(Path(path).read_bytes())


def labels(path):
    return {name.lstrip('.'): int(value, 16) for value, name in
            re.findall(r'^al ([0-9A-Fa-f]+) (\S+)$', Path(path).read_text(), re.M)}


def assemble(stem, text, config):
    (O / (stem + '.s')).write_text(text)
    (O / (stem + '.cfg')).write_text(config)
    cc = R / 'tools/Windows/cc65/bin'
    for command in [
        [cc / 'ca65.exe', O / (stem + '.s'), '-o', O / (stem + '.o')],
        [cc / 'ld65.exe', '-C', O / (stem + '.cfg'), O / (stem + '.o'),
         '-o', O / (stem + '.bin'), '-Ln', O / (stem + '.lbl')],
    ]:
        run = subprocess.run(list(map(str, command)), capture_output=True, text=True)
        assert run.returncode == 0, run.stderr
    (O / (stem + '.o')).unlink()
    return (O / (stem + '.bin')).read_bytes(), labels(O / (stem + '.lbl'))


def check_layout(raw, fit):
    """Require actual five-owner instructions/tables, allowing cookie data only."""
    f = R / 'build/mini-mario-owner-1103-v15'
    spans = [('owner-v15.bin', 65, 0xae00), ('owner-v15-extra.bin', 65, 0xab72),
             ('owner-v15-Sh.bin', 65, 0xa800), ('selector-v15.bin', 65, 0xa740),
             ('common-v15.bin', 123, 0xaf40), ('common-v15-map.bin', 123, 0xb9d6)]
    cookies = [fit['labels']['PrCookie'], fit['labels']['MiniCookie']]
    result = []
    for name, bank, pc in spans:
        want = (f / name).read_bytes()
        at = 16 + bank * 8192 + pc - 0xa000
        actual = raw[at:at + len(want)]
        ignored = {a - pc for cookie in cookies for a in range(cookie, cookie + 16)
                   if bank == 65 and pc <= a < pc + len(want)}
        assert all(a == b or i in ignored for i, (a, b) in enumerate(zip(actual, want))), name
        assert len(actual) == len(want)
        result.append(dict(name=name, physical_PRG=bank, CPU=pc, bytes=len(want),
                           SHA256=digest(actual), ignored_cookie_bytes=len(ignored)))
    assert fit['labels']['PrCookie'] == 0xaba4
    assert fit['labels']['CoRetire'] == 0xae0a
    return result


def rebase(parent=PARENT, expected_sha256=PIN, five_owner_fit=FIT):
    """Rebind owned carrier data and the current symbolic cookie, in memory.

    The caller supplies an exact parent/hash and the current compiled five-owner
    layout. Every other byte, including Mini's entire latest payload, is exact.
    """
    parent = Path(parent)
    raw = parent.read_bytes()
    assert digest(raw) == expected_sha256
    fit = json.loads(Path(five_owner_fit).read_text())
    layout = check_layout(raw, fit)
    old = json.loads((OLD.O / 'body-manifest-v180.json').read_text())
    prior = OLD.PARENT.read_bytes()
    carriers = sorted((r for r in old['patches'] if 'physical_CHR' in r),
                      key=lambda row: row['source_offset'])
    assert len(carriers) == 44 and len({r['physical_CHR'] for r in carriers}) == 44
    pool = (O / 'pose-pool.bin').read_bytes()
    plan = json.loads((O / 'pose-source.json').read_text())
    assert digest(pool) == plan['pool_SHA256'] and len(pool) <= 45056
    new_cookie = bytes.fromhex(plan['Prince_cookie'])
    address = fit['labels']['PrCookie']
    cookie_at = 16 + 65 * 8192 + address - 0xa000
    old_cookie = bytes.fromhex(old['old_Prince_cookie'])
    assert raw[cookie_at:cookie_at + 16] == old_cookie
    out = bytearray(raw)
    patches = []

    def put(at, new, **fields):
        before = raw[at:at + len(new)]
        out[at:at + len(new)] = new
        patches.append(dict(file_offset=at, bytes=len(new), old_hex=before.hex(),
                            new_hex=new.hex(), old_SHA256=digest(before),
                            new_SHA256=digest(new), **fields))

    put(cookie_at, new_cookie, physical_PRG=65, CPU=address, role='Prince cookie data only')
    for index, row in enumerate(carriers):
        at = 16 + 128 * 8192 + row['physical_CHR'] * 1024
        assert at == row['file_offset']
        assert raw[at:at + 1024] == prior[at:at + 1024], 'Current Prince carrier changed'
        data = pool[index * 1024:(index + 1) * 1024]
        if data:
            put(at, data, physical_CHR=row['physical_CHR'], source_offset=index * 1024,
                role='Existing Prince carrier, no new page')
    allowed = set()
    for row in patches:
        allowed.update(range(row['file_offset'], row['file_offset'] + row['bytes']))
    changed = [i for i, (a, b) in enumerate(zip(raw, out)) if a != b]
    assert all(i in allowed for i in changed)
    art = (V.O / 'prince-body-8x16.chr').read_bytes()
    assert pool[:len(art)] == art and len(art) == 31072
    template, _ = OLD.image()
    receipt = dict(passed=True, source_backed_cold_qualified=False, ROM_written=False,
                   parent_ROM=parent.relative_to(R).as_posix(), parent_SHA256=expected_sha256,
                   expected_memory_only_SHA256=digest(out), patches=patches,
                   Prince_cookie=new_cookie.hex(), old_Prince_cookie=old_cookie.hex(),
                   cookie_CPU=address, five_owner_layout=layout,
                   shared_instructions_tables_headers_unchanged=True,
                   Mini_all_carriers_and_cookie_exact=True,
                   physical_pages=44, payload_bytes=len(pool), physical_spare=45056-len(pool),
                   runtime_bytes=8159, metadata_bytes=6092, state_bytes=1607,
                   original_art_bytes_exact=len(art), changed_bytes=len(changed))
    return dict(template, raw=bytes(out)), receipt


def image():
    q = json.loads((O / 'pose-manifest.json').read_text())
    for name, value in q['bindings'].items():
        assert sha(R / name) == value, name
    base, rebuilt = rebase(R / q['parent_ROM'], q['parent_SHA256'])
    assert rebuilt['expected_memory_only_SHA256'] == q['expected_memory_only_SHA256']
    return base, q


def main():
    STORAGE.preflight(private_root=O, reserved_bytes=600000, reserved_files=20, fresh=True)
    O.mkdir(exist_ok=True)
    source = (V.O / 'grid-render-labels-v37.s').read_text()
    old = ' sta PpNativePacket\n clc\n adc CurrentOAMOffset'
    new = ' sta PpNativePacket\n sta $6b05 ; Stable native length, source partCount*4.\n clc\n adc CurrentOAMOffset'
    assert source.count(old) == 1
    source = source.replace(old, new)
    old = ' lda #0\n sta SafecallA_SMC+1\n lda #<MetaspriteRenderLoop'
    new = ' lda #0\n ; Native emitter overwrites incomingA with the packet header before use.\n lda #<MetaspriteRenderLoop'
    assert source.count(old) == 1
    source = source.replace(old, new)
    # Preserve the already-qualified42+ native palette-slot adaptation. The
    # source hues are unchanged; native player slot0 replaces source slot1.
    old = ' lda #1\n ldx PpState+$615\n beq :+\n lda #$41'
    assert source.count(old) == 1
    source = source.replace(old, ' lda #0\n ldx PpState+$615\n beq :+\n lda #$40')
    render, lab = assemble('pose-render', source, (V.O / 'host-render-v11.cfg').read_text())
    oldlab = labels(V.O / 'grid-render-labels-v37.lbl')
    assert len(render) == 545
    for name in ['Byte', 'Read', 'Header', 'PpHostProject', 'PpReadProjection',
                 'PpRenderX', 'PpRenderY', 'PpPosePointer', 'PpRenderEnd']:
        assert lab[name] == oldlab[name], name
    grid = labels(V.O / 'pose-grid-helper-v37.lbl')
    data = bytearray(render)
    def patch(pc, blob):
        at = pc - lab['PpHostDraw']
        data[at:at + len(blob)] = blob
    def calls(lo, hi, target):
        return [a for a in range(lo, hi - 2)
                if render[a-lab['PpHostDraw']:a-lab['PpHostDraw']+3] == b'\x20'+target.to_bytes(2,'little')]
    for lo, hi, target, replacement in [
        (lab['PpHostDraw'], lab['PpHostProject'], lab['PpReadProjection'], grid['PpGridProjection']),
    ]:
        sites = calls(lo, hi, target); assert len(sites) == 1
        patch(sites[0], b'\x20' + replacement.to_bytes(2, 'little'))
    parts = calls(lab['Parts'], lab['PpGridPartEnd'], lab['Byte']); assert len(parts) == 3
    patch(parts[0], b'\x20' + grid['PpGridY'].to_bytes(2, 'little'))
    patch(parts[2], b'\x20' + grid['PpGridX'].to_bytes(2, 'little'))
    runtime, meta, state = OLD.images()
    runtime, meta = bytearray(runtime), bytearray(meta)
    end = lab['Byte'] - lab['PpHostDraw']
    runtime[lab['PpHostDraw']-0xa000:lab['Byte']-0xa000] = data[:end]
    upper = bytes.fromhex('bdc3bdaa')
    sites = [i for i in range(len(runtime)) if runtime[i:i+4] == upper]
    assert len(sites) == 1
    runtime[sites[0]:sites[0]+4] = bytes.fromhex('20c3bdea')
    helper = bytes(runtime[0x1dc3:0x1de2])
    assert helper.count(bytes.fromhex('a9e18d066ba9068d076b')) == 1
    runtime[0x1dc3:0x1de2] = helper.replace(bytes.fromhex('a9e18d066ba9068d076b'),
                                          bytes.fromhex('a9058d066ba96b8d076b'))
    chunks = [bytes(runtime), bytes(meta), state]
    for name, blob in zip(['runtime', 'metadata'], chunks):
        (O / ('pose-' + name + '.bin')).write_bytes(blob)
    packed = [CODEC.encode(blob) for blob in chunks]
    text = (OLD.O / 'body-worker.s').read_text()
    streams = []
    for name, blob, encoded in zip(['Runtime','Metadata','State'], chunks, packed):
        start = 0xc500 if name == 'Runtime' else 0xc300 if name == 'State' else 0xe100-len(encoded)
        for suffix, value in [('Input',start),('Packed',len(encoded)),('Bytes',len(blob))]:
            text, n = re.subn(r'(?m)^'+name+suffix+r'=\$[0-9a-f]+$',
                              name+suffix+f'=${value:04x}',text); assert n == 1
        streams.append(dict(name=name, bytes=len(blob), packed=len(encoded), source_start=start,
                            SHA256=digest(blob)))
    worker, _ = assemble('pose-worker', text, (OLD.O / 'body-worker.cfg').read_text())
    assert len(worker) == 444
    art = (V.O / 'prince-body-8x16.chr').read_bytes()
    pool = art + (V.O / 'cold-decoder-v25.bin').read_bytes() + worker + b''.join(packed)
    assert len(pool) <= 45056
    (O / 'pose-pool.bin').write_bytes(pool)
    cookie = bytes([0xa7,38,2]) + hashlib.sha256(b''.join(chunks)+pool).digest()[:13]
    count_sites = [i+0xa000+3 for i in range(len(runtime)-5)
                   if runtime[i:i+6] == bytes.fromhex('8d00c28d056b')]
    assert len(count_sites) == 1
    source_receipt = dict(measured=True, CPU_qualified=False, ROM_written=False,
                          original_renderer_bytes=545, renderer_bytes=len(render),
                          source_inserted_bytes=3, source_removed_bytes=3,
                          count_store_CPU=count_sites[0],
                          upper_call_CPU=sites[0]+0xa000, stable_header=0x6b05,
                          stable_pointer=0x6b06, streams=streams, payload_bytes=len(pool),
                          physical_spare=45056-len(pool), pool_SHA256=digest(pool),
                          Prince_cookie=cookie.hex(), labels=lab)
    (O / 'pose-source.json').write_text(json.dumps(source_receipt,indent=2)+'\n')
    base, q = rebase()
    inputs = [Path(__file__), PARENT, FIT, OLD.O/'body-manifest-v180.json',
              OLD.O/'body-runtime.bin', OLD.O/'body-metadata.bin',
              V.O/'grid-render-labels-v37.s', V.O/'native-state-v153.bin',
              V.O/'native-live-v149.bin', V.O/'source-art.json',
              O/'pose-render.s', O/'pose-render.bin', O/'pose-render.lbl',
              O/'pose-worker.s', O/'pose-worker.bin', O/'pose-runtime.bin',
              O/'pose-metadata.bin', O/'pose-pool.bin', O/'pose-source.json']
    q['bindings'] = {p.relative_to(R).as_posix():sha(p) for p in inputs}
    (O / 'pose-manifest.json').write_text(json.dumps(q,indent=2)+'\n')
    assert image()[0]['raw'] == base['raw']
    print(json.dumps({k:v for k,v in q.items() if k not in ['patches','bindings','five_owner_layout']}))


if __name__ == '__main__':
    main()
