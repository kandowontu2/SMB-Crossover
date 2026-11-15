"""Current BT camera research: RAM-only proposals, no composed ROM or outputs."""
from hashlib import sha256
import argparse,json,itertools
from pathlib import Path
from unittest.mock import patch

import replay_battletoads_full11_current_1114 as Route
import check_battletoads_full11_current_1114 as Cold
import compose_gimmick_private_window7_1114 as Gimmick

W,N=Route.W,Route.N
BASE=1989648
CACHE_SHA='e6548f57de4aefbd6ece22193bcf7a5320f5b9a151fd3ba28209c688d211d876'
IMPORT,EXPORT,TAIL=0xaed8,0xaf9e,0xb5e6
COOKIE_AT=765863


def load_current():
    raw=Route.ROM.read_bytes();pin=sha256(raw).hexdigest()
    if pin==Gimmick.CANDIDATE:raw=Gimmick.inverse(raw)
    assert sha256(raw).hexdigest()==Gimmick.PIN,'Exact1daca or explicit Gimmick inverse required'
    Route.normalize(raw)
    return raw,pin


def recipe(raw):
    b=dict(W.Symbols.bundle(),raw=raw);cache=raw[BASE:BASE+8192]
    assert len(cache)==8192 and sha256(cache).hexdigest()==CACHE_SHA
    assert raw[COOKIE_AT:COOKIE_AT+16]==bytes((167,33,1,117))+sha256(cache).digest()[:12]
    assert cache[0x1fe0:0x1ff0]==bytes(16)
    for name,address in(('BtImportNative',IMPORT),('BtExportNative',EXPORT),('Player_X_Position',0x75),
            ('Player_X_Scroll',0x701),('Player_Rel_XPos',0x571),('Player_Pos_ForScroll',0x75a),
            ('BtSrc_Objects_Xpos_L',0xbf1c)):
        assert W.address(b,name)==address,(name,hex(W.address(b,name)))
    assert cache[IMPORT&8191:(IMPORT&8191)+5]==bytes.fromhex('a575186908')
    assert cache[EXPORT&8191:(EXPORT&8191)+6]==bytes.fromhex('bd1cbf38e908')
    # Rebind the current source segment, not the obsolete BtUnavailable end.
    host=b['segs'][b['syms']['BtImportNative']['seg']]
    assert host['name']=='"BT_CACHE_HOST"'
    start,size=int(host['start'],0),int(host['size'],0)
    assert(start,start+size)==(0xad9c,TAIL),(start,size)
    names=[dict(name=n,CPU=int(s['val'],0))for n,s in b['syms'].items()
        if s.get('seg')==b['syms']['BtImportNative']['seg']]
    assert not[n for n in names if TAIL<=n['CPU']<TAIL+29]
    assert cache[TAIL&8191:(TAIL&8191)+29]==b'\xff'*29
    overlap=[]
    for key,seg in b['segs'].items():
        if not all(n in seg for n in('start','size','ooffs')):continue
        at,length=int(seg['ooffs'],0),int(seg['size'],0)
        if at<BASE+(TAIL&8191)+29 and BASE+(TAIL&8191)<at+length:
            overlap.append(dict(id=key,name=seg['name'],start=seg['start'],size=seg['size'],ooffs=seg['ooffs']))
    assert len(overlap)==1 and overlap[0]['name']=='"BT_STREAM"',('Tail has a consumer beyond its exact existing carrier container',overlap)
    carrier=b['segs'][overlap[0]['id']]
    assert int(carrier['ooffs'],0)==BASE and int(carrier['size'],0)==8192
    imp=bytes.fromhex('ad71058d5a07a57518690860')
    exp=bytes.fromhex('bd1cbf38e908084838e5758d0107682860')
    assert len(imp)==12 and len(exp)==17
    spans=((IMPORT,bytes.fromhex('20e6b5eaea')),(EXPORT,bytes.fromhex('20f2b5eaeaea')),(TAIL,imp+exp))
    proposed=bytearray(cache)
    for pc,code in spans:proposed[pc&8191:(pc&8191)+len(code)]=code
    proposed=bytes(proposed)
    changed=[i for i,(a,z)in enumerate(zip(cache,proposed,strict=True))if a!=z]
    assert all(any((pc&8191)<=i<(pc&8191)+len(code)for pc,code in spans)for i in changed)
    # A source proposal is a cache byte recipe, not an allocated cartridge.
    return b,cache,spans,dict(parent_SHA256=sha256(raw).hexdigest(),cache_SHA256=CACHE_SHA,
        current_BT_CACHE_HOST=dict(start=start,end=start+size,size=size),tail_CPU=[TAIL,TAIL+29],
        tail_file=[BASE+(TAIL&8191),BASE+(TAIL&8191)+29],tail_old_SHA256=sha256(b'\xff'*29).hexdigest(),
        host_symbols=len(names),tail_current_emitted_carrier_container=overlap,
        spans=[dict(CPU=pc,file=BASE+(pc&8191),old=cache[pc&8191:(pc&8191)+len(code)].hex(),new=code.hex())for pc,code in spans],
        proposed_cache_SHA256=sha256(proposed).hexdigest(),proposed_cookie_file=COOKIE_AT,
        proposed_cookie=(bytes((167,33,1,117))+sha256(proposed).digest()[:12]).hex(),
        cache_changed_bytes=len(changed),new_ROM_composed=False,allocation_granted=False,
        no_physics_map_input_CHR_art_or_other_family_change=True,outputs=0,Mesen_run=False)


