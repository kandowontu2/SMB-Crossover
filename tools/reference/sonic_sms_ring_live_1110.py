"""Source-only ninth-row and raw43 ring lifecycle proposal."""
import ast
from hashlib import sha256
from pathlib import Path

from sonic_sms_compact_cold_worker_1110 import assemble
import sonic_sms_native_eighth_payload_1110 as Eighth

ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / 'tools/reference/sonic_sms_ring_adapter_1110.s'
SOURCE = ROOT / 'tools/reference/sonic_sms_ring_live_1110.s'
PAGE, CODE, CONTEXT = 333, 0xd400, 0xc340
BOOT, BOOT_END, META_TAIL = 0xd25e, 0xd2e9, 0xd31f
OLD_ADAPTER = '14a3e78cf0c33088a0e94fb78ef9672b24f1dc33826b8d99f7b89152830fc017'


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def bootstrap(old):
    """Reassemble the exact eighth loader before adding the typed ninth row."""
    recipe = ast.parse(Eighth.OldCold.REFERENCE.read_text(encoding='utf-8'))
    body = next(ast.literal_eval(n.value) for n in recipe.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'BOOT' for t in n.targets))
    body = body.replace('Mini', 'Sonic')
    body = once(body, '"MINI_COLD"', '"SONIC_COLD"')
    body = once(body, ' cmp #5\n', ' cmp #8\n')
    for label in ('Copy', 'Verify'):
        needle = f' iny\n bne {label}\n inc R1'
        partial = (f' iny\n beq {label}PageDone\n cpy #$e0\n bne {label}\n'
                   f' lda R1\n cmp #$bf\n bne {label}\n{label}PageDone:\n inc R1')
        body = once(body, needle, partial)
    pages = ','.join(str(n) for n in Eighth.CODE_PAGES)
    table = 'SonicCodePages:\n .word '
    body = once(body, table + '962,963,964,965,966', table + pages)
    layout = {'SONIC_COLD': (BOOT, BOOT_END - BOOT)}
    original = assemble(body, layout)
    assert original['images']['SONIC_COLD'] == old['startup']['image'] == old['metadata'][0x25e:0x2e9]
    body = once(body, ' cmp #8\n bne NextRow\n sec\n rts',
                ' cmp #8\n bcc NextRow\n jmp RingColdMore')
    body = once(body, table + pages + '\nSonicColdEnd:', '''SonicColdEnd:
.segment "COLD_TAIL"
RingColdMore:
 cmp #8
 bne RingColdDone
 lda #$d4
 sta R1
 jmp NextRow
RingColdDone:
 sec
 rts
''' + table + pages + f',{PAGE}')
    layout['COLD_TAIL'] = (META_TAIL, 0xd400 - META_TAIL)
    result = assemble(body, layout)
    assert result['symbols']['SonicColdBoot'] == BOOT
    assert result['symbols']['SonicCodePages'] + 18 == META_TAIL + result['used']['COLD_TAIL']
    return result


def build(p, bundle):
    old = p['packet']
    assert old['code_pages'] == Eighth.CODE_PAGES
    assert old['cookie'].hex() == 'a72b0194a989064ae62ef75a04986523'
    boot = bootstrap(old)
    adapter = ADAPTER.read_bytes()
    assert sha256(adapter).hexdigest() == OLD_ADAPTER
    adapter_source = f'RingContext = ${CONTEXT:04x}\n' + adapter.decode('ascii')
    reference = assemble(adapter_source, {'RINGS': (CODE, 394)})
    assert reference['used']['RINGS'] == 394
    svc = p['service']['symbols']
    project, fresh, ctor = (svc[n] for n in ('HostProject', 'SonicHostFresh', 'SonicHostConstruct'))
    kernel, meta = bytearray(old['kernel']), bytearray(old['metadata'])
    ready = p['service']['fields']['Ready']
    definitions = {k: int(bundle['syms'][k]['val'], 0) for k in ('WorldNumber', 'LevelNumber', 'AreaAddrsLOffset')}
    definitions.update(HostReady=ready, FreshContinue=fresh+5, CtorTileX=0xc117,
        CtorContinue=ctor+5, SourceX=0xc071, SourceY=0xc074, HostProjectContinue=project+3)
    code = assemble(adapter_source + '\n' + '\n'.join(f'{k}=${v:04x}' for k, v in definitions.items()) +
        '\n' + SOURCE.read_text(encoding='ascii'), {'RINGS': (CODE, 394), 'RING_SCENE': (CODE+394, 630)})
    assert code['images']['RINGS'] == reference['images']['RINGS']
    assert code['symbols']['SceneEnd'] == CONTEXT + 59
    extension = (code['images']['RINGS'] + code['images']['RING_SCENE']).ljust(1024, b'\xff')
    assert len(extension) == 1024
    sites = ((fresh, b'\xa9\x00\x8d' + ready.to_bytes(2, 'little'), 'RingFresh'),
             (ctor, b'\xa9\x00\x8d\x17\xc1', 'RingConstruct'),
             (project, b'\xad\x71\xc0', 'RingProject'))
    for pc, before, target in sites:
        at = pc - 0xa000
        assert kernel[at:at + len(before)] == before
        kernel[at:at + len(before)] = (b'\x4c' + code['symbols'][target].to_bytes(2, 'little')).ljust(len(before), b'\xea')
    cold = boot['images']['SONIC_COLD']
    meta[BOOT - 0xd000:BOOT_END - 0xd000] = cold.ljust(BOOT_END - BOOT, b'\xff')
    tail = boot['images']['COLD_TAIL']
    at = META_TAIL - 0xd000
    assert meta[at:at + len(tail)] == b'\xff' * len(tail)
    meta[at:at + len(tail)] = tail
    cookie = bytes((0xa7, 43, 1)) + sha256(kernel + meta + extension).digest()[:13]
    startup = dict(image=cold, symbols=boot['symbols'], tail=tail, tail_address=META_TAIL)
    packet = dict(old, kernel=bytes(kernel), metadata=bytes(meta), cookie=cookie,
                  startup=startup, ring_extension=extension, ring_extension_page=PAGE)
    return dict(p, packet=packet, ring_program=code, ring_boot=boot, ring_sites=sites)
