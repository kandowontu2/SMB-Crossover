"""In-memory Prince pose78 head projection and bounded C280 cold staging."""

from hashlib import sha256
import struct

from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

import prince_cold_packet_1111 as Packet

WORKER = bytes.fromhex('ad17c6c94ed015a5bdc930900f4838e91085bd2087956885bda506604c8795')
CODE = 0xb0fe
OLD_CODE_END = 0xc21c
OLD_WORKER_END = 0xc25d
BOOT_BYTES = 97
LOADER_BYTES = 450
CONFIG = Packet.LOADER+396
STREAMS = Packet.LOADER+LOADER_BYTES
WRAP = 0xc280


def relocate_loader(old):
    assert len(old) == 446
    stage, = [i for i in range(97,381) if old[i:i+8] == bytes.fromhex('c9dcd004a9c38504')]
    cut = 0xc100+stage+4-97
    extra = bytes.fromhex('a9808503')
    new = bytearray(old[:stage+4]+extra+old[stage+4:])
    new[stage+4+len(extra)+1] = 0xc2
    memory = [0]*65536
    memory[0xc100:OLD_WORKER_END] = old[97:]
    decoder = Disassembler(MPU(memory=memory))
    pc, relocations = 0xc100, []
    moved = lambda address:address+4 if cut<=address<OLD_WORKER_END else address
    while pc < OLD_CODE_END:
        size, instruction = decoder.instruction_at(pc)
        assert instruction != '???',hex(pc)
        at = BOOT_BYTES+moved(pc)-0xc100
        opcode = memory[pc]
        if size == 3:
            target = memory[pc+1]|memory[pc+2]<<8
            shifted = moved(target)
            if shifted != target:
                new[at+1:at+3] = shifted.to_bytes(2,'little')
                relocations.append((pc,target,shifted))
        elif opcode & 0x1f == 0x10:
            relative = memory[pc+1]
            target = pc+2+relative-(256 if relative&128 else 0)
            displacement = moved(target)-(moved(pc)+2)
            assert -128<=displacement<=127
            new[at+1] = displacement&255
        pc += size
    assert pc == OLD_CODE_END
    assert new[:97] == old[:97]
    # Source cursor is the physical PPU offset of the first stream in the
    # last15 carrier rows, four bytes later after the enlarged loader.
    assert new[394:396] == bytes.fromhex('1c0c')
    new[394:396] = bytes.fromhex('200c')
    return new,dict(insert_PC=cut,relocations=relocations,
                    old_worker_end=OLD_WORKER_END,new_worker_end=OLD_WORKER_END+4)


def unrelocate_loader(new):
    assert len(new) == LOADER_BYTES
    stage, = [i for i in range(97,385) if new[i:i+12] == bytes.fromhex('c9dcd008a9808503a9c28504')]
    cut = 0xc100+stage+4-97
    old = bytearray(new[:stage+4]+new[stage+8:])
    old[stage+5] = 0xc3
    memory = [0]*65536
    memory[0xc100:OLD_WORKER_END+4] = new[97:]
    decoder = Disassembler(MPU(memory=memory))
    moved = lambda address:address-4 if cut+4<=address<OLD_WORKER_END+4 else address
    pc = 0xc100
    while pc < OLD_CODE_END+4:
        if pc == cut:
            pc += 4
            continue
        size,instruction = decoder.instruction_at(pc)
        assert instruction != '???',hex(pc)
        at = BOOT_BYTES+moved(pc)-0xc100
        opcode = memory[pc]
        if size == 3:
            target = memory[pc+1]|memory[pc+2]<<8
            shifted = moved(target)
            if shifted != target:
                old[at+1:at+3] = shifted.to_bytes(2,'little')
        elif opcode & 0x1f == 0x10:
            relative = memory[pc+1]
            target = pc+2+relative-(256 if relative&128 else 0)
            displacement = moved(target)-(moved(pc)+2)
            assert -128<=displacement<=127
            old[at+1] = displacement&255
        pc += size
    assert pc == OLD_CODE_END+4
    assert old[390:392] == bytes.fromhex('200c')
    old[390:392] = bytes.fromhex('1c0c')
    assert relocate_loader(old)[0] == new
    return old


