"""Prepare granted Prince native controls outside the near-full source root."""
from pathlib import Path
import argparse
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'tools/audit/prepare_prince_live_native_1103_v174.py'
CANDIDATE = ROOT/'build/prince-live-root-candidate-1103-v113/prince-live-private.nes'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['controls','contact-death'], default='controls')
    args = parser.parse_args()
    out = ROOT/('build/prince-live-root-'+args.mode+'-1103-v114')
    out.mkdir(exist_ok=False)
    grant_path = ROOT/'docs/qa/allocations/prince-live-lifetime-1103-v113.json'
    grant = json.loads(grant_path.read_text())
    assert grant['granted'] and grant['expected_candidate_SHA256'] == '6c9e85a94d34a4623d21789d5293c61af2ad14d214f5780f57613a51ae6bb25a'
    sys.path.insert(0,str(ROOT/'tools/audit'))
    spec = importlib.util.spec_from_file_location('prince_live174',SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original = module.prepare
    def prepare(output, rom, controller, refs, **kwargs):
        assert rom.resolve() == CANDIDATE.resolve()
        kwargs['timeout'] = min(kwargs['timeout'],240)
        kwargs['allow_interactive'] = True
        return original(out/'native',rom,controller,
            set(refs)|{Path(__file__),grant_path},**kwargs)
    module.prepare = prepare
    sys.argv = [str(SOURCE),'--rom',str(CANDIDATE),'--mode',args.mode]
    module.main()


if __name__=='__main__':
    main()
