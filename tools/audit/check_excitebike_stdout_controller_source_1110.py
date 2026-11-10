"""Syntax, symbols and Mesen API-only controller mocks; no gameplay proof."""
from hashlib import sha256
import json
from pathlib import Path
import re

import check_ff_stdout_controller_source_1110 as Base
import check_excitebike_powerup_progression_1110 as P

LUA=P.W.R/'tools/playthroughs/excitebike_earned_powerup_stdout_1110.lua'
LUA_PIN=None


def runtime():
    rt=Base.LuaRuntime(unpack_returned_tuples=True);rt.execute(Base.MOCK)
    rt.globals().host.env['SMB_STDOUT_ROM_SHA']='a76d7610eed8493806200c52b96065af0369b926c55d033e17841f818756e2e0'
    rt.execute('''
function emu.convertAddress(pc)
 if host.wrongMap then return{address=0,memType=2}end
 if pc==0xb299 then return{address=10*8192+(pc&8191),memType=2}end
 if pc>=0xa000 and pc<0xc000 then return{address=3*8192+(pc&8191),memType=3}end
 return{address=(pc>=0xc000 and 127 or 126)*8192+(pc&8191),memType=2}
end
function host.write(at,v)
 local n=#host.callbacks
 for i=1,n do local q=host.callbacks[i];if q.kind==2 and q.first<=at and at<=q.last then q.fn(at,v)end end
end
''')
    rt.execute(LUA.read_text())
    return rt


def receipt(rt):
    rows=[json.loads(s.removeprefix('SMB_NATIVE_RECEIPT ')) for s in rt.globals().host.prints.values()
        if s.startswith('SMB_NATIVE_RECEIPT ')]
    assert len(rows)==1,rows
    return rows[0]


def bits(rt):
    pad=rt.globals().host.pad
    return sum(value for name,value in [('right',1),('left',2),('down',4),('up',8),('start',16),
        ('select',32),('b',64),('a',128)] if pad and pad[name])


def main(rt):
    rt.execute('host.main();host.event(1)')


def startup(rt):
    rt.execute('''
host.mem[0x6004]=1;host.mem[0x75f]=2;host.mem[0x300]=1
host.menu='title';host.previous={};host.edges={}
function host.advance()
 host.event(1);local pad=host.pad or{}
 for _,name in ipairs({'start','select','down','right'})do
  if pad[name]and not host.previous[name]then
   host.edges[#host.edges+1]=name
   if name=='start'and host.menu=='title'then host.menu='roster';host.mem[0x7307]=2
   elseif name=='start'and host.menu=='roster'then
    host.menu='game';host.mem[0x7307]=0;host.mem[0x771]=1;host.mem[0x773]=3
    host.mem[0xf]=8;host.mem[0x75]=40;host.mem[0xbd]=176
   elseif host.menu=='roster'then
    if name=='down'then host.mem[0x7309]=(host.mem[0x7309]or 0)+8
    elseif name=='right'then host.mem[0x7309]=(host.mem[0x7309]or 0)+1 end
    if host.mem[0x7309]==29 then host.mem[0x6002]=37 end
   end
  end
 end
 host.previous=pad;host.event(2)
end
''')
    for _ in range(300):
        rt.execute('host.advance()')
        assert rt.globals().host.status is None,receipt(rt)
        # Opening's first controller sample is neutral. Completion hooks
        # advance the policy only after the coroutine admits actual play.
        if rt.globals().host.menu=='game' and len(list(rt.globals().host.edges.values()))==10:
            for _ in range(12):rt.execute('host.advance()')
            break
    else:raise AssertionError('API menu bound')
    assert list(rt.globals().host.edges.values())==['start','down','down','down',*['right']*5,'start']
    samples=[]
    for _ in range(60):
        rt.execute('host.event(1)');samples.append(bits(rt));main(rt)
    assert samples==[0]*4+[1]*32+[129]*16+[1]*8,samples
    assert bits(rt)==65


