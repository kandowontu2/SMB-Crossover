"""Read one stable native table/CPU witness; retain no ROM/debug copy."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
O=R/'build/kirby-inhale-shell-fix-1101-v1';P=R/'build/karnov-host-resource-base-1101-v1/candidate.nes'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    pin=sha(P);assert pin.startswith('99bf88c8'),pin;b=scoped_load(P);j=json.loads((O/'current-witness.json').read_text());blob=(O/'current-kirby-code.bin').read_bytes()
    for s in j['segments']:assert b['raw'][s['file_offset']:s['file_offset']+s['bytes']]==blob[s['witness_offset']:s['witness_offset']+s['bytes']]
    rows={}
    for n,size in[('BoundBoxCtrlData',84),('BoundingBoxCore',160),('GetEnemyBoundBox',192),('GetMaskedOffScrBits',128),('SprObjectCollisionCore',96),('PlayerEnemyCollision',640),('KbBodyDispatch',160)]:
        at=location(b,n);rows[n]=dict(CPU=address(b,n),physical_PRG=(at-16)//8192,bytes=b['raw'][at:at+size].hex())
    q=dict(passed=True,ROM_sha256=pin,DBG_sha256=sha(P.with_suffix('.dbg')),old_Kirby_segments_exact=True,rows=rows,globals={n:address(b,n)for n in['Enemy_BoundBoxCtrl','SprObj_BoundBoxCtrl','Enemy_BoundBox','Player_BoundBoxCtrl']if n in b['syms']},
      bindings={str(x.resolve()):sha(x)for x in[Path(__file__),O/'current-witness.json',O/'current-kirby-code.bin']})
    assert sha(P)==pin;(O/'native-box-witness.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['rows','bindings']}))
if __name__=='__main__':main()
