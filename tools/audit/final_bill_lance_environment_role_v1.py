"""Read-only classify watched human settings versus the explicit portable worker."""
from pathlib import Path
import argparse,json
from final_bill_lance_combined_prepare_v3 import D,ROOT,sha,put


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    ready=json.loads((a.ready/'proof.json').read_text());env=ready['environment']
    host=ROOT/'tools/audit/final_bill_lance_combined_run_v1.py';isolate=ROOT/'tools/audit/run_mesen_isolated.py';driver=ROOT/'tools/run_mesen.py'
    text=host.read_text();command=text[text.index('    cmd=['):text.index('    with(out/\'launch.json\')')]
    assert "'--emulator',env['emulator']"in command and "env['user_settings']"not in command and 'settings.json'not in command
    assert "for n in ['emulator','core','worker_settings','user_settings']:assert sha(env[n])==env[n+'_sha256']"in text
    assert "emulator_options=args.option"in isolate.read_text()
    dt=driver.read_text();assert "executable = emulator or"in dt and "[executable, '--testRunner'"in dt
    assert Path(env['emulator']).parent/'settings.json'==Path(env['worker_settings'])
    for n in ['emulator','core','worker_settings','user_settings']:assert sha(env[n])==env[n+'_sha256']
    oldprobe=D/'mmc3-flag-fix-v23/script-budget-probe-v2/proof.json';probe=json.loads(oldprobe.read_text())
    assert probe['passed'] and probe['private_emulator']==env['emulator'] and probe['callback_host_budget_seconds']==5
    assert [q['exit']for q in probe['cases']]==[1,0]
    files=[Path(__file__),a.ready/'proof.json',host,isolate,driver,oldprobe,Path(env['emulator']),Path(env['core']),Path(env['worker_settings']),Path(env['user_settings'])]
    proof=dict(passed=True,read_only=True,native_run=False,CPU_controls_repeated=False,settings_written=False,
        user_GUI_settings_role='Monitored context/integrity file only in this launcher: explicit SHA pre/postcheck; its path is not passed to the worker command. C:/Mesen2 fallback is bypassed by the explicit private executable.',
        runtime_settings_role='settings.json beside the explicit isolated portable Mesen.exe. Historical same-binary 1/5-second host-callback experiment verifies private local setting consumption; no new emulator launch here.',
        actual_worker=env['emulator'],worker_settings_sha256=env['worker_settings_sha256'],current_human_context_sha256=env['user_settings_sha256'],
        historical_private_settings_probe=dict(path=str(oldprobe),sha256=sha(oldprobe),scope=probe['scope']),
        command_configuration_scope='Same exact private exe/core/worker settings and literal deterministic CLI options. Only watched human-file context hash changed; originally-bound Nes/Emulation dictionaries unchanged.',
        limitation='Source command/config role plus historical private-setting experiment, not a complete operating-system file-read trace. No claim that every incidental host-file access was observed.')
    put(a.output/'proof.json',proof)
    put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in files]))
    print(json.dumps(dict(passed=True,proof_sha256=sha(a.output/'proof.json'),bindings=len(files))))


if __name__=='__main__':main()
