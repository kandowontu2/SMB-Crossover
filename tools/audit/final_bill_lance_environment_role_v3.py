"""Classify frozen human context and strict portable-worker inputs, source only."""
from pathlib import Path
import argparse,json
from final_bill_lance_combined_prepare_v3 import D,ROOT,sha,put


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    ready=json.loads((a.ready/'proof.json').read_text());env=ready['environment']
    before=ROOT/'tools/audit/final_bill_lance_combined_run_v1.py';host=ROOT/'tools/audit/final_bill_lance_combined_run_v2.py'
    isolate=ROOT/'tools/audit/run_mesen_isolated.py';driver=ROOT/'tools/run_mesen.py'
    old=before.read_text();text=host.read_text();command=lambda t:t[t.index('    cmd=['):t.index('    with(out/\'launch.json\')')]
    assert command(old)==command(text) and "'--emulator',env['emulator']"in command(text)
    assert "env['user_settings']"not in command(text) and 'settings.json'not in command(text)
    assert "for n in ['emulator','core','worker_settings']:assert sha(env[n])==env[n+'_sha256']"in text
    assert 'human_GUI_changes_are_informational_only=True'in text
    assert "emulator_options=args.option"in isolate.read_text()
    dt=driver.read_text();assert "executable = emulator or"in dt and "[executable, '--testRunner'"in dt
    assert Path(env['emulator']).parent/'settings.json'==Path(env['worker_settings'])
    for n in ['emulator','core','worker_settings']:assert sha(env[n])==env[n+'_sha256']
    snapshot=a.ready.parents[1]/'environment-addendum-v1/current-user-settings.json'
    assert sha(snapshot)==env['user_settings_sha256']=='f2658357e6f7e3e393644660d075b113b7c87f6cca970bd7563d119eb4781fc3'
    oldprobe=D/'mmc3-flag-fix-v23/script-budget-probe-v2/proof.json';probe=json.loads(oldprobe.read_text())
    assert probe['passed'] and probe['private_emulator']==env['emulator'] and probe['callback_host_budget_seconds']==5
    assert [q['exit']for q in probe['cases']]==[1,0]
    assets=[Path(env['emulator']).parent/n for n in ['Mesen.exe','MesenCore.dll','libSkiaSharp.dll','libHarfBuzzSharp.dll','MesenNesDB.txt','settings.json']]
    files=[Path(__file__),a.ready/'proof.json',before,host,isolate,driver,oldprobe,snapshot,
        ROOT/'tools/audit/final_bill_lance_environment_role_v1.py',ROOT/'tools/audit/final_bill_lance_environment_role_v2.py',a.ready.parents[1]/'environment-role-v1/failure.json',a.ready.parents[1]/'environment-role-v2/failure.json']+assets
    proof=dict(passed=True,read_only=True,native_run=False,CPU_controls_repeated=False,settings_written=False,
        user_GUI_settings_role='Non-runtime provenance: frozen f265 snapshot bound. Versioned host records live pre/post hashes or read errors informationally; they cannot reject a private-worker run.',
        runtime_settings_role='Actual settings.json beside explicitly selected portable Mesen.exe; all executable/core/DLL/database/settings files remain strict manifest inputs. Historical same-binary timeout1/5 experiment proves private setting consumption.',
        original_and_successor_worker_commands_literal=True,actual_worker=env['emulator'],worker_settings_sha256=env['worker_settings_sha256'],
        frozen_human_context=dict(path=str(snapshot),sha256=sha(snapshot),functional_worker_input=False),
        historical_private_settings_probe=dict(path=str(oldprobe),sha256=sha(oldprobe),scope=probe['scope']),
        strict_private_runtime_assets=[dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size)for f in assets],
        limitation='Launcher source/config role and actual historical private-setting experiment, not a complete operating-system file-read trace. No CPU/oracle/mechanics/sample change or new emulator run.')
    put(a.output/'proof.json',proof)
    put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in files]))
    print(json.dumps(dict(passed=True,proof_sha256=sha(a.output/'proof.json'),bindings=len(files),private_probe_sha256=sha(oldprobe))))


if __name__=='__main__':main()
