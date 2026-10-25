"""Matched full BG calls: verify the HL guards and quantify their local cost."""
from pathlib import Path
import collections,csv,hashlib,importlib.util,json,sys,traceback
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'ryu-dispatch-cost-ho'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sys.path.insert(0,str(V/'specialist-mario-easy-hard-source-a/deps'));G=V/'ryu49-head-status-bridge-g';sys.path.insert(0,str(G))
sp=importlib.util.spec_from_file_location('ryu_ho_model',G/'check.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g);CPU=g.loadcpu().NesMPU


def execute(im,raw,regs,banks,start,stop,stopbank):
    m=g.Bus(im,raw,banks);c=CPU(memory=m);c.a,c.x,c.y,c.p,c.sp=regs;c.pc=start;c.processorCycles=0;steps=0;g.native_input(c.p)
    while steps==0 or c.pc!=stop or m.banks.get(c.pc&0xe000,-1)!=stopbank:
        m.pc=c.pc;m.op=m.data[c.pc];pop=m.data[0x100+((c.sp+1)&255)]if m.op in(0x28,0x40)else None
        bank=m.banks.get(c.pc&0xe000,-1);code=bytes(m.data[c.pc:c.pc+8]).hex();c.step()
        if pop is not None:g.restore_native_status(c,m.op,pop,m.pc,bank,code)
        steps+=1;assert steps<60000
    return dict(regs=[c.a,c.x,c.y,c.p,c.sp,c.pc],ram=m.ram(),trace=m.trace,cycles=c.processorCycles)


def main():
    assert not O.exists();O.mkdir();report=dict(passed=False,cases=[],gaps=[],goal_complete=False)
    try:
        for mapper in('mmc3','mmc5'):
            images=[g.Image(V/f'ryu-current-{tag}/source/build/smb-crossover-{mapper}.nes')for tag in('hd','hl')]
            d=V/f'ryu-native-hm/caller-f-candidate-{mapper}';cfg=json.loads((d/'binding.json').read_text())['config'];n=d/'native-output'
            post=next(z for z in cfg['hooks']if z['name']=='post');ad=images[1].ram['SmCeilingHit']
            assert post['bytes'][:3]==[0xad,ad&255,ad>>8],'Actual next caller instruction overwrites A/N/Z before use'
            rows=list(csv.DictReader((n/'events.csv').open()));pairs=collections.defaultdict(dict)
            for z in rows:pairs[int(z['case'])][z['event']]=z
            fmt=__import__('struct').Struct('<IHBBH');w=(n/'writes.bin').read_bytes();ws=collections.defaultdict(list)
            for off in range(0,len(w),fmt.size):z=fmt.unpack_from(w,off);ws[z[0]].append(z)
            for sid,pair in pairs.items():
                if set(pair)!= {'pre','post'}or any(z[3]for z in ws[sid]):report['gaps'].append(dict(mapper=mapper,case=sid,reason='actual interrupt or incomplete capture'));continue
                e,z=pair['pre'],pair['post'];raw=(n/f'{sid:03}-pre.bin').read_bytes();regs=[int(e[k])for k in('A','X','Y','P','SP')]
                banks={a:int(e[k])for a,k in((0x8000,'bank8'),(0xa000,'bankA'),(0xc000,'bankC'),(0xe000,'bankE'))}
                qs=[execute(i,raw,regs,banks,int(e['PC']),int(z['PC']),int(z['bankA']))for i in images];a,b=qs
                assert a['regs'][1:3]+a['regs'][4:]==b['regs'][1:3]+b['regs'][4:]
                assert(a['regs'][3]^b['regs'][3])&~0x82==0
                L=images[1].ram;smc={L[k]+v for k,v in(('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('NextBank_SMC',1),('SafereturnA_SMC',1))}
                differences=[]
                for i,(av,bv)in enumerate(zip(a['ram'],b['ram'])):
                    if av==bv:continue
                    address=i if i<2048 else i-2048+0x6000
                    aw=[t for t in a['trace']if t[3]==address];bw=[t for t in b['trace']if t[3]==address]
                    if address not in smc:
                        assert 0x100<=address<=0x100+regs[4],('live RAM',mapper,sid,address,av,bv)
                        assert any(t[1]in(0x20,0x48,0x08)for t in aw+bw)
                    differences.append(dict(address=address,old=av,new=bv,old_writers=aw,new_writers=bw))
                report['cases'].append(dict(mapper=mapper,case=sid,kind=cfg['cases'][sid-1]['kind'],cycles=[a['cycles'],b['cycles']],delta=b['cycles']-a['cycles'],same_live_RAM_and_live_registers=True,dead_A_NZ_values=[a['regs'][0],a['regs'][3]&0x82,b['regs'][0],b['regs'][3]&0x82],individually_traced_stack_SMC_differences=differences))
            print(mapper,dict(collections.Counter((z['kind'],z['delta'])for z in report['cases']if z['mapper']==mapper)),flush=True)
        report.update(passed=True,scope='Same-entry compiled whole BG calls with real attained native component states; source guard optimization only. All live RAM/X/Y/SP/PC/physical flags except A/N/Z match. Actual next compiled LDA overwrites A/N/Z. Popped stack and exact mutable-call operands individually listed. Five native interrupt captures excluded from this local cost comparison, retained in HM.')
    except Exception as ex:report.update(error=repr(ex),traceback=traceback.format_exc());raise
    finally:(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
