from pathlib import Path
import datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=V/'root49-hud-inclusive-supplement-hz.json';assert not out.exists();parent=V/'root49-hud-mapper-caller-allocation-hy.json'
 assert sha(parent)=='9dedfc4592d5a051908ce36daad829b13118a8a6b0a7006bf6cb2db4420c6e7a'
 H=V/'specialist-rygar-hud-h-a';roots=[H]+sorted((R/'build/roster-through-2-2').glob('specialist-h-rygar-hud-*'))
 used={str(p.relative_to(R)):sum(z.stat().st_size for z in p.rglob('*')if z.is_file())for p in roots}
 total=sum(used.values());assert total+200000000+75000000<750000000
 out.write_text(json.dumps(dict(status='AUTHORITATIVE_HY_INCLUSIVE_FOOTPRINT_SUPPLEMENT',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),HY_sha256=sha(parent),scope_correction='HY current_phase_bytes159995323 counted only verification folder. This supplement includes every related specialist-h-rygar-hud-* route packet, matching existing owner census.750MB cap applies to their combined sum; it is not an additional independent750MB grant.',owned_roots_and_bytes=used,inclusive_bytes=total,inclusive_cap_bytes=750000000,reserve_bytes=75000000,global_cap_bytes=100000000000,scope=json.loads(parent.read_text())['scope']),indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(supplement_sha256=sha(out),inclusive_bytes=total)))
if __name__=='__main__':main()
