"""Merge reviewed MMC5 hardware and Proto packets without installing Bass WIP."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

R = Path(__file__).resolve().parents[2]
G = R / 'build/player-guide-agent/mmc5-native-kb-private'
P = R / 'build/verification/protoman-candidate-agent'
O = R / 'build/verification/proto-adoption-ks'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    gm = json.loads((G/'incremental-merge-manifest.json').read_text())
    pm = json.loads((P/'manifest.json').read_text())
    # Check all dependencies before the first workspace mutation.
    for item in gm['merge_files']:
        stage, main = G/'merge-staging'/item['path'], R/item['path']
        assert sha(stage) == item['sha256'], stage
        assert (sha(main) if main.exists() else None) == item['baseline_sha256'], main
    stock = json.loads((P/'stock-hook-sources.json').read_text())
    for name, text in stock.items():
        assert (R/name).read_text() == text, name
    for name, digest in pm['new_source_hashes'].items():
        assert not (R/name).exists(), name
        assert sha(P/'source'/name) == digest, name
    subprocess.run(['git','apply','--check',str(G/'incremental-merge.patch')],cwd=R,check=True)
    subprocess.run(['git','apply','--check','--exclude=src/entrypoint.s',str(P/'implementation.patch')],cwd=R,check=True)
    O.mkdir()
    before = {}
    names = sorted(set([i['path'] for i in gm['merge_files']] + list(stock) + list(pm['new_source_hashes'])))
    for name in names:
        main = R/name
        before[name] = sha(main) if main.exists() else None
        if main.exists():
            dest=O/'before'/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(main,dest)
    subprocess.run(['git','apply',str(G/'incremental-merge.patch')],cwd=R,check=True)
    subprocess.run(['git','apply','--exclude=src/entrypoint.s',str(P/'implementation.patch')],cwd=R,check=True)
    # Entry's header/core hooks came from the production packet. Add only the
    # Proto fixed aliases and include, keeping the single production mapper.
    ep=R/'src/entrypoint.s'
    text=ep.read_text()
    old='.include "memory.s"'
    assert text.count(old)==1
    text=text.replace(old, '''.if ::ENABLE_MMC5_EXPANDED
ProtoVariant=$73dd
ProtoAudioState=$73de
.export ProtoVariant,ProtoAudioState
.endif
'''+old)
    marker='.include "mmc5_expanded.s"'
    assert text.count(marker)==1
    text=text.replace(marker,marker+'\n.include "protoman.s"')
    ep.write_text(text)
    cfg=R/'smb1base-mmc5-expanded.cfg'
    text=cfg.read_text()
    assert text.count('SEGMENTS {')==1
    text=text.replace('SEGMENTS {','''SEGMENTS {
    PROTO_MM3_AUDIO: load=X5_NEW_40,type=ro,align=$100;
    PROTO_GFX: load=X5_NEW_41,type=ro;
    PROTO_COLD: load=X5_NEW_42,type=ro;
    PROTO_MENU: load=X5_NEW_42,type=ro;
''',1)
    cfg.write_text(text)
    for name in pm['new_source_hashes']:
        target=R/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(P/'source'/name,target)
    report=dict(status='SOURCE_MERGED_PENDING_BUILD_AND_NATIVE_VERIFICATION',
        checkpoint='rygar-walk-kb', hardware_packet_sha256=sha(G/'incremental-merge-manifest.json'),
        proto_packet_sha256=sha(P/'manifest.json'), before=before,
        after={name:sha(R/name) for name in names},
        Bass_corner_installed=False, level_helpers_installed=False, goal_complete=False)
    (O/'adoption.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'])


if __name__=='__main__':
    main()
