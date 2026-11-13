"""Read-only native empty-scene cadence, excluding forced-blank cold startup."""

from hashlib import sha256
import argparse
import json

import replay_steve_armor_native_1113 as S
from run_stdout_mesen_1110 import run


def controller(image,info, *, parent=False):
    text=S.controller(image,info,mode='ingress')
    if parent:
        original=S.Live.reverse(image)
        assert original==S.Live.Art.D.HOST.read_bytes()
        offset=S.Packet.Entry.prg(94,0xb2ef)
        cookie=original[offset:offset+16]
        assert cookie.hex()=='a810200c4dbf5b49c59d4e142de148bf'
        assert text.count(info['cookie'].hex())==1
        text=text.replace(info['cookie'].hex(),cookie.hex())
        # The delivered parent owns raw2/raw3. Raw1 is added by armor admission.
        assert text.count('for bank=1,3 do assert(header(bank)==cookie')==1
        text=text.replace('for bank=1,3 do assert(header(bank)==cookie',
                          'for bank=2,3 do assert(header(bank)==cookie')
    start=text.index('observe(0xb586,3,function()')
    end=text.index('local function transition(name,bits)',start)
    # This ingress never attacks; avoid binding new wave observers to old code.
    text=text[:start]+text[end:]
    bundle=dict(S.Roster.W.Symbols.bundle(),raw=image)
    saved=S.Roster.W.address(bundle,'SavedJoypadBits')
    enemy_id=S.Roster.W.address(bundle,'Enemy_ID')
    declarations='''local perfActive,perfPolled,perfLast=false,false,0
local perf={walk={frames=0,polls=0,updates=0},idle={frames=0,polls=0,updates=0}}
'''
    edits=(
        ('local expected,pending={},{}','local expected,pending={},{}\n'+declarations),
        ('  updates=updates+1','  updates=updates+1;perfActive=true'),
        ('  done=true\n  print(string.format(','''  done=true
  local perfJson=string.format('{"walk":{"frames":%d,"poll_frames":%d,"updates":%d},"idle":{"frames":%d,"poll_frames":%d,"updates":%d}}',
    perf.walk.frames,perf.walk.polls,perf.walk.updates,perf.idle.frames,perf.idle.polls,perf.idle.updates)
  print(string.format('''),
        ('"updates":%d,"phase":%q','"updates":%d,"performance":%s,"phase":%q'),
        ('frame,updates,phase,prepared,collected,','frame,updates,perfJson,phase,prepared,collected,'),
        ('  emu.setInput({right=pad&1~=0,','  perfPolled=true\n  emu.setInput({right=pad&1~=0,'),
        ('  local ok,message=coroutine.resume(route);assert(ok,message)',f'''  if perfActive then
    for slot=0,5 do
      local flag=read(F.Enemy_Flag+slot)
      assert(not(flag>0 and flag<128 and read({enemy_id}+slot)<21),'No NPCs in empty-scene cadence window')
    end
    local row=perf[read({saved})&1~=0 and 'walk' or 'idle']
    row.frames=row.frames+1
    if perfPolled then row.polls=row.polls+1 end
    row.updates=row.updates+updates-perfLast
    perfLast=updates
  end
  perfPolled=false
  local ok,message=coroutine.resume(route);assert(ok,message)'''),
    )
    for before,after in edits:
        assert text.count(before)==1,before
        text=text.replace(before,after)
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    return text


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent',action='store_true')
    args=parser.parse_args()
    root=S.Packet.Entry.ROOT/'build/metal-flower-native-1112'
    image,info=S.proposal(S.Live.Art.D.HOST.read_bytes())
    rom,script=root/'candidate.nes',root/'controller.lua'
    assert rom.read_bytes()==image
    script.write_text(controller(image,info,parent=args.parent),encoding='utf-8',newline='\n')
    if args.parent:rom=S.Live.Art.D.HOST
    result=run(script,rom,root/'capture',sha256(rom.read_bytes()).hexdigest(),180)
    q=result['receipt']
    print(json.dumps(dict(passed=result['passed'],ROM_SHA256=result['ROM_SHA256'],
        receipt_SHA256=result['receipt_SHA256'],script_SHA256=result['script_SHA256'],
        receipt=q,nominal_60Hz_summary={k:dict(source_updates_per_second=60*v['updates']/v['frames'] if v['frames'] else None,
        frames_without_input_poll=v['frames']-v['poll_frames'])for k,v in q.get('performance',{}).items()},
        no_runtime_state_writes=True,baseline_parent=args.parent,output_files=0)),flush=True)
    raise SystemExit(0 if result['passed'] else 1)
