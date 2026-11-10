"""Verify current Mike pose factoring and the resident bank94 source gap."""
from hashlib import sha256
import json
from pathlib import Path
import re
from unittest.mock import patch

import check_jay_silius_scene_lifecycle_1110 as C

H, W, N = C.H, C.W, C.N
PIN = 'a20d254d4730583ee1f039b10abcf873559987e4f989968037a38e17427faac1'
SOURCE = H.ROOT / 'tools/reference/jay_silius_mike_resident_1110.s'
HOT_FIXTURE = 0x4a00
GAP_A, GAP_C, GAP_SIZE = 0xb25f, 0xd25f, 161


def pose_proposal(raw, *, transport=HOT_FIXTURE):
    assert C.digest(raw) == PIN
    start, end = C.offset(96,0xa276), C.offset(96,0xa2cb)
    history = H.ROOT/'build/mike-alternate-prototypes-1110/linked-v3.json'
    manifest = history.read_bytes()
    assert C.digest(manifest) == '959389538468f3de750144878f58d7450e355cc9d98997a1a9b6f0dcbf8d0b2d'
    pose, = (r for r in json.loads(manifest)['patches'] if r['role'] == 'POSE')
    assert pose['file_offset'] == start and raw[start:end] == bytes.fromhex(pose['new_hex'])
    assert raw[C.offset(126,0x80c2):C.offset(126,0x80c9)] == bytes.fromhex('8da17d8d165160')
    source = (H.ROOT/'src/mmc5.s').read_text()
    assert re.search(r'StoreGraphics:\s+sta CurrentBankC\s+sta .*\s+rts',source,re.I)
    # The old source exposes the whole pose as a single procedure. Its
    # interior branch target A297 is the sole same-bank instruction transfer.
    b = W.Symbols.bundle()
    assert W.location(b,'JnSetPose') == start
    core = (H.ROOT/'src/mike_jones_core.s').read_text()
    assert core.count('jmp JnSetPose') == core.count('jsr JnSetPose') == 1
    pose_blob = raw[start:end]
    assert pose_blob[0x19:0x1b] == bytes.fromhex('d006')
    bank=raw[16+96*8192:16+97*8192]
    calls=[(0xa000+i,bank[i],int.from_bytes(bank[i+1:i+3],'little'))
           for i in range(len(bank)-2) if bank[i] in (0x20,0x4c)
           and 0xa276<=int.from_bytes(bank[i+1:i+3],'little')<0xa2cb]
    assert calls==[(0xa264,0x4c,0xa276),(0xa270,0x20,0xa276)]
    for physical in range(128):
        page=raw[16+8192*physical:16+8192*(physical+1)]
        for at in range(len(page)-14):
            if (page[at]==0xa9 and page[at+2:at+5]==bytes.fromhex('8d6c01')
                and page[at+5:at+7]==bytes.fromhex('a9a2')
                and page[at+7:at+10]==bytes.fromhex('8d6d01')
                and page[at+10:at+12]==bytes.fromhex('a9e0')):
                assert not 0x76<=page[at+1]<0xcb, (physical,hex(at+0xa000))
    at = C.offset(96,0xa53d)
    assert raw[at:at+3] == bytes.fromhex('4ccba2')
    program = H.assemble(f'JayTransport = ${transport:04x}\n'+SOURCE.read_text(), {'MIKE_POSE':(0xa276,85)})
    assert program['used']['MIKE_POSE'] == 85 and program['symbols']['JayMovementRoute'] == 0xa2bc
    result = bytearray(raw)
    result[start:end] = program['images']['MIKE_POSE']
    result[at:at+3] = bytes.fromhex('4cbca2')
    return dict(b,raw=raw),dict(b,raw=bytes(result)),program


def pose_parity(base,trial,program):
    seeds = [N.fresh(q) for q in (base,trial)]
    count = 0
    for variant in (0,32,64,96):
        for facing in (1,2):
            for pose in range(7):
                for flags in (0x30,0x31,0x79,0xfc):
                    values = []
                    for seed in seeds:
                        m = N.fork(seed)
                        N.put(m,SelectedCharacter=16,PlayerFacingDir=facing)
                        m[0x730b] = variant
                        r = N.invoke(m,'JnSetPose',a=81,x=pose,y=2,p=flags)
                        values.append((tuple(r[n] for n in ('A','X','Y','P')),
                            bytes(m[:0x1c0]),bytes(m[0x200:0x8000]),m.ram,m.rawtags,m.chr_latches,
                            m.upper,m.lastset,m.ppu_log,m.ppu_reads))
                    assert values[0] == values[1], (variant,facing,pose,flags)
                    count += 1
    selector = 0
    seed = N.fresh(trial)
    seed.raw_page(1,224)
    N.put(seed,CurrentBank=224,SelectedCharacter=16)
    entry = program['symbols']['JayMovementRoute']
    for alternate in range(256):
        m = N.fork(seed)
        m[0x730b] = alternate
        c = N.NesMPU(memory=m,pc=entry)
        for _ in range(8):
            if c.pc in (0xa2cb,HOT_FIXTURE):
                break
            c.step()
        assert c.pc == (HOT_FIXTURE if alternate&0x60 == 0x20 else 0xa2cb)
        selector += 1
    family = C.family_parity(base,trial,dict(images={},symbols={'JaySceneOrRetire':0,'PublishPosition':0},instructions=[]),
                             {'symbols':{'JayHostTile':0}},None)
    return dict(exact_pose_pairs=count,all_selector_byte_values=selector,exact_native_non_Jay=family)


