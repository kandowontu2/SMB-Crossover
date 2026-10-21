"""Rebuild a private contact revision with complete source/layout receipts."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-easy-contact-private-d';S=H/'source';P=R/'build/verification/root49-easy-injury-private-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--fix-long-native-branches',action='store_true');a=p.parse_args()
    sys.dont_write_bytecode=True;out=H/('build-review-'+a.revision+'.json');assert not out.exists()
    if a.fix_long_native_branches:
        f=S/'src/guest_body_contact.s';text=f.read_text();assert text.count('  beq NativeBody')==2
        (H/'negative-e-guest_body_contact.s').write_bytes(f.read_bytes());f.write_text(text.replace('  beq NativeBody','  jeq NativeBody'))
    oldcat=json.loads((P/'build-review-c.json').read_text())['all_candidate_source_hashes']
    cat={n:sha(S/n)for n in oldcat}|{'src/guest_source_stomp.s':sha(S/'src/guest_source_stomp.s')}
    report=dict(status='BUILDING_SOURCE_STOMP',revision=a.revision,script_sha256=sha(__file__),input_source_hashes=cat,builds=[],main_changed=False,complete_Easy_behavior=False)
    def save():out.write_text(json.dumps(report,indent=2)+'\n')
    save();spec=importlib.util.spec_from_file_location('stomp_image_rebuild',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for mapper in ['mmc3','mmc5']:
        log=H/(mapper+'-build-'+a.revision+'.log')
        with log.open('wb')as f:rc=subprocess.run([sys.executable,str(H/'build-driver.py'),'--mapper',mapper],cwd=R,stdout=f,stderr=subprocess.STDOUT).returncode
        row=dict(mapper=mapper,exit=rc,log_sha256=sha(log));report['builds'].append(row);save();assert rc==0
        im=mod.Image(S/('build/smb-crossover-'+mapper+'.nes'));before=mod.Image(P/('source/build/smb-crossover-'+mapper+'.nes'))
        assert all(im.ram[n]==v for n,v in before.ram.items());assert im.ram['GuestBodyStompAllowed']==0x7fe3
        assert im.raw[16+64*8192:]==before.raw[16+64*8192:];assert im.sym('GuestBodyContactBridge')['size']==35
        for sym in before.data['sym']:
            if sym.get('scope')==1 and 'seg'in sym and 'val'in sym and before.segs[sym['seg']]['name']in ['FIXED','OAMALIGNED','BASS_DPCM','COLLISION']:
                assert im.sym(sym['name'])['val']==sym['val'],sym['name']
        d=next(v for v in im.segs.values()if v['name']=='BASS_DPCM');assert im.raw[d['ooffs']:d['ooffs']+d['size']]==before.raw[d['ooffs']:d['ooffs']+d['size']]
        row.update(ROM_sha256=sha(im.path),old_RAM_exact=True,resident_global_PCs_exact=True,CHR_exact=True,DPCM_exact=True,segments={n:next(v for v in im.segs.values()if v['name']==n)for n in ['SAMUS','OAMALIGNED','COLLISION','SRAM']});save()
    base=json.loads((R/'build/verification/root49-easy-hard-user-baseline-a/baseline.json').read_text());assert all(sha(R/n)==h for n,h in base['current_source_hashes'].items())
    assert all(sha(S/n)==h for n,h in cat.items())
    report['status']='PASS_PRIVATE_SOURCE_STOMP_BUILD_ONLY';report['all_source_hashes']=cat;save();print(report['status'],sha(out),flush=True)
if __name__=='__main__':main()
