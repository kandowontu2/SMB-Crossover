"""Read-only SMB2 allocation proposal against the exact accepted RCR build.

Does not allocate, patch, assemble, copy a source tree, or launch an emulator.
The two proposed E banks are NOT empty: freeing them requires the disclosed
Roll relocation and its independent caller/IRQ qualification first.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT.parent / 'mario in kid icarus/vendor/smb2'
PARENT = ROOT / 'build/roster-shared-rcr-adopted-v8.nes'
SHA = '4cbd019100ba4dfc51fd9f71c5d3cabd844828eb7d5d2a4aa39413e3579ab39a'


def digest(b):
    return hashlib.sha256(b).hexdigest()


def binding(p):
    p = Path(p)
    b = p.read_bytes()
    return dict(path=str(p.resolve()), bytes=len(b), sha256=digest(b))


def fields(line):
    return dict(re.findall(r'(\w+)=("[^"]*"|[^,\r\n]+)', line))


def linked_metadata(p):
    segments, symbols = [], {}
    for line in p.open():
        if line.startswith('seg\t'):
            d = fields(line)
            if 'ooffs' in d and int(d['size'], 0):
                segments.append(dict(name=d['name'].strip('"'), id=int(d['id']),
                    start=int(d['start'], 0), bytes=int(d['size'], 0), offset=int(d['ooffs'], 0)))
        elif line.startswith('sym\t'):
            d = fields(line)
            if 'val' in d and d.get('scope') == '1':
                symbols[d['name'].strip('"')] = int(d['val'], 0)
    return segments, symbols


def original_symbols():
    result = {}
    for p in (REF / 'bin').glob('native.nes.*.nl'):
        for line in p.read_text().splitlines():
            m = re.match(r'\$([0-9a-fA-F]+)#([^#]+)#', line)
            if m:
                result[m[2]] = int(m[1], 16)
    return result


def main():
    raw = PARENT.read_bytes()
    assert digest(raw) == SHA and len(raw) == 2097168
    blank_PRG_banks = [b for b in range(128)
        if raw[16+b*8192:16+(b+1)*8192] == bytes([255])*8192]
    assert not blank_PRG_banks
    segments, symbols = linked_metadata(PARENT.with_suffix('.dbg'))
    reserved = [(62, 0xaa00, 0xc000, 'FF_CORE'), (93, 0xb000, 0xc000, 'FF_ART'),
        (86, 0xa800, 0xc000, 'DRAGON_CORE'), (85, 0xc900, 0xd900, 'DRAGON_ART'),
        (96, 0xa980, 0xc000, 'DRAGON_AUDIO'), (124, 0xae00, 0xc000, 'ROGUE_CORE_AUX'),
        (95, 0xa600, 0xc000, 'ROGUE_HOST'), (94, 0xdf50, 0xe000, 'ROGUE_BRIDGE'),
        (26, 0xb140, 0xb600, 'CELESTE_HELPER')]
    protected = {70, 97, 125, 126, 127}
    # Safe tails only. Existing named segments are never mined for FF runs.
    proposals = [
        ('SMB2_CORE', 118, 0xa640, 0xc000),
        ('SMB2_ART', 80, 0xce00, 0xd600),
        ('SMB2_AUDIO_CODE_AND_SMALL_TABLES', 74, 0xb180, 0xc000),
        ('SMB2_AUDIO_MUSIC_AND_INSTRUMENT_DATA', 117, 0xca00, 0xe000),
        ('RELOCATE_ROLL_CORE_HERE_IF_APPROVED', 79, 0xab00, 0xc000),
        ('RELOCATE_ROLL_WORLD_HERE_IF_APPROVED', 78, 0xae80, 0xc000)]
    spans = []
    for role, bank, start, end in proposals:
        assert bank not in protected
        off = 16 + bank * 8192 + (start & 8191)
        stop = off + end - start
        collisions = [s for s in segments if s['offset'] < stop and s['offset'] + s['bytes'] > off]
        assert not collisions, (role, collisions)
        assert raw[off:stop] == bytes([255]) * (end - start), role
        assert not [(b, a, z, n) for b, a, z, n in reserved
            if b == bank and (a & 8191) < (end & 8191 or 8192)
            and (z & 8191 or 8192) > (start & 8191)]
        prior = [s for s in segments if 16 + bank * 8192 <= s['offset']
            and s['offset'] + s['bytes'] <= off]
        spans.append(dict(role=role, bank=bank, bank_hex=f'{bank:02X}',
            cpu_start=f'{start:04X}', cpu_end_exclusive=f'{end:04X}', bytes=end-start,
            offset=off, all_FF=True, no_linked_segment_overlap=True,
            sha256=digest(raw[off:stop]), preceding_segments=prior))
    roll = [next(s for s in segments if s['name'] == n) for n in ['ROLL_CORE', 'ROLL_WORLD']]
    assert [(s['offset']-16)//8192 for s in roll] == [119, 120]
    assert [s['bytes'] for s in roll] == [2785, 3271]
    assert all((s['offset']-16)//8192 not in protected for s in roll)
    # CHR provenance is linked memory + actual consumer limits, not zero alone.
    chr_offset = 16 + 1048576 + 796 * 1024
    chr_stop = chr_offset + 12288
    assert raw[chr_offset:chr_stop] == bytes(12288)
    assert not [s for s in segments if s['offset'] < chr_stop and s['offset']+s['bytes'] > chr_offset]
    art = (ROOT/'src/tmnt_art.inc').read_text()
    part = art.split('TnBodyChr:', 1)[1].split('TnHealthTiles:', 1)[0]
    values = [int(v) for line in part.splitlines() if '.byte' in line
        for v in line.split('.byte', 1)[1].split(',')]
    assert len(values) == 99 and min(values) == 92 and max(values) == 114
    tn_pages = sorted({p for v in values for p in (512+v, 513+v)} | {628, 629})
    assert not set(tn_pages) & set(range(756, 832))
    cfg = (ROOT/'smb1base-mmc5-expanded.cfg').read_text()
    assert re.search(r'TMNT_CHR_TAIL:\s*start=\$bd000,\s*size=\$13000', cfg)
    # There is no loaded SEGMENT for the tail. Future reservations still exclude
    # FF756..787 and Dragon788..795 even though this parent does not emit them.
    assert not re.search(r'load\s*=\s*TMNT_CHR_TAIL\b', cfg)
    assert 'ldx #>TN_FIRST_CHR' in (ROOT/'src/tmnt_draw.s').read_text()
    eq = (ROOT/'src/tmnt_equipment_draw.s').read_text()
    assert '.lobyte(628)' in eq and '.hibyte(628)' in eq
    # Exact original DMC requests include the hardware's +1 fetch byte. The
    # shorter drum is a prefix of the longer, not an independently omitted cue.
    original = Path('C:/NES/Super Mario Bros. 2 (USA).nes')
    source = original.read_bytes()
    assert digest(source) == '41300bc4942a8a4f9b53148b404dd5cae3dd708ebdd9b617888d290a51a83e43'
    labels = original_symbols()
    def orig4(pc, count):
        off = 16+4*8192+pc-0x8000
        return source[off:off+count]
    starts = orig4(labels['DMCStartTable'], 8)
    lengths = orig4(labels['DMCLengthTable'], 8)
    rates = orig4(labels['DMCFreqTable'], 8)
    names = ['DoorBomb', 'DrumA', 'PlayerHurt', 'ItemPull', 'BossDeath', 'DrumB', 'BossHurt', 'PlayerDeath']
    samples, blobs = [], {}
    union = set()
    for i, (start, length, rate, name) in enumerate(zip(starts, lengths, rates, names)):
        cpu = 0xc000+start*64
        n = length*16+1
        off = 16+14*8192+cpu-0xc000
        blob = source[off:off+n]
        assert len(blob) == n
        union.update(range(cpu, cpu+n))
        blobs[i] = blob
        samples.append(dict(request_bit=1 << i, name=name, source_cpu=f'{cpu:04X}',
            register_start=start, register_length=length, rate=rate,
            actual_fetch_bytes=n, sha256=digest(blob)))
    assert blobs[1] == blobs[5][:len(blobs[1])]
    assert symbols['BassWaterDpcm'] == 0xf140 and symbols['BassWaterDpcmEnd'] == 0xfe11
    assert symbols['Cv3DmcStartGate'] == 0xfe15 and symbols['Cv3DmcOwnerWrite'] == 0xfee1
    bass_blob = (ROOT/'audio/bass/water-shield.dmc').read_bytes()
    fixed = raw[16+127*8192:16+128*8192]
    assert len(bass_blob) == 3281 and fixed[0x1140:0x1e11] == bass_blob
    clone_proposals = []
    # Balanced64-byte-aligned packing; current fixed127 is only READ. Never
    # overwrite FE11 rates, FE15 gate, FEE1 owner code, body tail, or vectors.
    for bank, sample_ids in [(119, [7, 6, 3]), (120, [0, 5, 2, 4])]:
        cursor = 0xf140
        entries = []
        hypothetical = bytearray(fixed)
        for i in sample_ids:
            cursor = (cursor+63) & ~63
            blob = blobs[i]
            assert cursor+len(blob) <= 0xfe11
            hypothetical[cursor-0xe000:cursor-0xe000+len(blob)] = blob
            entries.append(dict(name=names[i], request_bit=1 << i, cpu=f'{cursor:04X}',
                bytes=len(blob), register_start=(cursor-0xc000)//64,
                sha256=digest(blob)))
            cursor += len(blob)
        assert cursor == 0xfe01
        assert hypothetical[:0x1140] == fixed[:0x1140]
        assert hypothetical[0x1e11:] == fixed[0x1e11:]
        clone_proposals.append(dict(bank=bank, old_owner=roll[bank-119],
            status='NOT_FREE_REQUIRES_APPROVED_RELOCATION_AND_FRESH_BUILD',
            source_fixed_bank_sha256=digest(fixed), samples=entries,
            footprint=cursor-0xf140, remaining_before_FE11=0xfe11-cursor,
            protected_from_FE11_through_FFFF_exact=True,
            hypothetical_clone_sha256=digest(hypothetical),
            shorter_drumA_reuses_DrumB_prefix=(bank == 120)))
    # Actual current global Celeste fields must NOT be re-used. The proposal is
    # instead an explicitly exclusive overlay of inactive PnHistory.
    assert [symbols[n] for n in ['CmTier', 'CmMarker', 'CmLife', 'CmArea', 'CmWorld', 'CmActive']] == list(range(0x5ff8, 0x5ffe))
    assert symbols['PnHistory'] == 0x5f40 and symbols['X5MenuVariants'] == 0x5fe0
    direct_FE3 = [name for name, value in symbols.items() if value == 0x5fe3]
    assert not direct_FE3
    references = [
        'smb1base-mmc5-expanded.cfg', 'src/entrypoint.s', 'src/character_select.s',
        'src/x5_profiles.s', 'src/mmc5_expanded.s', 'src/mmc5.s',
        'src/parodius_adapter.s', 'src/parodius_native.s', 'src/parodius_bells.s',
        'src/parodius_bell_native.s', 'src/parodius_fast_render.s',
        'src/chip_dale_art.inc', 'src/chip_dale_render.s',
        'src/kirby_weapons.s', 'src/kirby_core.s', 'src/kirby_state.inc',
        'src/x5_profiles.s', 'src/bass_corner_profile.inc',
        'src/roll.s', 'src/roll_core.s', 'src/roll_dispatch.s', 'src/roll_motion.inc',
        'src/roll_shot_bank.inc', 'src/roll_weapons.s', 'src/roll_render.s',
        'src/roll_fast_render.s', 'src/roll_empty_space.s', 'src/roll_drop_fade.s',
        'src/chr_map_mmc5.inc', 'src/parodius_art.inc', 'src/parodius_render.s',
        'src/parodius_death.s', 'src/mac_roster.s', 'src/mac_roster_data.inc',
        'src/sunny.s', 'src/sunny_art.inc', 'src/celeste_mario_render.s',
        'src/celeste_mario_art.inc', 'src/river_city_shared_palette_host_v8.inc',
        'src/river_city_shared_palette_art.inc',
        'src/tmnt.s', 'src/tmnt_state.inc', 'src/tmnt_draw.s', 'src/tmnt_art.inc',
        'src/tmnt_equipment_draw.s', 'src/celeste_mario_host_state.inc',
        'src/roster_audio.s', 'src/guest_audio.s', 'src/bass_source_sfx.s',
        'src/cv3_dmc_gate.inc', 'src/cv3_dmc_complete.s', 'src/cv3_dmc_owner.inc',
        'src/cv3_dmc_completion.inc', 'tools/prepare_cv3_dmc_mirror.py']
    original_refs = ['src/prg-4-5.asm', 'src/music/dpcm-samples.asm',
        'src/prg-0-1.asm', 'src/prg-2-3.asm', 'src/prg-e-f.asm', 'src/ram.asm']
    receipt = dict(status='READ_ONLY_PROPOSAL_NOT_RESERVED_NOT_IMPLEMENTED',
        parent=binding(PARENT), metadata=[binding(PARENT.with_suffix(s)) for s in ['.dbg', '.map', '.lbl', '.build.json', '.cv3-mirror.json']],
        frozen_original_audit=binding(ROOT/'build/smb2-roster-source-v1/handoff.json'),
        proposed_empty_tails=spans, approved_exclusions=[dict(bank=b, cpu_start=f'{a:04X}', cpu_end_exclusive=f'{z:04X}', owner=n) for b,a,z,n in reserved],
        protected_physical_banks=sorted(protected),
        no_blank_whole8KB_bank=not blank_PRG_banks,
        no_unallocated_whole_PRG_bank=all(any(s['offset'] < 16+(b+1)*8192 and s['offset']+s['bytes'] > 16+b*8192 for s in segments) or raw[16+b*8192:16+(b+1)*8192] != bytes([255])*8192 for b in range(128)),
        CHR=dict(first_page=796, last_page=807, bytes=12288, publication_upper=3,
            all_zero=True, no_emitted_segment=True, original_owner='fill-only TMNT_CHR_TAIL',
            reserved_before=['FF756..787', 'Dragon788..795'], remaining_tail='808..83124KB NOT allocated',
            legal_TN_body_table_entries=99, legal_TN_pages=tn_pages,
            constraint='Keep TMNT lower64KB and all existing pointer/CHR-map bytes exact; add a declared separate segment only after ROOT approval.'),
        audio=dict(original_code_small_tables_bytes=2066, original_music_instruments_bytes=5103,
            driver_code_budget=3712, code_adapter_headroom=1646, music_data_budget=5632, data_headroom=529,
            packing='Actual8000..875E plus8F00..8FB2 -> A74; actual9000..A3EE -> C117 with genuine pointer/instruction relocation. Future assembled fit, flags, ordered APU, complete calls and cost controls still required.',
            samples=samples, actual_unique_fetch_union_bytes=len(union), stored_seven_complete_fetches_bytes=sum(len(blobs[i]) for i in [0,2,3,4,5,6,7]),
            proposed_E_clones=clone_proposals,
            cloning='Regenerate both from FINAL current127 after every link; replace only BassWaterDpcmF140..FE10 for SMB2 owner. KeepFE11..FFFF and all fixed code/vector bytes exact; do not copy old clones.',
            repacking='Move complete2785B ROLL_CORE119 to79:AB00 and3271B ROLL_WORLD120 to78:AE80, then repurpose119/120. These are not unused banks; old Roll/Parodius helper physical PCs move and need genuine source rebuild, all compiled callers/pointers, foreign paths and IRQ/NMI controls.',
            lifecycle_blocker='A new raw-ID-gated DMC owner must keep E clone until actual fetch completion, restore127 on complete/cancel/selection/title and source-correct pause, preserve DAC semantics and actual foreground C/CurrentBank/shadows. Existing Cv3 owner/GuestDmcStatus cannot be assumed compatible. No live hooks implemented.',
            proposed_owner_protocol='Retain source low-set-bit request priority and SFX/music call order; stage clone privately; translate4012 to genuine packed address; switch E only between source4015=0F stop and4015=1F start. Completion restores127 without inventing4011=0 or changing sourceDPCMTimer. Exact continuation/RTS code is preserved in all three E views. Original pause4015=0C still processes queues; no blanket frozen tick/pause cancellation assumed.',
            actual_callable_mirror_bytes_preserved=['NMI E33C and all original code E000..F13F','Cv3DmcStartGate FE15..FE39','Cv3DmcOwnerWrite FEE1..FEFF','Samus body tail FFC1..FFF6','vectors FFFA..FFFF'],
            avoided='No graphics-C sample pinning, no sample/channel/tick cuts, no existing125/126/127/70/97 overwrite, no whole-engine ROM copy or per-read mapper assumption.'),
        RAM_proposal=dict(active='5C00..5C7F128B exclusively SMB2 rawID; overlaps existing inactive profiles, not globally free',
            active_sketch='0..3F64B native stats23+input/physics/state;40..4F one16B held record;50..6F two16B throw records;70..7F scratch. Exact projection/complete original callers remain a fit gate.',
            persistent='5F98..5F9F8B: Health,MaxHealth,VegetableReserve,Ready,Life,Area,World,PaletteAck; proposed exclusive reuse of inactive PnHistory, NOT global storage',
            persistent_existing_owner='PnHistory5F40..BF and PnEnsure clear5F00..DF. Cold/new-selection initialize after exact rawID admission; never trust Ready alone. Preserve area/life rules and actual1Up gains. Existing Celeste fields are globally live5FF8..FD and untouched.',
            variant='5FE3 proposed unused byte in existing16-byte menu-variant vector; requestedUI0,1,2,3 maps original0,3,2,1. No current named symbol equals5FE3; only existing cold clear/save/restore sweeps touch this byte in inspected source. ROOT must approve before use.',
            audio='Use existing512B RgAudioRam6F3D..713C private owner slab; sourceBB..C6 and5EC..61F fit64B projection before wrapper fields, reserve<=128B only after reachable-liveness proof. Save borrowed12B foregroundZP in actual RgAudioCpuZp71DD..727C. Do not use RgAudioZp: shared Silent/CV3 reset has live aliases.',
            no_new_SRAM=True, no_global_fast_admission_byte=True),
        source_consumer_snapshot=[binding(ROOT/p) for p in dict.fromkeys(references)],
        original_consumer_snapshot=[binding(REF/p) for p in original_refs]+[binding(original)],
        report=binding(ROOT/'docs/qa/smb2-roster-allocation-2026-10-28.txt'), tool=binding(__file__),
        limits=['No ROM or source modified, no allocations/cfg edits, no assembler/native/emulator run, no copied trees or samples written.',
            'Linked extents and untouched FF/zero tails are actual evidence. Proposed budget is not assembled fit or gameplay/audio correctness.',
            'Source snapshot describes current consumers; immutable parent metadata/ROM binding is independent. Existing reservations remain protected even when not emitted in this parent.',
            'Roll repacking is an explicit additional prerequisite, not implied authority to relocate public hooks or retag old native results.'])
    assert receipt['no_unallocated_whole_PRG_bank']
    out = ROOT/'build/smb2-roster-allocator-v1.json'
    out.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(output=binding(out), proposed=[(x['role'],x['bank'],x['cpu_start'],x['bytes']) for x in spans],
        CHR='796..807', DPCM_union=len(union), E_clone_footprints=[p['footprint'] for p in clone_proposals],
        status=receipt['status']), indent=2))


if __name__ == '__main__':
    main()
