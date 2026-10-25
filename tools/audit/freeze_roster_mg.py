"""Freeze Kirby plus existing alternates, including selector/palette safeguards."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
O=R/'build/checkpoints/kirby-roster-mg'
V=R/'build/verification/kirby-adoption-me'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    parent=R/'build/checkpoints/darkwing-zelda2-md'
    old=json.loads((parent/'manifest.json').read_text())
    paths={m:V/f'standard-{m}'/f'smb-crossover-{m}.nes' for m in ('mmc3','mmc5')}
    paths['mmc5-expanded']=V/'smb-crossover-mmc5-kirby-final.nes'
    assert all(sha(paths[m])==old['ROMs'][m] for m in ('mmc3','mmc5'))
    raw=paths['mmc5-expanded'].read_bytes();chr_offset=16+1048576
    expected=(R/'chr/characters/packed-mmc5-expanded.chr').read_bytes()
    assert len(expected)<=0x40000 and raw[chr_offset:chr_offset+len(expected)]==expected
    assert not any(raw[chr_offset+len(expected):chr_offset+0x40000])
    physical={}
    for who,(address,path) in {
        'Proto':(256,'protoman.chr'),'Darkwing':(276,'darkwing.chr'),
        'ZeldaII body':(308,'zelda2-link-body.chr'),'ZeldaII items':(335,'zelda2-link-items.chr'),
        'Kirby':(340,'kirby.chr')}.items():
        p=R/'chr/characters'/path;data=p.read_bytes();start=chr_offset+address*1024
        assert raw[start:start+len(data)]==data,who
        physical[who]=dict(first_physical_1k_page=address,bytes=len(data),sha256=sha(p))
    assert json.loads((V/'admission-proof.json').read_text())['passed']
    native=[]
    for folder in ('root-food','root-health','root-families','final-z2','final-darkwing','final-darkwing-controls','final-proto'):
        logs=list((V/folder).glob('*.log'));assert len(logs)==1
        text=logs[0].read_text();assert 'PASS' in text and 'FAIL' not in text
        native.append(logs[0])
    names=set(old['source_files'])
    adoption=json.loads((V/'adoption.json').read_text())
    names.update(adoption['before'])
    names.update('src/'+n for n in adoption['new_sources'])
    names.update(('src/x5_palette.s','src/x5_profiles.s','src/mmc5_expanded.s',
                  'chr/characters/kirby.chr','chr/characters/packed-mmc5-expanded.chr',
                  'chr/raw/x5-character-select.bin','tools/audit/adopt_kirby_me.py',
                  'tools/audit/check_x5_admission_mf.py','tools/audit/freeze_roster_mg.py',
                  'tools/reference/build_x5_menu.py'))
    O.mkdir(parents=True)
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(names):z.write(R/name,name)
    for m,path in paths.items():
        for ext in ('.nes','.lbl','.dbg','.map'):
            dest=O/'build'/('smb-crossover-'+m+ext);dest.parent.mkdir(exist_ok=True)
            shutil.copyfile(path.with_suffix(ext),dest)
            if m=='mmc5-expanded':shutil.copyfile(dest,R/'build'/dest.name)
    report=dict(status='ADOPTED_KIRBY_PLUS_DARKWING_ZELDAII_PROTO',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_checkpoint='darkwing-zelda2-md',
        ROMs={m:sha(p) for m,p in paths.items()},source_files={n:sha(R/n) for n in sorted(names)},
        physical_chr_slice_proofs=physical,native_logs={str(p.relative_to(R)):sha(p) for p in native},
        admission_proof_sha256=sha(V/'admission-proof.json'),
        implemented_identities=18,target_identities=32,
        selector='6/6/7 navigation geometry; only current12 portraits and real Kirby linked,18identities via alternatives.',
        scope='Native Kirby body/inflate/inhale/spit/14SMBcopies/sixHP and healing; combined alternate regression checks.',
        limitations=['Kirby/Pit,Darkwing/Scrooge,ZeldaII/ZeldaI inherited audio; native new-profile soundtracks pending.',
                     'ZeldaII fairy/item palette and original death-scene polish; campaign coverage unclaimed.'],
        remaining_profiles=['Chip/Dale','Grant/Sypha/Alucard','TMNT four turtles','Vic Viper','SMB3 Mario/Luigi','Little Mac','Mike Jones'],
        videos_deferred=True,goal_complete=False)
    report['artifacts']={str(p.relative_to(O)):sha(p) for p in O.rglob('*') if p.is_file()}
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(O),ROMs=report['ROMs'],identities=18,source_count=len(names))))


if __name__=='__main__':main()