def install_ram(m,spans):
    for pc,code in spans:m.ram[3][pc&8191:(pc&8191)+len(code)]=code


def prefix(m,pc,length,flags,x):
    if m.rawtags[1]!=3:m.raw_page(1,3)
    N.put(m,CurrentBank=3)
    c=N.NesMPU(memory=m,pc=pc);c.a=83;c.x=x;c.y=109;c.p=flags;c.sp=224
    minimum=c.sp
    for _ in range(200):
        if c.pc==pc+length:break
        assert m[c.pc],('Prefix BRK',hex(c.pc));c.step();minimum=min(minimum,c.sp)
    else:raise AssertionError(('Prefix bound',hex(c.pc)))
    return dict(A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,CPU=c.processorCycles,minimum_SP=minimum)


def units(raw):
    b,cache,spans,info=recipe(raw);old=Cold.cold(raw,'rash');new=N.fork(old);install_ram(new,spans)
    assert bytes(old.ram[3][:0x1ee0])==cache[:0x1ee0],'Actual cold source program before research patches'
    counts={'import':0,'export':0};deltas={};minimum=255
    flags=(0x20,0x21,0x60,0x61,0xa0,0xa1,0xe0,0xe1)
    for x,xlow,rel,flag in itertools.product((0,1),range(256),(0,112,239),flags):
        pair=(old,new);results=[]
        for m in pair:
            N.put(m,Player_X_Position=xlow,Player_Rel_XPos=rel,Player_Pos_ForScroll=87)
            results.append(prefix(m,IMPORT,5,flag,x))
        assert all(results[0][k]==results[1][k]for k in('A','X','Y','SP'))
        assert results[0]['P']&0xef==results[1]['P']&0xef,results
        assert N.get(new,'Player_Pos_ForScroll')==rel and N.get(old,'Player_Pos_ForScroll')==87
        assert N.get(old,'Player_X_Position')==N.get(new,'Player_X_Position')==xlow
        counts['import']+=1;deltas['import']=results[1]['CPU']-results[0]['CPU'];minimum=min(minimum,results[1]['minimum_SP'])
    for x,xlow,delta,flag in itertools.product((0,1),range(256),(-5,-1,0,1,5),flags):
        results=[]
        for m in(old,new):
            N.put(m,Player_X_Position=xlow,Player_X_Scroll=87)
            m.ram[3][(0xbf1c+x)&8191]=(xlow+8+delta)&255
            results.append(prefix(m,EXPORT,6,flag,x))
        assert all(results[0][k]==results[1][k]for k in('A','X','Y','SP'))
        assert results[0]['P']&0xef==results[1]['P']&0xef,results
        assert N.get(new,'Player_X_Scroll')==delta&255 and N.get(old,'Player_X_Scroll')==87
        assert N.get(old,'Player_X_Position')==N.get(new,'Player_X_Position')==xlow
        counts['export']+=1;deltas['export']=results[1]['CPU']-results[0]['CPU'];minimum=min(minimum,results[1]['minimum_SP'])
    return dict(proposal=info,prefix_cases=counts,complete_AXY_SP_and_architectural_flags_original_result_carry_exact=True,
        P_comparison_mask='EF: PHP/PLP normalizes the emulator break-copy bit; all real flags including C/V/N/Z/I/D exact',
        all256_native_low_bytes_page_wraps_both_player_slots_and_both_directions=True,
        exact_new_fields='pre-stepPlayer_Rel_XPos→Player_Pos_ForScroll; committed signed low-byte movement delta→Player_X_Scroll',
        additional_source_CPU_cycles=deltas,minimum_SP=minimum,source_RAM_research_only=True,outputs=0,Mesen_run=False)


