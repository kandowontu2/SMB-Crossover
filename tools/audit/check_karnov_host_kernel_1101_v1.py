"""Differentially execute donor and actual RAM3-linked Karnov actor/weapons."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
from check_karnov_actor_1101_v1 import Memory
from verify_native_relocation import NesMPU
from check_tmnt_render_oa import address
from recover_karnov_actor_1101_v1 import ROM,EXPECTED
O=R/'build/karnov-host-resource-base-1101-v1'
REF=R/'build/karnov-native-reference-1101-v1/capture/reference.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    q=dict(passed=False,source_CPU=True,native=False,installed=False,menu_admitted=False)
    try:
        proof=json.loads((O/'cache-CPU-controls.json').read_text());assert proof['passed']and sha(ROM)==EXPECTED
        for p,h in proof['bindings'].items():assert sha(p)==h,p
        b=H.C.qualified(O/'candidate.nes');raw=ROM.read_bytes();fixture=bytes(json.loads(REF.read_text())['initial_fixture'])
        seed=L.make(b);H.put(seed,SelectedCharacter=7,FmAlts=1);c,_=L.call(seed,'KrLoad');assert c.p&1
        seed.raw_page(1,3);seed.raw_page(2,2);H.put(seed,CurrentBank=3,CurrentBankC=2)
        old=Memory();old[:2048]=fixture;old[0xa000:0xc000]=raw[16+11*8192:16+12*8192];old[0xc000:]=raw[16+14*8192:16+16*8192]
        sets=[{'LDA','PLA','TXA','TYA','ADC','SBC','AND','ORA','EOR'},{'LDX','TAX','TSX','INX','DEX'}]
        count=0;normalized=0;digest=hashlib.sha256();maximum=0
        def make():
            a=Memory();a[:]=old;a.writes.clear();z=L.fork(seed);z.ram[2][:2048]=fixture;z.writes.clear();z.ram_writes.clear();return a,z
        def run(m,port,kind,flags,ceiling):
            nonlocal maximum
            entry=address(b,'KrSourceFrame'if kind=='actor'else'KrSourceWeapons')if port else 0xf28d if kind=='actor'else 0xaab2
            if port:m.ram[2][0x800]=int(ceiling>0)
            c=NesMPU(memory=m,pc=entry);c.a,c.x,c.y,c.p,c.sp=85,19,23,flags,224;c.stPushWord(0x5aff);last=[None,None];events=[]
            for step in range(16000):
                if c.pc==0x5b00:break
                if not port and c.pc in [0xc1c7,0xc81d,0xc3d8]:
                    events.append((c.pc,c.a,c.x,c.y))
                    if c.pc==0xc3d8:c.a=int(ceiling>0);c.FlagsNZ(c.a)
                    c.pc=(c.stPopWord()+1)&65535;continue
                if port and c.pc in [address(b,n)for n in ['KrSceneCallback','KrSoundCallback','KrTerrainCallback']]:
                    at={address(b,n):a for n,a in [('KrSceneCallback',0xc1c7),('KrSoundCallback',0xc81d),('KrTerrainCallback',0xc3d8)]};events.append((at[c.pc],c.a,c.x,c.y))
                op,mode=c.disassemble[m[c.pc]]
                if op in sets[0]or(op in ['ASL','LSR','ROL','ROR']and mode=='acc'):last[0]=c.pc
                if op in sets[1]:last[1]=c.pc
                assert m[c.pc]!=0,('BRK',kind,port,hex(c.pc));c.step()
            else:raise AssertionError(('kernel leaf bound',port,kind,hex(c.pc)))
            assert c.sp==224;maximum=max(maximum,step);return c,events,last
        def pair(mems,kind,flags=0x71,ceiling=0):
            nonlocal count,normalized
            host=bytes(mems[1][:256]);code=bytes(mems[1].ram[3]);mems[1].writes.clear();mems[1].ram_writes.clear()
            (a,ea,la),(z,ez,lz)=[run(m,p,kind,flags,ceiling)for p,m in enumerate(mems)]
            assert ea==ez,('callback events',kind,ea,ez)
            assert(a.y,a.p&0xcf)==(z.y,z.p&0xcf),('Y/P',kind,a.y,z.y,a.p,z.p)
            for i,(x,y)in enumerate([(a.a,z.a),(a.x,z.x)]):
                if x!=y:
                    source=0xc83e if i==0 else 0xc83c
                    # Wrapper's final PLA reloads the saved source A.
                    assert la[i]==source and (lz[i]==address(b,'KrInlineDispatch')+source-0xc831 or i==0),('unexplained A/X',kind,i,x,y,la,lz)
                    target=mems[0][0x58]|mems[0][0x59]<<8;translated=address(b,f'Kr_{target:04X}')
                    assert x==(target>>8 if i==0 else target&255)and y==(translated>>8 if i==0 else translated&255);normalized+=1
            skip=set(range(0x100,0x200))|{0x58,0x59,0x7fe,0x7ff}
            delta=[i for i in range(2048)if i not in skip and mems[0][i]!=mems[1].ram[2][i]]
            assert not delta,('source RAM',kind,[(hex(i),mems[0][i],mems[1].ram[2][i])for i in delta[:10]])
            assert bytes(mems[1][:256])==host and bytes(mems[1].ram[3])==code
            assert all(0x100<=at<0x200 or at in [3,4]or 0xc000<=at<=0xc802 for at,v in mems[1].writes),('foreign write',kind,mems[1].writes[-12:])
            digest.update(bytes(mems[0][0x5e:0x8e]));digest.update(json.dumps(ea).encode());count+=1
        def put(mems,values):
            for p,m in enumerate(mems):
                for at,v in values.items():
                    if p:m.ram[2][at]=v
                    else:m[at]=v
        selectors=0
        for state,face,held,flags in itertools.product(range(32),[0,128],[0,1,2,3,32,64,128,129],[0x30,0xf1]):
            mems=make();put(mems,{0x62:state|face,0x63:128,0x64:144,0x66:16,0x67:4,0x1b:held,0x21:held&3,0x89:9,0x8a:0,0x8b:9,0x8c:0,0x8d:0,0x6b0:1,0x737:4});pair(mems,'actor',flags,80);selectors+=1
        updates=0;peaks=[]
        for boots,weapon in itertools.product([0,128],[0,1,2,8]):
            mems=make();put(mems,{0x62:0,0x63:128,0x64:144,0x65:boots|weapon,0x66:0,0x1b:0,0x21:0,0x89:0,0x8a:0,0x8b:2,0x8c:0,0x8d:0});prev=0;peak=144
            for tick in range(180):
                held=1 if 10<=tick<35 else 2 if 55<=tick<100 else 64 if 115<=tick<145 else 0
                y=mems[0][0x64];st=mems[0][0x62]
                if y>=144 and(st&64 or st&31 in [0,1,2,3,4,5,6,7,23]):put(mems,{0x64:144})
                put(mems,{0x1b:held,0x21:(held&~prev)&3,0xe8:tick&255,0x8b:2 if mems[0][0x64]>=144 else 0})
                pair(mems,'actor');pair(mems,'weapons');peak=min(peak,mems[0][0x64]);prev=held;updates+=1
            peaks.append(144-peak)
        assert set(peaks)=={48,88},peaks
        q.update(passed=True,ROM_sha256=proof['ROM_sha256'],donor_sha256=EXPECTED,actor_selector_pairs=selectors,actor_weapon_sequence_updates=updates,engine_executions=count*2,source_jump_rises=peaks,pointer_normalizations=normalized,max_instruction_steps=maximum,trace_sha256=digest.hexdigest(),actual_host_pointer=[3,4],no_NMI_ZP_RAM0_1_or_kernel_mutation=True,scope='Actual CHR loader constructs the host RAM3 code image; explicit original-player fixture is then placed in conditional C2. All32actor selectors, twofacings/eightinputs/twoflags plus eight180-update source actor→weapon sequences. Original external sound/terrain/scene calls compared to declared event callbacks. No SMB terrain, earned pickups, audio, raster or gameplay admission.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),O/'cache-CPU-controls.json',O/'candidate.nes',O/'candidate.dbg',O/'kr-kernel.bin',REF,ROM]}
    (O/'kernel-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','traceback']}));assert q['passed'],q.get('error')

if __name__=='__main__':main()
