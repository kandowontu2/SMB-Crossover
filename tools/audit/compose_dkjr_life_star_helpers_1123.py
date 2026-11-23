"""Private bcc DK Jr lift proposal; memory-only, no game/asset file writer.

Preserve all15 authored helpers and the original motor. A semantics-paired
visible-entry tail relocation funds17 contiguous oscillator bytes. Physical
qualification and delivery remain Root's separate work.
"""
import argparse
from contextlib import redirect_stdout
from functools import lru_cache
import io
import json
from pathlib import Path
from unittest.mock import patch

from py65.devices.mpu6502 import MPU
import probe_dkjr_life_star_1123 as Probe

Joined, S, Check, Head, H = Probe.Joined, Probe.S, Probe.Check, Probe.Head, Probe.H
N, W = Check.N, Check.W
offset = S.C.Old.Old.offset
PIN = Probe.PIN
CANDIDATE = '04fc8b962f1403707aa89039cc9379f4503f44acc6189e63e54694a9f01c5817'
GOKU = '93f140baee70d97dd061dae60d549c2ac1ed1920a80b2288fa2b52b9e4be1712'
WITH_GOKU = 'f0ed6a426bc224bb2b2c176bc9d5e5019dcc65b37f15000842672ebb06237da9'
OUT = Joined.Native.R / 'build/dkjr-life-star-lifts-1123'
PROBE_SHA = 'db935939d403028f4429da32b3530741da5bb656b13fd7f26f43d1eedf0acd05'
COOKIE = bytes.fromhex('a72801ce1e0ffdc9d951b88b4b623e71')
OLD_COLUMNS = (21,26,30,35,39,43,47,55,59,79,88,161,165,177,190)
OLD_CENTERS = (188,128,128,177,177,169,169,161,161,176,0,177,128,177,128)
COLUMNS = OLD_COLUMNS[:9]+(63,)+OLD_COLUMNS[9:11]+(102,)+OLD_COLUMNS[11:]
CENTERS = OLD_CENTERS[:9]+(176,)+OLD_CENTERS[9:11]+(176,)+OLD_CENTERS[11:]
GATE_BEFORE = bytes.fromhex('2082ad9009a51e29fdd0034c4cb21860')+b'\xea'*12
TAIL = bytes.fromhex('a51e29fdd0034c4cb21860')
LAYOUT = dict(ROWS=(0xd2c4,17), PIPE=(0xd18b,117), REFRESH=(0xb624,129), VISIBLE=(0xbfc4,28))


@lru_cache(maxsize=1)
def images():
    assert H(Path(Probe.__file__).read_bytes()) == PROBE_SHA
    p = S.C.program()
    assert p['symbols']['OscillatorY'] == 0xb696
    old = dict(ROWS=bytes(OLD_COLUMNS)+b'\xa1\xa1', PIPE=p['images']['PIPE'],
        REFRESH=p['images']['REFRESH'], VISIBLE=GATE_BEFORE)
    refresh=bytearray(old['REFRESH']);refresh[0xb69f-0xb624]=176
    old['REFRESH']=bytes(refresh)
    assert old['REFRESH'][-15:] == bytes(OLD_CENTERS)
    new=dict(old, ROWS=bytes(COLUMNS), VISIBLE=bytes.fromhex('2082adb00218604c96b6')+bytes(CENTERS)+b'\xea')
    pipe=bytearray(old['PIPE']);refresh=bytearray(old['REFRESH'])
    changes=[]
    for op, operand, before, after, section, pc_base in (
        ('LDY',14,b'\xa0\x0e',b'\xa0\x10','PIPE',0xd18b),
        ('LDA',0xb696,bytes.fromhex('b996b6'),bytes.fromhex('b9cebf'),'PIPE',0xd18b),
        ('CPY',10,b'\xc0\x0a',b'\xc0\x0b','REFRESH',0xb624)):
        ins=[r for r in p['instructions']if r['op']==op and r.get('operand')==operand and pc_base<=r['pc']<pc_base+LAYOUT[section][1]]
        assert len(ins)==1,(op,operand,ins)
        pc=ins[0]['pc'];at=pc-pc_base;part=pipe if section=='PIPE'else refresh
        assert part[at:at+len(before)]==before
        part[at:at+len(after)]=after;changes.append(dict(PC=pc,before=before.hex(),after=after.hex()))
    refresh[-15:]=TAIL+b'\xea'*4
    new.update(PIPE=bytes(pipe),REFRESH=bytes(refresh))
    assert len(COLUMNS)==len(CENTERS)==17 and COLUMNS[11]==88 and CENTERS[11]==0
    old_map=dict(zip(OLD_COLUMNS,OLD_CENTERS,strict=True));new_map=dict(zip(COLUMNS,CENTERS,strict=True))
    assert all(new_map[x]==y for x,y in old_map.items())
    for name,(_,size)in LAYOUT.items():assert len(old[name])==len(new[name])==size
    return old,new,changes


