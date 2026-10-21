from pathlib import Path
import datetime,hashlib,json,shutil,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=V/'root49-hud-mapper-caller-allocation-hy.json';assert not out.exists()
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 phase=V/'specialist-rygar-hud-h-a';used=workspace_bytes(phase);total=workspace_bytes(R);free=shutil.disk_usage(R).free
 assert used+200000000+75000000<750000000 and total+350000000<100000000000 and free>1000000000
 out.write_text(json.dumps(dict(status='ADDITIVE_RETAINED_HUD_MMC5_AND_CALLER_REVIEW_SCOPE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),authority='User explicitly requested retained lossless captures and raised cap; existing100GB global authority remains. Prior500MB admissions stay unchanged.',phase=str(phase.relative_to(R)),current_phase_bytes=used,current_workspace_bytes=total,disk_free_bytes=free,private_cap_bytes=750000000,reserve_bytes=75000000,global_cap_bytes=100000000000,owner='/root/mario_luigi_scrooge_s2',scope=['Freeze and retain efficient HUD source-p/R/T/W/Y/Z evidence and all negatives.','Validate exact actual source numeric producers, A/Y/scratch/P clobber lifetimes and foreign partial-overlap/ordering semantics; no blanket ignored RAM.','Run actual ordinary MMC5 overflowing-room scene with guarded complete queue/flush/publication/NMI/IRQ/PPU/native support capture, then independent exact fixed proof.','Measure complete producer+flush and whole GameLoop costs with actor-state/timing differences qualified.','Census/forecast before every launch including final reserve. No main install; coordinate shared bank layout HV.']),indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(allocation_sha256=sha(out),phase_bytes=used,workspace_bytes=total,disk_free=free)))
if __name__=='__main__':main()
