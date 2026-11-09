"""Track the published OAM packet across Mini's native injury handoff."""

import argparse
import json
from pathlib import Path
import sys

import prepare_mini_injury_status_native_1110 as Status


V1, R = Status.V1, Status.R
FAILED = R/'build/mini-injury-status-native-1110'
OBSERVER = R/'tools/reference/mini_injury_status_oam_handoff_1110.lua'


def qualify_clear(raw):
    at = lambda pc: 16+4*8192+(pc&8191)
    assert raw[at(0xa030):at(0xa035)]==bytes.fromhex('a9f8202ca3')
    clear = b''.join(b'\x8d'+(0x200+i).to_bytes(2,'little') for i in range(0,256,4))+b'\x60'
    assert raw[at(0xa32c):at(0xa32c)+len(clear)]==clear
    return V1.prg_hook(raw,'All 64 OAM Y bytes just hidden',4,0xa035)


def repaired(text, raw):
    clear = qualify_clear(raw)
    text = V1.unique(text,'local function observe_return(name,store,onreturn)', '''local function injuryOamScope()
 return phase=='fullstage' and injury.force and r('SelectedCharacter')==41
  and r('OperMode')==1 and r('OperMode_Task')==3 and r('WorldNumber')==0 and r('LevelNumber')==0
end
local function observe_return(name,store,onreturn)''')
    text = V1.unique(text,"  if not active()or not valid(p)then return end;check(not waiting,'Synchronous '..name);",
        "  local scope=active() or (name=='MiniNativeDraw' and injuryOamScope())\n"
        "  if not scope or not valid(p)then return end;check(not waiting,'Synchronous '..name);")
    text = V1.unique(text,'local latestDraw,checkedTiles=nil,{}',
        'local latestDraw,checkedTiles=nil,{}\nlocal injuryOamDraw,injuryOamDma')
    text = V1.unique(text,'pose=ram(0xc310)}end,function(p)\n draws=draws+1',
        '''pose=ram(0xc310),frame=frame,counter=r('FrameCounter'),engine=r('GameEngineSubroutine')}end,function(p)
 draws=draws+1''')
    text = V1.unique(text,' if ram(0xc315)==1 then latestDraw=p end\n injuryDrawReturn(p)',
        ' if ram(0xc315)==1 then latestDraw=p;injuryOamDraw(p) end\n injuryDrawReturn(p)')
    text = V1.unique(text,' if not active()then return end;dmas=dmas+1;if dmas<3 then return end',
        ' if not active() and not injuryOamScope() then return end;dmas=dmas+1;if dmas<3 then return end\n injuryOamDma(page)')
    text = V1.unique(text,'  q.enemy=enemy\n  injury.force=q',
        '  q.enemy=enemy\n  injury.force=q\n  injury.preinjury_draw=latestDraw')
    return text+'\nlocal injuryOamClear='+V1.lua(clear)+'\n'+OBSERVER.read_text(encoding='utf-8')


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    text,ready_path,ready = V1.bound_template(FAILED/'controller.lua')
    result_path,binding_path = (FAILED/'capture'/f'{n}.json' for n in ('result','binding'))
    q = json.loads(result_path.read_text(encoding='utf-8'))
    b = json.loads(binding_path.read_text(encoding='utf-8'))
    assert q['ROM_sha256']==ready['ROM_sha256']==b['ROM_sha256']
    assert b['exit_code']==1 and b['ready_sha256']==V1.sha(ready_path)
    assert not q['passed'] and 'Actual one-part source canvas in normal DMA' in q['error']
    old = q['injury_helper']
    last_draw = q['native_end_handoff']['last_native_draw']
    assert old['visible']['right']==864 and len(old['native_steps'])==39 and 'first_source_step' not in old
    assert last_draw['GameEngineSubroutine']==10 and last_draw['FrameCounter']==216
    assert q['terminal_native']['GameEngineSubroutine']==8 and q['terminal_native']['FrameCounter']==217
    rom = Path(ready['ROM'])
    for path,digest in ready['bindings'].items():
        assert V1.sha(path)==digest,path
    source = repaired(text,rom.read_bytes())
    assert not any(token in source for token in ('emu.write(', 'emu.reset(', 'emu.loadSavestate('))
    sys.path.insert(0,str(V1.LUA))
    from lupa.lua54 import LuaRuntime

    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(source)
    refs = {Path(__file__),OBSERVER,ready_path,result_path,binding_path,*map(Path,ready['bindings'])}
    V1.prepare(args.output,rom,source,refs,expected=ready['ROM_sha256'],timeout=180,
               allow_interactive=ready['allow_interactive'],
               scope='Controller-only corrected injury replay. Track actual OAM draw and clear ownership '
                     'through native injury, then require the first small source body and a real DMA.')


if __name__=='__main__':
    main()
