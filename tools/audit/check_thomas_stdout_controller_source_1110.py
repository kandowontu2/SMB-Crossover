"""Thomas standalone stdout controller API mocks; no ROM/native proof."""
from hashlib import sha256
import json
import re

import check_ff_stdout_controller_source_1110 as Base
import check_thomas_powerup_progression_1110 as P

LUA=P.W.R/'tools/playthroughs/thomas_earned_powerup_stdout_1110.lua'


def runtime():
    rt=Base.LuaRuntime(unpack_returned_tuples=True);rt.execute(Base.MOCK)
    rt.globals().host.env['SMB_STDOUT_ROM_SHA']='6d83dea872b42cd39c14d756334a801c8f7da7dfa63ecea16d9f13835c63638d'
    rt.execute('''
host.work={}
function emu.read(at,kind)
 if kind==3 then assert(at>=0x4000 and at<0x6000);return host.work[at]or 0 end
 if kind==4 then return host.ppu[at]or 0 end;return host.mem[at]or 0
end
function emu.convertAddress(pc)
 if pc==0xb299 then return{address=10*8192+(pc&8191),memType=2}end
 if pc>=0xa000 and pc<0xc000 then return{address=3*8192+(pc&8191),memType=3}end
 return{address=(pc>=0xc000 and 127 or 126)*8192+(pc&8191),memType=2}
end
function host.write(at,v)
 for _,q in ipairs(host.callbacks)do if q.kind==2 and q.first<=at and at<=q.last then q.fn(at,v)end end
end
''')
    rt.execute(LUA.read_text());return rt


def bits(rt):
    p=rt.globals().host.pad
    return sum(v for n,v in [('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128)] if p and p[n])


def main_frame(rt):rt.execute('host.main();host.event(1)')


def receipt(rt):
    q=[json.loads(s.removeprefix('SMB_NATIVE_RECEIPT ')) for s in rt.globals().host.prints.values() if s.startswith('SMB_NATIVE_RECEIPT ')]
    assert len(q)==1,q;return q[0]


def startup(rt):
    rt.execute('''
host.mem[0x6004]=1;host.mem[0x75f]=2;host.menu='title';host.previous={};host.edges={};host.select=0
function host.advance()
 host.event(1);local pad=host.pad or{}
 for _,n in ipairs({'start','down','right','select'})do if pad[n]and not host.previous[n]then
  host.edges[#host.edges+1]=n
  if n=='start'and host.menu=='title'then host.menu='roster';host.mem[0x7307]=2
  elseif n=='start'and host.menu=='roster'then host.menu='game';host.mem[0x7307]=0;host.mem[0x771]=1;host.mem[0x773]=3;host.mem[0xf]=8;host.mem[0x75]=40;host.mem[0xbd]=176
  elseif host.menu=='roster'then
   if n=='down'then host.mem[0x7309]=(host.mem[0x7309]or 0)+8
   elseif n=='right'then host.mem[0x7309]=(host.mem[0x7309]or 0)+1
   elseif n=='select'then host.select=host.select+1 end
   if host.mem[0x7309]==10 then host.mem[0x6002]=host.select==1 and 36 or 10;host.mem[0x5fe5]=host.select==2 and 64 or 0 end
  end
 end end;host.previous=pad;host.event(2)
end
''')
    for _ in range(300):
        rt.execute('host.advance()');assert rt.globals().host.status is None,receipt(rt)
        if rt.globals().host.menu=='game':
            for _ in range(12):rt.execute('host.advance()')
            break
    assert list(rt.globals().host.edges.values())==['start','down','right','right','select','select','start']
    pads=[]
    for _ in range(60):
        rt.execute('host.event(1)');pads.append(bits(rt));main_frame(rt)
    assert pads==[0]*4+[1]*32+[129]*16+[1]*8,pads
    assert bits(rt)==65


def hardware(rt,bad=False):
    m=rt.globals().host.mem;p=rt.globals().host.ppu
    m[0x6de]=4;m[0x6e1]=0;m[0x6b06]=0x4a;m[0x6b07]=0xc8
    for at,v in enumerate((39,48,15),0x3f11):p[at]=v
    for i,v in enumerate((29,17,24,22,10,28,36),1):p[0x2042+i]=v
    rt.execute('host.write(0x5130,1)')
    for i in range(4):rt.execute(f'host.write({0x5124+i},{0 if bad else 178+i})')
    for _ in range(4):rt.execute('host.write(0x4014,2)')


def collected(rt,write=True):
    startup(rt);hardware(rt);m=rt.globals().host.mem
    m[0x75]=69;m[0x5c]=1;main_frame(rt);assert bits(rt)==73
    for _ in range(8):main_frame(rt)
    assert bits(rt)==65
    m[0x75]=145;main_frame(rt);assert bits(rt)==0
    m[0x14]=1;m[0x1b]=46;m[0x23]=192;m[0x38]=0;m[0x7a]=155;m[0x61]=1;m[0xc2]=158
    main_frame(rt)
    rt.execute('host.cpu["cpu.x"]=4;host.stack(0xe100);host.exec(0x9b28)')
    if write:rt.execute('host.write(0x104,32);host.write(0x104,0)')
    m[0x14]=0;m[0x111]=6;m[0x104]=0
    m[0xf]=9;m[0x6bfd]=1;m[0x6bfe]=0;m[0x74a]=255
    rt.execute('host.cpu["cpu.ps"]=49;host.exec(0xe100,250)');main_frame(rt)
    return m


def checks():
    assert sha256(Base.DLL.read_bytes()).hexdigest()==Base.DLL_SHA
    s=LUA.read_text();code='\n'.join(l.split('--',1)[0] for l in s.splitlines())
    assert not re.search(r'\bio\s*[.:]|\bemu\s*[.:]\s*(?:write|save|load)|os\s*\.\s*(?:execute|remove|rename)',code)
    b=P.W.Symbols.bundle();fields=re.search(r'local L=\{(.*?)\}',s,re.S)[1]
    for name,value in re.findall(r'(\w+)\s*=\s*(0x[0-9a-f]+)',fields):assert P.W.address(b,name)==int(value,16),(name,value)
    rt=runtime();m=collected(rt)
    for age in range(60):
        m[0x6bfe]=age;rt.execute('host.stack(0xe101);host.exec(0xb299)');m[0x6bfe]=age+1
        if age==59:m[0xf]=8;m[0x6bfd]=0;m[0x74a]=0;m[0x75b]=1
        rt.execute('host.exec(0xe101,250)');main_frame(rt)
    hardware(rt);m[0x75]=162;main_frame(rt);q=receipt(rt)
    assert q['passed'] and q['powerup_ticks']==60 and q['collected']['actor']['slot']==4,q
    rt=runtime();collected(rt,write=False);q=receipt(rt);assert not q['passed'] and 'SFX20 write witness' in q['reason'],q
    rt=runtime();startup(rt);hardware(rt,bad=True);assert not receipt(rt)['passed']
    print(json.dumps(dict(passed=True,API_mock_only=True,Mesen_run=False,output_files=0,ROM_written=False,
        Lua_SHA256=sha256(LUA.read_bytes()).hexdigest(),natural_menu='Down,Right2,Select2',
        opening_samples=60,original_Up_jump_updates=8,slot4_earned_collection_mock=True,
        native60tick_and16px_resume_mock=True,consumed_sound_queue_with_write_witness=True,
        absent_sound_write_and_wrong_hardware_negatives=2)),flush=True)


if __name__=='__main__':checks()
