"""Run Mike's source-art arena or established arsenal fixture on an exact ROM."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--behavior', choices=('easy', 'hard'), required=True)
    parser.add_argument('--arsenal', action='store_true')
    parser.add_argument('--expect-negative', action='store_true')
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    hard = int(args.behavior == 'hard')
    if args.arsenal:
        source = ROOT / 'build/mike-kd-private/arsenal-c.lua'
        text = source.read_text()
        old = 'emu.setInput({start=f==60,down=f==100 or f==120,right=f==140 or f==160,a=f==180,select=select,b=b},0)'
        assert text.count(old) == 1
        text = text.replace(old, '''local buttons={select=select,b=b}
 if r('OperMode')~=1 or r('OperMode_Task')~=3 or r('GameEngineSubroutine')~=8 then
  if f>=60 and f%12==0 then
   if r('CrossoverMenuState')~=2 then buttons.start=true
   elseif r('CrossoverMenuIndex')<12 then buttons.down=true
   elseif r('CrossoverMenuIndex')~=15 then buttons.right=true else buttons.a=true end
  end
 end
 emu.setInput(buttons,0)''')
        text = text.replace(' f=f+1', " f=f+1\n if f==60 then w('CrossoverBehaviorVersion'," + str(hard) + ')end')
        # The old single wall-frame B edge is missed by the sampled input;
        # source trace shows SavedJoypad/Pressed remain zero at1491. Hold an
        # ordinary fresh B edge for three frames, and observe the split before
        # the downward blade reaches SMB ground. No game/terrain edits.
        assert text.count('if f==1490 then b=true end') == 1
        text = text.replace('if f==1490 then b=true end', 'if f>=1489 and f<1492 then b=true end')
        assert text.count('if f==1495 then') == 1
        text = text.replace('if f==1495 then', 'if f>=1491 and f<=1495 then')
        text = text.replace('split=(a==3 or a==253)and(b==3 or b==253)',
                            'split=split or((a==3 or a==253)and(b==3 or b==253))')
    else:
        source = ROOT / 'tests/mike-source-art.lua'
        text = 'BEHAVIOR=' + str(hard) + '\n' + source.read_text()
    script = out / 'fixture.lua'; script.write_text(text)
    spec = importlib.util.spec_from_file_location('nx_mesen', ROOT / 'tools/run_mesen.py')
    runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner); runner.ROOT = out
    code = runner.run(script, args.rom.resolve(), timeout=55, emulator_options=[
        '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
        '--nes.randomizeMapperPowerOnState=false'])
    if args.expect_negative:
        assert code != 0
        log = next((out / 'build/verification').glob('*.log')).read_text()
        assert 'Native star has both source halves' in log
    else:
        assert code == 0
    files = {p.relative_to(out).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p))
             for p in out.rglob('*') if p.is_file()}
    report = dict(passed=code == 0, expected_negative=args.expect_negative, exit=code,
                  ROM_sha256=sha(args.rom), original_fixture_sha256=sha(source),
                  actual_fixture_sha256=sha(script), behavior=args.behavior, arsenal=args.arsenal,
                  retained_files=files,
                  scope='Cold real menu, then arranged native component interactions. No 1-1 campaign clear/every-item final matrix claim.')
    (out / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'retained_files'}))


if __name__ == '__main__':
    main()
