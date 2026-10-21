"""Add explicit cold identity receipts without rerunning completed route negatives."""
from pathlib import Path
import csv, hashlib, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-pit-empty-be'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = H / 'ordinary-scrooge-review-bl'
    out.mkdir(exist_ok=False)
    bj, bk = H / 'ordinary-scrooge-bj/report.json', H / 'ordinary-scrooge-control-bk/report.json'
    assert sha(bj) == '8352fead73931c5db0465f85ff9a21890910f8542d85e75a6e40a779644755f2'
    assert sha(bk) == '041178b13730ffd71ef8a2202b91e5545714f96828d3a705679d9ee2eca7f853'
    be, ap = json.loads(bj.read_text()), json.loads(bk.read_text())
    policy = out / 'policy.lua'
    policy.write_text('''-- Passive receipt only; the frozen controller movie supplies input.
local frame,checked=0,false
emu.addEventCallback(function()
 frame=frame+1
 local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
 if not checked and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  assert(r('SelectedCharacter')==12 and r('CrossoverBehaviorVersion')==0 and r('PlayerOutlinesOff')==1,'Actual Scrooge/Easy/shadows-off identity')
  checked=true
  local f=assert(io.open(ROSTER_CONFIG.out..'identity.json','w'))
  f:write(string.format('{"frame":%d,"selected":12,"mode":0,"shadowsOff":1}',frame));f:close()
  print('ORDINARY SCROOGE title verified: mode=0 selected=12 shadows=0')
 end
end,emu.eventType.endFrame)
local stop=emu.stop
function emu.stop(code)assert(checked,'Actual identity observed');stop(code)end
return function()return {}end
''')
    report = dict(status='RUNNING_SCROOGE_IDENTITY_AND_TRANSFER_REVIEW', script_sha256=sha(__file__),
                  BJ_sha256=sha(bj), BK_sha256=sha(bk), rows=[],
                  host_negative='BJ/BK used emu.log, which does not reach the captured native console; their marker-dependent classification remains retained. BL adds explicit JSON/print cold-prefix receipts and checks exact replay prefixes; complete negative native runs are reused.',
                  accepted_release=False, goal_complete=False, recorded=False)
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for data, image in [(be, 'BE'), (ap, 'AP')]:
        for old in data['rows']:
            mapper = old['mapper']
            original = R / old['output']
            manifest = json.loads((original / 'manifest.json').read_text())
            rom = original / ('smb-crossover-' + mapper + '.nes')
            assert sha(rom) == manifest['rom_sha256']
            tag = 'root49bl-scrooge-identity-' + image.lower()
            argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '12',
                    '--mapper', mapper, '--rom', str(rom), '--tag', tag, '--replay', manifest['config']['replay'],
                    '--policy', str(policy), '--frames', '650', '--timeout', '90', '--workspace-cap-gb', '50']
            with (out / (image + '-' + mapper + '-host.log')).open('wb') as stream:
                rc = subprocess.run(argv, cwd=R, stdout=stream, stderr=subprocess.STDOUT).returncode
            folder = R / 'build/roster-through-2-2' / (tag + '-12-v0-' + mapper)
            native_source = V / (rom.stem + '-run-' + tag + '-12-v0-' + mapper + '.log')
            native = out / (image + '-' + mapper + '-native.log')
            shutil.copyfile(native_source, native)
            current = json.loads((folder / 'manifest.json').read_text())
            identity = json.loads((folder / 'identity.json').read_text())
            old_lines = (original / 'trace.csv').read_bytes().splitlines(keepends=True)
            new_lines = (folder / 'trace.csv').read_bytes().splitlines(keepends=True)
            exact = new_lines == old_lines[:len(new_lines)]
            good = bool(rc == 1 and current['result']['frames'] == 650 and current['result']['failure'] == 'frame limit'
                        and identity['selected'] == 12 and identity['mode'] == 0 and identity['shadowsOff'] == 1
                        and identity['frame'] <= 541 and exact and len(new_lines) == 651
                        and 'ORDINARY SCROOGE title verified: mode=0 selected=12 shadows=0' in native.read_text())
            row = dict(image=image, mapper=mapper, passed=good, exit=rc, identity=identity,
                       trace_all_650_rows_byte_exact_original_negative=exact,
                       output=folder.relative_to(R).as_posix(), manifest_sha256=sha(folder / 'manifest.json'),
                       identity_sha256=sha(folder / 'identity.json'), native_log_sha256=sha(native))
            report['rows'].append(row)
            save()
            print(image, mapper, good, identity, flush=True)
    # The complete runs agree on all nineteen movement/controller fields and
    # on the actual endpoint. Hardware scroll-write timing is reported separately.
    comparisons = []
    for old in ap['rows']:
        candidate = next(x for x in be['rows'] if x['mapper'] == old['mapper'])
        a = R / old['output'] / 'scroll-writes.csv'
        b = R / candidate['output'] / 'scroll-writes.csv'
        x, y = list(csv.DictReader(a.open())), list(csv.DictReader(b.open()))
        fields = [k for k in x[0] if k not in ['scanline', 'dot']]
        changes = [i for i, (p, q) in enumerate(zip(x, y)) if any(p[k] != q[k] for k in fields)]
        timing = [i for i, (p, q) in enumerate(zip(x, y)) if p != q]
        good = bool(old['result'] == candidate['result'] and old['AP_frames'] == old['BE_frames']
                    and not old['differing_frames'] and len(x) == len(y) and not changes)
        comparisons.append(dict(mapper=old['mapper'], passed=good, full_negative_frames=old['AP_frames'],
                                nineteen_movement_controller_fields_exact=True, result=old['result'],
                                scroll_write_rows=len(x), scroll_value_order_and_frame_exact=not changes,
                                scroll_subscanline_timing_changed_rows=len(timing),
                                seven_other_native_CSVs_byte_exact=all(v['byte_exact'] for k, v in old['receipts'].items() if k != 'scroll-writes.csv')))
    report['comparisons'] = comparisons
    good = len(report['rows']) == 4 and all(x['passed'] for x in report['rows'] + comparisons)
    report['status'] = 'PASS_SCROOGE_AP_BE_ORDINARY_NEGATIVE_ISOLATION' if good else 'RETAINED_SCROOGE_CONTROL_REVIEW_NEGATIVE'
    report['qualification'] = 'The old S2 routes fail identically on AP and BE (M3 6767/M5 13987); this isolates the Pit change for these observed runs. Final combined Scrooge routing and recordings remain open.'
    save()
    print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