def functional(raw):
    b,cache,spans,info=recipe(raw);rows=[]
    for key in('rash','zitz'):
        original=Cold.cold(raw,key);pair=(original,N.fork(original));install_ram(pair[1],spans)
        for label,m in zip(('exact_parent','RAM_camera_research'),pair,strict=True):
            samples=[];maximum=0
            for tick in range(180):
                m.controller_pad=1;Cold.Runner.Frames.frame(m,whole_pass=True)
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');maximum=max(maximum,x)
                if tick in(39,79,119,149,179):
                    samples.append(dict(Main=tick+1,x=x,y=N.get(m,'Player_Y_Position'),
                        Scroll=N.get(m,'Player_X_Scroll'),PosForScroll=N.get(m,'Player_Pos_ForScroll'),
                        ScreenLeft=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc'),
                        ScrollAmount=N.get(m,'ScrollAmount'),engine=N.get(m,'GameEngineSubroutine'),
                        HP=m.ram[3][W.address(b,'BtSrc_Objects_Life')&8191],lives=N.get(m,'NumberofLives')))
            rows.append(dict(identity=key,scope=label,maximum_x=maximum,samples=samples))
        assert rows[-2]['maximum_x']==239 and all(s['ScreenLeft']==0 and s['Scroll']==0 and s['PosForScroll']==0 for s in rows[-2]['samples'])
        assert rows[-1]['maximum_x']>239 and any(s['ScreenLeft']>0 for s in rows[-1]['samples']),rows[-1]
    return dict(proposal=info,ordinary_right180_source_comparisons=rows,source_RAM_research_only=True,
        full_stage_qualified=False,outputs=0,Mesen_run=False)


