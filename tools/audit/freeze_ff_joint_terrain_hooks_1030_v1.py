"""Freeze verified genuine FF terrain hooks, without admitting/releasing FF."""
from pathlib import Path
import hashlib,json,zipfile

R=Path(__file__).resolve().parents[2]
P=R/'build/ff-joint-terrain-hooks-1030-v3'
O=R/'build/ff-joint-terrain-hooks-qualified-1030-v1'
Q=R/'docs/qa/checkpoints/2026-10-30/ff-terrain-hooks'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists() and not Q.exists()
    files={Path(__file__)}
    parents=[P/'source-closure.json',P/'terrain-controls-v1.json',P/'actual-FF-walls-v1.json']
    for p in parents:
        d=json.loads(p.read_text());assert d['passed'],p
        for f,h in d['bindings'].items():assert sha(f)==h,f
        files|={p}|set(map(Path,d['bindings']))
    negatives=[]
    for n in[1,2]:
        leaf=R/f'build/ff-joint-terrain-hooks-1030-v{n}'
        p=leaf/'source-negative.json';assert not json.loads(p.read_text())['passed']
        files.add(p);negatives.append(str(p.relative_to(R)))
        files.add(R/f'tools/audit/prepare_ff_joint_terrain_hooks_1030_v{n}.py')
    local={f for f in P.rglob('*')if f.is_file()and '__pycache__'not in f.parts}
    files|=local
    O.mkdir();Q.mkdir(parents=True)
    proof=dict(passed=True,native=False,admitted=False,
       status='FROZEN_SOURCE_REAL_FF_FEET_AND_WALL_HOOKS_CPU_PASS',
       candidate=str(P/'joint/candidate.nes'),candidate_sha256=sha(P/'joint/candidate.nes'),
       parent_sha256='07cda1d4b0812717334dc15e886f56474953e30b2cb2f6ddc5ecfd5ace52ea13',
       checks=dict(foreign_foot_state_pairs=1760,FF_foot_active_native_pairs=96,
           foreign_wall_state_pairs=204,actual_FF_side_to_wall_page_seams=16,
           real_ISR_cases=628,actual_ISR_snapshots=157,
           all33SMC_live_page1_APXY_rawmaps=True,RAM3_image_cookie_exact=True,
           foreign_foot_extra_CPU=[2,16],foreign_wall_extra_CPU=[0,121]),
       ABI=dict(FwSvcAfterTerrain='Exported ROM62 typed wrapper: active selected22/engine8 and valid cookie -> FwHostAfterTerrain; inactive -> genuine HuLegacyPostBG.',
           FwSvcFeet='Installed real63B resident foot selector -> own DK tail -> typed FF feet.',
           FwSvcWall='Installed original SamusStopAtWall guest farcall operands -> typed FF wall; foreign fallback is original LmWallGate.'),
       limits=['Private source successor, not installed in Downloads and not native tested.',
           'Shared post-BG ingress remains dispatcher-owner work; this packet supplies its actual worker ABI.',
           'FF flash/NewEnemy, palette/audio integration and native earned-powerup/1-1 checks remain open.',
           'Own DkFlagSideGate moved7B with genuine own near JMP reassembled; all other old public PCs exact except own FwSvcEnd.'],
       negatives=negatives,parents=[str(p)for p in parents],
       bindings={str(p.resolve()):sha(p)for p in sorted(files)})
    hp=O/'handoff.json';hp.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    for p in parents+[P/'source-hooks.patch',hp]:
        (Q/p.name).write_bytes(p.read_bytes())
    for n in[1,2]:
        p=R/f'build/ff-joint-terrain-hooks-1030-v{n}/source-negative.json'
        (Q/f'producer-negative-v{n}.json').write_bytes(p.read_bytes())
    archive=Q/'source-packet.zip'
    own_tools=[R/'tools/audit'/n for n in[
        'prepare_ff_joint_terrain_hooks_1030_v1.py','prepare_ff_joint_terrain_hooks_1030_v2.py',
        'prepare_ff_joint_terrain_hooks_1030_v3.py','ff_joint_terrain_hooks_controls_1030_v1.py',
        'ff_joint_terrain_wall_controls_1030_v1.py','freeze_ff_joint_terrain_hooks_1030_v1.py']]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
        for p in sorted(local|set(own_tools)):
            if p.name=='candidate.nes':continue
            z.write(p,p.relative_to(R).as_posix())
    receipt=dict(passed=True,native=False,installed=False,handoff_sha256=sha(hp),
         ROM_sha256=sha(P/'joint/candidate.nes'),archive_sha256=sha(archive),
         archive_bytes=archive.stat().st_size,archive_members=len(zipfile.ZipFile(archive).namelist()),
         original_ROMs_included=False,checks=proof['checks'],limits=proof['limits'])
    (Q/'checkpoint.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(path=str(hp),handoff_sha256=sha(hp),ROM=proof['candidate_sha256'],
         archive_bytes=receipt['archive_bytes'],members=receipt['archive_members'])),flush=True)


if __name__=='__main__':main()
