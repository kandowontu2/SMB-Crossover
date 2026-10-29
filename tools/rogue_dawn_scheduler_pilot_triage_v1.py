"""Read-only f467 pilot/palette diagnosis and finite real-NMI cost attribution."""
from pathlib import Path
from collections import Counter, defaultdict
import csv
import json
import sys

R = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R/'tools'), str(R/'tools/audit')]
import rogue_dawn_scheduler_controls_v3 as v
from verify_native_relocation import NesMPU

O = R/'build/rogue-dawn-scheduler-v5'
N = R/'build/verification/rogue-dawn-scheduler-native-easy-v1'
OUT = R/'docs/qa/rogue-dawn-first-pilot-triage-2026-10-29.json'
q, get, put, address = v.q, v.get, v.put, v.address


def profile(m):
    b = m.bundle
    targets = {
        'RdaBorrow': 62, 'RdaRelease': 62, 'RdaAudioInit': 62,
        'RdaNA770': 97, 'RdaOriginalRng': 97, 'RdsAudioFrame': 62,
        'RdaReadAbsoluteY': 62, 'RdaReadAbsolute': 62,
        'RdaReadE6Y': 62, 'RdaReadECY': 62, 'RdaReadRom': 97,
        'GuestAudioBegin': 29, 'GuestAudioFinishTick': 29,
        'GuestAudioNativeFlush': 29,
    }
    # Actual assembler export is the local Tick entry inside GuestAudioFinish.
    keys = {(address(b, 'GuestAudioFinish::Tick' if n == 'GuestAudioFinishTick' else n), k): n
            for n, k in targets.items()}
    active, spans = [], defaultdict(list)
    by_bank = Counter()
    direct_original = 0
    old = NesMPU.step

    def step(c):
        nonlocal direct_original
        if c.memory is not m:
            return old(c)
        pc, bank = q.key(m, c)
        name = keys.get((pc, bank))
        if name:
            ret = (m[0x101+c.sp] + 256*m[0x102+c.sp] + 1) & 65535
            active.append((name, ret, c.sp+2, c.processorCycles))
        before = c.processorCycles
        result = old(c)
        delta = c.processorCycles-before
        by_bank[str(bank)] += delta
        if bank == 97 and 0xc480 <= pc < 0xe000:
            direct_original += delta
        for item in active[:]:
            name, ret, sp, start = item
            if c.pc == ret and c.sp == sp:
                spans[name].append(c.processorCycles-start)
                active.remove(item)
        return result

    NesMPU.step = step
    try:
        z = v.nmi(m)
    finally:
        NesMPU.step = old
    assert not active, active
    timing = {n: dict(calls=len(rows), inclusive_CPU=sum(rows), maximum=max(rows))
              for n, rows in spans.items()}
    readers = sum(timing.get(n, {}).get('inclusive_CPU', 0) for n in
                  ['RdaReadAbsoluteY', 'RdaReadAbsolute', 'RdaReadE6Y', 'RdaReadECY'])
    return dict(full_lagNMI_CPU=z['CPU'], minimum_SP=z['minimum_SP'],
                dynamic_calls=timing, reader_envelopes_CPU=readers,
                translated_original_C97_C480_DFFF_instruction_CPU=direct_original,
                all_instruction_CPU_by_physical_bank=dict(by_bank),
                accounting='Inclusive dynamic call spans overlap their children. reader_envelopes contains four disjoint entry types; rawreader is nested within them. C97 source-range instruction tally is exclusive by actual executed instruction address, including real replacement JSR cost.')


def packets(m):
    at = address(m.bundle, 'VRAM_Buffer1')
    end = get(m, 'VRAM_Buffer1_Offset')
    data = bytes(m[at:at+end+1])
    i, out = 0, []
    while i < end:
        hi, lo, flags = data[i:i+3]
        length = flags & 63
        payload = data[i+3:i+4] if flags & 64 else data[i+3:i+3+length]
        out.append(dict(address=hex(hi*256+lo), flags=flags, payload=payload.hex()))
        i += 3 + (1 if flags & 64 else length)
    assert i == end and data[-1] == 0
    return dict(raw=data.hex(), commands=out)


