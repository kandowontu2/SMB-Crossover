"""ROM-only scatter-loader/readback and native world-window CPU proposal tests."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
import prepare_metal_storm_resource_host_1101_v8 as P
from arthur_cache_host_controls_v1 import OverlayMemory
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
OUT=P.OUT;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Bus(OverlayMemory):
    def __init__(self,b):self.fault=None;self.armed=False;self.state_reads=0;super().__init__(b)
    def __getitem__(self,i):
        if isinstance(i,int)and 0xc000<=i<0xcd00 and self.rawtags[2]==2:self.state_reads+=1
        return super().__getitem__(i)
    def __setitem__(self,i,v):
        if isinstance(i,int)and i>=0x8000 and self.fault is not None:
            raw=self.rawtags[(i-0x8000)//8192]
            if not raw&128 and(raw&3,i&8191)==self.fault and v:self.armed=True;self.corrupt_at=self.fault
        super().__setitem__(i,v)
def main():
    q=dict(passed=False,granted=False,native=False,installed=False)
    try:
        stage=json.loads((OUT/'assembly.json').read_text());own=json.loads((OUT/'ownership.json').read_text());w=json.loads((OUT/'native-witness.json').read_text());lab=stage['labels']
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        raw=bytearray(w['raw_length'])
        for s in w['spans']:raw[s['offset']:s['offset']+s['size']]=bytes.fromhex(s['hex'])
        for h in own['PRG_proposals']:
            code=(OUT/(h['role'].lower()+'.bin')).read_bytes();at=h['file_interval'][0];raw[at:at+len(code)]=code
        carrier=(OUT/'carrier-pack.bin').read_bytes()
        for i,page in enumerate(own['actor_pages']+own['render_pages']):raw[1048592+page*1024:1048592+(page+1)*1024]=carrier[i*1024:(i+1)*1024]
        body=(OUT/'body-packed.chr').read_bytes()
        for i,page in enumerate(own['body_pages']):raw[1048592+page*1024:1048592+(page+1)*1024]=body[i*1024:(i+1)*1024]
        b=dict(raw=raw,syms=w['syms'],segs=w['segs']);cookie=(OUT/'cookie.bin').read_bytes();minimum=224;maxcycles=0;maxreads=0;executed=set();digest=hashlib.sha256()
        smc=[address(b,n)+i for n,i in [('NextBank_SMC',1),('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('SafereturnA_SMC',1)]]
        def put(m,**kw):
            for n,v in kw.items():m[address(b,n)]=v
        def make(wide=0,bankc=215):
            m=Bus(b)
            for bank in range(4):m.ram[bank][:]=bytes((i*17+bank*29+7)&255 for i in range(8192))
            m.raw_page(1,206);m.raw_page(2,bankc)
            put(m,CurrentBank=206,CurrentBankC=bankc,SelectedCharacter=35,OperMode=1,GameEngineSubroutine=8,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=160,NmiDisable=255,HorizontalScroll=73,VerticalScroll=32,ReloadCHRBank=7,SsChrActive=0,InvHudActive=0,X5WideChrActive=wide,CurrentOAMOffset=0,GuestOamRotationActive=0,RgOamRotation=0)
            m.ppuctrl=160
            for i in range(12):m[address(b,'CurrentCHRBank')+i]=20+i;m[address(b,'X5ChrMode')+i]=(0x82 if wide and i%2 else 0)
            for i in range(11):m[i]=(i*31+15)&255
            for i,at in enumerate(smc):m[at]=43+i*17
            m.writes.clear();m.ram_writes.clear();return m
        def run(m,pc,a=85,x=7,y=91,p=0x71,allow_ram=False):
            nonlocal minimum,maxcycles,maxreads
            c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224;c.stPushWord(0x5ffe);start=c.processorCycles
            for _ in range(1000000):
                if c.pc==0x5fff:break
                minimum=min(minimum,c.sp)
                if c.pc>=0x8000:
                    tag=m.rawtags[(c.pc-0x8000)//8192];executed.add(tag)
                    if not allow_ram:assert tag&128,('RAM opcode in coldloader',hex(c.pc),tag)
                assert m[c.pc]!=0,('BRK',hex(c.pc),m.rawtags);c.step()
            else:raise AssertionError(('bound',hex(c.pc)))
            assert c.sp==224;maxcycles=max(maxcycles,c.processorCycles-start);maxreads=max(maxreads,m.ppu_reads)
            return c.a,c.x,c.y,c.p&0xcf
        def publish(m):
            old=m.rawtags[1];put(m,CurrentBank=190);m.raw_page(1,190);run(m,address(b,'X5PublishChr'));m.raw_page(1,old);put(m,CurrentBank=old)
        def invoke(m,expect):
            maps=m.rawtags[:];zp=bytes(m[:11]);fields=bytes(m[a]for a in smc);banks01=[bytes(x)for x in m.ram[:2]]
            r=run(m,lab['Ms8Load']);assert r==(85,7,91,0x41 if expect else 0x40),r
            assert m.rawtags==maps and bytes(m[:11])==zp and bytes(m[a]for a in smc)==fields
            assert [bytes(x)for x in m.ram[:2]]==banks01 and m[address(b,'ReloadCHRBank')]==7
            return r
        def exact(m):
            a=bytearray(carrier[:8192]);a[0x1fe0:0x1ff0]=cookie;c=bytearray(8192);c[0xd00:0x1900]=carrier[8192:];c[0x1fe0:0x1ff0]=cookie
            assert bytes(m.ram[3])==a and bytes(m.ram[2])==c
        rows=[]
        for wide,bankc in itertools.product([0,1],[2,3,215]):
            m=make(wide,bankc);publish(m);old=m.chr_latches[:];before=bytes(m.ram[2]);invoke(m,True);exact(m)
            assert m.ram_writes[:2]==[(3,0x1fe0,0),(2,0x1fe0,0)]
            assert m.ram_writes[-2:]==[(3,0x1fe0,167),(2,0x1fe0,167)]
            assert m.chr_latches==old and m.upper==0 and m.ppuctrl==160 and m.ppu_log[-2:]==[(0x2005,73),(0x2005,32)]
            assert m.ppu_reads==22550,m.ppu_reads # 11rows *2 passes *(1024+dummy)
            reads=m.ppu_reads;writes=len(m.ram_writes);invoke(m,True);assert reads==m.ppu_reads and writes==len(m.ram_writes);exact(m)
            rows.append(dict(wide=wide,bankc=bankc,read_bytes=reads));digest.update(bytes(m.ram[3]));digest.update(bytes(m.ram[2]))
        q['cold_warm_cases']=len(rows);q['actual_buffered_read_count']=22550
        failures=[]
        for fault in[(3,17),(3,0x1c00),(2,0xd00),(2,0x1100),(2,0x1500)]:
            m=make();publish(m);old=m.chr_latches[:];m.fault=fault;invoke(m,False)
            assert m.armed and m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
            assert m.chr_latches==old and m.upper==0 and m.ppuctrl==160 and m.ppu_log[-2:]==[(0x2005,73),(0x2005,32)];failures.append(list(fault))
        q['carrier_readback_failures']=failures
        m=make();publish(m);old=m.chr_latches[:];m.corrupt_at=(2,0);invoke(m,False)
        assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0 and m.chr_latches==old and m.ppuctrl==160
        q['zero_state_readback_failure']=True
        negatives=[]
        for name,value in [('SelectedCharacter',11),('OperMode',0),('FamilyMainCommit',0),('DisableScreenFlag',0),('Mirror_PPUMASK',24),('NmiDisable',0)]:
            m=make();put(m,**{name:value});images=[bytes(x)for x in m.ram];invoke(m,False);assert images==[bytes(x)for x in m.ram]and m.ppu_reads==0;negatives.append(name)
        q['ineligible_no_effect_cases']=negatives
        authcases=0
        for bank,index in itertools.product([2,3],range(16)):
            m=make();invoke(m,True);m.ram[bank][0x1fe0+index]^=1;m.raw_page(1,153);put(m,CurrentBank=153);before=[bytes(x)for x in m.ram];old=m.rawtags[:]
            r=run(m,lab['Ms8Auth']);assert not r[3]&1 and old==m.rawtags and before==[bytes(x)for x in m.ram];authcases+=1
        q['full_header_auth_rejections']=authcases
        m=make();invoke(m,True);m.raw_page(1,159);m.raw_page(2,2);put(m,CurrentBank=159,CurrentBankC=2);m[0xc800]=167;gatecases=0
        for bank,index in itertools.product([2,3],range(16)):
            m.ram[bank][0x1fe0+index]^=1;before=[bytes(x)for x in m.ram];m.state_reads=0;r=run(m,lab['MsRenderGate']);assert r==(85,7,91,0x40)and m.state_reads==0 and before==[bytes(x)for x in m.ram];m.ram[bank][0x1fe0+index]^=1;gatecases+=1
        q['warm_gate_bad_headers_no_state_read_or_RAM_opcode']=gatecases
        # Corrected body0/5 and shot6 retain all native world1..4 and7.
        art=json.loads((V7:=P.V7/'art.json').read_text());sourcebody=(P.V7/'body.chr').read_bytes();sourceshots=(P.V7/'shots.chr').read_bytes()
        def pixels(cells,chrdata,anchor=(128,112)):
            out={}
            for cell in cells:
                attr=cell['attributes'];data=chrdata[cell['pattern_index']*32:cell['pattern_index']*32+32]
                for yy,xx in itertools.product(range(16),range(8)):
                    py=15-yy if attr&128 else yy;px=7-xx if attr&64 else xx;at=(py//8)*16+(py&7);v=((data[at]>>(7-px))&1)+2*((data[at+8]>>(7-px))&1)
                    if v:out.setdefault((anchor[0]+cell['dx']+xx,anchor[1]+cell['dy']+yy),(attr&3,v))
            return out
        def image(m):
            out={}
            for off in range(0,m[address(b,'CurrentOAMOffset')],4):
                yy,t,attr,xx=m[0x200+off:0x204+off];slot=(t&1)*4+((t&254)*16)//1024;at=1048592+m.chr_latches[slot]*1024+((t&254)*16)%1024
                for k,v in pixels([dict(dx=xx,dy=yy+1,pattern_index=0,attributes=attr)],raw[at:at+32],(0,0)).items():out.setdefault(k,v)
            return out
        pixelcases=0
        m=make();publish(m);world=m.chr_latches[:];invoke(m,True);m.raw_page(1,159);m.raw_page(2,2);put(m,CurrentBank=159,CurrentBankC=2,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,Player_SprAttrib=0)
        for kind,records in [('body',art['body_packets']),('shot',art['shot_packets'])]:
            for r in records:
                if kind=='shot'and r['type']==131 and r['phase']>2:continue
                # Pose fixtures reset actor data only. Executable bytes remain
                # those copied/read back by the actual loader above.
                m[0xc000:0xc8a1]=bytes(0x8a1);m[0xc800]=167;put(m,CurrentOAMOffset=0)
                if kind=='body':
                    values={0x480:128,0x4b0:112,0x510:128,0x4e0:r['state'],0x4f8:r['frame'],0x540:r['facing']|r['gravity']};expected=pixels(r['cells'],sourcebody)
                else:values={0x482:128,0x4b2:112,0x512:128,0x52a:r['type'],0x542:r['flags'],0x55a:0 if r['vertical']else 12,0x632:r['phase']};expected=pixels(r['cells'],sourceshots)
                for a,v in values.items():m[0xc000+a]=v
                before_smc=bytes(m[a]for a in smc);before_zp=bytes(m[:11]);r2=run(m,lab['MsRenderGate'],allow_ram=True);assert r2==(85,7,91,0x41)
                assert bytes(m[a]for a in smc)==before_smc and bytes(m[:11])==before_zp,'Warm entire child ABI/SMC'
                publish(m);got=image(m);assert got==expected,(kind,r,len(got),len(expected))
                assert all(m.chr_latches[i]==world[i]for i in[1,2,3,4,7,8,9,10,11]);pixelcases+=1;digest.update(repr(sorted(got.items())).encode())
        q.update(loaded_native_original_pixel_cases=pixelcases,native_world_and_background_windows_retained=[1,2,3,4,7,8,9,10,11],no_cold_RAM_opcode=True,actual_native_farcall=True,minimum_standalone_SP=minimum,maximum_standalone_cycles=maxcycles,physical_ROM_tags_executed=sorted(executed),aggregate_sha256=digest.hexdigest(),passed=True,scope='Real emitted6502 scatter copy/readback/auth/publication and actual native PPU-buffer/CHR/OAM helper CPU model. Proposal overlays only its declared holes in-memory. Current ROM untouched; no resource grant, timing/native Main/ISR, menu or full gameplay admission. Source palette1 versus native world palette1 remains unresolved.')
        q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(P.__file__),P.REF,OUT/'ownership.json',OUT/'assembly.json',OUT/'native-witness.json',OUT/'carrier-pack.bin',OUT/'body-packed.chr',OUT/'cookie.bin',P.V7/'art.json']}
    except Exception:q['error']=traceback.format_exc();raise
    finally:(OUT/'CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings','error']}))
if __name__=='__main__':main()
