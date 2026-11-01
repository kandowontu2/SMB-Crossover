"""Execute combined actor/projectile source against original Karnov banks."""
from pathlib import Path
import hashlib,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from verify_native_relocation import NesMPU
from check_karnov_actor_1101_v1 import Memory
from recover_karnov_actor_1101_v1 import ROM,EXPECTED
O=R/'build/karnov-original-weapons-1101-v1';B=R/'build/karnov-original-source-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    result=dict(passed=False,source_CPU=True,native_port=False,installed=False)
    try:
        q=json.loads((O/'assembly.json').read_text());order=json.loads((R/'build/karnov-frame-order-native-1101-v1/controls.json').read_text())
        for proof in [q,order]:
            assert proof['passed']
            for p,h in proof['bindings'].items():assert sha(p)==h,p
        assert order['order']==['body','shots','actor','projectiles']
        raw=ROM.read_bytes();assert sha(ROM)==EXPECTED;combined=(O/'combined.bin').read_bytes();initial=bytes(json.loads((R/'build/karnov-native-reference-1101-v1/capture/reference.json').read_text())['initial_fixture']);labels={}
        for line in(O/'combined.dbg').read_text().splitlines():
            if line.startswith('sym\t'):
                d=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',line))
                if 'val'in d:labels[d['name'].strip('"')]=int(d['val'],0)
        assert combined[:labels['KrActorEnd']-0x9000]==(B/'portable.bin').read_bytes()[:labels['KrActorEnd']-0x9000]
        events_count={};normalizations=0;count=0;digest=hashlib.sha256();clears=0
        def make(p):
            m=Memory()
            if p:m[0x6000:0x6800]=initial;m[0x9000:0xb000]=combined;m[:256]=bytes((i*37+19)&255 for i in range(256))
            else:m[:2048]=initial;m[0xa000:0xc000]=raw[16+11*8192:16+12*8192];m[0xc000:]=raw[16+14*8192:16+16*8192]
            m.writes=[];return m
        def put(m,p,a,v):m[(0x6000 if p else 0)+a]=v
        def get(m,p,a):return m[(0x6000 if p else 0)+a]
        def run(m,p,entry,flags):
            nonlocal clears
            pc=labels['KrWeaponFrame'if entry=='weapon'else'KrFrame']if p else 0xaab2 if entry=='weapon'else 0xf28d
            stop=labels['KrWeaponResult'if entry=='weapon'else'KrFrameResult']if p else None
            c=NesMPU(memory=m,pc=pc);c.sp=224;c.p=flags;c.a=85;c.x=19;c.y=23;c.stPushWord(0x7ffe)
            incoming=bytes(m[:256]);events=[];last=[None,None,None];snapshot=None
            for _ in range(12000):
                if c.pc==0x7fff:break
                if p and c.pc==stop:snapshot=(last.copy(),m[0]+256*m[1])
                if c.pc==(labels['Kr_C2B7']if p else 0xc2b7):clears+=1
                if c.pc in [0xc81d,0xc3d8]:
                    key=f'{c.pc:04X}';events_count[key]=events_count.get(key,0)+1;events.append((key,c.a,c.x,c.y))
                    if c.pc==0xc3d8:c.a=int(c.y>=144);c.FlagsNZ(c.a)
                    c.pc=(c.stPopWord()+1)&65535;continue
                op,mode=c.disassemble[m[c.pc]]
                if op in {'LDA','PLA','TXA','TYA','ADC','SBC','AND','ORA','EOR'}or(op in {'ASL','LSR','ROL','ROR'}and mode=='acc'):last[0]=c.pc
                if op in {'LDX','TAX','TSX','INX','DEX'}:last[1]=c.pc
                if op in {'LDY','TAY','INY','DEY'}:last[2]=c.pc
                assert m[c.pc]!=0,('BRK',p,entry,hex(c.pc));c.step()
            else:raise AssertionError(('CPU bound',p,entry,hex(c.pc)))
            assert c.sp==224
            if p:
                assert bytes(m[:256])==incoming and snapshot
                assert all(0x6000<=a<0x6800 or 0x100<=a<0x200 or a<2 for a in m.writes),'Foreign RAM write'
                return c,events,*snapshot
            return c,events,last,m[0x58]+256*m[0x59]
        def pair(mems,entry='weapon',flags=0x31):
            nonlocal count,normalizations
            (a,ea,la,pa),(b,eb,lb,pb)=[run(m,p,entry,flags)for p,m in enumerate(mems)]
            assert ea==eb and(a.y,a.p&0xcf)==(b.y,b.p&0xcf),('Event/Y/flags',ea,eb,a.y,b.y,a.p,b.p)
            for i,(x,y)in enumerate([(a.a,b.a),(a.x,b.x)]):
                if x!=y:
                    source=0xc83e if i==0 else 0xc83c;assert la[i]==source and lb[i]==labels['KrDispatch']+source-0xc831
                    assert pb==labels[f'Kr_{pa:04X}']and x==(pa>>8 if i==0 else pa&255)and y==(pb>>8 if i==0 else pb&255);normalizations+=1
            skip=set(range(0x100,0x200))|{0x58,0x59,0x7fe,0x7ff};delta=[i for i in range(2048)if i not in skip and mems[0][i]!=mems[1][0x6000+i]]
            assert not delta,('Weapon RAM divergence',entry,[(hex(i),mems[0][i],mems[1][0x6000+i])for i in delta[:12]])
            digest.update(bytes(mems[0][0x5e:0x8e]));digest.update(json.dumps(ea).encode());count+=1
        boundaries=0
        for weapon in [0,1,2]:
            for face in [0,64]:
                for flags in [0x30,0x31,0x71,0xf1]:
                    for x in [4,8,64,128,248,252]:
                        for y in [4,8,64,192]:
                            for impact in [0,16]:
                                mems=[make(p)for p in range(2)]
                                for p,m in enumerate(mems):
                                    put(m,p,0x65,weapon)
                                    for off in range(0,27,3):
                                        for a,v in {0x6e+off:0x84|face|impact,0x6f+off:x,0x70+off:y}.items():put(m,p,a,v)
                                pair(mems,flags=flags);boundaries+=1
        boomerangs=0
        for phase in range(4):
            for substate in range(8):
                for face in [0,64]:
                    for flags in [0x30,0x31,0x71,0xf1]:
                        for x in [4,8,64,124,248,252]:
                            mems=[make(p)for p in range(2)]
                            for p,m in enumerate(mems):
                                for a,v in {0x65:8,0x68:2,0x63:128,0x64:144,0x6e:0x84|face,0x6f:x,0x70:120,0x71:phase,0x72:substate,0x73:4}.items():put(m,p,a,v)
                            pair(mems,flags=flags);boomerangs+=1
        sequences=[]
        for weapon in [0,1,2,8]:
            for face in [0,128]:
                mems=[make(p)for p in range(2)];peak=0;first=None;phase_seen=set()
                for p,m in enumerate(mems):
                    for a,v in {0x65:weapon,0x62:face,0x63:128,0x64:144,0x89:0,0x8a:0,0x8b:2,0x8c:0,0x8d:0,0x68:0,0x6a:0,0x6b:0}.items():put(m,p,a,v)
                    for a in range(0x6e,0x89):put(m,p,a,0)
                for tick in range(180):
                    key=2 if tick in [0,12,24,36]else 0
                    for p,m in enumerate(mems):
                        for a,v in {0x1b:key,0x21:key,0xe8:tick&255}.items():put(m,p,a,v)
                    pair(mems,'actor');pair(mems,'weapon')
                    active=sum(bool(get(mems[0],0,0x6e+i)&128)for i in range(0,27,3));peak=max(peak,active)
                    if tick==0:first=active
                    if weapon==8:phase_seen.add(get(mems[0],0,0x71))
                assert first=={0:1,1:2,2:3,8:1}[weapon]
                if weapon==8:assert phase_seen=={0,1,2,3},('Boomerang did not complete source phases',phase_seen)
                sequences.append(dict(weapon=weapon,facing=face,initial_projectiles=first,peak_projectiles=peak,boomerang_phases=sorted(phase_seen)))
        assert clears>0 and 'C3D8'in events_count
        result.update(passed=True,donor_sha256=EXPECTED,combined_actor_weapon_bytes=labels['KrCombinedEnd']-0x9000,normal_projectile_boundaries=boundaries,boomerang_boundaries=boomerangs,coherent_sequences=sequences,coherent_updates=1440,total_engine_executions=2*count,native_clear_helper_executions=clears,external_callbacks=events_count,pointer_register_normalizations=normalizations,trace_sha256=digest.hexdigest(),source_actor_prefix_exact=True,real_original_order=order['order'],scope='Original actor then original projectile update in observed native order; all nine projectile slots, screen edges, spread/terrain queries, four boomerang phases, catches/misses and clear helper. Exact private RAM/events/flags with proved pointer-byte register normalization. Native SMB contacts, graphics, drops/upgrades/UI, audio and admission remain unqualified.')
    except Exception as e:result.update(error=repr(e),traceback=traceback.format_exc())
    result['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/check_karnov_actor_1101_v1.py',O/'assembly.json',O/'combined.bin',O/'combined.dbg',ROM,R/'build/karnov-frame-order-native-1101-v1/controls.json']}
    (O/'CPU-controls.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items()if k!='bindings'}));assert result['passed']


if __name__=='__main__':main()