def hardware(rt,wrong=False):
    m=rt.globals().host.mem;ppu=rt.globals().host.ppu
    m[0x6de]=4;m[0x6e1]=0;m[0x6b06]=0xe1;m[0x6b07]=6
    for at,v in enumerate((32,22,15),0x3f11):ppu[at]=v
    for i,v in enumerate((14,33,11,18,20,14,36),1):ppu[0x2042+i]=v
    rt.execute('host.write(0x5130,2)')
    for i in range(4):rt.execute(f'host.write({0x5124+i},{(0 if wrong else 736+i)&255})')
    for _ in range(4):rt.execute('host.write(0x4014,2)')


def before_collect(rt):
    startup(rt);m=rt.globals().host.mem;hardware(rt)
    m[0x75]=144;m[0x5c]=1;main(rt);assert bits(rt)==0
    main(rt);assert bits(rt)==66
    m[0x75]=109;m[0x5c]=1;main(rt);assert bits(rt)==74
    for _ in range(4):main(rt)
    assert bits(rt)==202
    for _ in range(8):main(rt)
    assert bits(rt)==0
    m[0x75]=34;m[0x5c]=1
    m[0x15]=1;m[0x1c]=46;m[0x24]=128;m[0x39]=0;m[0x7b]=46;m[0x62]=1;m[0xc3]=184
    main(rt)
    rt.execute('host.cpu["cpu.x"]=5;host.stack(0xe100);host.exec(0x9b28)')
    m[0x15]=0;m[0x112]=6;m[0x104]=32
    m[0xf]=9;m[0x6bfd]=1;m[0x6bfe]=0;m[0x74a]=255
    rt.execute('host.cpu["cpu.ps"]=49;host.exec(0xe100,250)')
    main(rt)
    return m


def success():
    rt=runtime();m=before_collect(rt)
    for age in range(60):
        m[0x6bfe]=age
        rt.execute('host.stack(0xe101);host.exec(0xb299)')
        m[0x6bfe]=age+1
        if age==59:m[0xf]=8;m[0x6bfd]=0;m[0x74a]=0;m[0x75b]=1
        rt.execute('host.exec(0xe101,250)');main(rt)
    hardware(rt);m[0x75]=50;main(rt)
    q=receipt(rt);assert q['passed'] and q['powerup_ticks']==60 and q['recovery_hardware_checks']>0,q


def checks():
    assert sha256(Base.DLL.read_bytes()).hexdigest()==Base.DLL_SHA
    source=LUA.read_text();code='\n'.join(line.split('--',1)[0] for line in source.splitlines())
    assert not re.search(r'\bio\s*[.:]|\bemu\s*[.:]\s*(?:write|save|load)|os\s*\.\s*(?:execute|remove|rename)',code)
    symbols=re.search(r'local L=\{(.*?)\}',source,re.S)[1]
    b=P.W.Symbols.bundle()
    for n,v in re.findall(r'(\w+)\s*=\s*(0x[0-9a-f]+)',symbols):assert P.W.address(b,n)==int(v,16),(n,v)
    success()
    rt=runtime();m=before_collect(rt)
    for _ in range(96):
        main(rt)
        if rt.globals().host.status is not None:break
    q=receipt(rt);assert not q['passed'] and 'recovery bound' in q['reason'],q
    rt=runtime();startup(rt);hardware(rt,wrong=True)
    q=receipt(rt);assert not q['passed'] and 'OAM/CHR/palette/HUD' in q['reason'],q
    print(json.dumps(dict(passed=True,API_mock_only=True,source_CPU_gameplay=False,Mesen_run=False,
        outputs_written=0,ROM_written=False,Lua_SHA256=sha256(LUA.read_bytes()).hexdigest(),
        menu_inputs='Start,Down3,Right5,Start',opening_exact_samples=60,
        policy_prelean_updates=4,policy_A_updates=8,exact_tick_and_resume_success=1,
        unchanged_freeze_negative=1,wrong_hardware_negative=1)),flush=True)


if __name__=='__main__':checks()
