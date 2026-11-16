"""Actual mounted entry-funding pointer/draw/fruit components; zero outputs."""
from collections import Counter,defaultdict
from hashlib import sha256
from itertools import product
import json

import compose_dkjr_forced_entry_current_1116 as C
import check_dkjr_carry_camera_route_1116 as Route

N,W,L=Route.N,Route.Cold.W,Route.Cold.H.L
H=lambda value:sha256(value).hexdigest()


def setup():
    current=C.BT.ROM.read_bytes();parent,_=C.Parent.proposal(current);raw,composition=C.proposal(parent)
    assert C.inverse(raw)==parent
    fit=C.Plan.measure(current)
    source,known=C.Camera.Plan.source_inputs()
    old=C.Camera.Plan.Source.T.assemble(''.join(f'{n}=${v:x}\n'for n,v in known.items())+
        C.Camera.Plan.Source.expand_branches(source),dict(DKJR=(0xa000,8160),DK_MAIN=(0xd65e,73),
        DK_PAUSE=(0xd540,286),DK_PORTS=(0xd6a7,345)))
    labels=old['symbols'];moved={row['label']:row['new_PC']for row in fit['moved_labels']}
    import re
    funded={row['label']:row for row in fit['exact_funding_templates']}
    sites=[]
    for match in re.finditer(r'^DIndirect_([0-9a-f]+): (lda|sta) \$ffff,y$',source,re.M):
        suffix,op=match.groups();name='D_'+suffix;oldpc=labels[name];newpc=moved.get(name,oldpc)
        start=source.index(name+':');piece=source[start:match.end()]
        pointer=int(re.findall(r' lda \$(c[0-9a-f]{3})\n',piece)[0],16)
        folded=name in funded
        newcell=(fit['self_contained_readers']['cell_PC']if op=='lda'else fit['self_contained_readers']['store_cell_PC'])if folded else newpc+22
        sites.append(dict(name=name,operation=op,pointer=pointer,oldpc=oldpc,newpc=newpc,
            oldcell=oldpc+22,newcell=newcell,folded=folded))
    assert len(sites)==23 and sum(row['folded']for row in sites)==10
    code_cells=[]
    for version in('old','new'):
        cells={row[version+'cell']+offset-0xa000 for row in sites for offset in(1,2)}
        for name in('StoreRect','StoreEnd'):cells.add(labels[name]+1-0xa000)
        code_cells.append(cells)
    seeds=[];openings=[]
    for image,cells in zip((parent,raw),code_cells):
        opening,seed=Route.cold(image);packet=C.Camera.payload(image)
        differences={i for i,(a,b)in enumerate(zip(packet[:0x1fe0],seed.ram[3][:0x1fe0]))if a!=b}
        assert differences<=cells,('Unclassified constructor code writes',H(image),sorted(differences-cells))
        assert all(bytes(seed.ram[b][0x1fe0:0x1ff0])==image[534485:534501]for b in(2,3))
        seeds.append(seed);openings.append(dict(ROM_SHA256=H(image),opening=opening,
            post_constructor_precise_code_field_deltas=sorted(differences)))
    assert bytes(seeds[0].ram[2][:0x900])==bytes(seeds[1].ram[2][:0x900]),'Cold source data differ'
    return parent,raw,composition,fit,labels,sites,code_cells,seeds,openings


def fork(seed):
    m=L.clone(seed);m.raw_page(1,3);m.raw_page(2,2);N.put(m,CurrentBank=3,CurrentBankC=2)
    # Declared component caller's live stack. No gameplay outcome is seeded.
    m[0x1e1:0x200]=bytes((i*19+7)&255 for i in range(31))
    return m


def execute(m,pc,stop,*,a=85,x=37,y=0,p=0x61,whole=False,watch=None):
    c=N.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224
    if whole:c.stPushWord(0x5aff)
    minimum=c.sp
    for steps in range(100000):
        if (c.pc,c.sp)==(stop,224):return c,minimum
        minimum=min(minimum,c.sp)
        if watch:watch(m,c)
        assert m[c.pc],('Component BRK',hex(c.pc),c.sp)
        c.step()
    raise AssertionError(('Component bound',hex(c.pc),c.sp))


def snapshot(m,c):
    return ((c.a,c.x,c.y,c.p,c.sp),bytes(m.ram[2][:0x1fe0]),bytes(m[:0x100]),
        bytes(m[0x15a:0x17b]),bytes(m[0x200:0x800]),bytes(m[0x1e1:0x200]),
        tuple(m.rawtags),bytes(m[0x5c00:0x8000]),bytes(m.vram),tuple(m.chr_latches))


def code_delta(before,m,allowed):
    changes={i for i,(a,b)in enumerate(zip(before,m.ram[3][:0x1fe0]))if a!=b}
    assert changes<=allowed,('Unexpected private-code write',sorted(changes-allowed))
    return changes


