"""Same ownership controls using a genuine non-fastpath Koopa enemy caller."""
from pathlib import Path
import json,sys
import final_bill_lance_combined_hud_ownership_v1 as old
from final_bill_lance_combined_prepare_v3 import sha,put
from check_tmnt_render_oa import address

original_foreign=old.foreign


def foreign(q,b,kind):
    gateway,kwargs=original_foreign(q,b,kind)
    if kind=='enemy':
        # ce635's real Goomba construction pivot legitimately bypasses the
        # generic renderer. It cannot reproduce a generic-render admission.
        # A native Koopa's actual DrawMetasprite path still reaches that owner.
        q.set('Enemy_ID',0,0)
        kwargs['x']=address(b,'METASPRITE_KOOPA_WALKING_1')
    return gateway,kwargs


def main():
    old.foreign=foreign;old.main()
    output=Path(sys.argv[sys.argv.index('--output')+1]);manifest=json.loads((output/'manifest.json').read_text())
    files={Path(z['path'])for z in manifest['bindings']};files.add(Path(__file__))
    negative=output.parent/'ownership-controls-v1/failure.json';assert negative.exists();files.add(negative)
    put(output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(files)]))
    print(json.dumps(dict(successor=True,proof_sha256=sha(output/'proof.json'),manifest_sha256=sha(output/'manifest.json'),bindings=len(files),Goomba_fastpath_assumption_failure_retained=str(negative))))


if __name__=='__main__':main()