def replace(raw,parts):
    result=bytearray(raw)
    for name,(pc,_)in LAYOUT.items():
        for at,data in S.C.Old.chunks(pc,parts[name]):result[at:at+len(data)]=data
    return result


def proposal(parent):
    assert H(parent)==PIN and parent[S.C.Old.Head.COOKIE_AT:S.C.Old.Head.COOKIE_AT+16]==COOKIE
    old,new,changes=images();body=S.C.Old.Head.payload(parent)
    for name,(pc,size)in LAYOUT.items():
        assert body[offset(pc):offset(pc)+size]==old[name],name
    # Conservative literal census is also exact for the original named leaf:
    # its only public entry isADC5's JMPBFC4; no moved interior export exists.
    refs={target:[]for target in(0xbfc4,0xbfc9,0xbfd2,0xbfd4)}
    for start,part in ((0xa000,body[:8192]),(0xc900,body[8192:9216]),(0xd000,body[9216:])):
        for i in range(len(part)-2):
            target=int.from_bytes(part[i+1:i+3],'little')
            if part[i]in(0x20,0x4c)and target in refs:refs[target].append(start+i)
    assert refs=={0xbfc4:[0xadc5],0xbfc9:[],0xbfd2:[],0xbfd4:[]},refs
    result=replace(parent,new);at=S.C.Old.Head.COOKIE_AT
    result[at:at+16]=b'\xa7\x28\x01'+bytes.fromhex(H(S.C.Old.Head.payload(result)))[:13]
    result=bytes(result)
    if CANDIDATE is not None:assert H(result)==CANDIDATE
    owned={i for name,(pc,_)in LAYOUT.items()for pos,data in S.C.Old.chunks(pc,new[name])for i in range(pos,pos+len(data))}
    owned.update(range(at,at+16))
    assert {i for i,(a,b)in enumerate(zip(parent,result,strict=True))if a!=b}<=owned
    restored=replace(result,old);restored[at:at+16]=COOKIE;assert bytes(restored)==parent
    return result,dict(parent_SHA256=PIN,candidate_SHA256=H(result),cookie=result[at:at+16].hex(),
        owned=LAYOUT,operand_changes=changes,old15_positions_centers_and_types_exact=True,
        original_motor_and_jump_and_fall_guard_exact=True,new_RAM=0,new_CHR_pages=0,
        entry_predicate='SameBFC4 entry; original11B tail moved toB696, paired below.',
        oscillator_table=[0xbfce,0xbfdf],only_external_gate_entry=refs,
        helpers=[dict(character='Donkey Kong Jr.',stage='1-1',left=x,center=x+16,initial_top=192,
            native_ID=37,collision_width=32,oscillator_center=176)for x in(1008,1632)],
        natural_pickup_pass=False,native_qualified=False,outputs=0)


