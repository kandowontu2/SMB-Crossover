"""Distinct full-Main replay of retained stack negative with private frames."""
import contextlib,io,json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O


def main():
    path=R/'tools/audit/check_dkjr_native_earned_main_1102_v41.py'
    source=path.read_text().replace('native-effects-v39','native-packets-v42').replace('native-effects-','native-packets-').replace('-v39.bin','-v42.bin')
    source=source.replace('native-earned-Main-v41','native-packets-v43-Main')
    source=source.replace("'epoch_boundaries=epochs'","'epoch_boundaries=epochs'")
    old="physical_native_defeats=1,source_native_score_400plus800=score,lives_before=2,lives_after=2,epoch_boundaries=epochs,actual_calls=dict(counts),"
    new=old+"minimum_CPU_SP=minimum,first_SMC_stack_overlap=overlap,"
    assert source.count(old)==1;source=source.replace(old,new)
    source=source.replace("O/'native-packets-v40-CPU.json'","O/'native-effects-v40-CPU.json'")
    env={'__name__':'dk_repaired_earned_main','__file__':str(path)}
    with contextlib.redirect_stdout(io.StringIO()):exec(compile(source,str(path),'exec'),env);env['main']()
    receipt=json.loads((O/'native-packets-v43-Main-CPU.json').read_text());assert receipt['passed']and receipt['first_SMC_stack_overlap']is None
    assert receipt['minimum_CPU_SP']>=0x80
    q=json.loads((O/'native-packets-v42-layout.json').read_text())
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        full_native_Main=receipt,body_bytes=q['body_bytes'],header_spare=q['header_spare'],
        corrected_negative='native-earned-Main-v41-negative.json',private_save_packet_extent=[0xc460,0xc4b4],
        scope='Exact same earned nativeMain controls/fixture as immutablev41 negative. Only native save frames moved to audited privateRAM; source fruit/defeat/60D1AE timer/nativeAI/draw/score assertions unchanged. Full IRQ and foreign/latest-owner/cold/lifecycle qualification pending.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),path,O/'native-packets-v42-layout.json',O/'native-packets-v42.bin',O/'native-packets-v43-Main-CPU.json',O/'native-earned-Main-v41-negative.json']})
    (O/'native-packets-v43-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,minimum_CPU_SP=receipt['minimum_CPU_SP'],epoch_boundaries=receipt['epoch_boundaries'],actual_calls=receipt['actual_calls'])))


if __name__=='__main__':main()
