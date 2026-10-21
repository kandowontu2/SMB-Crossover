"""Execute the literal frozen E checker with cached immutable DBG lookups.

CPU emulator, seeds, case loops, bus and every assertion are untouched. Each
cached symbol record is checked against its original result again afterward.
"""
from pathlib import Path
import hashlib,importlib.util,json,sys,time
ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'build/verification/ryu49o2-head-components-e'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True
    assert '--cache-receipt'in sys.argv
    at=sys.argv.index('--cache-receipt');receipt=Path(sys.argv[at+1]);del sys.argv[at:at+2]
    assert not receipt.exists()
    frozen=json.loads((PACKET/'freeze.json').read_text())
    assert sha(PACKET/'freeze.json')=='af8cd27a8ca330d34e5d0d0ad01ca86b5849208077f3b7f2aef7ef0707760b86'
    for n,r in frozen['files'].items():assert sha(PACKET/n)==r['sha256']
    spec=importlib.util.spec_from_file_location('literal_frozen_E_checker',PACKET/'check.py')
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    original=checker.Image.sym;cache={};snapshots={};hits=0;misses=0
    def sym(im,name,scope=None):
        nonlocal hits,misses
        key=(im,name,scope)
        if key not in cache:
            value=original(im,name,scope);cache[key]=value;snapshots[key]=dict(value);misses+=1
        else:hits+=1
        assert cache[key]==snapshots[key],'No symbol record mutations permitted'
        return cache[key]
    checker.Image.sym=sym
    before=time.monotonic();error=None
    try:checker.main()
    except BaseException as ex:error=repr(ex);raise
    finally:
        rows=[]
        for (im,name,scope),value in cache.items():
            assert original(im,name,scope)==value==snapshots[(im,name,scope)]
            rows.append({'ROM':str(im.path),'name':name,'scope':scope,'original_record':value})
        for n,r in frozen['files'].items():assert sha(PACKET/n)==r['sha256']
        result={'status':'PASS_HOST_METADATA_CACHE_WITH_LITERAL_CHECKER'if error is None else'NEGATIVE_LITERAL_CHECKER_WITH_HOST_METADATA_CACHE',
                'wrapper_sha256':sha(Path(__file__)),'frozen_checker_sha256':sha(PACKET/'check.py'),
                'frozen_packet_sha256':sha(PACKET/'freeze.json'),'error':error,'cache_hits':hits,'cache_misses':misses,
                'seconds':time.monotonic()-before,'all_original_symbol_records_rechecked':rows,
                'CPU_model_seed_bus_loops_and_assertions_modified':False,
                'interrupted_A_receipt_sha256':sha(ROOT/'build/verification/root49o2-head-e-foot-host-interruption-a.json'),
                'checker_command_arguments':sys.argv[1:]}
        receipt.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'metadata_cache_status':result['status'],'receipt_sha256':sha(receipt),'hits':hits,'misses':misses}))

if __name__=='__main__':main()