def inverse(raw):
    assert CANDIDATE is not None and H(raw)==CANDIDATE
    old,new,_=images();body=S.C.Old.Head.payload(raw)
    for name,(pc,size)in LAYOUT.items():assert body[offset(pc):offset(pc)+size]==new[name]
    parent=replace(raw,old);at=S.C.Old.Head.COOKIE_AT;parent[at:at+16]=COOKIE;parent=bytes(parent)
    assert H(parent)==PIN and proposal(parent)[0]==raw
    return parent


def current_parent(raw,work,*,with_goku=False):
    """Authenticate bcc or Goku93; optional future composition is memory-only."""
    if H(raw)==PIN and not with_goku:return raw,raw,None
    import repair_goku_hidden_head_1123 as G
    assert(G.BASE,G.CANDIDATE,G.NATIVE_BANK,G.QUERY,G.QUERY_SIZE,G.HELPER,G.HELPER_SIZE)==(
        PIN,GOKU,86,0xb236,192,0xb83b,34)
    if H(raw)==PIN:
        with patch.object(G,'SCRATCH',work):current=G.compose(raw)
        assert H(current)==GOKU
    else:assert H(raw)==GOKU;current=raw
    baseline=G.recover_parent(current);assert H(baseline)==PIN
    return baseline,current,G


def compose_current(current,private,goku):
    if goku is None:
        assert H(current)==PIN and H(private)==CANDIDATE
        return private,None
    assert H(current)==GOKU and H(private)==CANDIDATE
    baseline=goku.recover_parent(current);old,new,_=images()
    dk_changes={i for i,(a,b)in enumerate(zip(baseline,private,strict=True))if a!=b}
    g_changes={i for i,(a,b)in enumerate(zip(baseline,current,strict=True))if a!=b}
    g_regions=((709190,709382),(710731,710765))
    assert g_changes<={i for lo,hi in g_regions for i in range(lo,hi)} and not(dk_changes&g_changes)
    merged=replace(current,new);at=S.C.Old.Head.COOKIE_AT;merged[at:at+16]=private[at:at+16];merged=bytes(merged)
    assert goku.replace_spans(merged,goku.PARENT_QUERY,goku.PARENT_HELPER)==private
    recovered=replace(merged,old);recovered[at:at+16]=COOKIE
    assert bytes(recovered)==current and {i for i,(a,b)in enumerate(zip(current,merged,strict=True))if a!=b}==dk_changes
    if WITH_GOKU is not None:assert H(merged)==WITH_GOKU
    return merged,dict(current_Goku_SHA256=GOKU,DK_private_SHA256=CANDIDATE,combined_SHA256=H(merged),
        removing_Goku_is_exact04fc=True,removing_DK_is_exact93f1=True,
        all_actual_changes_disjoint=True,Goku_regions=g_regions,DK_changed_bytes=len(dk_changes),Goku_changed_bytes=len(g_changes))


def gate_units():
    old,new,_=images();count=0;costs={};digest=__import__('hashlib').sha256()
    for carry in(0,1):
        for state in range(256):
            for p in(0x20,0x61,0xee):
                results=[];cycles=[]
                for parts in(old,new):
                    mem=[0]*65536
                    for name,(pc,_)in LAYOUT.items():mem[pc:pc+len(parts[name])]=parts[name]
                    # Declared callee-return fixtures; the two real callee
                    # bodies are byte-identical and route tests use them.
                    mem[0xad82:0xad84]=[0x38 if carry else 0x18,0x60]
                    mem[0xb24c]=0x60;mem[0x1e]=state
                    c=MPU(memory=mem,pc=0xbfc4);c.a,c.x,c.y,c.p,c.sp=85,37,91,p,224
                    c.stPushWord(0x5aff);start=c.processorCycles
                    for _ in range(50):
                        if(c.pc,c.sp)==(0x5b00,224):break
                        c.step()
                    else:raise AssertionError(('Visible-entry fixture bound',hex(c.pc)))
                    results.append((c.a,c.x,c.y,c.p,c.sp,bytes(mem[:0x800])))
                    cycles.append(c.processorCycles-start)
                assert results[0]==results[1],(carry,state,p,results)
                diff=cycles[1]-cycles[0];expected=4 if carry else-1
                assert diff==expected,(carry,state,diff)
                costs.setdefault(str(carry),set()).add(diff);count+=1
                digest.update(bytes(results[0][:5])+results[0][5])
    return dict(passed=True,cases=count,exact_AXYP_SP_and_all_native_ZP_stack_RAM=True,
        cycle_delta_by_context_carry={k:sorted(v)for k,v in costs.items()},
        aggregate_SHA256=digest.hexdigest(),fixture_only=True,outputs=0)


