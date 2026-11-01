"""Bounded CPU/packet/font/consumer proof of the isolated Karnov HUD."""
from pathlib import Path
import ast,hashlib,itertools,json,re,sys,traceback,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from verify_native_relocation import NesMPU
from check_karnov_actor_1101_v1 import Memory
from recover_karnov_actor_1101_v1 import ROM,EXPECTED
from prepare_karnov_equipment_hud_1101_v9 import CURRENT,CURRENT_SHA
O=R/'build/karnov-equipment-hud-1101-v9';V7=R/'build/karnov-options-component-1101-v7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
enc=lambda s:bytes(36 if c==' 'else 60 if c=='+'else int(c)if c.isdigit()else ord(c)-55 for c in s)


class Values(Memory):
    def __init__(self):super().__init__();self.events=[]
    def __setitem__(self,key,value):
        if isinstance(key,int):self.events.append((key,value))
        super().__setitem__(key,value)


class Proof:
    def __init__(self,a):self.a=a;self.count=0;self.cycles=[];self.minimum=224;self.trace=hashlib.sha256()
    def make(self,mode='component',fields=None,globals=None):
        m=Memory();b=(O/(mode+'.bin')).read_bytes()
        if mode=='component':m[0x9000:0x9000+len(b)]=b
        else:m[0x9000:0x9000+361]=b[:361];m[0xcd40:0xcd40+79]=b[361:]
        m[:256]=bytes((i*37+23)&255 for i in range(256))
        m[0x6000:0x600d]=bytes([34,1,3,8,0,255,0,0,0,0,0,0,0])
        values={0x8e:0,0x8f:0x89,0xbd:3,0xbe:0x12,0xbf:1,0xe8:0};values.update(fields or{})
        for at,v in values.items():m[0xc000+at]=v
        for at,v in(globals or{}).items():m[0x6000+at]=v
        m.writes=[];return m
    def run(self,m,mode='component',entry='KrHudTick'):
        labels=self.a['labels'if mode=='component'else'split_labels'];c=NesMPU(memory=m,pc=labels[entry]);c.sp=224;c.a=85;c.x=17;c.y=91;c.p=0xf1;c.stPushWord(0x5aff)
        zp=bytes(m[:256]);source=bytes(m[0xc000:0xc800]);low=c.sp
        for step in range(2000):
            if c.pc==0x5b00:break
            low=min(low,c.sp);assert m[c.pc]!=0,(hex(c.pc),entry);c.step()
        else:raise AssertionError(('HUD bound',hex(c.pc)))
        assert c.sp==224 and bytes(m[:256])==zp and bytes(m[0xc000:0xc800])==source
        assert all(0x100<=a<0x200 or 0x301<=a<0x301+36 or 0x6007<=a<=0x600c or 0xc87a<=a<0xc880 for a in m.writes),('Undeclared HUD write',[hex(a)for a in m.writes if not(0x100<=a<0x200 or 0x301<=a<0x301+36 or 0x6007<=a<=0x600c or 0xc87a<=a<0xc880)])
        if entry=='KrHudTick':assert c.a==0
        self.minimum=min(low,self.minimum);self.count+=1;self.cycles.append(c.processorCycles)
        self.trace.update(bytes(m[0x301:0x301+36]));return c
    def packet(self,m):
        assert m[0x6007]==35 and m[0x301+35]==0
        q=[];x=0
        while x<35:
            at=m[0x301+x]*256+m[0x302+x];n=m[0x303+x];assert 0<n<64
            q.append((at,bytes(m[0x304+x:0x304+x+n])));x+=3+n
        assert x==35 and [(a,len(v))for a,v in q]==[(0x2023,12),(0x204a,7),(0x2037,2),(0x2057,2)]
        return q


