"""Paired real original fruit-touch callers through leased relocated code."""
from collections import Counter,defaultdict
from hashlib import sha256
from itertools import product
import json

import check_dkjr_entry_components_1116 as K

C,N,W=K.C,K.N,K.W
H=lambda value:sha256(value).hexdigest()


def prepared(seed,labels,count,kind,dx,y):
    m=K.fork(seed)
    for name in('DkjrNativeImportAnchor','DkjrNativeCameraSync','DkjrBounds','DkjrNativeFruitReset'):
        K.Route.Cold.H.call(m,labels[name])
    world=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
    for slot in range(count):
        x=world+dx+8*slot
        m[3:7]=bytes((x&255,x>>8,y,kind))
        c=K.Route.Cold.H.call(m,labels['DkjrNativeFruitSet'],x=slot)
        assert c.p&1
    K.Route.Cold.H.call(m,labels['DkjrNativeFruitProject'])
    # Exactly the original move caller's freshly published player rectangle.
    K.Route.Cold.H.call(m,labels['DkjrBounds'])
    return m


def run():
    parent,raw,composition,fit,labels,sites,allowed,seeds,openings=K.setup()
    moved={row['label']:row['new_PC']for row in fit['moved_labels']}
    entry=labels['D_d955'];count=0;digest=sha256();minimum=255;executed=Counter();costs=defaultdict(set);hits=0
    for fruit_count,kind,dx,y,p in product((0,1,4),range(3),(0,40),(160,190),(0x20,0x61,0xff)):
        outputs=[];traces=[];clocks=[];semantics=[]
        for version,seed in enumerate(seeds):
            m=prepared(seed,labels,fruit_count,kind,dx,y)
            before=bytes(m.ram[3][:0x1fe0]);trace=[];active=None
            entries={row['oldpc'if version==0 else'newpc']:row for row in sites}
            cells={row['oldcell'if version==0 else'newcell']for row in sites}
            def watch(memory,c):
                nonlocal active
                if c.pc in entries:active=entries[c.pc]
                if c.pc in cells:
                    assert active is not None
                    addr=memory[c.pc+1]+256*memory[c.pc+2]
                    trace.append((active['name'],active['operation'],addr,c.a,c.x,c.y,c.p,c.sp+(2 if version and active['folded']else 0)))
            c,depth=K.execute(m,entry if version==0 else moved.get('D_d955',entry),0x5b00,
                a=85,x=37,y=91,p=p,whole=True,watch=watch)
            minimum=min(minimum,depth);K.code_delta(before,m,allowed[version])
            outputs.append(K.snapshot(m,c));traces.append(trace);clocks.append(c.processorCycles)
            semantics.append(dict(active_touch=m.ram[2][0x8c],fruit_visible=list(m.ram[2][0x9a:0x9e]),
                actorY=m.ram[2][0x210],phase=m.ram[2][0x6b],fruit_records=bytes(m.ram[2][0x400:0x41d]).hex()))
        assert outputs[0]==outputs[1],('Fruit caller ABI/data',fruit_count,kind,dx,y,p,outputs[0][0],outputs[1][0])
        assert traces[0]==traces[1],('Fruit semantic pointer trace',fruit_count,kind,dx,y,p,traces)
        assert semantics[0]==semantics[1]
        executed.update(row[0]for row in traces[1]);hits+=bool(semantics[1]['active_touch'])
        digest.update(bytes(outputs[0][0])+outputs[0][1]);count+=1
        costs[fruit_count].add(clocks[1]-clocks[0])
    assert all(executed['D_'+suffix]>0 for suffix in('d973','d978','d9b6','d9c7'))
    return dict(passed=True,parent_SHA256=H(parent),candidate_SHA256=H(raw),paired_fruit_calls=count,
        real_typed_FruitSet_Project_and_Bounds_used=True,declared_component_only=True,
        actual_semantic_pointer_calls=dict(executed),active_touch_cases=hits,
        full_AXYP_SP_source_native_maps_SMC33_live_stack_equal=True,minimum_SP=minimum,
        measured_extra_cycles_by_FruitCount={key:sorted(value)for key,value in costs.items()},
        aggregate_SHA256=digest.hexdigest(),no_natural_stock_or_route_claim=True,outputs=0)


if __name__=='__main__':
    report=run();text=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_ENTRY_FRUIT '+text,flush=True)
    print('DKJR_ENTRY_FRUIT_SHA256 '+H(text.encode()),flush=True)
