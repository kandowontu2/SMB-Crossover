"""Private body-first draw probe: no native or installed source changes."""
from pathlib import Path
import argparse, hashlib, itertools, json, traceback
import mm_proto_shot_mux_cpu_v1 as harness
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(b, cfg, irq=None, reference=False):
    c, m, before = harness.setup(b, cfg)
    put = lambda n,v: m.__setitem__(address(b,n),v)
    for n,v in dict(OperMode_Task=cfg.get('task',3),GameEngineSubroutine=cfg.get('engine',8),
                    OperMode=cfg.get('mode',1), RgOamFirst=cfg.get('first',0),
                    RgOamUsed=cfg.get('used',160), SpriteShuffleOffset=cfg.get('shuffle',0)).items():
        put(n,v)
    if cfg.get('body') is not None:
        put('ObjectMetasprite', cfg['body'])
    # World fixtures use actual original record indices and native locations.
    for slot in cfg.get('world',[]):
        m[address(b,'ObjectMetasprite')+slot] = address(b,'METASPRITE_GOOMBA_WALK1')
        for n,v in [('SprObject_Rel_XPos',128),('SprObject_Y_Position',192),('SprObject_Y_HighPos',1)]:
            if n in b['syms']:
                m[address(b,n)+slot] = v
    m[0x5204] = 128
    m.writes=[]
    trace=[]
    for index in range(100000):
        if c.pc == 0x7f00:
            break
        trace.append((index,c.pc,m.banks[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1))
        c.step()
    else:
        raise AssertionError(('Timeout',cfg,hex(c.pc),m.banks))
    assert c.sp == 253
    for name,value in before.items():
        assert bytes(m[address(b,name):address(b,name)+4]) == value, ('Changed live projectile',name,cfg)
    return c,m,trace


def state(b,c,m):
    return (c.a,c.x,c.y,c.p&207,c.sp,bytes(m[:0x1c0]+m[0x200:0x8000]),tuple(m.banks),tuple((at,v) for at,v in m.writes if 0x2000<=at<0x5c00))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['parent','candidate','output']:
        p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--pilot',action='store_true')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    old,new=[scoped_load(v) for v in [a.parent,a.candidate]]
    rows=[]
    try:
        for char,variant,flag,frame in itertools.product([i for i in range(20) if i!=1],[0,1],[0x20,0x61,0xa2,0xeb],[0,1]):
            cfg=dict(entry='DrawAllMetasprites',char=char,variant=variant,frame=frame,flags=flag,types=[1,1,1,1])
            c,m,_=run(old,cfg);d,n,_=run(new,cfg)
            assert state(old,c,m)==state(new,d,n),('Foreign state',cfg,(c.a,c.x,c.y,c.p),(d.a,d.x,d.y,d.p),[(hex(i),m[i],n[i]) for i in range(0x8000) if not 0x1c0<=i<0x200 and m[i]!=n[i]][:24])
            assert d.processorCycles<=c.processorCycles,('Foreign cost regression',cfg,c.processorCycles,d.processorCycles)
            rows.append(dict(tag='foreign',cfg=cfg,baseline=c.processorCycles,candidate=d.processorCycles,delta=d.processorCycles-c.processorCycles))
        owned=[]
        for variant,mask,first,frame in itertools.product([0,1],[0,1,3,7,15],[0,4,80,156],[0,1]):
            cfg=dict(entry='DrawAllMetasprites',char=1,variant=variant,frame=frame,flags=0x20,types=[mask>>i&1 for i in range(4)],first=first)
            c,m,t=run(old,cfg);d,n,u=run(new,cfg)
            diffs=[dict(address=hex(i),old=m[i],new=n[i]) for i in range(0x8000) if not 0x1c0<=i<0x200 and m[i]!=n[i]]
            owned.append(dict(cfg=cfg,old_regs=[c.a,c.x,c.y,c.p&207,c.sp],new_regs=[d.a,d.x,d.y,d.p&207,d.sp],old_cycles=c.processorCycles,new_cycles=d.processorCycles,delta=d.processorCycles-c.processorCycles,differences=diffs))
        result=dict(passed=True,probe_only=True,source_only=True,native_run=False,parent_ROM_sha256=sha(a.parent),candidate_ROM_sha256=sha(a.candidate),foreign_cases=len(rows),foreign_full_state_exact=True,foreign_cost_range=[min(r['delta'] for r in rows),max(r['delta'] for r in rows)],owned_probe_cases=len(owned),checker_sha256=sha(__file__))
        (a.output/'owned-probe.json').write_text(json.dumps(owned,indent=2)+'\n')
        (a.output/'foreign-cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
        (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))
    except BaseException as e:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(e),traceback=traceback.format_exc(),completed_foreign=len(rows),checker_sha256=sha(__file__)),indent=2)+'\n')
        (a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes())
        raise


if __name__=='__main__':
    main()
