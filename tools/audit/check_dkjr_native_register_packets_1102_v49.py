"""Independent deepest real IRQ/lagNMI replay after private register packets."""
import contextlib,io,json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O


def main():
    path=R/'tools/audit/check_dkjr_native_service_irq_1102_v47.py';text=path.read_text()
    old='source=path.read_text();base=N.NesMPU'
    new="source=path.read_text().replace('native-defeat','native-registers').replace('v45','v48').replace('v46','v49');base=N.NesMPU"
    assert text.count(old)==1;text=text.replace(old,new)
    text=text.replace("O/'native-defeat-v46-qualified.json'","O/'native-registers-v49-qualified.json'").replace("O/'native-defeat-v45.bin'","O/'native-registers-v48.bin'")
    text=text.replace('native-service-v47-IRQ','native-registers-v49-IRQ')
    env={'__name__':'dk_register_packet_irq','__file__':str(path)}
    with contextlib.redirect_stdout(io.StringIO()):exec(compile(text,str(path),'exec'),env);env['main']()
    irq=json.loads((O/'native-registers-v49-IRQ.json').read_text());qualified=json.loads((O/'native-registers-v49-qualified.json').read_text())
    assert irq['passed']and qualified['passed']
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,body_bytes=qualified['body_bytes'],header_spare=qualified['header_spare'],
        deepest_actual_IRQ=irq,actual_whole_Main=qualified['full_native_Main'],exact_native_defeat_service_cases=qualified['exact_native_defeat_service_cases'],
        retained_negatives=['native-earned-Main-v41-negative.json','native-packets-v43-Main-negative.json','native-service-v47-IRQ-negative.json'],
        scope='Source mechanism unchanged: earned physical native fruit defeat and original60D1AE/score1200/nextnormal thaw pass complete native Main. Exact native defeat service parity192cases and real deepest IRQ/lagNMI with full continuation pass. Private source-dead save frames total91B C460..C4BB; no shared change. Final current-owner/cold/fullcut closure and17remainingrows still pending.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),path,O/'native-registers-v48-layout.json',O/'native-registers-v48.bin',O/'native-registers-v49-IRQ.json',O/'native-registers-v49-qualified.json']})
    (O/'native-registers-v49-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,body_bytes=out['body_bytes'],header_spare=out['header_spare'],minimum_foreground_SP=irq['minimum_foreground_SP'],minimum_ISR_SP=irq['minimum_ISR_SP'],exact_defeat_cases=out['exact_native_defeat_service_cases'])))


if __name__=='__main__':main()