def admission_units():
    """Compare actual old/new scope code, then every slot mask/constructor."""
    from bisect import bisect_right
    old,new,_=images();p=S.C.program();cpus=[]
    for parts in(old,new):
        mem=[0]*65536
        for name,(pc,_)in LAYOUT.items():mem[pc:pc+len(parts[name])]=parts[name]
        cpus.append(MPU(memory=mem))
    def call(c,pc,*,y=0,stop=()):
        c.pc,c.sp,c.a,c.x,c.y,c.p=pc,0xfd,0x5a,0,y,0x31
        c.memory[0x1fe],c.memory[0x1ff]=0xff,0x7f;start=c.processorCycles
        for _ in range(500):
            if c.pc==0x8000 or c.pc in stop:return c.processorCycles-start
            c.step()
        raise AssertionError(('Admission fixture bound',hex(c.pc)))
    scope_cases=extra_windows=0;cost_min=0;cost_max=0
    for page in range(11):
        for xpos in range(256):
            for seen in range(16):
                last=-1 if seen==0 else OLD_COLUMNS[seen-1]
                answers=[];cycles=[]
                for c,columns in zip(cpus,(OLD_COLUMNS,COLUMNS),strict=True):
                    c.memory[0x71d],c.memory[0x71f],c.memory[0xd6]=page,xpos,0xce
                    c.memory[0xc8fd]=bisect_right(columns,last)
                    cycles.append(call(c,p['symbols']['DkPipeScope']))
                    answers.append(columns[c.y]if c.p&1 else None)
                if answers[1]in(63,102):
                    assert answers[0]is None;extra_windows+=1
                else:assert answers[0]==answers[1],(page,xpos,seen,answers)
                diff=cycles[1]-cycles[0];cost_min=min(cost_min,diff);cost_max=max(cost_max,diff);scope_cases+=1
    c=cpus[1];allocations=constructors=0
    for row in range(17):
        for mask in range(64):
            c.memory[0xc8fd]=row
            for i in range(6):c.memory[0x10+i]=bool(mask&(1<<i))
            call(c,p['symbols']['DkPipeTry'],stop=(p['symbols']['Birth'],p['symbols']['RefreshStart']))
            expected=next((i for i in range(4 if row==0 else 5,-1,-1)if not mask&(1<<i)),None)
            got=c.x if c.pc==p['symbols']['Birth']else None
            assert got==expected and c.y==row,(row,mask,got,expected,c.y);allocations+=1
        for slot in range(6):
            c.x=slot
            # Call explicitly preserves the original native constructor slot.
            c.pc,c.sp,c.a,c.y,c.p=p['symbols']['DkSetPlatformTypeAndPosition'],0xfd,0x5a,row,0x31
            c.memory[0x1fe],c.memory[0x1ff]=0xff,0x7f
            for _ in range(80):
                if c.pc==0x8000:break
                c.step()
            else:raise AssertionError('Constructor fixture bound')
            assert(c.a,c.y,c.p&1)==(0x4f,0xa7,1)
            assert c.memory[0x17+slot]==(40 if row==11 else 37)
            assert c.memory[0xbe+slot]==(208 if row==11 else 192)
            assert c.memory[0x76+slot]==(COLUMNS[row]*16)&255
            constructors+=1
    return dict(passed=True,old_new_scope_cases=scope_cases,new_helper_only_windows=extra_windows,
        original_column_selection_exact=True,scope_cycle_delta=[cost_min,cost_max],
        all17_row_slot_masks=allocations,constructor_cases=constructors,
        new_rows_use_ordinary_scan=True,only_existing_row0_skips5=True,global_slot_reserved=False,outputs=0)


