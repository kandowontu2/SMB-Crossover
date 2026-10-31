"""Execute the actual linked buffered-PPU loader with eight physical RAM pages."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import bowser_split_loader_controls_v1 as T
from arthur_cache_host_controls_v1 import OverlayMemory
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU

J=R/'build/smb2j-cache-loader-source-1031-v3/joint'
S=R/'build/smb2j-cache-loader-source-1031-v3/source-stage.json'
D=R/'build/smb2j-campaign-data-1031-v2'
O=R/'build/smb2j-cache-loader-controls-1031-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Memory8(OverlayMemory):
    def __init__(self,b):
        super().__init__(b)
        self.ram += [bytearray(8192) for _ in range(4)]

    def __getitem__(self,i):
        if isinstance(i,int)and i>=0x8000:
            raw=self.rawtags[(i-0x8000)//8192]
            if not raw&128:
                v=self.ram[raw&7][i&8191]
                return v^1 if self.corrupt_at==(raw&7,i&8191)else v
        return super().__getitem__(i)

    def __setitem__(self,i,v):
        if isinstance(i,int)and i>=0x8000:
            raw=self.rawtags[(i-0x8000)//8192]
            if not raw&128:
                v&=255
                self.writes.append((i,v));self.ram_writes.append((raw&7,i&8191,v))
                if self.protection==[2,1]:self.ram[raw&7][i&8191]=v
                else:self.blocked.append((raw&7,i&8191,v))
                return
        return super().__setitem__(i,v)


def make(b,ctrl=160,wide=0,**extra):
    m=Memory8(b)
    m.raw_page(1,157);m.raw_page(2,193)
    T.H.put(m,CurrentBank=157,CurrentBankC=193,SelectedCharacter=0,MarioVariant=6,
        DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=ctrl,NmiDisable=255,
        X5WideChrActive=wide,ReloadCHRBank=1,HorizontalScroll=73,VerticalScroll=32,
        InvHudActive=0,SsChrActive=0,X5SpecialChrUpper=0,X5HudChrUpper=0,**extra)
    for i in range(12):
        m[address(b,'CurrentCHRBank')+i]=(868+i)&255
        m[address(b,'X5ChrMode')+i]=131 if wide and i%2 else 0
    m.ppuctrl=ctrl
    for i in range(8):m.ram[i][:]=bytes((j*17+i*29+13)&255 for j in range(8192))
    T.H.invoke(m,'X5PublishChr')
    m.writes.clear();m.ram_writes.clear()
    return m


def call(m,profile=0,flags=0x30):
    c=NesMPU(memory=m,pc=address(m.bundle,'J2LoadCache'))
    c.a,c.x,c.y,c.p,c.sp=profile,83,91,flags,224
    c.stPushWord(0x5aff)
    c,low=T.H.finish(m,c)
    assert c.sp==224
    return c,low


def main():
    assert not O.exists();O.mkdir()
    stage=json.loads(S.read_text())
    for n,h in stage['bindings'].items():assert sha(n)==h,n
    b=scoped_load(J/'candidate.nes');data=json.loads((D/'data-stage.json').read_text())
    q=dict(passed=False,source_CPU=True,native=False,installed=False)
    try:
        cases=[]
        for profile,ctrl,wide in itertools.product(range(4),[128,160,164],[0,1]):
            m=make(b,ctrl,wide)
            prior=[bytes(x)for x in m.ram]
            hardware=m.chr_latches[:]
            fields=bytes(m[0x5c00:0x8000]);reads=m.ppu_reads
            c,low=call(m,profile)
            assert c.p&1 and c.a==0
            expected=bytearray((D/(data['profiles'][profile]['name']+'.cache.bin')).read_bytes())
            expected[0x1fe0:0x1ff0]=bytes([167,74,50,profile])+bytes.fromhex(data['profiles'][profile]['cache_sha256'])[:12]
            assert m.ram[4]==expected
            assert all(bytes(m.ram[i])==prior[i]for i in range(8)if i!=4)
            assert all(bank==4 for bank,offset,value in m.ram_writes)
            assert m.ram_writes[0]==(4,0x1fe0,0)and m.ram_writes[-1]==(4,0x1fe0,167)
            assert m.rawtags[1]==157 and m.rawtags[2]==193
            assert T.H.get(m,'CurrentBank')==157 and T.H.get(m,'CurrentBankC')==193
            assert bytes(m[0x5c00:0x8000])==fields
            assert m.chr_latches==hardware and m.upper==0 and m.ppuctrl==ctrl and m.toggle==0
            assert m.ppu_log[-2:]==[(0x2005,73),(0x2005,32)]
            assert m.ppu_reads-reads==data['profiles'][profile]['packed_bytes']+1
            assert not any(a in [0x5102,0x5103,0x5113]for a,v in m.writes)
            cases.append(dict(profile=profile,PPUCTRL=ctrl,wide=wide,CPU=c.processorCycles,minimum_SP=low,
                              packed_reads=m.ppu_reads-reads,verified_cache_bytes=8192,all_other7_RAM_pages_exact=True))
        rejects=[]
        for name,profile,changes in [('bad-profile',4,{}),('no-blank',0,dict(DisableScreenFlag=0)),
                                      ('rendering',0,dict(Mirror_PPUMASK=30)),('normal-NMI',0,dict(NmiDisable=0))]:
            m=make(b);T.H.put(m,**changes)
            before=[bytes(x)for x in m.ram];reads=m.ppu_reads
            c,low=call(m,profile)
            assert not c.p&1 and before==[bytes(x)for x in m.ram]and reads==m.ppu_reads
            rejects.append(name)
        for name,locked,corrupt in [('protected',True,None),('readback',False,(4,0x123))]:
            m=make(b);m.protection=[0,0]if locked else[2,1];m.corrupt_at=corrupt
            c,low=call(m)
            assert not c.p&1 and m.ram[4][0x1fe0]!=167
            rejects.append(name)
        q.update(passed=True,candidate=stage['candidate'],actual_buffered_loader_cases=cases,
                 negative_cases=rejects,physical_WRAM4_only=True,all8192_bytes_and_full16_byte_cookie_verified=True,
                 no_RAM_code_execution=True,scope='Actual source-linked ROM/PPU/mapper leaf loader. Private64KiB header. No host2J parser/gameplay or native emulator evidence.')
    except Exception as error:q.update(error=repr(error),traceback=traceback.format_exc())
    refs=[Path(__file__),Path(T.__file__),Path(sys.modules[OverlayMemory.__module__].__file__),S,J/'candidate.nes',J/'candidate.dbg',D/'data-stage.json']
    q['bindings']={str(p.resolve()):sha(p)for p in refs}
    (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','traceback','actual_buffered_loader_cases']}))
    assert q['passed'],q.get('error')


if __name__=='__main__':main()
