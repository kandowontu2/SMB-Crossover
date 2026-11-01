"""Prepare a read-only native score/PPU queue diagnosis on the exact CF cart."""
from pathlib import Path
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools'), str(R/'tools/audit')]
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address, location

OLD = R/'build/contra-force-score-native-1031-v1/burns'
O = R/'build/contra-force-score-queue-native-1031-v2/burns'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    q = json.loads((OLD/'ready.json').read_text())
    for p, digest in q['bindings'].items():
        assert sha(p) == digest, p
    b = qualified(Path(q['ROM']))
    text = (OLD/'controller.lua').read_text()
    names = ['VRAM_Buffer1_Offset', 'VRAM_Buffer1', 'NativeStatusPending',
             'HudUpdateNumberLocal', 'HudNativeStatusReserve',
             'X5NativeStatusReserve', 'X5NativeStatusFlush', 'AddToScore']
    prefix = ''.join(f'L[{json.dumps(n)}]={address(b,n)}\n' for n in names)
    prefix += ''.join(f'B[{json.dumps(n)}]={(location(b,n)-16)//8192}\n'
                      for n in names[3:])
    old_start = text.index('local rootScore=assert(')
    old_end = text.index('\nlocal function finish(', old_start)
    observer = r'''local rootScore=assert(io.open(OUTPUT..'score-lifecycle.csv','w'))
rootScore:write('frame,Main,hook,A,X,Y,control,timer,score,PPU2062,queue_offset,pending,queue\n')
local function rootScoreRow(hook,x)
 local s=emu.getState();local score,tiles,queue={},{},{}
 for i=0,5 do score[#score+1]=r('Player1ScoreDisplay',i);tiles[#tiles+1]=ppu(0x2062+i)end
 local size=math.min(84,r('VRAM_Buffer1_Offset'))
 for i=0,size do queue[#queue+1]=r('VRAM_Buffer1',i)end
 rootScore:write(table.concat({frame,updates,hook,s['cpu.a'],s['cpu.x'],s['cpu.y'],r('FloateyNum_Control',x),r('FloateyNum_Timer',x),table.concat(score,':'),table.concat(tiles,':'),size,r('NativeStatusPending'),table.concat(queue,':')},',')..'\n')
 rootScore:flush()
end
for _,name in ipairs({'HudUpdateNumberLocal','HudNativeStatusReserve','X5NativeStatusReserve','X5NativeStatusFlush','AddToScore'})do
 emu.addMemoryCallback(function()
  if active()and bank(L[name])==B[name]then rootScoreRow(name,0)end
 end,emu.callbackType.exec,L[name])
end
emu.addMemoryCallback(function()
 if active()and bank(L.FloateyNumbersCore)==B.FloateyNumbersCore and emu.getState()['cpu.x']==0 then rootScoreRow('FloateyCore',0)end
end,emu.callbackType.exec,L.FloateyNumbersCore)
'''
    text = prefix+text[:old_start]+observer+text[old_end:]
    assert 'emu.write(' not in text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    ok, error = LuaRuntime(unpack_returned_tuples=True).eval(
        'function(s) local f,e=load(s);return f~=nil,e end')(text)
    assert ok, error
    O.mkdir(parents=True)
    (O/'controller.lua').write_text(text,encoding='utf-8',newline='\n')
    (O/'run.py').write_text((OLD/'run.py').read_text(),encoding='utf-8',newline='\n')
    q.update(scope='Same exact CF ROM and real controller route; passive score digits, actual PPU2062 and native numeric queue diagnosis. No emulated writes.')
    refs = [Path(__file__), OLD/'ready.json', OLD/'controller.lua', OLD/'run.py',
            O/'controller.lua', O/'run.py']
    q['bindings'].update({str(p.resolve()):sha(p) for p in refs})
    (O/'ready.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(prepared=str(O/'ready.json'),sha256=sha(O/'ready.json'),ROM=q['ROM_sha256'],launch=False)))


if __name__ == '__main__':
    main()
