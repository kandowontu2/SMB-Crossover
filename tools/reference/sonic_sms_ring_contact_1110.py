"""Bind the source ring hurt state to the existing authenticated Sonic entries."""
from hashlib import sha256

import sonic_sms_ring_live_1110 as Live
from sonic_sms_compact_cold_worker_1110 import assemble

SOURCE = Live.ROOT / 'tools/reference/sonic_sms_ring_contact_1110.s'


def build(p, bundle):
    old = p['packet']
    assert old['cookie'].hex() == 'a72b01ca06c3735f445ca7db4a682ae3'
    assert sha256(old['ring_extension']).hexdigest() == 'd768c9a9965ab0ee60544ab60724af010da66774dcd82ae4c02d2015e07ece30'
    prior = p['ring_program']
    use = sum(prior['used'].values())
    assert use == 589
    start, end = Live.CODE + use, Live.CODE + 1024
    core = p['service']['symbols']
    addr = lambda name: int(bundle['syms'][name]['val'], 0)
    definitions = {key: prior['symbols'][key] for key in (
        'RingBCD', 'HurtFlags', 'StarFlags', 'DropFlags', 'ActorFlags', 'ActorX', 'ActorY',
        'ActorVX', 'ActorVY', 'PoolSlot', 'DropRecord', 'RingHurt', 'SourceX', 'SourceY',
        'ScrollY', 'HostReady', 'HostProjectContinue', 'WorldNumber', 'LevelNumber', 'AreaAddrsLOffset')}
    definitions.update(GameEngineSubroutine=addr('GameEngineSubroutine'), OriginalStatus=core['SonicHostStatus'],
        OriginalInjury=0xd31b, NativeFrame=old['frame']['symbols']['SonicNativeOrdinaryFrame'],
        SourceVX=0xc020, SourceVY=0xc060, SourceFlags=0xc030, SourcePose=0xc031,
        SourceWidth=0xc041, SourceInput=0xc0a8, SourceTick=0xc092)
    text = '\n'.join(f'{key}=${value:04x}' for key, value in definitions.items())
    program = assemble(text + '\n' + SOURCE.read_text(encoding='ascii'), {'RING_CONTACT': (start, end-start)})
    code = program['images']['RING_CONTACT']
    labels = program['symbols']
    kernel, meta, extension = (bytearray(old[k]) for k in ('kernel', 'metadata', 'ring_extension'))
    assert extension[use:] == b'\xff' * (1024-use)
    extension[use:use + len(code)] = code

    def jump(where, location, before, target, opcode=0x4c):
        assert where[location:location + 3] == bytes((opcode,)) + before.to_bytes(2, 'little')
        where[location + 1:location + 3] = labels[target].to_bytes(2, 'little')

    native_frame = definitions['NativeFrame']
    candidates = [i['pc'] for i in p['service']['instructions'] if i['op'] == 'JSR' and i['operand'] == native_frame]
    assert len(candidates) == 1
    motor_call, = candidates
    jump(kernel, motor_call - 0xa000, native_frame, 'RingMotor', opcode=0x20)
    jump(meta, 0x10f, definitions['OriginalInjury'], 'DamageContact')
    jump(meta, 0x112, definitions['OriginalStatus'], 'DamageStatus')
    jump(extension, use - 3, definitions['HostProjectContinue'], 'RingPostCommit')
    assert kernel[:5526] == old['kernel'][:5526] and kernel[0x1fe0:] == old['kernel'][0x1fe0:]
    assert meta[0x25e:] == old['metadata'][0x25e:]
    cookie = bytes((0xa7, 43, 1)) + sha256(kernel + meta + extension).digest()[:13]
    packet = dict(old, kernel=bytes(kernel), metadata=bytes(meta), ring_extension=bytes(extension), cookie=cookie)
    return dict(p, packet=packet, ring_contact_program=program,
                ring_contact_sites=dict(motor_call=motor_call, post_commit=Live.CODE + use - 3,
                                        damage_rows=[5, 6], extension_half_open=[start, start + len(code)]))
