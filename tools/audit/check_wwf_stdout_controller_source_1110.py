"""Standalone WWF Lua API-only mocks, including role palette mux gaps."""
from hashlib import sha256
import json
import re

import check_ff_stdout_controller_source_1110 as Base
import check_wwf_native_powerups_1110 as P

LUA=P.W.R/'tools/playthroughs/wwf_earned_powerup_stdout_1110.lua'
PALETTES=[(40,39,23),(0,15,23),(40,22,15),(39,23,15),(39,2,23),(38,23,8)]


def runtime(role):
    rt=Base.LuaRuntime(unpack_returned_tuples=True);rt.execute(Base.MOCK)
    rt.globals().host.env['SMB_STDOUT_ROM_SHA']='62c9a3d212659c1447afcb561113fa4ce1c2703fe6cd6be357a8b97ba20deb3c'
    rt.globals().host.env['SMB_TEST_VARIANT']=str(role)
    rt.execute('''
host.work={}
function emu.read(at,kind)
 if kind==3 then assert(at>=0x4000 and at<0x6000);return host.work[at]or 0 end
 if kind==4 then return host.ppu[at]or 0 end;return host.mem[at]or 0
end
function emu.convertAddress(pc)
 if pc==0xb299 then return{address=10*8192+(pc&8191),memType=2}end
 if pc==0xb61d or pc==0xb2e6 then return{address=96*8192+(pc&8191),memType=2}end
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


def frame(rt):rt.execute('host.main();host.event(1)')


def receipt(rt):
    q=[json.loads(s.removeprefix('SMB_NATIVE_RECEIPT ')) for s in rt.globals().host.prints.values() if s.startswith('SMB_NATIVE_RECEIPT ')]
    assert len(q)==1,q;return q[0]


def startup(rt,role):
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
   if host.mem[0x7309]==28 then host.mem[0x6002]=29;host.mem[0x5fe8]=host.select end
  end
 end end;host.previous=pad;host.event(2)
end
''')
    for _ in range(350):
        rt.execute('host.advance()');assert rt.globals().host.status is None,receipt(rt)
        if rt.globals().host.menu=='game':
            for _ in range(12):rt.execute('host.advance()')
            break
    assert list(rt.globals().host.edges.values())==['start',*['down']*3,*['right']*4,*['select']*role,'start']
    pads=[]
    for _ in range(60):rt.execute('host.event(1)');pads.append(bits(rt));frame(rt)
    assert pads==[0]*4+[1]*32+[129]*16+[1]*8
    assert bits(rt)==1


def hardware(rt,role,bad=False,hidden=False):
    m=rt.globals().host.mem;w=rt.globals().host.work;p=rt.globals().host.ppu
    w[0x5d29]=167;w[0x5d2a]=4
    for i in range(1,5):w[0x5d2a+i]=0
    rt.execute('host.exec(0xb61d)')
    m[0x6de]=4;m[0x6e1]=0;m[0x6b06]=0xcf;m[0x6b07]=0x86
    for i in range(64):m[0x200+4*i]=248
    if not hidden:m[0x200]=176;m[0x201]=0;m[0x202]=0;m[0x203]=40
    for at,v in enumerate(PALETTES[role],0x3f11):p[at]=v
    for i,v in enumerate((36,17,24,16,10,23,36),1):p[0x2042+i]=v
    rt.execute('host.write(0x5130,2);host.write(0x5101,3);host.write(0x5120,'+str(0 if bad else 34)+')')
    for _ in range(4):rt.execute('host.write(0x4014,2)')


def collect(rt,role,write=True):
    startup(rt,role);hardware(rt,role);m=rt.globals().host.mem
    m[0x75]=72;m[0x5c]=1;frame(rt);assert bits(rt)==128
    for _ in range(18):frame(rt)
    assert bits(rt)==1
    m[0x75]=145;frame(rt);assert bits(rt)==0
    m[0x15]=1;m[0x1c]=46;m[0x24]=192;m[0x39]=0;m[0x7b]=157;m[0x62]=1;m[0xc3]=164
    frame(rt);rt.execute('host.cpu["cpu.x"]=5;host.stack(0xe100);host.exec(0x9b28)')
    if write:rt.execute('host.write(0x104,32);host.write(0x104,0)')
    m[0x15]=0;m[0x112]=6;m[0x104]=0;m[0xf]=9;m[0x6bfd]=1;m[0x6bfe]=0;m[0x74a]=255
    rt.execute('host.cpu["cpu.ps"]=49;host.exec(0xe100,250)');frame(rt)
    return m


def main():
    assert sha256(Base.DLL.read_bytes()).hexdigest()==Base.DLL_SHA
    s=LUA.read_text();code='\n'.join(l.split('--',1)[0] for l in s.splitlines())
    assert not re.search(r'\bio\s*[.:]|\bemu\s*[.:]\s*(?:write|save|load)|os\s*\.\s*(?:execute|remove|rename)',code)
    b=P.W.Symbols.bundle();fields=re.search(r'local L=\{(.*?)\}',s,re.S)[1]
    for n,v in re.findall(r'(\w+)\s*=\s*(0x[0-9a-f]+)',fields):assert P.W.address(b,n)==int(v,16),(n,v)
    for role in range(6):
        rt=runtime(role);m=collect(rt,role)
        for age in range(60):
            m[0x6bfe]=age;rt.execute('host.stack(0xe101);host.exec(0xb299)');m[0x6bfe]=age+1
            if age==59:m[0xf]=8;m[0x6bfd]=0;m[0x74a]=0;m[0x75b]=1
            rt.execute('host.exec(0xe101,250)');frame(rt)
        hardware(rt,role);m[0x75]=162;frame(rt);q=receipt(rt)
        assert q['passed'] and q['powerup_ticks']==60 and q['role']==role,q
    rt=runtime(0);startup(rt,0);hardware(rt,0,hidden=True);assert rt.globals().host.status is None
    hardware(rt,0,bad=True);assert not receipt(rt)['passed']
    rt=runtime(0);collect(rt,0,write=False);assert 'SFX20 write witness' in receipt(rt)['reason']
    print(json.dumps(dict(passed=True,API_mock_only=True,Mesen_run=False,output_files=0,ROM_written=False,
        Lua_SHA256=sha256(LUA.read_bytes()).hexdigest(),six_natural_menu_cycles=6,
        original_A_jump_updates=18,native60ticks_resume_cases=6,actual_sound_write_then_consume=True,
        hidden_palette_mux_group_not_counted_as_art_pass=True,wrong_consumed_art_and_absent_sound_fail=True)),flush=True)


if __name__=='__main__':main()
