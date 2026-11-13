"""Exact native3/9 Prince enemy-box admission; metadata-only reversible recipe."""

import contextlib
import io
from hashlib import sha256

from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

import prince_cold_packet_1111 as Packet

OLD_TAGS = bytes.fromhex('ffffdec1ebc1f8c105c213c221c22ec23c8253c263c270c27dc28fc2a1c2dec1aec2aec2bbc2ffffc6c2d3c2e2c2f08205831a83328347c355c362c370c370c37dc38bc398c3a8c3ffffb683cbc3d9c3ea8303841b8432844b845ec469c469c478c488c496c496c496c4a3c4b4c4c384d8c4e6c4e6c4f6840bc50bc519852ec53cc54ac5ffff5bc55bc566c571c571c57fc57fc58dc59bc5a8c5b6c5c3c5d0c5ddc5ffffffffebc5f8c5f8c5ffff06c614c614c622c622c62fc62fc640c640c652c652c665c665c6ffffffff76c684c694c6a3c6b0c6bdc6c7c6d2c6d2c6ddc6eac6f9c607c714c714c721c730c730c7ffff3dc749c756c763c763c770c77dc77dc78bc799c7a7c7b7c7ffffffffc2c7cdc7dac7e5c7f2c7fdc70bc819c828c838c848c857c865c872c880c88a48a548bc88d448f248164931494849484960496049ffff8a48ffff78499049ffff9049ffffa9496049604976c684c694c6ffffffffc789d6c9e4c9f1c9fcc908ca12caffff1dcaffffffffffffffffffffffffffff28ca35ca35ca42caffff50ca61ca61ca6fca7dca8dca9bcaa9caffffbacac7cad4cae5cafffffffffffffffffffff94a12cbffffffff1fcb2dcb3acb47cb53cb5ecb69cb74cb7ecb894b9e4bb74bd04be64b014c1c4c374c4ccc5ecc')
OLD_SUPPORT = bytes.fromhex('20e2bdd07f0820fca6d076a5a438e9010d85c00d87c0051ed067a5bd6920b061cd84c0d005cd86c0f0052082bdd052e9018d6bb3a9008d6cb3ad15c6290b690165758d69b3a55c69008d6ab32010b39030c9149015c958f011c951f008c957f004c9c0d01ceaeaeaeaeace6bb32010b3b00f8d80c0ad6bb369018d7fc028a9016028a90060')
SUPPORT = 0xd6d1
CUT = 0xd736
TAIL = 0xd751
POSE_END = 0xd46e
HELPER = 0xd466
HEAD = bytes.fromhex('bd4606c9094c51d7')
END = bytes.fromhex('d002a90360')


def compact_support():
    assert len(OLD_SUPPORT) == 133
    assert OLD_SUPPORT[CUT-SUPPORT:CUT-SUPPORT+5] == bytes([234])*5
    memory = [0]*65536
    memory[SUPPORT:SUPPORT+len(OLD_SUPPORT)] = OLD_SUPPORT
    decoder = Disassembler(MPU(memory=memory))
    result = bytearray(OLD_SUPPORT[:CUT-SUPPORT]+OLD_SUPPORT[CUT-SUPPORT+5:])
    shifted = lambda target:target-5 if CUT+5<=target<=0xd756 else target
    pc = SUPPORT
    while pc < 0xd756:
        if pc == CUT:
            pc += 5
            continue
        size,instruction = decoder.instruction_at(pc)
        assert instruction != '???',hex(pc)
        offset = shifted(pc)-SUPPORT
        if memory[pc]&0x1f == 0x10:
            rel = memory[pc+1]
            target = pc+2+rel-(256 if rel&128 else 0)
            assert not CUT<target<CUT+5
            distance = shifted(target)-(shifted(pc)+2)
            assert -128<=distance<=127
            result[offset+1] = distance&255
        pc += size
    assert pc == 0xd756 and len(result) == TAIL-SUPPORT
    return bytes(result)


def repack(metadata):
    from check_prince_native_foot_motion_1110 import overlap_funding
    from check_prince_run_support_funding_1110 import geometry
    with contextlib.redirect_stdout(io.StringIO()):
        result,report = overlap_funding(bytes(metadata))
    assert report['best']['used'] == HELPER-0xc800,report
    assert all(geometry(metadata,frame) == geometry(result,frame) for frame in range(239))
    assert result[HELPER-0xc800:POSE_END-0xc800] == bytes([255])*8
    return bytearray(result),report['best']


def restore_pose(metadata):
    old_tags = [int.from_bytes(OLD_TAGS[i:i+2],'little') for i in range(0,478,2)]
    new_tags = [int.from_bytes(metadata[i:i+2],'little') for i in range(0,478,2)]
    tags = sorted(set(old_tags)-{65535},key=lambda n:n&0x3fff)
    output = bytearray(POSE_END-0xc800)
    output[:478] = OLD_TAGS
    for tag,stop in zip(tags,tags[1:]+[POSE_END-0xc800],strict=True):
        start = tag&0x3fff
        end = stop&0x3fff
        frame = old_tags.index(tag)
        current = new_tags[frame]
        assert current&0xc000 == tag&0xc000
        at = current&0x3fff
        output[start:end] = metadata[at:at+end-start]
    return output


def transform(raw):
    layout = {}
    def mutate(runtime,metadata,state):
        assert metadata[:478] == OLD_TAGS
        assert metadata[SUPPORT-0xc800:0xd756-0xc800] == OLD_SUPPORT
        metadata,packing = repack(metadata)
        metadata[SUPPORT-0xc800:TAIL-0xc800] = compact_support()
        metadata[TAIL-0xc800:0xd756-0xc800] = END
        metadata[HELPER-0xc800:POSE_END-0xc800] = HEAD
        pattern = bytes.fromhex('bd4606c903d01c')
        site, = [i for i in range(0xddbe-0xc800,0xde89-0xc800) if metadata[i:i+7] == pattern]
        metadata[site:site+3] = bytes.fromhex('2066d4')
        layout.update(proxy_load=0xc800+site,helper_head=[HELPER,POSE_END],
                      helper_tail=[TAIL,0xd756],pose_packing=packing,
                      support_compacted_bytes=5,accepted_controls=[3,9])
        return runtime,metadata,state
    image,packet = Packet.rebuild(raw,mutate)
    _,chunks,_ = Packet.extract(image)
    layout.update(packet)
    layout.update(metadata_input=0xe100-packet['packed_bytes'][1],
                  decoded_bytes=list(map(len,chunks)),memory_SHA256=sha256(image).hexdigest())
    return image,chunks,layout


def reverse(raw):
    def mutate(runtime,metadata,state):
        assert metadata[HELPER-0xc800:POSE_END-0xc800] == HEAD
        assert metadata[TAIL-0xc800:0xd756-0xc800] == END
        pattern = bytes.fromhex('2066d4c903d01c')
        site, = [i for i in range(0xddbe-0xc800,0xde89-0xc800) if metadata[i:i+7] == pattern]
        metadata[site:site+3] = bytes.fromhex('bd4606')
        metadata[SUPPORT-0xc800:0xd756-0xc800] = OLD_SUPPORT
        metadata[:POSE_END-0xc800] = restore_pose(metadata)
        return runtime,metadata,state
    image,_ = Packet.rebuild(raw,mutate)
    assert transform(image)[0] == raw
    return image