def source_stock_and_icons(p):
    raw=ROM.read_bytes();count=0;labels=json.loads((V7/'assembly.json').read_text())['labels'];oldbytes=(V7/'component.bin').read_bytes()
    for option,field,entry in[(0,0xbd,0xe25e),(3,0xbe,0xe2cf),(7,0xbf,0xe340)]:
        for value in range(100):
            bcd=(value//10)*16+value%10
            m=Values();m[0xc000:]=raw[16+14*8192:16+16*8192];m[field]=bcd;m[0xa2]=40;m.writes=[];m.events=[]
            c=NesMPU(memory=m,pc=entry);c.sp=224;c.stPushWord(0x5aff)
            for i in range(1000):
                if c.pc==0x5b00:break
                assert m[c.pc]!=0;c.step()
            else:raise AssertionError('Original stock publisher bound')
            original=[v for a,v in m.events if a==0x2007][:2]
            expected=[0xbb,0xbb]if not value else[0xa4+value//10,0xa4+value%10]
            assert original==expected
            for mode in['component','split']:
                h=p.make(mode,{0x8e:option,field:bcd});p.run(h,mode);q=p.packet(h)
                translated=bytes(36 if v==0xbb else v-0xa4 for v in original)
                assert q[0][1][-2:]==translated;count+=1
    icons=0
    for option,tile in[(0,0x82),(3,0x88),(7,0x8c)]:
        for owned in[0,255]:
            original=[]
            for port in[False,True]:
                m=Memory()
                if port:m[0x7000:0x7000+len(oldbytes)]=oldbytes
                else:m[0xc000:]=raw[16+14*8192:16+16*8192]
                c=NesMPU(memory=m,pc=labels['Kr_C534']if port else 0xc534);c.sp=224;c.a=option;c.x=owned;c.stPushWord(0x5aff)
                for i in range(1000):
                    if c.pc==0x5b00:break
                    assert m[c.pc]!=0;c.step()
                else:raise AssertionError('Original icon builder bound')
                original.append(bytes(m[(0xc000 if port else 0)+0xb6:(0xc000 if port else 0)+0xba]))
            assert original[0]==original[1]
            assert original[0]==bytes([tile,tile+1,tile+16,tile+17]if owned else[0xb7,0xb5,0xbc,0xb6]);icons+=1
    return dict(passed=True,exact_original_NMI_stock_to_native_pairs=count,original_relocated_icon_builder_pairs=icons,valid_BCD_values_per_option=100,zero_stock_original_blank_preserved=True)


def queue_cases(p):
    n=clean=deferred=foreign=0
    for mode,option,owned,phase in itertools.product(['component','split'],[0,3,7,255,1],[0,1,8,128,137,255],[0,128]):
        m=p.make(mode,{0x8e:option,0x8f:owned,0xe8:phase});c=p.run(m,mode);assert c.p&1
        q=p.packet(m);idx=[0,3,7].index(option)if option in[0,3,7]and owned&{0:1,3:8,7:128}[option]else 3
        assert q[0][1][:9]==enc(['BOOTS    ','BOOMERANG','WINGS    ','FIRE     '][idx])
        assert q[1][1]==enc('DOWN+B 'if idx<3 and phase else'SELECT ')
        assert q[2][1]+q[3][1]==bytes(range(0x30+idx*4,0x34+idx*4))if idx<3 else q[2][1]+q[3][1]==bytes([36]*4)
        assert list(m[0x6008:0x600d])==[0xe9,255,3,1,1]
        # Native consumption empties Buffer1; unchanged source state performs
        # no queue/cache/font writes and does not trigger a CHR reload.
        m[0x6007]=0;m[0x301]=0;m[0x600c]=0;m.writes=[];before=bytes(m)
        p.run(m,mode);assert bytes(m[:0x100])==before[:0x100]
        assert not any(a<0x100 or a>=0x200 for a in m.writes);clean+=1;n+=1
        # Unselected earned stock changes need no visual mutation.
        if idx<3:
            field=[0xbd,0xbe,0xbf][(idx+1)%3];m[0xc000+field]=0x99;m.writes=[];p.run(m,mode)
            assert not any(a<0x100 or a>=0x200 for a in m.writes)
    for mode,offset,header,ctrl in itertools.product(['component','split'],[0,1,35,80],[0,32],[0,1,6]):
        if offset==0 and header==0 and ctrl==0:continue
        m=p.make(mode,globals={6:ctrl,7:offset});m[0x301]=header;m[0xc87a:0xc880]=bytes([91]*6);before=bytes(m);m.writes=[]
        p.run(m,mode);assert bytes(m[0x301:0x301+84])==before[0x301:0x301+84]and m[0x6007]==offset and bytes(m[0xc87a:0xc880])==before[0xc87a:0xc880]
        assert m[0x6008:0x600d]==before[0x6008:0x600d];deferred+=1
    for mode,index,value in itertools.product(['component','split'],range(6),[0,1,2,3,7,8,34,255]):
        defaults=[34,1,3,8,0,255]
        valid=(index==0 and value==34)or(index==1 and value==1)or(index==2 and value==3)or(index==3 and value==8)or(index==4 and value==0)or(index==5 and value&128)
        if valid:continue
        m=p.make(mode,globals={index:value,8:0xe9,9:255,10:3,11:1,12:0});before=bytes(m);p.run(m,mode)
        assert m[0x6007]==0 and m[0x301]==0
        should_cancel=index in[1,2,3]
        assert m[0x6008]==(0 if should_cancel else 0xe9)and m[0x600c]==(1 if should_cancel else 0)
        assert bytes(m[0xc87a:0xc880])==before[0xc87a:0xc880];foreign+=1
    for owner in[0,1,3,0xe8,0xe9,255]:
        m=p.make(globals={8:owner,12:0});p.run(m,entry='KrHudCancel');assert m[0x6008]==(0 if owner==0xe9 else owner)
    return dict(passed=True,selection_owner_hint_pairs=n,clean_cache_no_publication_cases=clean,deferred_foreign_queue_cases=deferred,mode_owner_guard_cases=foreign,cancel_owners_tested=6)


def original_controls_sequence(p):
    from check_karnov_options_1101_v7 import Proof as OptionsProof
    original=OptionsProof(json.loads((V7/'assembly.json').read_text()));m=p.make(fields={0x8e:255,0x8f:137,0xbd:2,0xbe:2,0xbf:2,0x62:0,0x63:128,0x64:144,0x65:2,0x8b:2,0x8d:0x1c,0x61:0})
    b=(V7/'component.bin').read_bytes();m[0x7000:0x7000+len(b)]=b;rows=[]
    for option,name,field in[(0,'BOOTS    ',0xbd),(3,'BOOMERANG',0xbe),(7,'WINGS    ',0xbf),(255,'FIRE     ',None)]:
        m[0xc021]=4;m[0xc01b]=4;m.writes=[];original.run(m,True,'controls');assert m[0xc08e]==option
        m[0x6007]=0;m[0x301]=0;m.writes=[];p.run(m);q=p.packet(m);assert q[0][1][:9]==enc(name)
        if field is not None:
            m[0xc021]=2;m[0xc01b]=0x22;m.writes=[];original.run(m,True,'controls');assert m[0xc000+field]==1
            m[0x6007]=0;m[0x301]=0;m.writes=[];p.run(m);q=p.packet(m);assert q[0][1][-2:]==bytes([0,1])
        rows.append(dict(selection=option,name=name.strip(),stock=None if field is None else m[0xc000+field],source_state=m[0xc062]))
    assert m[0xc062]&31==15,'Choosing normal fire must not cancel original Wings'
    return dict(passed=True,actual_assembled_Select_and_DownB_steps=7,display_rows=rows,normal_fire_does_not_cancel_active_source_effect=True)


def pixels():
    source=(O/'original-icon-patterns.chr').read_bytes();atlas=(O/'equipment-font.chr').read_bytes();font=(O/'base-font.chr').read_bytes();count=0
    for tile in range(12):
        old=source[tile*16:tile*16+16];new=atlas[(0x30+tile)*16:(0x31+tile)*16]
        for y,x in itertools.product(range(8),repeat=2):
            a=((old[y]>>x)&1)|(((old[y+8]>>x)&1)<<1);b=((new[y]>>x)&1)|(((new[y+8]>>x)&1)<<1)
            assert b==[0,2,1,3][a]and bool(a)==bool(b);count+=1
    assert all(font[i*16:i*16+16]==atlas[i*16:i*16+16]for i in range(64)if i not in range(0x30,0x3d))
    return dict(passed=True,original_icon_pixels=count,index_permutation=[0,2,1,3],alpha_and_color_distinctions_preserved=True,unleased_native_font_cells_unchanged=51)


def exact_irq(p):
    irq=(O/'native-IRQ31.bin').read_bytes();tail=(O/'native-publisher-tail.bin').read_bytes();cases=0;cycles=[]
    for scroll,control,flags in itertools.product(range(256),[0,1],[0x31,0xf1]):
        m=Values();m[0x8000:0x8000+len(irq)]=irq;m[0x7000:0x7000+len(tail)]=tail
        m[0x137]=scroll;m[0x138]=control;m[3]=123;m[0x5130]=3;m[0x5128]=255
        c=NesMPU(memory=m,pc=0x7000);c.sp=224;c.a=113;c.x=43;c.y=97;c.p=flags;c.stPushWord(0x5aff)
        for i in range(30):
            if c.pc==0x5b00:break
            c.step()
        assert m[0x5130]==0 and c.a==113 and c.sp==224
        m.writes=[];m.events=[];c.pc=0x8000;c.a=59;c.x=43;c.y=97;c.p=flags|4;c.stPushWord(0x5b00);c.stPush(flags)
        start=c.processorCycles
        for i in range(100):
            if c.pc==0x5b00:break
            c.step()
        assert(c.a,c.x,c.y,c.p,c.sp)==(59,43,97,flags,224)
        assert m[0x5128]==0 and m[0x5130]==0 and m[0x137]==scroll
        writes=[(a,v)for a,v in m.events if a>=0x2000]
        assert [a for a,v in writes]==[0x2006,0x5128,0x2005,0x2005,0x2006]
        assert not any(a in range(8)for a in m.writes)
        cases+=1;cycles.append(c.processorCycles-start)
    return dict(passed=True,exact_current_ROM_sha256=CURRENT_SHA,native_consumer_cases=cases,IRQ_cycle_range=[min(cycles),max(cycles)],publisher_resets_upper_before_IRQ=True,IRQ_restores_full_physical_font0=True,no_added_IRQ_NMI_instruction=True,scope='Actual captured1c publisher tail and68-byte IRQ. Not an owning HUD integration or complete NMI deadline replay.')


def cache_ownership():
    with zipfile.ZipFile(CURRENT)as z:
        names=[n for n in z.namelist()if(n.startswith('host/kr-')or n=='host/karnov-options-portable-v7.inc'or n.startswith('original-source/'))and n.endswith(('.inc','.s'))]
        texts={n:z.read(n).decode()for n in names};meta=len(z.read('host/kr-pose-meta.bin'))
    syms={'KrState':0xc000,'KrPointer':3,'R0':3,'R1':4,'R2':5,'R3':6,'R4':7,'R5':8,'R6':9,'R7':10}
    def value(expr):
        tree=ast.parse(re.sub(r'\$([0-9a-fA-F]+)',r'0x\1',expr),mode='eval').body
        def visit(n):
            if isinstance(n,ast.Constant)and isinstance(n.value,int):return n.value
            if isinstance(n,ast.Name):return syms[n.id]
            if isinstance(n,ast.BinOp)and isinstance(n.op,(ast.Add,ast.Sub)):return visit(n.left)+(1 if isinstance(n.op,ast.Add)else-1)*visit(n.right)
            raise KeyError(expr)
        return visit(tree)
    assignments=[]
    for text in texts.values():assignments+=re.findall(r'^\s*(\w+)\s*=\s*([^;\n]+)',text,re.M)
    for i in range(20):
        for name,expr in assignments:
            try:syms[name]=value(expr.strip())
            except(KeyError,SyntaxError):pass
    combat=texts['host/kr-combat-v7.inc'];assert syms['KC_PARK']==0xc869 and syms['KC_PARK_BYTES']==17
    assert re.search(r'ldy #0\s*KcParkFrame:\s*inx\s*lda \$0100,x\s*sta KC_PARK,y\s*iny\s*cpy #KC_PARK_BYTES\s*bne KcParkFrame',combat)
    assert re.search(r'ldx #7\s*KcSaveZp:\s*lda R0,x\s*sta KC_SAVE\+4,x\s*dex\s*bpl KcSaveZp',combat)
    assert re.search(r'ldy #3\s*KcSaveBox:\s*lda BoundingBox_UL_Corner\+28,y\s*sta KC_BOX,y\s*dey\s*bpl KcSaveBox',combat)
    records=[];unresolved=set();indirect=[]
    for name,text in texts.items():
        for line in text.splitlines():
            line=line.split(';')[0];line=re.sub(r'^\s*\w+:','',line).strip()
            m=re.match(r'(sta|stx|sty|inc|dec|asl|lsr|rol|ror)\s+(.+)$',line,re.I)
            if not m:continue
            expr=m[2].strip();indexed=bool(re.search(r',[xy]$',expr,re.I));expr=re.sub(r',[xy]$','',expr,flags=re.I)
            if '('in expr:indirect.append((name,expr));continue
            try:base=value(expr)
            except(KeyError,SyntaxError):
                if expr.startswith(('Kr','KC_')):unresolved.add(expr)
                continue
            if not(0xc000<=base<0xe000):continue
            bound=255 if indexed else 0
            if expr=='KC_PARK':bound=16
            if expr=='KC_SAVE+4':bound=7
            if expr=='KC_BOX':bound=3
            end=base+bound+1
            assert not(base<0xc880 and end>0xc87a),(name,expr,hex(base),hex(end))
            records.append((base,end,name,expr))
    assert not unresolved,sorted(unresolved)
    assert set(indirect)=={('host/kr-resident.inc','(R0)'),('host/kr-terrain.inc','(R0)'),('host/kr-render.inc','(R0)')},indirect
    terrain=texts['host/kr-terrain.inc'];render=texts['host/kr-render.inc'];resident=texts['host/kr-resident.inc'];loader=texts['host/kr-loader-carrier-v6.inc']
    assert 'lda #$c0\n sta R1\n ldy #0\n ldx #8\nKrClearState:'in terrain
    assert 'lda #$d0\n sta R1'in render and meta==1345
    assert 'ldx #32\nKrZeroPage:'in resident
    assert 'KrCarrierDestHi:.byte $c0,$c4,$c8,$cc,$d0,$d4,$d8,$dc,$c9,$cd,$d6,$da'in loader
    # Existing cold C2 zero writes the entire8KB before publication; all
    # subsequent C2 row destinations skip C800..C8FF. Row8 isC900..CCFF,
    # row9CD00..CDFF, rows10/11D600..DDFF. Other rows map C3, not C2.
    assert 'cpx #8\n bcc :+\n lda #2\n sta CurrentBankC'in loader
    return dict(passed=True,source_packet_sha256=sha(CURRENT),source_files=len(texts),resolved_store_operands=len(records),
        all_postcold_direct_indexed_writes_disjoint=True,nearest_parked_frame_end=syms['KC_PARK']+17,
        private_original_indexed_bound_end=max(end for start,end,name,expr in records if expr.startswith('KrState')),
        indirect_owners=[dict(owner='cold-cache-zero',range=[0xc000,0xe000],before_publication=True),
            dict(owner='new-life-original-state',range=[0xc000,0xc800]),dict(owner='metadata-copy',range=[0xd000,0xd000+meta]),
            dict(owner='cold-carrier-rows-C2',ranges=[[0xc900,0xce00],[0xd600,0xde00]])],
        proposal_range=[0xc87a,0xc880],granted=False,source_contract='All existing selected Karnov source/kernel/options/metadata/pickup/combat writers are disjoint after cold zero. Native callback/global alias and actual owning link still require root review.')


def preview(p):
    from PIL import Image,ImageDraw
    font=(O/'equipment-font.chr').read_bytes();palette=(R/'tools/Windows/NEXXT 3.0/defaults/nes.pal').read_bytes()
    colors=[tuple(palette[v*3:v*3+3])for v in[0x22,0x30,0x21,0x0f]]
    canvas=Image.new('RGB',(768,4*144+56),'#131c29');draw=ImageDraw.Draw(canvas)
    for row,(option,phase)in enumerate([(0,0),(3,128),(7,0),(255,128)]):
        m=p.make(fields={0x8e:option,0xe8:phase});p.run(m);packet=p.packet(m);nt=bytearray([36]*128)
        def put(at,s):nt[at-0x2000:at-0x2000+len(s)]=s
        put(0x2043,enc('KARNOV '));put(0x2052,enc('WORLD  TIME'));put(0x2062,enc('000000'));put(0x206b,bytes([46,41,0,0]));put(0x2073,bytes([1,40,1]));put(0x207a,bytes([4,0,0]))
        for at,s in packet:put(at,s)
        img=Image.new('RGB',(256,32),colors[0]);pix=img.load()
        for cell,t in enumerate(nt):
            b=font[t*16:t*16+16]
            for y in range(8):
                for x in range(8):pix[(cell%32)*8+x,(cell//32)*8+y]=colors[((b[y]>>(7-x))&1)|(((b[y+8]>>(7-x))&1)<<1)]
        draw.text((12,row*144+8),['BOOTS','BOOMERANG','WINGS','NORMAL FIRE'][row]+' — isolated HUD proposal',fill='white')
        canvas.paste(img.resize((768,96),Image.Resampling.NEAREST),(0,row*144+32))
    draw.text((12,4*144+4),'SELECT: next owned equipment or normal fire.  Hold DOWN + press B: use selected equipment.',fill='white')
    draw.text((12,4*144+24),'Original icon patterns; existing native HUD palette.  This is a rendered packet preview, not an emulator screenshot.',fill='#9eb5d5')
    canvas.save(O/'equipment-hud-preview.png')


def main():
    a=json.loads((O/'assembly.json').read_text());assert a['passed']and sha(ROM)==EXPECTED
    for path,h in a['bindings'].items():assert sha(path)==h,path
    p=Proof(a);q=dict(passed=False,component_only=True,native=False,installed=False,host_modified=False,code_lease_granted=False)
    try:
        q.update(source=source_stock_and_icons(p),queue=queue_cases(p),controls=original_controls_sequence(p),pixels=pixels(),consumer=exact_irq(p),cache_ownership=cache_ownership())
        preview(p);q['passed']=True
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q.update(worker_executions=p.count,worker_cycle_range=[min(p.cycles),max(p.cycles)]if p.cycles else[],minimum_standalone_SP=p.minimum,
        packet_trace_sha256=p.trace.hexdigest(),split_code_data_bytes=[361,79],font_pages=1,new_cache_bytes=6,
        limits=['No new source/code/CHR/cache lease granted; current ROM and owning sources unchanged.',
            'Authenticated service29 integration, ROM-owned retirement cleanup and whole native Main/ISR/NMI deadline validation remain required.',
            'Font cell preservation is scoped to ordinary Karnov gameplay HUD. The font must retire before menu/lives/time-up/game-over scene text.',
            'Original icon pixels/alpha preserved with explicit1<->2 palette-index permutation; BCD zero-blank stock retained. Native cursor sprites become a persistent selected icon/name.',
            'Preview is generated from actual assembled packets/font; not an emulator gameplay screenshot.'],
        bindings={str(path.resolve()):sha(path)for path in[Path(__file__),O/'assembly.json',O/'component.bin',O/'split.bin',O/'base-font.chr',O/'equipment-font.chr',O/'native-IRQ31.bin',O/'native-publisher-tail.bin',
            V7/'assembly.json',V7/'component.bin',CURRENT,ROM,R/'tools/audit/verify_native_relocation.py',R/'tools/audit/check_karnov_actor_1101_v1.py']})
    (O/'CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings','traceback']}))
    if not q['passed']:print(q['traceback']);raise SystemExit(1)
if __name__=='__main__':main()
