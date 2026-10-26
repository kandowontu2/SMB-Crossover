"""Finite source inventory: SMB3 normal-track pilot and existing Parodius proofs.

No music conversion, placement, game-source writes, or native emulator launch.
The 600-call pilot is a lower bound, not SMB3 driver closure or native cadence.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import struct

from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from mike_parodius_music_probe import Bus, spans
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OLD = D/'tmnt-native-storage-current50b5-v1/current-baseline-v1'
NEW = D/'cv3-remaining-legacy-wrapper-v2'
P = D/'parodius-native-music-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    out = ap.parse_args().output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    oldrom, newrom = OLD/'baseline.nes', NEW/'candidate.nes'
    assert sha(oldrom) == '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
    assert sha(newrom) == '2cb5fca0757c3e347c264eab0bf3f22bd02d851787f38802a4af3cb0c3aa1fa5'
    old, new = scoped_load(oldrom), scoped_load(newrom)
    route_spans = {}
    for name in ['VgAudioDispatch', 'KbAudioFamily', 'ExpandedAudioUpdate', 'ExpandedAudioTick']:
        n = int(old['syms'][name]['size'], 0)
        po, pn = location(old, name), location(new, name)
        assert address(old, name) == address(new, name)
        assert n == int(new['syms'][name]['size'], 0)
        assert old['raw'][po:po+n] == new['raw'][pn:pn+n]
        route_spans[name] = dict(address=address(new, name), bytes=n, physical_offset=pn,
                                 sha256=hashlib.sha256(new['raw'][pn:pn+n]).hexdigest())
    sources = {}
    for name in ['expanded_audio.s', 'gradius_audio.s', 'mac_native_music.s', 'mike_native_music.s']:
        a, b = OLD/'source/src'/name, NEW/'source/src'/name
        assert a.read_bytes() == b.read_bytes()
        sources[name] = dict(old=str(a), current=str(b), sha256=sha(b))
    routes_path = P/'current50b5-routes-v1/proof.json'
    assert sha(routes_path) == '39e3a33b8ae2f669eeb20bc56eb1b889b799712f336a7fd8741252993bf6e16e'
    requested = {'SMB3 Mario', 'SMB3 Luigi', 'Octopus', 'TwinBee', 'Pentarou'}
    rows = [r for r in json.loads(routes_path.read_text())['rows'] if r['identity'] in requested]
    assert len(rows) == 5 and all(r['source_music'] == ['Kid Icarus/Pit'] for r in rows)

    nsf = ROOT/'reference/new-roster-audio/mario3/crossover-named.nsf'
    nsfe = ROOT/'reference/crossover2/extracted/binaryData/254_com.explodingRabbit.cross.games.GameSuperMarioBros3_Nsfe.bin'
    raw, ext = nsf.read_bytes(), nsfe.read_bytes()
    assert sha(nsf) == '4f22166e5baf4db867564b57c3d152dacb85b6365f7bf94cf0883d612e7f915c'
    assert sha(nsfe) == '7b86c232cbd9643042fba9285a1ec900ce7544f8f33a3202e31ffe8950868aa3'
    chunks, pos = {}, 4
    while pos < len(ext):
        n = struct.unpack_from('<I', ext, pos)[0]
        key = ext[pos+4:pos+8].decode('ascii')
        chunks[key] = ext[pos+8:pos+8+n]
        pos += n+8
    assert raw[128:] == chunks['DATA']
    labels = chunks['tlbl'].rstrip(b'\0').decode('utf-8').split('\0')
    planpath = ROOT/'reference/new-roster-audio/playlist-plan.json'
    plan = json.loads(planpath.read_text())['mario3']['tracks']
    tracks = {role: dict(one_based_track=n, source_label=labels[n-1]) for role, n in plan.items()}
    load, init, play = struct.unpack_from('<HHH', raw, 8)
    assert (load, init, play) == (0x8000, 0x9000, 0xa000)
    m, executed, cycles, call_rows = Bus(raw), set(), [], []
    c = NesMPU(memory=m)
    for tick in range(601):
        c.pc, c.a, c.x, c.y, c.p, c.sp = (init if tick == 0 else play), (8 if tick == 0 else 0), 0, 0, 0x24, 0xfd
        list.__setitem__(m, 0x1fe, 0xff)
        list.__setitem__(m, 0x1ff, 0x7e)
        m.events, m.mapper = [], []
        before = c.processorCycles
        for _ in range(100000):
            if c.pc == 0x7f00:
                break
            assert c.pc >= 0x8000
            executed.add(m.physical(c.pc))
            c.step()
        else:
            raise AssertionError(('SMB3 pilot timeout', tick, hex(c.pc)))
        assert c.sp == 0xff
        elapsed = c.processorCycles-before
        if tick:
            cycles.append(elapsed)
        call_rows.append(dict(tick=tick, cycles=elapsed, APU=m.events, mapper=m.mapper, banks=m.maps.copy()))
    assert not m.io_reads and not m.bad_writes
    pilot_path = out/'smb3-track09-601-source-calls.json'
    pilot_path.write_text(json.dumps(call_rows, separators=(',', ':'))+'\n', encoding='utf-8')
    pilot = dict(one_based_track=9, play_calls=600, init_cycles=call_rows[0]['cycles'],
                 mean_play_cycles=sum(cycles)/600, p95_nearest_rank=sorted(cycles)[math.ceil(.95*600)-1],
                 peak_play_cycles=max(cycles), ordered_APU_stores=sum(len(r['APU']) for r in call_rows),
                 distinct_executed_instruction_entries=len(executed), ROM_read_bytes=len(m.rom_reads),
                 RAM_read_ranges=spans(m.ram_reads), RAM_write_ranges=spans(m.ram_writes),
                 DPCM_payload_ranges_inclusive=spans(m.sample_ranges), DPCM_bytes=len(m.sample_ranges),
                 unmodeled_IO_reads=dict(m.io_reads), unexpected_ROM_writes=m.bad_writes,
                 call_log=dict(path=str(pilot_path), sha256=sha(pilot_path)))
    mulpath = P/'multiply-v3/proof.json'
    mul = json.loads(mulpath.read_text())
    assert sha(mulpath) == '545dcadba7f30f180dc671e8c6c89f4af8e30a301810f58026db3f2ba7157136'
    parodius = [dict(identity=name, original_request=req, **next(r for r in mul['rows'] if r['song'] == req))
                for name, req in [('Octopus', 0x52), ('TwinBee', 0x56), ('Pentarou', 0x5a)]]
    dependencies = [Path(__file__), ROOT/'tools/audit/mike_parodius_music_probe.py',
                    ROOT/'tools/audit/verify_native_relocation.py', ROOT/'tools/audit/check_tmnt_render_oa.py',
                    ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py', nsf, nsfe, planpath,
                    oldrom, oldrom.with_suffix('.dbg'), newrom, newrom.with_suffix('.dbg'), routes_path,
                    mulpath, P/'ready-v1/receipt.json', P/'data-plan-current50b5-v3/proposal.json',
                    ROOT/'reference/new-roster-audio/encoding-report.json']
    proof = dict(passed=True, source_inventory_only=True, production_writes=False,
                 native_emulator_launched=False, RAM_or_PRG_allocations=False,
                 old_ROM_sha256=sha(oldrom), current_ROM_sha256=sha(newrom),
                 unchanged_compiled_route_spans=route_spans, unchanged_source_files=sources,
                 inherited_five_identity_routing=rows, SMB3=dict(NSF_bytes=len(raw), payload_bytes=len(raw)-128,
                    original_songs=raw[6], load=load, init=init, play=play, NSF_banks=list(raw[112:120]),
                    period_microseconds=struct.unpack_from('<H', raw, 110)[0], exact_Crossover_NSFE_DATA=True,
                    existing_role_plan=tracks, bounded_normal_track_pilot=pilot),
                 Parodius_existing_original_and_optimized_costs=parodius,
                 dependencies={str(p):sha(p) for p in dependencies},
                 limits='One original SMB3 normal track for 600 updates; observed RAM/DPCM are lower bounds. No SMB3 pointer closure, adapter, placement or native timing claim. Parodius costs inherited exactly from earlier full-source CPU proof. Old A62/C94 proposal unavailable because ROOT now reserves them for Chip. No bank124 release assumed.')
    (out/'proof.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, proof=str(out/'proof.json'), sha256=sha(out/'proof.json'),
                          SMB3_pilot=pilot, parodius=parodius), indent=2))


if __name__ == '__main__':
    main()