class GapBus(W.ControllerBus):
    reads = None
    all_reads = []

    def __getitem__(self,address):
        if isinstance(address,int):
            mapped_a = GAP_A <= address < GAP_A+GAP_SIZE and self.rawtags[1] == 222
            mapped_c = GAP_C <= address < GAP_C+GAP_SIZE and self.rawtags[2] == 222
            if mapped_a or mapped_c:
                self.all_reads.append(address)
                if self.reads is not None:
                    self.reads.append(address)
        return super().__getitem__(address)


def bank94_gap(raw):
    b = W.Symbols.bundle()
    b['raw'] = raw
    start = C.offset(94,GAP_C)
    end = start + GAP_SIZE
    assert W.location(b,'SunnyArtEnd') == start and W.location(b,'RdArtStart') == end
    assert W.address(b,'SunnyArtEnd') == GAP_C and W.address(b,'RdArtStart') == 0xd300
    assert raw[start:end] == bytes([255])*GAP_SIZE
    cfg = (H.ROOT/'smb1base-mmc5-expanded.cfg').read_text()
    assert 'SUNNY_ART: load=X5_NEW_5E,type=ro,start=$ce00' in cfg
    assert 'A:start=$D300,size=$D00,bank=94' in (H.ROOT/'tools/rogue_dawn_render_controls_v1.py').read_text()
    original_art = (H.ROOT/'src/sunny_art.inc').read_text()
    assert 'SunnyArtEnd:' in original_art and original_art.split('SunnySemanticBig:',1)[1].count('.byte') == 1
    assert (H.ROOT/'src/rogue_dawn_art.inc').read_text().index('RdArtStart:') < 240
    poison = raw[:start]+bytes((i*47+19)&255 for i in range(GAP_SIZE))+raw[end:]
    after = dict(b,raw=poison)
    count = 0
    with patch.object(N,'Bus',GapBus):
        seeds = [N.fresh(q) for q in (b,after)]
    for pose in range(256):
        for facing in (1,2):
            values = []
            for seed in seeds:
                m = N.fork(seed)
                m.reads = []
                N.put(m,SelectedCharacter=23,PlayerFacingDir=facing)
                r = N.invoke(m,'SunnySetPose',x=pose)
                assert not m.reads, (pose,facing,m.reads)
                values.append((r,bytes(m[0x200:0x8000]),m.ram,m.rawtags,m.chr_latches))
            assert values[0] == values[1]
            count += 1
    GapBus.all_reads=[]
    with patch.object(N,'Bus',GapBus),patch.object(W,'ControllerBus',GapBus):
        roster=H.Roster.Starts.C.inventory(raw)
        assert roster==H.Roster.Starts.C.inventory(poison)
    assert not GapBus.all_reads
    rows = roster['rows']
    names = ('SUNNY','ROGUE DAWN','LITTLE MAC','DOC LOUIS','MIKE TYSON')
    seen = []
    for row in rows:
        if row['name'] not in names:
            continue
        with patch.object(W,'ControllerBus',GapBus):
            left,a = H.Roster.cold(b,row)
            right,z = H.Roster.cold(after,row)
        assert left == right and (a.ram,a.vram,a.rawtags,a.chr_latches) == (z.ram,z.vram,z.rawtags,z.chr_latches)
        for pad in (0,1,1,129,1,65,0,0):
            for m in (a,z):
                m.reads = []
                m.controller_pad = pad
                C.Game.frame(m)
                assert not m.reads, (row['name'],pad,m.reads)
            assert (a.ram,a.vram,a.rawtags,a.chr_latches) == (z.ram,z.vram,z.rawtags,z.chr_latches)
        seen.append(row['name'])
    assert sorted(seen) == sorted(names)
    return dict(candidate_physical_PRG=94,A_half_open=[hex(GAP_A),hex(GAP_A+GAP_SIZE)],
                C_half_open=[hex(GAP_C),hex(GAP_C+GAP_SIZE)],bytes=GAP_SIZE,
                preimage_SHA256=C.digest(raw[start:end]),exhaustive_Sunny_selector_pairs=count,
                genuine_neighbor_openings=seen,all100_native_menu_entries_poison_exact=True,
                code_or_ownership_granted=False)


def main():
    raw = H.ROM.read_bytes()
    base,trial,program = pose_proposal(raw)
    pose = pose_parity(base,trial,program)
    gap = bank94_gap(raw)
    print(json.dumps(dict(passed=True,ROM_SHA256=PIN,ROM_written=False,Mesen=False,build_files=0,
        Mike_pose_factor=pose,Bank94=gap,resident_source_SHA256=C.digest(SOURCE.read_bytes())),sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
