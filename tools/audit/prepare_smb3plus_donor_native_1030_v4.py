"""Bounded native donor discovery with explicit controller/capture schedule."""
from pathlib import Path
import argparse
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_smb3plus_donor_native_1030_v1 as P


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--start',type=int,nargs='+',required=True)
    parser.add_argument('--snapshots',type=int,nargs=3,required=True)
    parser.add_argument('--buttons',default='',help='Comma-separated frame:button pulses; each lasts4 frames.')
    args=parser.parse_args()
    out=args.output.resolve()/'discovery'
    assert out.is_relative_to(P.R/'build')and not out.exists()
    assert P.sha(P.DONOR)==P.EXPECTED
    end=max(args.snapshots);assert 300<=end<=3600 and all(0<t<end for t in args.start)
    pulses=[(f,'start')for f in args.start]
    if args.buttons:
        for item in args.buttons.split(','):
            f,key=item.split(':');f=int(f)
            assert key in ['A','B','up','down','left','right','select']and 0<f<end
            pulses.append((f,key))
    out.mkdir(parents=True)
    source=P.R/'tools/reference/smb3plus_donor_discovery_1030_v2.lua'
    text=source.read_text()
    a=text.index('    local start =');b=text.index('    if frame % 30',a)
    text=text[:a]+'''    local input = {}
    for _, pulse in ipairs(PULSES) do
        if frame >= pulse[1] and frame < pulse[1] + 4 then input[pulse[2]] = true end
    end
    local start = input.start
    emu.setInput(input, 0, 0)
'''+text[b:]
    schedule='{'+','.join('{'+str(f)+',"'+key+'"}'for f,key in pulses)+'}'
    text='local PULSES = '+schedule+'\n'+text
    text=text.replace('frame == 120 or frame == 240 or frame == 360',' or '.join('frame == '+str(f)for f in args.snapshots))
    text=text.replace('if frame == 360 then',f'if frame == {end} then')
    text=text.replace("dump('ram' .. frame .. '.bin', 2048, emu.memType.nesDebug)",
        "dump('ram' .. frame .. '.bin', 32768, emu.memType.nesDebug)\n        dump('ppu' .. frame .. '.bin', 16384, emu.memType.nesPpuDebug)")
    (out/'controller.lua').write_text(text,encoding='utf-8',newline='\n')
    (out/'run.py').write_bytes((P.R/'build/peach-palette-native-1030-v1/peach/run.py').read_bytes())
    own=[Path(__file__),Path(P.__file__),source,P.DONOR,out/'controller.lua',out/'run.py',
         P.R/'tools/run_mesen.py',P.R/'tools/audit/capture_budget.py',Path('C:/mesen2/Mesen.exe')]
    d=dict(prepared=True,native=False,ROM=str(P.DONOR),ROM_sha256=P.EXPECTED,host_timeout_seconds=60,
        run_cap_bytes=536870912,max_files=64,max_PNGs=3,no_debug_RAM_writes=True,
        input_pulses=pulses,snapshots=args.snapshots,end_frame=end,
        bindings={str(p):P.sha(p)for p in own})
    (out/'ready.json').write_text(P.json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(P.json.dumps(dict(prepared=str(out/'ready.json'),source=P.EXPECTED)))


if __name__=='__main__':main()