def main():
    assert not OUT.exists(), 'Frozen triage'
    hand = json.loads((O/'handoff.json').read_text())
    for z in hand['bindings']:
        assert v.ref.binding(z['path']) == z, z['path']
    b = v.scoped_load(O/'candidate.nes')
    costs = []
    for area, ticks in [(1, 4), (0, 3)]:
        m = v.prepared(b, area)
        for tick in range(ticks):
            put(m, NmiDisable=255)
            m[0x5fb6] = 2*(tick % 3 if tick else 0)
            z = profile(m)
            costs.append(dict(area=area, tick=tick, **z))
    colors = []
    for variant in [0, 1]:
        for area, control in [(0,0),(1,0),(2,0),(3,0),(1,4),(1,5)]:
            m = q.make(b, 0)
            put(m, RdVariant=variant, AreaType=area, BackgroundColorCtrl=control,
                VRAM_Buffer1_Offset=0, RdColorRequest=1)
            q.invoke(m, 'GetPlayerColors')
            z = packets(m)
            colors.append(dict(variant=variant, AreaType=area, BackgroundColorCtrl=control,
                               **z))
    rogue = [z for z in colors if z['variant'] == 1]
    samus = [z for z in colors if z['variant'] == 0]
    assert all(not any(c['address'] in ['0x3f10','0x3f00'] for c in z['commands']) for z in rogue)
    assert all(any(c['address']=='0x3f10' for c in z['commands']) for z in samus)
    rows = list(csv.DictReader((N/'trace.csv').open()))
    terminal = rows[-1]
    tail = [z for z in rows if int(z['frame']) >= 700]
    result = json.loads((N/'result.json').read_text())
    output = dict(
        source_CPU_and_existing_native_evidence_only=True, new_native_run=False,
        no_source_ROM_or_settings_changes=True, candidate=v.ref.binding(O/'candidate.nes'),
        source_handoff=v.ref.binding(O/'handoff.json'),
        native_first_failure=dict(result=v.ref.binding(N/'result.json'), reason=result['reason'],
             completed_Main=result['completed_loops'], full_frames=result['full_frames'],
             completed_DMA=result['completed_DMAS'], min_SP=result['min_SP'],
             terminal_trace=terminal, mask_counts_last_window=dict(Counter(z['mask'] for z in tail))),
        controller=dict(
            exact_source='Original source D0E1/D0E3 uses RdFresh AND08 freshUp, then real upward clearance atD0FA and unmorph atD110/D116. Down-held is a separate path. RdHostInput derives fresh=(SavedJoypadBits XOR RdHeld) AND SavedJoypadBits once per actualMain.',
            actual_policy='roster_samus_contra.lua sets Up in its SmBall branch but then first-upgrade code replaces b={} before its bump logic. Final native mask128 is onlyA. This is a definite overwritten-input policy path; source ball state in the real native run is inferred from ROOT wholeframe, not present in this CSV.',
            limitation='No real native source-action/RdFresh snapshot exists in v1. No terrain/movement fix follows solely from this read-only diagnosis. ROOT owns subsequent standing-only controller.',
            erratum='Frozen scheduler report quoted ROOT provisional Down-toggle hypothesis in native-pilot status. Actual original admitted kernel requires freshUp as above; source CPU proof itself is unchanged.'),
        palette=dict(
            genuine_complete_GetPlayerColors_calls=colors,
            diagnosis='Exact raw2/RdVariant1 NrColors->RdBodyColors bypasses X5LegacyGetPlayerColors and its native BackgroundColors mirror restore. Rogue body queue correctly writes only3F11/3; it never restores universal3F00/3F10 on scene/lives transition. This is omitted host backdrop restoration, not an authenticated Rogue source0F write to3F10.',
            actual_source_native_colors='BackgroundColorCtrl nonzero else AreaType indexes native BackgroundColors[22,22,0F,0F,0F,22,0F,0F]. Ground1/control0 requires22. Existing X5QueueAreaBackdrop uses the same table.',
            minimal_successor='At exact owned color/lifecycle publication compose native universal background with source body three colors, preserving all world palettes and source suit/missile colors. Prefer one atomic3F10/4 packet with native backdrop+three source colors; guard full7-byte queue capacity and ACK only completecommit. Do not restore original Rogue nighttime backdrop or overwrite world palette1..3.',
            limitations='Actual native pilot log lacks PPU palette-write chronology, so no claim about the first physical black-sky writer. Native wholeframe black sky plus actual missing transition restore is concrete; eventual private fix needs real scene/coldmenu validation and deadline.'),
        performance=dict(cases=costs,
            conclusion='Borrow/Release swap only19 explicit ZP bytes each every driver tick, not512B. The512B image clears only on actual acquisition. Quantified dynamic spans below distinguish original translated driver, rawreader, mixer and context costs.',
            actionable_paths=[
                'Measure and reduce actual raw-ROM getter cost while retaining full original data views and every source read value/flag/callsite. Favor existing direct immutable table/data copies only after exact executed-code/reader closure; no new lease assumed.',
                'Unroll or direct-project the19 known ZP save/restore pairs only if measured benefit exceeds code space, with complete foreground/old-owner/IRQ preservation. NMI owns private state; do not skip source ticks.',
                'Profile real Main RdControl/terrain/render and original driver separately before claiming60FPS. Shared mixer work and original upper driver body remain genuine required costs.',
            ],
            limits='Finite representative initialized CPU cases, not a full differential rerun or universal maximum. Hardware DMA514, DMC steals, PPU line/dot and native audio playback are excluded; no clockskip/muting/behavior reduction authorized.'),
        bindings=[v.ref.binding(p) for p in [Path(__file__), O/'candidate.nes', O/'candidate.dbg',
            O/'candidate.lbl', O/'handoff.json', N/'result.json', N/'trace.csv', N/'inputs.csv',
            N/'events.jsonl', R/'tools/playthroughs/roster_samus_contra.lua',
            R/'tools/playthroughs/roster_samus_contra_nav.lua',
            U if False else R/'src/rogue_dawn_control.s', R/'src/rogue_dawn_host.s',
            R/'build/rogue-dawn-host-ui-v1/body-source.s',
            R/'build/rogue-dawn-host-ui-v1/new_roster_dispatch.s', R/'src/x5_palette.s']],
    )
    OUT.write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps(dict(passed_readonly_diagnosis=True, report=v.ref.binding(OUT),
                         profiles=[(x['area'],x['tick'],x['full_lagNMI_CPU'],
                                    x['reader_envelopes_CPU']) for x in costs]), indent=2))


if __name__ == '__main__':
    main()