def controller(baseline,parent,candidate):
    text=Probe.controller(baseline,parent,kind='star');original=text
    assert H(text.encode())=='072e2daa63c97239d2adcfc8151bd394e2ece36be1cd184f20852609c1998e7e'
    assert text.count(PIN)==2;text=text.replace(PIN,H(candidate))
    before=f"cookie=='{COOKIE.hex()}'";after=f"cookie=='{candidate[S.C.Old.Head.COOKIE_AT:S.C.Old.Head.COOKIE_AT+16].hex()}'"
    text=Check.Replay.one(text,before,after)
    text=Check.Replay.one(text,'local centers={[1264]=176,','local centers={[1008]=176,[1632]=176,[1264]=176,')
    assert text.count('ram(2,0x8fd)~=10')==2
    text=text.replace('ram(2,0x8fd)~=10','ram(2,0x8fd)~=11')
    restored=text.replace('ram(2,0x8fd)~=11','ram(2,0x8fd)~=10')
    restored=Check.Replay.one(restored,'local centers={[1008]=176,[1632]=176,[1264]=176,','local centers={[1264]=176,')
    restored=Check.Replay.one(restored,after,before).replace(H(candidate),PIN)
    assert restored==original
    assert not any(v in text for v in('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    Check.LuaRuntime().compile(text);return text


class Done(Exception):pass


def prefix(raw,text,*,limit=5200):
    m,opening=Head.cold(raw);births={};retired={};last_helpers={};recent=[];steps=0;end=None
    def observe(memory,c):
        if c.pc!=0xd1f0 or Head.point(c)!=(2,0xd1f0)or c.x>=6:return
        a=Head.actor(m,c.x)
        if a['id']not in(37,40):return
        assert str(a['x'])not in births
        births[str(a['x'])]=dict(step=steps,hero=Head.state(m),actor=a,row=m.ram[2][0x8fd],all_actors=Head.actors(m))
        if a['x']==1408:assert not any(v['x']==1008 and v['id']==37 for v in Head.actors(m)),'Life helper retired before critical second-gap admission'
    def after(memory):
        nonlocal steps,last_helpers,end
        steps+=1;s=Head.state(m)
        # Horizontal1408 changes X every few calls; its currentX is not an
        # identity or retirement. Only fixed-X verticals belong in this map.
        helpers={a['x']:a for a in Head.actors(m)if a['id']==37}
        for x,a in last_helpers.items():
            if x not in helpers and str(x)not in retired:retired[str(x)]=dict(step=steps,hero=s,last_actor=a)
        last_helpers=helpers
        if s['x']>=960:
            recent.append(dict(step=steps,hero=s,source_y=m.ram[2][0x210],pad=m.controller_pad,actors=Head.actors(m)))
            if len(recent)>8:recent.pop(0)
        if s['x']>=1700 and s['source']==s['prior']==1 and N.get(m,'Player_State')==0:
            assert s['lives']==2 and s['hurt']==0
            end=dict(step=steps,hero=s,actors=Head.actors(m));raise Done
    try:
        with patch.object(Check.Route.Frames,'frame',Check.normal_frame),redirect_stdout(io.StringIO()):
            result=Check.Route.route(m,raw,limit,controller_text=text,observe_extra=observe,after_frame=after)
    except Done:result=None
    except Exception as error:result={'receipt':{'reason':type(error).__name__+': '+str(error)}}
    q=(result or{}).get('receipt')or{}
    return dict(passed=end is not None,ROM_SHA256=H(raw),controller_SHA256=H(text.encode()),opening_Main=opening,
        steps=steps,births=births,retired=retired,endpoint=end,final=Head.state(m),recent=recent,
        reason=q.get('reason'),ordinary_compiled_menu_and_input_only=True,outputs=0)


def root_native(image,text,installed):
    """Root-only opt-in existing-slot full1-1/1-2 replay; no installer."""
    stock=Joined.Native;target,script=stock.OUT/'candidate.nes',stock.OUT/'controller.lua'
    assert set(stock.OUT.iterdir())=={target,script}
    old_target,old_script=target.read_bytes(),script.read_bytes();guard=stock.check(stock.ROM)
    assert stock.ROM.read_bytes()==installed and old_target==installed and not guard['matching_patch_files']
    stock.require_free_workspace(stock.R,target,allow_interactive=True)
    program=text.encode()
    try:
        target.write_bytes(image);script.write_bytes(program);private=stock.check(target)
        assert private['ROM_sha256']==H(image)and not private['matching_patch_files']
        result=stock.run(script,target,stock.OUT/'capture',H(image),360,long_no_capture=True)
        assert result['script_SHA256']==H(program)and result['outputs_written']==0 and not result['images']
        assert target.read_bytes()==image and script.read_bytes()==program and stock.check(target)==private
        print('DK LIFE STAR FULL NATIVE '+json.dumps(result,separators=(',',':')),flush=True)
        return int(not result['passed'])
    finally:
        script.write_bytes(old_script);target.write_bytes(old_target)
        assert set(stock.OUT.iterdir())=={target,script} and target.read_bytes()==old_target and script.read_bytes()==old_script
        assert stock.ROM.read_bytes()==installed and stock.check(stock.ROM)==guard


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--route',choices=('baseline','candidate'))
    ap.add_argument('--compose-only',action='store_true')
    ap.add_argument('--compile-only',action='store_true')
    ap.add_argument('--with-goku',action='store_true');ap.add_argument('--run',action='store_true')
    args=ap.parse_args();installed=Joined.Native.ROM.read_bytes()
    assert sum((bool(args.route),args.compose_only,args.compile_only,args.run))<=1
    work=Joined.Native.OUT if args.run else OUT
    if args.run:
        assert set(work.iterdir())=={work/'candidate.nes',work/'controller.lua'}
        Joined.Native.require_free_workspace(Joined.Native.R,work/'candidate.nes',allow_interactive=True)
    try:
        with Joined.cache(),patch.object(Probe,'OUT',work):
            baseline,current,goku=current_parent(installed,work,with_goku=args.with_goku)
            parent,binding=Probe.authenticate(baseline)
            private,layout=proposal(baseline)
            assert inverse(private)==baseline
            candidate,composition=compose_current(current,private,goku)
            units=gate_units();admissions=admission_units()
            text=None if args.compose_only else controller(baseline,parent,candidate)
            spans=[]
            for name,(pc,_)in LAYOUT.items():
                for at,data in S.C.Old.chunks(pc,images()[1][name]):
                    before=baseline[at:at+len(data)]
                    spans.append(dict(role=name,PC=pc,file_start=at,file_end=at+len(data),
                        before_SHA256=H(before),after_SHA256=H(data),before=before.hex(),after=data.hex()))
            report=dict(binding=binding,layout=layout,composition=composition,spans=spans,units=units,admissions=admissions,
                controller_SHA256=H(text.encode())if text else None,
                source_SHA256=H(Path(__file__).read_bytes()),outputs=0)
            print('DK LIFE STAR LIFTS '+json.dumps(report,separators=(',',':')),flush=True)
            if args.route:
                raw=candidate if args.route=='candidate'else current
                policy=text if args.route=='candidate'else Probe.controller(baseline,parent,kind='star')
                if args.route=='baseline'and H(current)!=PIN:policy=policy.replace(PIN,H(current))
                q=prefix(raw,policy);q['mode']=args.route
                print('DK LIFE STAR PREFIX '+json.dumps(q,separators=(',',':')),flush=True)
                print('RECEIPT '+H(json.dumps(q,sort_keys=True,separators=(',',':')).encode()),flush=True)
            if args.run:return root_native(candidate,text,installed)
    finally:
        if OUT.exists():assert not any(OUT.iterdir());OUT.rmdir()


if __name__=='__main__':raise SystemExit(main())
