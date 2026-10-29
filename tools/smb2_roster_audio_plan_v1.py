"""Read-only current emitted Roll/audio prerequisite audit; no ROM patch/build."""
from pathlib import Path
from collections import defaultdict, Counter
import hashlib, json, re, statistics, sys

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT.parent / 'mario in kid icarus/vendor/smb2'
PARENT = ROOT / 'build/roster-shared-celeste-small-chr-v1.nes'
PARENT_SHA = 'f56a0e154c86c2bcc3577bd99e48dfab71ee61282defa6d16963a2c73e4487c9'
ORIGINAL = Path('C:/NES/Super Mario Bros. 2 (USA).nes')
ORIGINAL_SHA = '41300bc4942a8a4f9b53148b404dd5cae3dd708ebdd9b617888d290a51a83e43'
OUT = ROOT / 'build/smb2-roster-audio-plan-v1.json'
sys.path.insert(0, str(ROOT / 'tools/audit'))
from verify_native_relocation import NesMPU


def digest(b): return hashlib.sha256(b).hexdigest()
def binding(p):
    p = Path(p); b = p.read_bytes()
    return dict(path=str(p.resolve()), bytes=len(b), sha256=digest(b))
def fields(line): return dict(re.findall(r'(\w+)=("[^"]*"|[^,\r\n]+)', line))


def metadata():
    result = {k: {} for k in ['file', 'line', 'span', 'seg', 'sym']}
    for line in PARENT.with_suffix('.dbg').open():
        kind = line.split('\t', 1)[0]
        if kind in result:
            d = fields(line); result[kind][int(d['id'])] = d
    return result


def original_labels():
    labels = {}
    for p in sorted((REF / 'bin').glob('native.nes.*.nl')):
        for line in p.read_text().splitlines():
            m = re.match(r'\$([0-9a-fA-F]+)#([^#]+)#', line)
            if m: labels[m[2]] = int(m[1], 16)
    return labels


def original_profile(raw, labels):
    """Actual original CPU calls only: no hardware DMC/PPU/scheduler model."""
    reads, writes, cycles, stack = set(), set(), [], 255
    apu_hash = hashlib.sha256(); code_reads = set()
    class Memory:
        def __init__(self):
            self.m = bytearray(65536)
            self.m[0x8000:0xc000] = raw[16+32768:16+49152]
            self.m[0xc000:] = raw[16+114688:16+131072]
            self.w = []
        def __getitem__(self, p):
            reads.add(p)
            return self.m[p]
        def __setitem__(self, p, v):
            self.m[p] = v & 255; writes.add(p); self.w.append((p, v & 255))
    def call(m):
        nonlocal stack
        c = NesMPU(memory=m, pc=labels['StartProcessingSoundQueue'])
        c.sp = 0xfd; c.p = 0x24
        m.m[0x1fe:0x200] = bytes([0xfe, 0x7f]); m.w = []
        for _ in range(5000):
            if c.pc == 0x7fff:
                assert c.sp == 255
                cycles.append(c.processorCycles)
                for p, v in m.w:
                    if 0x4000 <= p <= 0x4017:
                        apu_hash.update(bytes([p & 255, p >> 8, v]))
                return
            assert m.m[c.pc] != 0, hex(c.pc)
            if c.pc == labels['ProcessSoundEffectQueue3_RocketPart2'] + 3:
                code_reads.add(m.m[labels['SoundEffectTimer3']])
            c.step(); stack = min(stack, c.sp)
        raise AssertionError(('original audio did not return', hex(c.pc)))
    # Every released song selector, the eight genuine DMC requests, mixed
    # real effects, and exact original pause discriminator. Not all tracks.
    for bit in range(8):
        m = Memory(); m.m[labels['MusicQueue1']] = 1 << bit
        for _ in range(192): call(m)
    dmc = []
    for bit in range(8):
        m = Memory(); m.m[labels['DPCMQueue']] = 1 << bit
        call(m)
        stream = [(p, v) for p, v in m.w if 0x4010 <= p <= 0x4017]
        assert [p for p, _ in stream][-5:] == [0x4010, 0x4012, 0x4013, 0x4015, 0x4015]
        assert [v for p, v in stream if p == 0x4015][-2:] == [15, 31]
        dmc.append(dict(request=1 << bit, stores=[[f'{p:04X}', v] for p, v in stream]))
    for bit in range(8):
        m = Memory()
        m.m[labels['SoundEffectQueue1']] = 1 << bit
        m.m[labels['SoundEffectQueue2']] = 1 << (bit % 6)
        m.m[labels['SoundEffectQueue3']] = 1 << (bit % 3)
        for _ in range(64): call(m)
    m = Memory(); m.m[labels['StackArea']] = 0x41
    m.m[labels['MusicQueue2']] = 8
    m.m[labels['DPCMQueue']] = 1
    for _ in range(32): call(m)
    live = sorted((reads | writes) - set(range(0x100, 0x200)))
    audio = [p for p in live if p < 0x4000]
    assert not [p for p in audio if not (0xbb <= p <= 0xc6 or 0x5ec <= p <= 0x61f)]
    return dict(scope='Original NES CPU only; no PPU/NMI scheduler, mapper or DMC stalls/fetch model',
        calls=len(cycles), min_cycles=min(cycles), p50_cycles=statistics.median(cycles),
        p95_cycles=sorted(cycles)[int(.95*(len(cycles)-1))], max_cycles=max(cycles),
        minimum_SP=stack, live_nonstack_RAM=[f'{p:04X}' for p in audio],
        original_ordered_APU_sha256=apu_hash.hexdigest(), actual_DMC_starts=dmc,
        source_pause=dict(discriminator='StackArea0100==41',
            action='4017=FF,4015=0C; skip three SFX and first DPCM call; run ProcessMusicQueue then clear all six queues',
            note='Music DPCM may still start through actual ProcessMusicQueue; not a blanket stopped tick.'),
        noise_code_data=dict(source=f'{labels["ProcessMusicQueue"]:04X}+Y',
            legal_native_timer_range='1..127', conservative_all_byte_controls='retain256 original bytes',
            original256_sha256=digest(raw[16+32768+labels['ProcessMusicQueue']-0x8000:16+32768+labels['ProcessMusicQueue']-0x8000+256]),
            observed_indices=sorted(code_reads), required='Point this actual LDA at immutable original bytes, never translated instructions.'))


