"""Prepare static-host-callback successor; no native launch or old verdict edit."""
from pathlib import Path
import argparse
import json
import shutil
from tmnt_native_storage_driver import ROOT,sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['storage','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
    old=a.storage/'parser-native-pilot-v1/candidate-easy';out=a.output
    assert sha(old/'run.lua')=='cbf56a031f7a852ef31de08d98aab332c08d38685eabf7bccf318221280f0b98'
    binding=json.loads((old/'binding.json').read_text())
    out.mkdir(parents=True)
    core=ROOT/'tools/audit/tmnt_static_exec_dispatcher_v1.lua';shutil.copyfile(core,out/core.name)
    performance=old/'performance-observer.lua';shutil.copyfile(performance,out/'performance-observer.lua')
    chr_source=ROOT/'tools/audit/chr_commit_observer.lua'
    assert binding['dependencies'][str(chr_source)]==sha(chr_source)
    shutil.copyfile(chr_source,out/'chr-commit-observer.lua')
    text=(old/'run.lua').read_text();original=text
    replacements={
        'C:/Users/kando/Documents/ChatGPT/SMB Crossover/tools/audit/chr_commit_observer.lua':(out/'chr-commit-observer.lua').as_posix(),
        json.loads((old/'config.json').read_text())['observer']:(out/'performance-observer.lua').as_posix()}
    for before,after in replacements.items():
        assert text.count(before)==1,(before,text.count(before))
        text=text.replace(before,after)
    # Output/TEST_DIR are supplied by the isolated runner, not rewritten into
    # the workload. The old run has no hard-coded old output directory.
    assert old.as_posix() not in text
    prefix='dofile('+json.dumps((out/core.name).as_posix())+')\n'
    suffix='\nTMNT_STATIC_EXEC.install()\n'
    (out/'run.lua').write_text(prefix+text+suffix)
    reverse=text
    for before,after in replacements.items():reverse=reverse.replace(after,before)
    assert reverse==original
    proof=dict(prepared=True,native_run=False,qualified_for_native=False,ROM_scope='Frozen parser9a791 only; later ROM must be rebound separately',
        original_run_sha256=sha(old/'run.lua'),new_run_sha256=sha(out/'run.lua'),dispatcher_sha256=sha(out/core.name),
        unchanged_imported_observers={name:sha(out/name) for name in ['performance-observer.lua','chr-commit-observer.lua']},
        workload_change_only_dispatcher_prefix_suffix_and_two_readonly_import_paths=True,
        catches_dynamic_CHR_and_DMA_and_profile_returns=True,actual_native_trace_equivalence_still_required=True,
        checker_sha256=sha(Path(__file__)),limits='This is a separate source-only successor. No Mesen process was launched and no historical result was changed. Lua syntax/mock startup tests are not native RGB/CSV/JSON equivalence. Future qualification must retain the same complete workload and original guards.')
    (out/'preparation.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof))


if __name__=='__main__':main()
