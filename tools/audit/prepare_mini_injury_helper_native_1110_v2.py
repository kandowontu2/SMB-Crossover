"""Bind the earned-power injury fixture with a genuine native jump edge."""

import argparse
import json
from pathlib import Path
import re
import sys

import prepare_mini_injury_helper_native_1110 as V1


NEGATIVE = V1.R/'build/mini-injury-helper-native-1110/capture/result.json'
INIT_JS = 0xa847


def recover(text, raw):
    hook = V1.prg_hook(raw,'Native InitJS',1,INIT_JS)
    assert hook['bytes']==[0xa9,0x20,0x8d,0x7f]
    text = V1.unique(text,'  route_pad={right=true,b=true}\n end\n local function relevant()',
        '  route_pad={right=true,b=true,a=injury.jump_request~=nil}\n end\n local function relevant()')
    text = V1.unique(text,'   injury.start=snapshot_native()\n  end', '''   injury.start=snapshot_native()
   check(injury.start.input&0x80==0 and read(0x055b)&0x80==0,
    'A is released before requesting the native jump')
   check(r('Player_State')==0,'Native injury jump starts on solid ground')
   injury.jump_request=injury.start
   keep_holding_right()
  end''')
    text = V1.unique(text,' local function relevant()', ' local initJS='+V1.lua(hook)+'\n local function relevant()')
    text = V1.unique(text,' emu.addMemoryCallback(guard(function()\n  if not relevant() or not valid(injuryConfig.force)',
        ''' emu.addMemoryCallback(guard(function()
  if not relevant() or r('GameEngineSubroutine')~=10 or not valid(initJS) then return end
  check(injury.jump_request and not injury.jump_ack,'Exactly one requested native jump')
  check(read(0x0558)&0x80~=0 and read(0x055b)&0x80==0 and r('Player_State')==0,
   'Actual native InitJS accepts the fresh A edge')
  injury.jump_ack=snapshot_native()
 end),emu.callbackType.exec,initJS.pc)
 emu.addMemoryCallback(guard(function()
  if not relevant() or not valid(injuryConfig.force)''')
    text = V1.unique(text,'  if q.right<856 then return end', '''  if injury.jump_ack and not injury.airborne and r('Player_State')==1
   and r('Player_Y_Speed')>=0x80 and q.y<injury.jump_ack.y then
   injury.airborne=q
  end
  if q.right<856 then return end
  check(injury.airborne~=nil,'Accepted native jump rises before the admission window')''')
    text = V1.unique(text,"   check(q.status==0 and #injury.native_steps>0,'Lost the actual earned power during camera motion')",
        '''   check(q.status==41,'Preserve the separately tracked native PlayerStatus=41 injury defect')
   check(injury.jump_ack and injury.airborne,'Native jump and injury scroll are both witnessed')
   injury.native_status_anomaly={before=injury.force.status,during=q.status,expected=0}''')
    return text


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    for field in ('rom','kernel','controller','output'):
        cli.add_argument('--'+field,type=Path,required=True)
    cli.add_argument('--validate-only',action='store_true')
    args = cli.parse_args()
    rom,kernel,controller = (p.resolve() for p in (args.rom,args.kernel,args.controller))
    route,route_ready,route_meta = V1.bound_template(controller)
    power,power_ready,_ = V1.bound_template(V1.POWER)
    raw,kernel_bytes = rom.read_bytes(),kernel.read_bytes()
    metadata = rom.with_suffix('.json')
    info = json.loads(metadata.read_text(encoding='utf-8'))
    expected,kernel_hash = V1.sha(rom),V1.sha(kernel)
    assert info['candidate_SHA256']==expected and info['kernel_SHA256']==kernel_hash
    assert raw[:5]==b'NES\x1a\x40' and not raw[6]&4
    assert len(kernel_bytes)==5120 and raw[V1.CODE_OFFSET:V1.CODE_OFFSET+5120]==kernel_bytes
    failure = json.loads(NEGATIVE.read_text(encoding='utf-8'))
    injury = failure['injury_helper']
    assert not failure['passed'] and injury['start']['right']==844
    assert len(injury['native_steps'])==39 and max(q['right'] for q in injury['post_control'])==852
    assert {q['status'] for q in injury['native_steps']}=={41}
    kernel_labels = kernel.with_suffix('.lbl')
    labels = {name:int(pc,16) for pc,name in re.findall(
        r'^al ([0-9A-F]+) \.(\w+)$',kernel_labels.read_text(),re.M)}
    source = V1.build_controller(raw,kernel_bytes,labels,route,power,expected,kernel_hash,650)
    source = recover(source,raw)
    sys.path.insert(0,str(V1.LUA))
    from lupa.lua54 import LuaRuntime

    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(source)
    if args.validate_only:
        print(json.dumps(dict(validated=True,ROM_sha256=expected,controller_bytes=len(source.encode()),
                              negative_SHA256=V1.sha(NEGATIVE))))
        return
    refs = {Path(__file__),Path(V1.__file__),V1.OBSERVER,controller,route_ready,V1.POWER,
            power_ready,metadata,kernel,kernel_labels,NEGATIVE,V1.R/'src/player.s'}
    V1.prepare(args.output,rom,source,refs,expected=expected,timeout=180,
               allow_interactive=route_meta['allow_interactive'],
               scope='Earned mushroom and side injury, then an acknowledged native A jump over the pipe. '
                     'Requires the X864 native helper constructor during the offscreen mode10 interval '
                     'and subsequent visible entry. Records the separate native status downgrade defect.')


if __name__=='__main__':
    main()