def main():
    raw = PARENT.read_bytes(); original = ORIGINAL.read_bytes()
    assert digest(raw) == PARENT_SHA and digest(original) == ORIGINAL_SHA
    assert (REF / 'bin/native.nes').read_bytes()[16:] == original[16:]
    d = metadata(); segs = d['seg']
    syms = {x['name'].strip('"'): int(x['val'], 0) for x in d['sym'].values()
        if x.get('scope') == '1' and 'val' in x}
    roll = {i: x for i, x in segs.items() if x.get('name') in ['"ROLL_CORE"', '"ROLL_WORLD"']}
    assert [(int(x['ooffs'])-16)//8192 for x in roll.values()] == [119, 120]
    changes = {119: (79, 0xab00), 120: (78, 0xb000)}
    source_paths = set(); ref_records = []
    def source(line):
        p = Path(d['file'][int(line['file'])]['name'].strip('"'))
        source_paths.add(p)
        n = int(line['line']); text = p.read_text().splitlines()
        return dict(path=str(p), line=n, text=text[n-1].strip() if n else '<generated>')
    for sym in d['sym'].values():
        if int(sym.get('seg', -1)) not in roll: continue
        for ref in sorted(set(int(i) for i in sym.get('ref', '').split('+') if i)):
            line = d['line'][ref]
            spans = [d['span'][int(i)] for i in line.get('span', '').split('+') if i]
            emitted = [x for x in spans if 'ooffs' in segs[int(x['seg'])]]
            if not emitted: continue
            ref_records.append(dict(target=sym['name'].strip('"'), target_cpu=sym.get('val'),
                target_segment=roll[int(sym['seg'])]['name'].strip('"'), source=source(line),
                emitted=[dict(segment=segs[int(x['seg'])]['name'].strip('"'),
                    bank=(int(segs[int(x['seg'])]['ooffs'])-16)//8192,
                    pc=f'{int(segs[int(x["seg"])]["start"],0)+int(x["start"]):04X}', bytes=int(x['size'])) for x in emitted]))
    # Exact macro instruction signature, anchored to emitted segment bytes and
    # real shared SMCCODE fields. Numeric address aliases in other banks are
    # never treated as a symbol/call target.
    fc = syms['FarCallCommon'].to_bytes(2, 'little')
    macro = []; same_bank = []
    for seg in segs.values():
        if 'ooffs' not in seg: continue
        off, size = int(seg['ooffs']), int(seg['size'], 0)
        if not 16 <= off < 16+1048576: continue
        blob = raw[off:off+size]; bank = (off-16)//8192
        for i in range(len(blob)-17):
            q = blob[i:i+18]
            if not (q[0] == 0x8d and q[3] == q[8] == q[13] == 0xa9
                and q[5] == q[10] == 0x8d and q[15] in [0x20, 0x4c] and q[16:18] == fc): continue
            assert q[1:3] == bytes([0x6a, 1]) and q[6:8] == bytes([0x6c, 1]) and q[11:13] == bytes([0x6d, 1])
            target_bank, target = q[14] & 127, q[4] + 256*q[9]
            if bank not in changes and target_bank not in changes: continue
            new_bank = changes.get(bank, (bank, 0))[0]
            new_target_bank = changes.get(target_bank, (target_bank, 0))[0]
            new_target = target + changes[target_bank][1]-0xa000 if target_bank in changes else target
            if new_bank == new_target_bank: same_bank.append([bank, i, target_bank, target])
            names = [s['name'].strip('"') for s in d['sym'].values() if s.get('scope') == '1'
                and 'val' in s and int(s['val'], 0) == target and int(s.get('seg', -1)) in segs
                and 'ooffs' in segs[int(s['seg'])]
                and (int(segs[int(s['seg'])]['ooffs'])-16)//8192 == target_bank]
            macro.append(dict(source_bank=bank, pc=f'{int(seg["start"],0)+i:04X}',
                target_bank=target_bank, target=f'{target:04X}', names=names,
                kind='JSR' if q[15] == 0x20 else 'JMP', original_bytes=q.hex(),
                proposed_target_bank=new_target_bank, proposed_target=f'{new_target:04X}'))
    assert not same_bank
    # Unambiguous ca65 leaf instruction spans, not a linear decode through data.
    instructions = {}; mpu = NesMPU()
    mode_size = dict(imp=1, acc=1, imm=2, zpg=2, zpx=2, zpy=2, rel=2, inx=2, iny=2,
        abs=3, abx=3, aby=3, ind=3)
    for span in d['span'].values():
        seg_id = int(span['seg'])
        if seg_id not in roll or 'type' in span or int(span['size']) > 3: continue
        s = roll[seg_id]; rel, n = int(span['start']), int(span['size'])
        off = int(s['ooffs']) + rel; q = raw[off:off+n]
        mnemonic, mode = mpu.disassemble[q[0]]
        if mode_size.get(mode) != n or mnemonic == '???': continue
        instructions[(seg_id, rel)] = (q, mnemonic, mode)
    absolute, branches, indirect = [], [], []
    for (seg_id, rel), (q, mn, mode) in sorted(instructions.items()):
        s = roll[seg_id]; bank = (int(s['ooffs'])-16)//8192; pc = int(s['start'], 0)+rel
        row = dict(bank=bank, pc=f'{pc:04X}', op=mn, mode=mode, bytes=q.hex())
        if mode == 'rel': branches.append(row)
        if mode == 'ind': indirect.append(row)
        if mode in ['abs', 'abx', 'aby']:
            operand = q[1] + 256*q[2]
            if 0xa000 <= operand < 0xa000+int(s['size'], 0):
                row.update(operand=f'{operand:04X}', proposed_operand=f'{operand+changes[bank][1]-0xa000:04X}')
                absolute.append(row)
    proposed = []
    for bank, start, size, role in [(79, 0xab00, 2785, 'ROLL_CORE'), (78, 0xb000, 3271, 'ROLL_WORLD'),
            (74, 0xb180, 3712, 'SMB2_AUDIO_CODE'), (117, 0xca00, 5632, 'SMB2_AUDIO_DATA')]:
        off = 16+bank*8192+(start & 8191); end = off+size
        assert raw[off:end] == bytes([255])*size
        assert not [s for s in segs.values() if 'ooffs' in s and int(s['ooffs']) < end
            and int(s['ooffs'])+int(s['size'],0) > off]
        proposed.append(dict(role=role, bank=bank, start=f'{start:04X}',
            end_inclusive=f'{start+size-1:04X}', bytes=size, all_FF_no_emitted_segment=True))
    fixed = raw[16+127*8192:16+128*8192]
    labels = original_labels()
    profile = original_profile(original, labels)
    allocator = json.loads((ROOT/'build/smb2-roster-allocator-v1.json').read_text())
    samples = allocator['audio']['samples']; clones = []
    for bank, ids in [(119, [7, 6, 3]), (120, [0, 5, 2, 4])]:
        cursor = 0xf140; entries = []
        for i in ids:
            cursor = (cursor+63)&~63; s = samples[i]
            cpu = int(s['source_cpu'],16); n = s['actual_fetch_bytes']
            blob = original[16+114688+cpu-0xc000:16+114688+cpu-0xc000+n]
            assert digest(blob) == s['sha256'] and cursor+n <= 0xfe11
            entries.append(dict(request=1 << i, source=s['source_cpu'], target=f'{cursor:04X}', bytes=n, sha256=digest(blob)))
            cursor += n
        assert cursor == 0xfe01
        clones.append(dict(bank=bank, entries=entries, footprint=3265, end_inclusive='FE00',
            preserve='Every byte outsideF140..FE10 from FINAL current127; incl FE11/FE15/FEE1/NMI/vectors'))
    incoming = [m for m in macro if m['source_bank'] not in changes and m['target_bank'] in changes]
    external_refs = [r for r in ref_records if any(x['bank'] not in changes for x in r['emitted'])]
    assert len(incoming) == len({(m['source_bank'],m['pc']) for m in incoming})
    for p in ROOT.glob('src/roll*'): source_paths.add(p)
    source_paths.update(ROOT/p for p in ['src/parodius_fast_render.s','src/parodius_render.s',
        'src/mmc5.s','tools/Windows/cc65/asminc/smc.inc','src/roster_audio.s','src/guest_audio.s','src/expanded_audio.s',
        'src/cv3_dmc_gate.inc','src/cv3_dmc_complete.s','src/cv3_dmc_completion.inc',
        'src/cv3_dmc_owner.inc','src/reset.s','tools/build_mmc5_expanded.py',
        'tools/prepare_cv3_dmc_mirror.py','smb1base-mmc5-expanded.cfg'])
    report = ROOT/'docs/qa/smb2-roster-audio-plan-2026-10-28.txt'
    record = dict(status='READ_ONLY_CONCRETE_PLAN_NO_RELOCATION_OR_AUDIO_IMPLEMENTATION',
        parent=binding(PARENT), parent_metadata=[binding(PARENT.with_suffix(x)) for x in ['.dbg','.lbl','.map','.cv3-mirror.json']],
        original=binding(ORIGINAL), original_matching_source=binding(REF/'bin/native.nes'),
        frozen_gameplay=binding(ROOT/'build/smb2-roster-component-v1/handoff.json'),
        frozen_palette_additive=binding(ROOT/'build/smb2-roster-palette-v2/handoff.json'),
        frozen_allocator=binding(ROOT/'build/smb2-roster-allocator-v1-handoff.json'),
        ranges=proposed, exact_Roll_segments=[dict(name=s['name'].strip('"'),
            bank=(int(s['ooffs'])-16)//8192, start=s['start'], bytes=int(s['size'],0),
            sha256=digest(raw[int(s['ooffs']):int(s['ooffs'])+int(s['size'],0)])) for s in roll.values()],
        emitted_farcall_edges=macro, incoming_macro_count=len(incoming),
        incoming_counts=dict(Counter(str(m['target_bank']) for m in incoming)),
        complete_symbol_references=ref_records, external_symbol_reference_count=len(external_refs),
        audited_leaf_instruction_count=len(instructions), internal_absolute_operands=absolute,
        relative_branches=branches, indirect_JMPs=indirect, no_new_same_bank_farcall=True,
        relocation_contract='Reassemble only complete two Roll segments and their exact symbolic callers; retain all instruction sizes. CORE+0B00 and WORLD+1000 keep low bytes/page timing. No numeric global rewrite, fake old-PC alias or omitted PN helpers.',
        mirror_rebuild=dict(final_fixed127_sha256=digest(fixed), existing125=binding(PARENT.with_suffix('.cv3-mirror.json')),
            affected_fixed_incoming_calls=[m for m in incoming if m['source_bank']==127],
            action='Regenerate existing125 from final127 through existing producer after changing fixed caller operands; generate119/120 from that SAME final127 after Roll relocation. No stale clones.',
            current70_97='Neither is a current fixed-E mirror; both contain actual unrelated owners. No write/lease proposed.'),
        samples=clones, original_CPU=profile,
        audio_budget=dict(code_small2066='original8000..875E and8F00..8FB2;1646B wrapper/projection headroom',
            data5103='original9000..A3EE toC117CA00..DDEE',
            immutable_noise256='reserveDDEF..DEEE within data tail;273B data headroom after this exact source byte view',
            measured_original_only=True, projected_host_cost='Unknown until actual assembled writer/projection/mapper wrapper controls; no native estimate substituted.'),
        RAM_plan=dict(slab='Existing raw25-exclusive RgAudioRam6F3D..713C512B; no globally checked marker',
            source='Preserve complete5EC..61F52B plus allBB..C612B (incl holes/read-only seeds) in owner slab',
            pause='Translate original0100 StackArea to one private discriminator; never overwrite actual host hardware-stack bottom',
            borrow='12 CPU ZP bytesBB..C6 saved/restored through existing RgAudioCpuZp71DD..727C, include actual decoder/graphics interrupted values',
            borrow_copy_estimate='12*(LDAzpX4+STAabsX5+LDAabsX4+STAzpX4)*2 =408CPU indexed copy body before loop/calls; unrolled direct copies336CPU. Actual projection/writer/full-call cost must be measured.',
            state_keys='RgAudioCharacter raw25 owner/init gate; selection/newgame before trust; source audio state exclusively shared slab, PnHistory/gameplay bytes not borrowed',
            pending='Use existing owner-private state for cue/sample request; no Main mutable multi-byte publication without a correct producer/consumer boundary proof'),
        DMC_lifecycle=dict(owner='Need distinct raw25 owner value, audit all BassDmcActive comparisons and Cv3 priority alias reset first',
            start='Original4017FF; preserve low-set-bit queue priority,4010/12/13 order,160tick nativeDPCMTimer,4015stop0F thenstart1F. Switch physicalE strictly between actualstop andstart.',
            finish='Poll actual4015 before mixerstatus writes; hold clone through hardware fetch; finalbuffer/DAC drains naturally. Stop/release restore127 without4011zero and without skipping sourceDPCMTimer progression.',
            title_scene_owner_exit='Cancel hardware before127 restore; source queues/init/scene pause semantics independently defined and tested; do not let generic GuestAudioBegin/Finish clear4011 or reset source owner inadvertently.',
            pause='OriginalStackArea41:4015=0C thenmusic-onlypath (can issueDPCM); host pause/title policy must explicitly preserve/adapt this. Existing GuestAudioFinish Silent4011/15=0 cannot be silently inherited.',
            leases='Lease A74/C117 once whole callback; restore actual hardware A/C and shadows. E119/120 aliases preserve all callable continuation/NMI/IRQ/RTS bytes. NMI bank restoration must not end an ongoing sample.',
            mixer='Use authentic buffered16-register image/dirty high semantics and original4017/DMCstatus order; sharedSMB worldeffects remain GuestAudioBegin/Finish with declared channel arbitration, not dropped/retriggered source notes.'),
        staged_units=['ROOT review this exact plan first; no relocation implemented.',
            'Unit1 sparse Roll source relocation+all direct/dispatch/PN/foreign fullcall/IRQ/SMC/bank/timing controls; fresh existing125 clone. No SMB2 hooks yet.',
            'Unit2 original authentic driver/data projection+APUwriter fullcalls; all8samples bytefetch/readback; regenerated119/120 current-E clones and cancellation/IRQ aliases. No gameplay scheduling yet.',
            'Unit3 ROOT-only host cue publication/mixer/pause/title/owner lifecycle integration; source/current ROM triple, bounded native sameinput audio/render/cadence controls before admission.'],
        source_snapshot=[binding(p) for p in sorted(source_paths)],
        original_source_snapshot=[binding(REF/p) for p in ['src/prg-4-5.asm','src/ram.asm','src/defs.asm','src/music/dpcm-samples.asm']],
        tool=binding(__file__), report=binding(report),
        setup_negative=binding(ROOT/'build/smb2-roster-audio-plan-v1-first-setup-negative.txt'),
        limits=['No source/CFG/ROM/clone/sample mutation or assembly/native/emulator launch.',
            'DBG symbolic references plus exact emitted farcall signature are finite actual evidence; not a completed relocation or proof of arbitrary dynamic call/pointer admission.',
            'OriginalCPU costs omit DMC steals/PPU/NMI/mapper/host mixer/writer/borrow overhead. Gameplay remains unexposed and authentic audio prerequisite unimplemented.'])
    OUT.write_text(json.dumps(record, indent=2)+'\n')
    handoff = ROOT/'build/smb2-roster-audio-plan-v1-handoff.json'
    handoff.write_text(json.dumps(dict(status=record['status'], receipt=binding(OUT),
        owned=[binding(__file__),binding(report)], all_input_bindings=record['source_snapshot']+record['original_source_snapshot']+
        [record['parent'],*record['parent_metadata'],record['original'],record['original_matching_source'],record['frozen_gameplay'],record['frozen_palette_additive'],record['frozen_allocator'],record['setup_negative']]),indent=2)+'\n')
    print(json.dumps(dict(handoff=binding(handoff), incoming=len(incoming), source_references=len(ref_records),
        instruction_spans=len(instructions), internal_absolute=len(absolute), branches=len(branches),
        original_CPU=profile|{'actual_DMC_starts':'8 exact source starts','live_nonstack_RAM':'see receipt','noise_code_data':'256 source bytes required'}),indent=2))


if __name__ == '__main__': main()