def interrupts(raw):
    b,cache,spans,info=recipe(raw);base=N.NesMPU;captures={};minimum=255
    class Trace(base):
        def step(self):
            m=self.memory
            if m.rawtags[1]==3 and self.pc in(IMPORT,EXPORT)and N.get(m,'GameEngineSubroutine')==8:
                if self.pc not in captures:captures[self.pc]=(N.fork(m),{n:getattr(self,n)for n in('pc','sp','a','x','y','p')})
            return super().step()
    with patch.object(N,'NesMPU',Trace),patch.object(W.UI.F,'NesMPU',Trace):
        m=Cold.cold(raw,'rash')
        for _ in range(4):m.controller_pad=1;Cold.Runner.Frames.frame(m,whole_pass=True)
    assert set(captures)=={IMPORT,EXPORT}
    rows=[]
    for entry,(arena,regs)in captures.items():
        install_ram(arena,spans);sp=regs['sp'];ret=(arena[256+((sp+1)&255)]+256*arena[256+((sp+2)&255)]+1)&65535
        boundaries=[]
        def execute(cut=None,kind=None):
            nonlocal minimum
            m=N.fork(arena);cpu=base(memory=m,pc=entry)
            for key,value in regs.items():setattr(cpu,key,value)
            index=0;injected=False
            for _ in range(2000):
                if(cpu.pc,cpu.sp)==(ret,(sp+2)&255):break
                minimum=min(minimum,cpu.sp)
                reached=m.rawtags[1]==3 and(any(pc<=cpu.pc<pc+len(code)for pc,code in spans))
                if reached:
                    if cut is None:boundaries.append((index,cpu.pc))
                    if cut==index:
                        original=tuple(getattr(cpu,n)for n in('pc','sp','a','x','y','p'))
                        before=dict(ram=tuple(map(bytes,m.ram)),maps=m.rawtags[:],smc=bytes(m[0x15a:0x17b]),
                            modes=bytes(m[0x73e0:0x73ef]),latches=m.chr_latches[:],upper=m.upper,
                            disable=N.get(m,'NmiDisable'),skipped=N.get(m,'NmiSkipped'))
                        assert before['disable']&128,'Only genuinely reached Main busy arm'
                        assert not(kind=='IRQ'and cpu.p&4),'Do not count an actually masked IRQ'
                        cpu.irq()if kind=='IRQ'else cpu.nmi()
                        for _ in range(200000):
                            minimum=min(minimum,cpu.sp)
                            if(cpu.pc,cpu.sp)==original[:2]:break
                            assert m[cpu.pc],('ISR BRK',kind,hex(cpu.pc));base.step(cpu)
                        else:raise AssertionError('ISR return bound')
                        actual=tuple(getattr(cpu,n)for n in('pc','sp','a','x','y','p'))
                        assert actual[:5]==original[:5]and actual[5]&0xef==original[5]&0xef
                        assert tuple(map(bytes,m.ram))==before['ram']and m.rawtags==before['maps']
                        assert bytes(m[0x15a:0x17b])==before['smc']and bytes(m[0x73e0:0x73ef])==before['modes']
                        assert m.chr_latches==before['latches']and m.upper==before['upper']
                        assert N.get(m,'NmiDisable')==before['disable']
                        assert(N.get(m,'NmiSkipped')-before['skipped'])&255==(kind=='NMI');injected=True
                    index+=1
                assert m[cpu.pc],('Source continuation BRK',hex(cpu.pc));base.step(cpu)
            else:raise AssertionError('Actual source boundary return bound')
            assert cut is None or injected
            return m,tuple(getattr(cpu,n)for n in('a','x','y','p','sp'))
        baseline,result=execute()
        for index,pc in boundaries:
            for kind in('IRQ','NMI'):
                m,current=execute(index,kind)
                assert current[:3]==result[:3]and current[3]&0xef==result[3]&0xef and current[4]==result[4]
                assert tuple(map(bytes,m.ram))==tuple(map(bytes,baseline.ram))
                assert bytes(m[512:768])==bytes(baseline[512:768])
        rows.append(dict(entry=entry,actual_registers=regs,actual_return_PC=ret,actual_return_SP=(sp+2)&255,
            reached_instruction_boundaries=len(boundaries),PCs=sorted({pc for _,pc in boundaries}),IRQ_cuts=len(boundaries),busy_NMI_cuts=len(boundaries)))
    return dict(proposal=info,actual_source_calls=rows,minimum_SP=minimum,
        regular_NMI_inside_Main_busy_unreachable=True,source_RAM_research_only=True,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--units',action='store_true');p.add_argument('--functional',action='store_true');p.add_argument('--interrupts',action='store_true');a=p.parse_args()
    raw,actual=load_current()
    def forbid(*args,**kwargs):raise RuntimeError('BT research attempted file/Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Cold.Runner.Native,'run',forbid):
        q=interrupts(raw)if a.interrupts else functional(raw)if a.functional else units(raw)if a.units else recipe(raw)[3]
    q.update(actual_input_SHA256=actual,physical_RAM3_reads=True,file_and_Mesen_traps=True)
    print(json.dumps(q,separators=(',',':')),flush=True)
