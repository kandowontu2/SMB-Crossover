"""Compiled placement/identity review only; ABI and gameplay remain separate."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49o2-head-private-build-b2'
PARENT=ROOT/'build/checkpoints/roster-audit-v49-provisional-o2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode=True
    helper=ROOT/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py'
    spec=importlib.util.spec_from_file_location('head_image',helper)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    report=json.loads((OUT/'report.json').read_text())
    contract=json.loads((ROOT/'build/verification/ryu49o2-head-implementation-b/contract.json').read_text())
    parent_catalog=json.loads((PARENT/'manifest.json').read_text())['source_hashes']
    assert all(sha(ROOT/n)==h for n,h in parent_catalog.items()), 'Shared source must remain O2'
    cases=[]
    for mapper in ('mmc3','mmc5'):
        old=module.Image(PARENT/f'smb-crossover-{mapper}.nes')
        new=module.Image(OUT/f'source/build/smb-crossover-{mapper}.nes')
        for ext,key in (('.nes','rom_sha256'),('.dbg','dbg_sha256'),('.lbl','lbl_sha256')):
            assert sha(old.path.with_suffix(ext))==contract['parent'][mapper][key]
            assert sha(ROOT/'build'/old.path.with_suffix(ext).name)==sha(old.path.with_suffix(ext))
        assert old.ram==new.ram, 'Every logical global RAM symbol and address must match'
        old_foot=old.sym('GuestFootContactSide');new_foot=new.sym('RosterGuestFootContactSide')
        def body(image,s):
            seg=image.segs[s['seg']];off=seg['ooffs']+s['val']-seg['start']
            return image.raw[off:off+s['size']]
        assert old_foot['size']==new_foot['size']==38
        assert body(old,old_foot)==body(new,new_foot)
        assert hashlib.sha256(body(new,new_foot)).hexdigest()==contract['parent'][mapper]['old_foot']['sha256']
        assert new.sym('GuestFootContactSide')['size']==19
        assert new.sym('CrossoverHeadProbe')['size']==60 and old.sym('CrossoverHeadProbe')['size']==33
        assert new.sym('RyuSourceHeadGate')['size']==658
        old_segments={s['name']:s for s in old.segs.values()}
        new_segments={s['name']:s for s in new.segs.values()}
        growth={name:new_segments[name]['size']-s['size'] for name,s in old_segments.items()
                if new_segments[name]['size']!=s['size']}
        assert growth=={'FIXED':8,'ROSTER':696},growth
        free=8192-new_segments['ROSTER']['size'];assert free==108
        last=new_segments['SAMUS_CROUCH_WATER'];next_seg=new_segments['BASS_DPCM']
        fixed_slack=next_seg['start']-last['start']-last['size']
        assert fixed_slack==({'mmc3':5,'mmc5':6}[mapper])
        changed=[i for i,(a,b) in enumerate(zip(old.raw,new.raw)) if a!=b]
        chr_start=16+old.raw[4]*16384
        assert old.raw[chr_start:]==new.raw[chr_start:]
        assert old.raw[:16]==new.raw[:16]
        banks={}
        for offset in changed:
            b=(offset-16)//8192;banks[b]=banks.get(b,0)+1
        cases.append({'mapper':mapper,'old':old.metadata(),'candidate':new.metadata(),
                      'old_foot':old.hook('GuestFootContactSide'),
                      'relocated_foot':new.hook('RosterGuestFootContactSide'),
                      'exact_38_byte_body_sha256':hashlib.sha256(body(new,new_foot)).hexdigest(),
                      'head':new.hook('RyuSourceHeadGate'),'head_bytes':658,'wrapper_bytes':19,
                      'segment_growth':growth,'ROSTER_free':free,'pre_DPCM_slack':fixed_slack,
                      'all_global_RAM_symbols_exact':len(new.ram),
                      'changed_PRG_bytes':len(changed),'changed_PRG_banks_counts':banks,
                      'CHR_literal_parent':True,'header_literal_parent':True})
    result={'status':'PASS_COMPILED_PLACEMENT_EXACT_RELOCATED_BODY_AND_RAM_SYMBOLS_ONLY',
            'accepted_release':False,'goal_complete':False,'script_sha256':sha(Path(__file__)),
            'build_report_sha256':sha(OUT/'report.json'),'image_helper_sha256':sha(helper),
            'shared_O2_source_and_ROMs_unchanged':True,'cases':cases,
            'open_gates':['All actual linked operand relocations and page timing remain unclassified',
                          'Foot full-register/RAM/ordered-stack/SMC/mapper ABI execution',
                          'Head seeded native/CPU component controls and actual writer receipts',
                          'Current ordinary full route, full regression suite and final recordings',
                          'Full source head/cache/pose/multicell fidelity gaps listed in frozen overlay']}
    path=OUT/'compiled-review-a.json';assert not path.exists()
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'report_sha256':sha(path),
                      'build_report_sha256':sha(OUT/'report.json'),'cases':[{k:c[k] for k in ('mapper','head_bytes','ROSTER_free','pre_DPCM_slack','changed_PRG_bytes')}for c in cases]},indent=2))


if __name__=='__main__':main()
