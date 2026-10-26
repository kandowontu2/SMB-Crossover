"""Finite current-ROM mask-order audit; no ROM candidate or native launch."""
from pathlib import Path
import argparse, hashlib, json, sys, urllib.request
from check_tmnt_render_oa import Memory, address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = D / 'root-chip-hud-composed-v1'
SHA = '3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


class SerialMemory(Memory):
    def __init__(self, bundle, pads):
        super().__init__(bundle)
        self.pads = pads
        self.reads = [0, 0]

    def __getitem__(self, at):
        if isinstance(at, int) and at in [0x4016, 0x4017]:
            port = at - 0x4016
            n = self.reads[port]
            self.reads[port] += 1
            assert n < 8
            return (self.pads[port] >> (7 - n)) & 1
        return super().__getitem__(at)


def phase(cpu_cycles):
    # Relative to the upcoming pre-render scanline start; no assumed +1 frame.
    dot = (256 - 261) * 341 + 255 + cpu_cycles * 3
    line, cycle = divmod(dot, 341)
    return dict(relative_scanline=line - 1, dot=cycle,
                convention='Upcoming pre-render=-1, first visible=0; 341-dot/no-stall arithmetic, not a native observation.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    assert sha(PARENT / 'candidate.nes') == SHA
    b = scoped_load(PARENT / 'candidate.nes')
    rows = []
    for buttons in range(256):
        for flags in [0x30, 0x71]:
            m = SerialMemory(b, [buttons, buttons ^ 255])
            c = NesMPU(memory=m, pc=address(b, 'OAMandReadJoypad'))
            c.a, c.x, c.y, c.p, c.sp = 0x5a, 73, 19, flags, 0xfd
            c.stPushWord(0x5aff)
            writes = []
            for step in range(1000):
                if c.pc == 0x5b00:
                    break
                before = len(m.writes)
                pc, clock = c.pc, c.processorCycles
                c.step()
                writes += [dict(PC=pc, clock_before=clock, clock_after=c.processorCycles, address=at, value=v)
                           for at, v in m.writes[before:]]
            else:
                raise AssertionError('Input routine did not finish')
            dma = [r for r in writes if r['address'] == 0x4014]
            assert len(dma) == 1 and dma[0]['value'] == 2 and dma[0]['clock_after'] == 6
            assert c.sp == 0xfd and c.processorCycles == 266 and m.reads == [8, 8]
            assert m[address(b, 'SavedJoypad1Bits')] == buttons
            assert m[address(b, 'SavedJoypad2Bits')] == buttons ^ 255
            rows.append(dict(pad1=buttons, pad2=buttons ^ 255, flags=flags,
                             actual_instruction_cycles=266, after_DMA_STA_instruction_cycles=260,
                             DMA_instruction_clock=[2, 6], reads=m.reads, stack_exact=True))
    put(a.output / 'current-input-CPU-cases.json', rows)
    source = PARENT / 'source/src/reset.s'
    text = source.read_text()
    assert text.count('  jsr OAMandReadJoypad') == 1
    assert 'USE_MOUSE_SUPPORT=0' in (PARENT / 'source/build_options.ini').read_text()
    at = location(b, 'NonMaskableInterrupt::SkipSprite0') + 11
    expected = bytes.fromhex('ad7a078d01202092802000e0')
    assert b['raw'][at:at + 12] == expected
    block_address = address(b, 'NonMaskableInterrupt::SkipSprite0') + 11
    named = sorted(n for n, s in b['syms'].items() if n.startswith('NonMaskableInterrupt::')
                   and block_address <= int(s['val'], 0) < block_address + 12)
    assert not named
    segments = [dict(name=s['name'].strip('"'), start=int(s['start'], 0), size=int(s['size'], 0))
                for s in b['segs'].values() if 'ooffs' in s and (int(s['ooffs'], 0) - 16) // 8192 in [126, 127]]
    comparison = D / 'mm-proto-bootstrap-dma-diagnostic-ready-v1/comparison-v1/proof.json'
    diag = json.loads(comparison.read_text())
    assert diag['diagnostic_analysis_complete'] and not diag['game_or_hardware_equality_pass']
    assert diag['all_raw_events_ordered_semantically_exact']
    bad = diag['cases']['baseline']['first_bad']
    put(a.output / 'actual-first-bad.json', bad)
    timing = dict(
        reported_start=bad['start']['begin'], actual_comparison_sha256=sha(comparison),
        immediate_after_DMA_pair_end_no_stall_model=[phase(513), phase(514)],
        after_controller_pair_end_no_stall_model=[phase(513 + 260), phase(514 + 260)],
        moved_pair_instruction_cycles=8, normal_DMA_start_delta=-8,
        straight_line_instruction_total_delta=0,
        caveat='No candidate executed. DMA callback/write/completion phase, mask response delay, odd-dot skip, DMC and IRQ can change exact dots. This is a feasibility bound; actual same184 frame semantics are retained.')
    put(a.output / 'timing-model.json', timing)
    references = []
    for name, url in [
        ('NesPpu.cpp', 'https://raw.githubusercontent.com/SourMesen/Mesen2/master/Core/NES/NesPpu.cpp'),
        ('MMC5.h', 'https://raw.githubusercontent.com/SourMesen/Mesen2/master/Core/NES/Mappers/Nintendo/MMC5.h')]:
        data = urllib.request.urlopen(url, timeout=30).read()
        (a.output / name).write_bytes(data)
        references.append(dict(path=str(a.output / name), sha256=sha(a.output / name), URL=url,
                               scope='Official upstream source snapshot used for policy explanation; not claimed byte-identical to the running DLL.'))
    put(a.output / 'upstream-source-references.json', references)
    report = '''Current3cee NMI PPUMASK order audit - source-only, 2026-10-26

No ROM candidate is built or launched. Production/default/settings/Git are untouched and no native worker is held. The existing Sophia emitter remains frozen separately. This finite audit rejects enabling after controller polling and records a conditional immediate-post-DMA plan with an explicit placement/address blocker; it does not reject all mask scheduling remedies.

Current ROM is3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99. A's matched220-frame bootstrap diagnostics on3cee and the unexecuted c5 helper have semantically identical streams and one actual hardware inequality among207 DMAs each. DMA171 starts at actual184:256:255, mask30/OAMADDR0. The actual last data write is184:-1:92; completion is184:-1:99/OAMADDR48. Ordinal241 writes at-1:2 with OAMADDR240; ordinal242 at-1:8 sees244 instead of241. First-row source offsets0/1/3/4/7 expected168/2/128/168/120 become248/0/0/248/0. These actual bytes support rendering-time OAM corruption/invalid destinations; this audit does not replace A's detailed first-owner/profile interpretation. The original inequality remains FALSE.

Current source regular NMI disables actual rendering first, flushes pending VRAM/palette/HUD publication, prepares IRQ31 and PPUCTRL, enables Mirror_PPUMASK, publishes CHR, then calls OAMandReadJoypad. Lag NMI follows a different path and does not call the DMA routine. There is one actual source JSR caller. The linked current runtime has USE_MOUSE_SUPPORT0. Its actual assembled OAM/controller routine takes266 instruction cycles without DMA:260 after STA4014 completes.512 CPU cases cover every pad1 byte with complementary pad2 and two incoming flag profiles; exactly8 reads/port and saved input/stack results match. These are current-code CPU cases, not a proposed NMI qualification or real DMC timing proof.

Register liveness supports moving the pair in isolation. LDA Mirror_PPUMASK/STA PPUMASK is8 cycles and preserves C/V/X/Y. BankSwitchCHR immediately loads ReloadCHRBank, overwriting A/NZ; OAM begins LDA2. At a new immediate-post-DMA point, the next native LDX1 and the later LDA4017 overwrite its A/NZ before any use. In the mouse-enabled source branch, the following LDA mouse_mask likewise overwrites A/NZ; its NMI scratch snapshots are untouched. After the full controller return, LDY0/LDX/CPX then LDA0 also make relocated A/NZ dead. Mirror_PPUMASK itself need not change. A canonical rearrangement would advance CHR/DMA8 cycles and restore the pair before continuing; even parity preserves the intended input GET/PUT alignment in the no-extra-stall model. It does not prove asynchronous DMC read timing or input-frame sampling equality.

After-controller option: REJECTED as a standalone fix. From the reported DMA-start phase,513/514 DMA cycles plus260 controller-tail cycles place the moved mask store around the upcoming visible line1 dot187..190 in a341-dot no-stall model. It misses the pre-render horizontal/vertical reload and beginning of visible output. The frame label is not incremented by assumption: actual current saved observations show vblank3064 followed by startFrame3064:-1. An earlier preliminary message said185; that absolute-frame guess is withdrawn. The actual diagnostic and this report retain same184 semantics. Stalls only make this budget later; callback latency/odd-dot behavior prevent claiming an exact new native dot.

Immediate-post-DMA option: CONDITIONALLY PLAUSIBLE for the captured title failure. The same model puts enable near upcoming pre-render-1:89..92, consistent with the actual original transfer ending near-1:92/99. Rendering can remain disabled throughout DMA and then be enabled before horizontal257, vertical280..304 and background prefetch321..339. The original CHR/palette/HUD lease publication still precedes DMA, so the intended atomic image is retained in source order. However this is a bounded title timing opportunity, not a universal late-NMI fix: later packets, DMC/IRQ stalls, mask latency, stale v/t/x/w and missed sprite evaluation can still fail. Every actual first-row destination, first visible scroll/font/palette/body epoch and physical IRQ31 would need fresh native checks.

The official upstream Mesen PPU source conditions pre-render scrolling copies and sprite fetches on rendering state, resets OAMADDR during sprite fetches, and contains the early pre-render row-copy behavior when OAMADDR is nonzero. Its MMC5 source infers scanlines from repeated nametable reads and clears in-frame state after idle cycles. Therefore starting rendering later can affect first-line/sprite0 behavior and scanline IRQ origin. These are reference-policy sources, not a claim that downloaded master files exactly match the pinned local DLL. Source URLs/hashes are saved separately.

Current layout blocks a trivial old-address-preserving insertion. The existing12-byte NMI block atE3D6 is precisely LDA Mirror/STA2001/JSR BankSwitchCHR/JSR OAMandReadJoypad; there is no named NMI label inside it. Reordering this block after the full call keeps its length but is the rejected late option. A literal6-byte post-DMA insertion grows the input routine and moves its real read_loop and later OAMALIGNED helpers by6. OAMALIGNED currently occupiesE000..E051; SAMUS_FREEZE_NMI occupiesE052..E05F; FIXED beginsE060. Bank127's remaining code, crouch helpers and DPCM leave no43-byte clone tail; bank126 ends with its live9-byte freeze helper at9FF6..9FFE. These exact segment boundaries are bound in placement.json.

A coherent zero-instruction-count direct source experiment would have to move the ALIGN/FIXED boundary toE066, insert the6-byte pair after STA4014, and remove its original6 bytes from regular NMI. It would genuinely move reset/Start/NMI-entry and other pre-cut fixed addresses by6; addresses after the removed pair can balance back. There must be no fake old-PC aliases or reuse of old observer PCs. Branch page crossings and controller-loop alignment would need assembled measurement, so it cannot yet be called zero-total-cycle. The alternative of preserving all old addresses with padding/dispatch adds real CPU work and also needs a declared safe helper placement; no such extra variant is built here.

Actionable boundary: retain the after-controller rejection; the narrower immediate-post-DMA schedule deserves at most one separately declared source experiment after ROOT accepts genuine address movement or a measured positive-cost layout. Required controls are complete regular/lag NMI final AXYP/SP/application RAM/banks/fiveSMC, exact intentional PPUMASK ordering, all current CHR/palette/HUD pending/commit/cancel owners, forced blank and both controller/mouse source paths, compiled IRQ interference, honest changed-label inventory and matched actual title/full first-row/scroll/IRQ31 evidence. No complete candidate controls or adoption acceptance are claimed in this audit. Broad late-NMI and DMC coverage remain open.
'''
    (a.output / 'report.txt').write_text(report, encoding='utf-8')
    put(a.output / 'placement.json', dict(current_segments=segments, NMI_original_block_address=block_address,
                                         original12bytes=expected.hex(), named_labels_inside_old_block=named,
                                         direct_insertion_genuine_new_FIXED_start=0xe066,
                                         whole_candidate_address_and_cycle_proof_not_run=True))
    bindings = {str(a.output / f.name): sha(f) for f in a.output.iterdir() if f.is_file()}
    for f in [Path(__file__), PARENT / 'candidate.nes', PARENT / 'candidate.dbg', PARENT / 'candidate.lbl',
              source, PARENT / 'source/src/mmc5.s', PARENT / 'source/build_options.ini',
              PARENT / 'source/smb1base-mmc5-expanded.cfg', comparison,
              D / 'current3cee-vehicle-visibility-v1/sophia/native/visibility-frames.jsonl',
              ROOT / 'tools/audit/check_tmnt_render_oa.py', ROOT / 'tools/audit/link_pit_rygar_sophia_audit_cpu.py',
              ROOT / 'tools/audit/verify_native_relocation.py']:
        bindings[str(f)] = sha(f)
    put(a.output / 'bindings.json', bindings)
    put(a.output / 'proof.json', dict(audit_complete=True, source_only=True, ROM_sha256=SHA,
                                     ROM_candidate_built=False, native_run=False, native_workers_held=0,
                                     after_controller_option_rejected=True,
                                     immediate_post_DMA_conditionally_plausible=True,
                                     old_address_preserving_zero_cost_implementation_proved=False,
                                     current_input_CPU_cases=len(rows), whole_NMI_candidate_controls_run=False,
                                     source_only_implementation_boundary=True,
                                     actual_bootstrap_hardware_failure_preserved=True,
                                     report_sha256=sha(a.output / 'report.txt'), bindings=len(bindings),
                                     manifest_sha256=sha(a.output / 'bindings.json')))
    print(json.dumps(dict(audit_complete=True, no_ROM_candidate=True, bindings=len(bindings),
                          proof_sha256=sha(a.output / 'proof.json'), report_sha256=sha(a.output / 'report.txt'),
                          manifest_sha256=sha(a.output / 'bindings.json')), indent=2))


if __name__ == '__main__':
    main()
