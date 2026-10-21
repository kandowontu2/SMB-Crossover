"""Compare the optimized leaf to E for whole state and every ordered write."""
from pathlib import Path
import hashlib,importlib.util,json,random,statistics,traceback
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-freeze-render-fast-f'
A=V/'agent49-samus-bill-arsenal-a';E=V/'root49-ice-integrated-e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
at=lambda a:a if a<0x800 else a-0x6000+0x800
def main():
    out=H/'leaf-review-c.json';assert not out.exists()
    sp=importlib.util.spec_from_file_location('original_frozen_cpu_oracle',A/'palette_native_model_cu.py')
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    cp=R/'build/checkpoints/roster-audit-v49-ice-over-sophia-e/manifest.json';c=json.loads(cp.read_text())
    pre=json.loads((H/'preparation-b.json').read_text());b=json.loads((H/'build-review.json').read_text())
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    for n,h in pre['source_hashes'].items():assert sha(H/'source'/n)==h,n
    result=dict(status='REVIEWING',script_sha256=sha(__file__),groups=[],main_changed=False,goal_complete=False)
    try:
        for mp in ['mmc3','mmc5']:
            old=m.q.Image(cp.parent/f'smb-crossover-{mp}.nes');new=m.q.Image(H/'source/build'/f'smb-crossover-{mp}.nes')
            assert old.ram==new.ram;A0=old.ram
            z=E/('state-cm-'+mp);events=[json.loads(x)for x in(z/'trace.jsonl').read_text().splitlines()]
            raw=(z/'ram.bin').read_bytes();pairs={}
            for q in events:
                if q['event']in ['entry','return']:pairs.setdefault(q['id'],{})[q['event']]=q
            native=[q for q in pairs.values()if q['entry']['name']=='SamusFreezeRenderFinish']
            costs=[];digest=hashlib.sha256();count=0
            def compare(initial,regs,banks,stop,stopsp):
                nonlocal count
                oh=old.hook('SamusFreezeRenderFinish');nh=new.hook('SamusFreezeRenderFinish')
                x=m.execute(old,initial,regs,banks,oh['address'],stop,stopsp)
                y=m.execute(new,initial,regs,banks,nh['address'],stop,stopsp)
                assert x['regs']==y['regs']and x['ram']==y['ram']and x['banks']==y['banks']and x['selector']==y['selector'],('allRAM/registers/mapper',mp,count)
                assert[(t[2],t[4])for t in x['trace']]==[(t[2],t[4])for t in y['trace']],('allorderedwrites',mp,count)
                assert y['cycles']<x['cycles'],('actualleafmustsavecycles',mp,count,x['cycles'],y['cycles'])
                costs.append((x['cycles'],y['cycles']));digest.update(y['ram']);digest.update(bytes(y['regs'][:5]));count+=1
            for q in native:
                e,z=q['entry'],q['return'];banks={a:e[n]for a,n in [(0x8000,'bank8'),(0xa000,'bankA'),(0xc000,'bankC'),(0xe000,'bankE')]}
                compare(m.snapshot(raw,e),[e[n]for n in ['A','X','Y','P','SP']],banks,z['PC'],z['SP'])
            # Actual native start state, independently varied complete OAM,
            # physical flags, valid palette-control values and effect lifetimes.
            # These are compiled initial-state components, not ordinary gameplay.
            initial=m.snapshot(raw,native[0]['entry']);rng=random.Random(490621)
            h=old.hook('SamusFreezeRenderFinish');banks={0x8000:62,0xa000:11,0xc000:13,0xe000:63}
            for flags in range(256):
                for pattern in range(12):
                    ram=bytearray(initial);ram[0x1d1]=255;ram[0x1d2]=223
                    for i in range(64):
                        k=A0['Sprite_Data']+i*4
                        if pattern==0:y,a=248,0
                        elif pattern==1:y,a=100,16
                        elif pattern==2:y,a=100,1
                        elif pattern==3:y,a=100,16 if i&1 else 1
                        elif pattern==4:y,a=248,255
                        else:y,a=rng.randrange(256),rng.randrange(256)
                        ram[k:k+4]=bytes([y,rng.randrange(256),a,rng.randrange(256)])
                    for n in ['SmFreezeRenderState','SmFreezeTurn','SmFreezeLastBlue']:
                        ram[at(A0[n])]=rng.randrange(2)
                    ram[at(A0['SmFreezePaletteControl'])]=flags%9
                    ram[at(A0['VRAM_Buffer_AddrCtrl'])]=flags
                    ram[at(A0['SelectedCharacter'])]=flags%18
                    ram[at(A0['CrossoverBehaviorVersion'])]=pattern&1
                    for i in range(6):
                        rem=[0,1,75,76,255,256,360][(pattern+i)%7]
                        ram[at(A0['AvFrozen']+i)]=rem&255;ram[at(A0['AvFrozenHi']+i)]=rem>>8
                    compare(ram,[flags^123,flags,255-flags,flags&0xcf,0xd0],banks,0xe000,0xd2)
            oldc=[x for x,y in costs];newc=[y for x,y in costs];d=[x-y for x,y in costs]
            result['groups'].append(dict(mapper=mp,actual_native_initial_states=len(native),
              synthetic_initial_state_components=3072,physical_flags_supplied=256,complete_OAM_entries_each=64,
              total=count,exact_all10240RAM_registers_stack_mapper_and_ordered_writes=True,
              palette_control_domain=list(range(9)),digest=digest.hexdigest(),
              cycles=dict(old_min=min(oldc),old_median=statistics.median(oldc),old_max=max(oldc),
                new_min=min(newc),new_median=statistics.median(newc),new_max=max(newc),
                saved_min=min(d),saved_median=statistics.median(d),saved_max=max(d)),
              scope='Leaf instruction cycles without injected ISR/DMA stalls; actual native initial states include interrupted captures but their enclosing native poststate is not claimed here. Fresh native full lifecycle/ISR checks remain separate.'))
        result.update(status='PASS_EXACT_SINGLE_LEAF_OUTPUTS_ALL_ORDERED_WRITES_AND_LOWER_CYCLES',
          build_review_sha256=sha(H/'build-review.json'),
          limitations=['Initial-state components do not prove acquisition, complete routes or all-arsenal fidelity.',
            'Active-only optimization; Easy/inactive paths remain byte-identical. No whole-game lag/visibility promise.'])
    except Exception as ex:
        result.update(status='FAIL_RETAINED_NO_ADMISSION',error=repr(ex),traceback=traceback.format_exc());raise
    finally:out.write_text(json.dumps(result,indent=2)+'\n')
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    print(result['status'],sha(out),[(x['mapper'],x['total'],x['cycles'])for x in result['groups']],flush=True)
if __name__=='__main__':main()
