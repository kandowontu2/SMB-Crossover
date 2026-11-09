"""Compose a Mini performance candidate and run the existing bounded native replays."""

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from compose_mini_frame_budget_1108 import check_full_cpu, compose, load
from measure_column_graphics_1109 import BASE, PIN, ROOT, M
from observe_chip_committed_write import lua
from prepare_mini_mario_native_smoke_1103_v25 import labels
from prepare_selected_native_packet_v1 import prepare, sha


QA = ROOT/'build/mini-parser-lift-qa-1109'
OLD_KERNEL = ROOT/'build/mini-fireball-gbc-1108/mini-lift.bin'


def build(output, paths):
    raw = BASE.read_bytes()
    assert M.sha(raw) == PIN
    candidate = bytearray(raw)
    exclusions = {}
    for path in paths:
        proof = load(path)
        if 'kernel_size' in proof:
            irq = load(path.with_name('irq.json'))
            assert irq['passed'] and irq['base_SHA256'] == PIN and irq['proof_SHA256'] == sha(path)
            assert irq['image_SHA256'] == proof['expected_memory_only_SHA256']
            # These ranges contain executable code and matching authentication bytes.
            exclusions = {2: [(0x1fe3,0x1ff0)], 3: [(0,5120),(0x1fe3,0x1ff0)]}
        compose(raw,candidate,proof,parent=PIN)
    rows = check_full_cpu(raw,candidate,exclusions)
    assert all(row['min_saved'] >= 0 for row in rows), rows
    output.mkdir()
    rom = output/'candidate.nes'
    rom.write_bytes(candidate)
    for suffix in ('.dbg','.lbl'):
        shutil.copyfile(BASE.with_suffix(suffix),rom.with_suffix(suffix))
    data = load(BASE.with_suffix('.json'))
    data.update(parent_SHA256=PIN,candidate_SHA256=sha(rom),whole_GameCore=rows,
                performance_proofs={str(path):sha(path) for path in paths})
    rom.with_suffix('.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(ROM_SHA256=sha(rom),whole_GameCore=rows)),flush=True)


def bind_kernel(text, kernel):
    binary, symbols = kernel.read_bytes(), labels(kernel.with_suffix('.lbl'))

    def relink(match):
        name = match[1]
        pc = symbols[name]
        data = binary[pc-0xa000:pc-0xa000+4]
        assert len(data) == 4, name
        return lua(dict(name=name,pc=pc,physical=pc-0x4000,memory='nesWorkRam',bytes=list(data)))

    text = re.sub(r'\{\["name"\]="(Mini\w+)",\["pc"\]=\d+,\["physical"\]=\d+,'
                  r'\["memory"\]="nesWorkRam",\["bytes"\]=\{[\d,]+\}\}', relink,text)
    text = text.replace(sha(OLD_KERNEL),sha(kernel))
    for name in ('MiniHostMain','MiniStep','MiniNativeTile','MiniAnimate','MiniHostDraw','MiniHostBox','MiniNativeDraw'):
        text = re.sub(r'(\["'+name+r'"\]=\{)\d+,-1\}',r'\g<1>'+str(symbols[name])+',-1}',text)
    return text


def observe_columns(rom):
    image = M.bundle(rom.read_bytes())
    addr = lambda name:M.address(image,name)
    at = M.location(image,'MTileAttribute')
    attrs = list(image['raw'][at:at+256])
    names = ('RenderAreaGraphics','AreaParserTaskNum','CurrentColumnPos','AttributeBuffer','MetatileBuffer')
    config = lua({**{n:addr(n) for n in names},'physical':M.location(image,'RenderAreaGraphics')-16,'attrs':attrs})
    return '\nlocal columnConfig='+config+'''
local completedPairs, leftCount, left = 0, 0, nil
emu.addMemoryCallback(guard(function()
 local loc=emu.convertAddress(columnConfig.RenderAreaGraphics)
 if not loc or loc.memType~=emu.memType.nesPrgRom or loc.address~=columnConfig.physical then return end
 local task=read(columnConfig.AreaParserTaskNum)
 local column=read(columnConfig.CurrentColumnPos)
 local tiles={}
 for row=0,12 do tiles[row]=read(columnConfig.MetatileBuffer+row) end
 if task==7 or task==3 then
  left={task=task,column=column,tiles=tiles}
  leftCount=leftCount+1
 else
  assert(left and left.task==task+1 and left.column==column,'Native right column follows paired left column')
  for row=0,12 do
   assert(tiles[row]==left.tiles[row],'Paired native metatile column remains stable')
   local palette=columnConfig.attrs[tiles[row]+1]&0xc0
   local bitShift=2*(column&1)+4*(row&1)
   local mask=(palette>>6)<<bitShift
   local actual=read(columnConfig.AttributeBuffer+(row>>1))
   assert(actual&mask==mask,'Previous terrain pass already published palette bits')
  end
  left=nil
  completedPairs=completedPairs+1
 end
end),emu.callbackType.exec,columnConfig.RenderAreaGraphics)
local oldProfileFinish=profileFinish
profileFinish=function()
 oldProfileFinish()
 local file=assert(io.open(OUTPUT..'column-pairs.json','w'))
 file:write(json({pairs=completedPairs,left=leftCount}));file:close()
end
'''


def run_suite(output, rom, kernel, suites):
    manifest = rom.with_suffix('.json')
    digest = sha(rom)
    output.mkdir(exist_ok=True)
    for suite in suites:
        before = QA/suite/'controller.lua'
        text = before.read_text()
        assert PIN in text
        text = text.replace(PIN,digest)
        refs = [before,manifest,Path(__file__)]
        if kernel:
            text = bind_kernel(text,kernel)
            refs.extend((kernel,kernel.with_suffix('.lbl')))
        if suite == 'route':
            text += observe_columns(rom)
        run_root = output/suite
        prepare(run_root,rom,text,refs,expected=digest,timeout=180,allow_interactive=True,
                scope=f'Existing Mini {suite} controller regression on exact performance candidate.')
        subprocess.run([sys.executable,'-B',run_root/'run.py'],check=True)
        if suite == 'route':
            result = load(run_root/'capture/column-pairs.json')
            assert result['pairs'] > 100 and result['left'] >= result['pairs'], result
            timing = load(run_root/'capture/timing.json')['cadence']['fullstage']
            print(json.dumps(dict(column_pairs=result,fullstage=timing)),flush=True)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('action',choices=('build','test'))
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--proof',type=Path,action='append')
    cli.add_argument('--rom',type=Path)
    cli.add_argument('--kernel',type=Path)
    cli.add_argument('--suite',action='append',choices=('route','idle','power','fire'))
    args = cli.parse_args()
    if args.action == 'build':
        assert args.proof
        build(args.output,args.proof)
    else:
        assert args.rom and args.suite
        run_suite(args.output,args.rom,args.kernel,args.suite)


if __name__ == '__main__':
    main()
