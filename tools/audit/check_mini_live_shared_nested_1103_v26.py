"""Replay only the actual active-auth FF handler deepest IRQ winners."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_mini_live_shared_isr_1103_v25 as LIVE
import check_bub_shared_auth_nested_1103_v80 as Legacy
O=LIVE.O


def main():
    proof=json.loads((O/'live-shared-ISR-v25.json').read_text());assert proof['passed']and proof['nested_handler_winners']
    text=inspect.getsource(Legacy.main)
    text=text.replace('shared-auth-v79-ISR.json','live-shared-ISR-v25.json').replace('shared-auth-v80-nested.json','live-shared-nested-v26.json')
    text=text.replace('source=inspect.getsource(P.main)','source=LIVE.source_main()')
    text=text.replace("scope='Genuine full native IRQ","scope='Exact frozenhost28")
    text=text.replace('0xab72<=active.pc<0xabce','0xab72<=active.pc<0xabd4')
    text=text.replace('env=dict(P.__dict__,__file__=__file__,','env=dict(LIVE.environment(),__file__=__file__,')
    env=dict(Legacy.__dict__,O=O,__file__=__file__,LIVE=LIVE)
    exec(compile(text,__file__,'exec'),env);env['main']()
    path=O/'live-shared-nested-v26.json';q=json.loads(path.read_text())
    q['scope']='Exact frozenhost28/c393. Reuses all qualified25 active-auth/public41row4/foreign41retire IRQ+genuineFF cuts by binding. Reconstructs only actual deepest handler-winner foregroundcontexts, injects nativeIRQ, resumes exactFF outerhandler throughRTI. FullCPU/live stack/private/native/scratch/SMC/maps/PPU/audio match unchangednativehandler. Cold23 remains screenoff and has noCLI/nestedwinners; no gameplay/Main/sourceStep claim.'
    q['bindings'].update({p.relative_to(R).as_posix():Legacy.sha(p)for p in [Path(__file__),Path(LIVE.__file__),Path(Legacy.__file__),O/'live-shared-ISR-v25.json',O/'final-payload-v24.json']})
    path.write_text(json.dumps(q,separators=(',',':'))+'\n')


if __name__=='__main__':main()