def pointers(seeds,sites,allowed):
    count=0;digest=sha256();cycles=defaultdict(set);minimum=255
    flags=(0x20,0x21,0x61,0x69,0xff)
    for row,p,low,y in product([r for r in sites if r['folded']],flags,(0,255),(0,255)):
        outputs=[];clocks=[];traces=[]
        for version,seed in enumerate(seeds):
            m=fork(seed);ptr=row['pointer'];high=2 if ptr==0xc004 else 4
            m.ram[2][ptr-0xc000:ptr-0xc000+2]=bytes((low,high))
            target=((high|0xc0)<<8)+low+y
            m[target]=153
            before=bytes(m.ram[3][:0x1fe0]);trace=[]
            cell=row['oldcell']if version==0 else row['newcell']
            def watch(memory,c):
                if c.pc==cell:
                    address=memory[c.pc+1]+256*memory[c.pc+2]
                    trace.append((address,c.a,c.x,c.y,c.p,c.sp+(2 if version else 0)))
            start=row['oldpc']if version==0 else row['newpc'];end=start+(25 if version==0 else 3)
            c,depth=execute(m,start,end,p=p,y=y,watch=watch)
            minimum=min(minimum,depth);assert len(trace)==1
            code_delta(before,m,allowed[version]);outputs.append(snapshot(m,c));clocks.append(c.processorCycles);traces.append(trace)
        assert outputs[0]==outputs[1],('Actual pointer ABI/data',row['name'],p,low,y,outputs[0][0],outputs[1][0])
        assert traces[0]==traces[1],('Effective pointer/AXYP/liveStack',row,traces)
        digest.update(bytes(outputs[0][0]));count+=1
        cycles[row['operation']+':'+hex(row['pointer'])].add(clocks[1]-clocks[0])
    return dict(passed=True,actual_folded_prefixes=10,paired_cases=count,complete_AXYP_SP_data_maps_live_stack_equal=True,
        effective_cell_AXYP_SP_representations_equal=True,minimum_SP=minimum,
        actual_added_cycles={key:sorted(value)for key,value in cycles.items()},aggregate_SHA256=digest.hexdigest())


def whole_draw(seeds,fit,labels,sites,allowed):
    moved={row['label']:row['new_PC']for row in fit['moved_labels']};entry=labels['D_ea08']
    count=0;digest=sha256();cycles=defaultdict(set);minimum=255;executed=Counter()
    for op,p,xpos,ypos,tile in product(range(5),(0x20,0x61,0xff),(0,248),(0,240),(0,54)):
        outputs=[];clocks=[];traces=[]
        for version,seed in enumerate(seeds):
            m=fork(seed);m.ram[2][0:4]=bytes((xpos,ypos,tile,0x24));before=bytes(m.ram[3][:0x1fe0]);trace=[];active=None
            entries={row['oldpc'if version==0 else'newpc']:row for row in sites}
            cells={row['oldcell'if version==0 else'newcell']for row in sites}
            def watch(memory,c):
                nonlocal active
                if c.pc in entries:active=entries[c.pc]
                if c.pc in cells:
                    assert active is not None
                    addr=memory[c.pc+1]+256*memory[c.pc+2]
                    trace.append((active['name'],active['operation'],addr,c.a,c.x,c.y,c.p,c.sp+(2 if version and active['folded']else 0)))
            c,depth=execute(m,entry if version==0 else moved.get('D_ea08',entry),0x5b00,
                a=op,x=37,y=91,p=p,whole=True,watch=watch)
            minimum=min(minimum,depth);code_delta(before,m,allowed[version])
            outputs.append(snapshot(m,c));clocks.append(c.processorCycles);traces.append(trace)
        assert outputs[0]==outputs[1],('Actual whole Draw',op,p,xpos,ypos,tile,outputs[0][0],outputs[1][0])
        assert traces[0]==traces[1],('Actual Draw SMC semantics',op,p,traces)
        executed.update(row[0]for row in traces[1]);digest.update(bytes(outputs[0][0])+outputs[0][1]);count+=1
        cycles[op].add(clocks[1]-clocks[0])
    return dict(passed=True,paired_whole_draw_cases=count,operations=list(range(5)),all_source_RAM_and_native_data_equal=True,
        complete_AXYP_SP_maps_SMC33_live_stack_equal=True,actual_semantic_pointer_calls=dict(executed),minimum_SP=minimum,
        actual_added_cycles_by_operation={key:sorted(value)for key,value in cycles.items()},aggregate_SHA256=digest.hexdigest())


if __name__=='__main__':
    parent,raw,composition,fit,labels,sites,allowed,seeds,openings=setup()
    print('DKJR_ENTRY_COMPONENT_PHASE actual-cold-both-images',flush=True)
    pointer=pointers(seeds,sites,allowed)
    print('DKJR_ENTRY_COMPONENT_PHASE pointer-prefixes-pass',flush=True)
    draw=whole_draw(seeds,fit,labels,sites,allowed)
    report=dict(passed=True,parent_SHA256=H(parent),candidate_SHA256=H(raw),composition=composition,
        opening= openings,pointers=pointer,whole_draw=draw,
        scope='Actual independently cold-mounted old/new pointer and whole original draw components; declared input/stack fixtures, no natural route or pending entry claim.',
        outputs=0)
    text=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_ENTRY_COMPONENTS '+text,flush=True)
    print('DKJR_ENTRY_COMPONENTS_SHA256 '+H(text.encode()),flush=True)
