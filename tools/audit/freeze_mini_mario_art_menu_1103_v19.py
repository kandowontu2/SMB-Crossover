"""Freeze the compact original art/menu source proposal; no ROM or admission."""
import json,zipfile
from pathlib import Path
import measure_mini_mario_menu_1103_v14 as P
R,O=P.R,P.O


def main():
    art=R/'build/mini-mario-art-1103-v12'
    for f in[art/'receipt.json',art/'engine-art-v13.json',O/'menu-CPU-v17.json',O/'source-audit-v18.json']:assert json.loads(f.read_text())['passed']
    names=['prepare_mini_mario_art_1103_v12.py','prepare_mini_mario_engine_art_1103_v13.py',
        'measure_mini_mario_menu_1103_v14.py','check_mini_mario_menu_1103_v15.py',
        'measure_mini_mario_cycle_1103_v16.py','check_mini_mario_menu_1103_v17.py',
        'audit_mini_mario_menu_1103_v18.py','freeze_mini_mario_art_menu_1103_v19.py']
    sources=[R/'tools/audit'/n for n in names]
    art_names=['compiler-inputs.zip','body.chr','poses.bin','animations.bin','menu-portrait.chr','layout.json',
        'source-and-NES.png','facing-preview.png','receipt.json','engine-animation-index.bin','engine-animation-frames.bin','engine-art-v13.json']
    menu_names=['proposal.json','proposal-v16.json','menu-CPU-v15-negative.json','menu-CPU-v17.json','source-audit-v18.json','code.bin','data.bin']
    files=sources+[art/n for n in art_names]+[O/n for n in menu_names]
    files += [O/(stem+suffix)for stem in['nav','alt','menu']for suffix in['.s','.cfg','.bin','.lbl']]
    assert len(files)==len(set(files))and all(p.is_file()for p in files)
    archive=O/'mini-art-menu-source-v19.zip';assert not archive.exists()
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for p in files:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
    result=dict(frozen=True,source_and_CPU_passed=True,ROM_written=False,native_qualified=False,menu_admitted=False,
        parent_ROM_SHA256=P.PIN,memory_proposal_SHA256=json.loads((O/'proposal-v16.json').read_text())['expected_memory_only_SHA256'],
        art=dict(body_CHR_bytes=1024,original_pairs=32,one_sprite_per_body=True,pose_bytes=386,
            compiled_animation_index_bytes=352,compiled_animation_sequence_bytes=217,original_GB_nonblank_tiles_bound=43),
        menu=dict(MarioVariant=8,raw=41,slots=32,foreign_unique_profiles_exact=93,foreign_machine_states_exact=94,
            source_spans='214Bnav+17BAltCold+62Bqueuegate+146Bcodec-tail+46Bentrypadding;2operand/databytes in existing32BKmcycle capsule.',
            placeholder_art_page=0,allocation_claim=False,physical_PRG=66,page_low_operand_CPU=0xa5b5,page_high_operand_CPU=0xb0b3),
        source_commit_files=[p.relative_to(R).as_posix()for p in sources],archive=archive.relative_to(R).as_posix(),archive_SHA256=P.sha(archive),archive_bytes=archive.stat().st_size,
        members={p.relative_to(R).as_posix():P.sha(p)for p in files},
        remaining='Native origin/default/bounds proof is separately owned by world helper; v12relativeparts do not assert runtimeanchor. Rootmustbindactualartpage/resources/currentbackend, qualifyphysicalmenu/coldlaunch/1-1/Downloads anddeliver. Thisfreeze doesnotclaimunlock/playability/pausecompletion.')
    (O/'mini-art-menu-source-v19.json').write_text(json.dumps(result,indent=2)+'\n')
    (O/'commit-files-v19.txt').write_text('\n'.join(result['source_commit_files'])+'\n')
    print(json.dumps(dict(frozen=True,archive=str(archive),SHA256=P.sha(archive),bytes=archive.stat().st_size,members=len(files))))


if __name__=='__main__':main()
