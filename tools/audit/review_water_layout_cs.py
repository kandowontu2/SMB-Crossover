"""Bind current Water bytes, unaffected banks, RAM and original callers."""
from pathlib import Path
import hashlib,importlib.util,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'water-current-layout-cs'
P=V/'agent49-water-visible-j-a'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not O.exists();O.mkdir()
    path=V/'agent49g-samus-crouch-fix-proposal-b/image.py'
    spec=importlib.util.spec_from_file_location('water_cs_image',path);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    cp=json.loads((R/'build/checkpoints/firebar-budget-ci/manifest.json').read_text())
    changed={n for n,value in cp['source_hashes'].items()if sha(R/n)!=value}
    assert changed=={'src/special_weapons.s','src/entrypoint.s'},changed
    groups=[]
    for mapper in('mmc3','mmc5'):
        old=a.Image(R/'build/checkpoints/firebar-budget-ci/build'/f'smb-crossover-{mapper}.nes')
        new=a.Image(R/'build'/f'smb-crossover-{mapper}.nes');private=a.Image(P/'source-h/build'/f'smb-crossover-{mapper}.nes')
        assert old.ram==new.ram and old.raw[:16]==new.raw[:16]and old.raw[16+64*8192:]==new.raw[16+64*8192:]
        h=new.hook('WaterShieldEnemies');ph=private.hook('WaterShieldEnemies');assert h['address']==0xb600 and h['physical_bank']==36
        assert new.sym('WaterShieldEnemies')['size']==private.sym('WaterShieldEnemies')['size']==208
        assert new.raw[h['rom_offset']:h['rom_offset']+208]==private.raw[ph['rom_offset']:ph['rom_offset']+208]
        assert set(old.raw[h['rom_offset']:h['rom_offset']+208])=={255}
        os={s['name']:s for s in old.segs.values()};ns={s['name']:s for s in new.segs.values()}
        assert set(ns)-set(os)=={'WATER_ENEMY_COLD'}
        for name,s in os.items():
            t=ns[name];assert(s['start'],s.get('ooffs'))==(t['start'],t.get('ooffs'))
            assert t['size']-s['size']==(10 if name=='SPECIAL_MM'else 0),(mapper,name)
        special=ns['SPECIAL_MM'];allowed=set(range(special['ooffs'],special['ooffs']+special['size']))|set(range(h['rom_offset'],h['rom_offset']+208))
        external=[i for i,(x,y)in enumerate(zip(old.raw,new.raw))if x!=y and i not in allowed];covered=set();bindings=[]
        for off in external:
            if off in covered:continue
            hits=[]
            for start in(off-4,off-9):
                x,y=old.raw[start:start+18],new.raw[start:start+18]
                if len(x)!=18 or not(x[0]==y[0]==0x8d and x[3]==y[3]==x[8]==y[8]==x[13]==y[13]==0xa9 and x[15]==y[15]==0x20):continue
                if any(u!=v for j,(u,v)in enumerate(zip(x,y))if j not in(4,9)):continue
                bank=x[14]&127;shared=old.pointer(bank,x[4]+256*x[9])&new.pointer(bank,y[4]+256*y[9])
                if shared:hits.append((start,x,y,shared,bank))
            assert len(hits)==1,(mapper,off,hits)
            start,x,y,shared,bank=hits[0];assert bank==60
            bindings.append(dict(offset=start,targets=sorted(shared),bank=bank,old_bytes=x.hex(),new_bytes=y.hex()));covered|={start+4,start+9}
        assert set(external)<=covered
        baseline=R/'build'/f'smb-crossover-{mapper}-baseline.nes'
        assert sha(baseline)=={'mmc3':'0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146','mmc5':'34858561f4825dcc96cdd5fd46872f9230890c93af95351720c8536155f5cbbd'}[mapper]
        groups.append(dict(mapper=mapper,ROM=new.metadata(),RAM_unchanged=True,header_CHR_baseline_unchanged=True,
            exact_reviewed_helper_208_bytes=True,helper=h,SpecialMM_growth=10,symbolic_external_farcall_bindings=bindings,external_changed_bytes=len(external)))
    (O/'layout.json').write_text(json.dumps(dict(passed=True,groups=groups,changed_source=sorted(changed),new_RAM_bytes=0,goal_complete=False),indent=2)+'\n',encoding='utf-8')
    # Re-run the original private Bridge/both-consumer oracle against CI/CJ.
    path=P/'bridge_w.py';text=path.read_text()
    replacements={"out=H/'bridge-w.json'":"out=O/'bridge-w.json'",
        "V/'root49-water-enemy-filter-gy/source/build'":"R/'build/checkpoints/firebar-budget-ci/build'",
        "H/'source-h/build'":"R/'build'","p=H/'live-k'/f'{mapper}-1'/'native'":"p=V/'water-visible-profile-cm'/f'CJ-{mapper}-1'/'native'"}
    for x,y in replacements.items():assert text.count(x)==1,x;text=text.replace(x,y)
    (O/'bridge-review.py.txt').write_text(text,encoding='utf-8')
    exec(compile(text,str(path),'exec'),dict(__file__=str(path),__name__='water_cs_bridge',O=O))
    print('PASS_CURRENT_WATER_LAYOUT_AND_BRIDGE',len(groups),flush=True)

if __name__=='__main__':main()
