"""Record published laser hotfix without claiming the larger goal complete."""
from pathlib import Path
import datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=V/'root-current49-progress-w.json';assert not out.exists()
    cp=R/'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json';data=json.loads(cp.read_text())
    assert sha(cp)=='4e9e854ddcd78e5c4aa7231fcea81c95fe86d969eb3bab6129bef872a9ddd0d9'
    assert data['status']=='PASS_WORKING_BILL_LASER_RENDER_U_BOTH_MAPPERS'
    assert all(sha(R/n)==v for n,v in data['source_hashes'].items())
    for row in data['builds']:
        for ext in ['nes','lbl','map','dbg']:assert sha(R/row['artifacts'][ext]['path'])==row['artifacts'][ext]['sha256']
    refs=[V/'root-current49-progress-v.json',cp,
      V/'agent49easy-samus-stop-b/freeze.json',V/'agent49hard-samus-effects-c/freeze.json',
      R/'docs/qa/bill-laser-render-v49.md',R/'docs/qa/easy-hard-legacy-v49.md']
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(R);assert used<50_000_000_000
    report=dict(status='ACTIVE_PROGRESS_LASER_U_PUBLISHED_EASY_EXPANSION_PRIVATE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),
      working_checkpoint=cp.parent.name,source412_exact=True,latest_user_bug_fixed='Contra laser andFlare no longer double-render asmachinebullet; testedbothmappers.',
      references=[dict(path=str(p.relative_to(R)),sha256=sha(p),bytes=p.stat().st_size)for p in refs],
      completed_native_laser_cases='60/controllercases permapper, Bill/Lance fiveweapons threeposes bothfacings; old24wrongrender/map, fixed0 with actualmappedsourceartemission.',
      completed_regressions='16originalnativegroups, including4800LaserFlarecollision-equivalence outcomes.',
      Easy_expansion='Stillprivate: sharedinventory/injury/pickups/watereligibility validated; MM andSamus/Billtiers frozen; EasySamusSTOP108cases andHardSamusaggregate132cases frozen. LSRpriority/wholeclip finalfreeze andMario exactsourceCPU/native stillinprogress.',
      known_negative='Firstunion actualbankoverflow13GUEST/16SPECIAL_ROSTER; nextLSRcoldclosures addressbudget, freshunion notyetbuilt.',
      active_specialists=['Mario old/new dry+water/lifecycle/spring implementation andnative checks.',
       'Link/Simon finalpriority/boomerang/sourceeffect+numericretention freeze.',
       'Bill sourceaim/speed/offset/rapid projection corrections; drawing staysroot-owned.'],
      live_root_handles=[],workspace_bytes=used,cap_bytes=50_000_000_000,retain_lossless_captures=True,
      accepted_release=False,goal_complete=False,
      remaining='Broader all-character end2-2 controller routes, allattacks/upgrades/sourcefidelity, lagoptimization and finalsamecheckpoint recordings remainactive. S2recordings are not UorEasyupdate routeproofs.')
    out.write_text(json.dumps(report,indent=2)+'\n');print(out.name,sha(out),used,flush=True)
if __name__=='__main__':main()