def transform(raw):
    head, chunks, sizes = Packet.extract(raw)
    runtime,metadata,state = map(bytearray,chunks)
    assert runtime[0x10fe:0x111f] == bytes(33)
    runtime[0x10fe:0x10fe+len(WORKER)] = WORKER
    vector, = [i for i in range(len(metadata)-2) if metadata[i:i+3] == bytes.fromhex('4c8795')]
    metadata[vector:vector+3] = bytes.fromhex('4cfeb0')
    chunks = tuple(map(bytes,(runtime,metadata,state)))
    packed = tuple(map(Packet.encode,chunks))
    assert tuple(map(len,packed)) == (6428,5940,1231)
    decoder = bytearray(head[31072:Packet.LOADER])
    wrap, = [i for i in range(len(decoder)-14) if decoder[i:i+2] == bytes.fromhex('c9dc')]
    assert decoder[wrap+4:wrap+7] == bytes.fromhex('a9008d')
    assert decoder[wrap+9:wrap+12] == bytes.fromhex('a9c38d')
    decoder[wrap+5],decoder[wrap+10] = 0x80,0xc2
    loader,layout = relocate_loader(head[Packet.LOADER:])
    struct.pack_into('<12H',loader,396,0xc500,0xa000,len(packed[0]),len(chunks[0]),
                     0xe100-len(packed[1]),0xc800,len(packed[1]),len(chunks[1]),
                     0xc300,0xc100,len(packed[2]),len(chunks[2]))
    payload = head[:31072]+bytes(decoder)+bytes(loader)+b''.join(packed)
    assert len(payload) <= len(Packet.PAGES)*1024
    cookie = Packet.cookie(chunks,payload)
    image = bytearray(raw)
    image[Packet.COOKIE:Packet.COOKIE+16] = cookie
    for index,page in enumerate(Packet.PAGES):
        at = Packet.CHR+1024*page
        image[at:at+1024] = payload[1024*index:1024*(index+1)].ljust(1024,b'\xff')
    layout.update(cookie=cookie.hex(),packed_bytes=list(map(len,packed)),
                  decoded_bytes=list(map(len,chunks)),runtime_wrap=WRAP,
                  runtime_capacity=6528,worker_half_open=[CODE,CODE+len(WORKER)],
                  head_vector=vector+0xc800,payload_bytes=len(payload),
                  carrier_spare=len(Packet.PAGES)*1024-len(payload),
                  metadata_input=0xe100-len(packed[1]),loader_bytes=LOADER_BYTES,
                  memory_SHA256=sha256(image).hexdigest())
    return bytes(image),chunks,layout


def reverse(raw):
    head,chunks,_ = Packet.extract(raw)
    assert len(head) == STREAMS
    runtime,metadata,state = map(bytearray,chunks)
    assert runtime[0x10fe:0x10fe+len(WORKER)] == WORKER
    runtime[0x10fe:0x10fe+len(WORKER)] = bytes(len(WORKER))
    vector, = [i for i in range(len(metadata)-2) if metadata[i:i+3] == bytes.fromhex('4cfeb0')]
    metadata[vector:vector+3] = bytes.fromhex('4c8795')
    chunks = tuple(map(bytes,(runtime,metadata,state)))
    packed = tuple(map(Packet.encode,chunks))
    assert tuple(map(len,packed)) == (6400,5940,1231)
    decoder = bytearray(head[31072:Packet.LOADER])
    wrap, = [i for i in range(len(decoder)-14) if decoder[i:i+2] == bytes.fromhex('c9dc')]
    assert decoder[wrap+4:wrap+7] == bytes.fromhex('a9808d')
    assert decoder[wrap+9:wrap+12] == bytes.fromhex('a9c28d')
    decoder[wrap+5],decoder[wrap+10] = 0,0xc3
    loader = unrelocate_loader(head[Packet.LOADER:])
    struct.pack_into('<12H',loader,392,0xc500,0xa000,len(packed[0]),len(chunks[0]),
                     0xe100-len(packed[1]),0xc800,len(packed[1]),len(chunks[1]),
                     0xc300,0xc100,len(packed[2]),len(chunks[2]))
    payload = head[:31072]+bytes(decoder)+bytes(loader)+b''.join(packed)
    image = bytearray(raw)
    image[Packet.COOKIE:Packet.COOKIE+16] = Packet.cookie(chunks,payload)
    for index,page in enumerate(Packet.PAGES):
        at = Packet.CHR+1024*page
        image[at:at+1024] = payload[1024*index:1024*(index+1)].ljust(1024,b'\xff')
    result = bytes(image)
    assert transform(result)[0] == raw
    return result
