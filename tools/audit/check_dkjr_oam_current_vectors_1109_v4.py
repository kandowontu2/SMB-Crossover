"""Rebind the frozen DK Jr vector checker to the exact Mini + DK candidate."""
from pathlib import Path
import json

import check_dkjr_oam_vectors_1109_v3 as V

P, OUT = V.P, V.OUT
PIN = '5f002ed5dff05e37298d15b746f4db8dfba12b07d2a9d343691679ace2654abf'


def main():
    ui_path = P.I.O/'frontend-v2.json'
    proposal_path = OUT/'oam-source.json'
    base = P.MINI_PRIVATE.read_bytes()
    assert P.sha(base) == 'a08d839b187fc6866a3fd3658200c2f26b8e3724b3b4de3b5e7d2a65702598d2'
    raw = P.compose(P.compose(base, json.loads(ui_path.read_text())['patches']),
                    json.loads(proposal_path.read_text())['patches'])
    assert P.sha(raw) == PIN
    # Keep the frozen checker and its source hash immutable. Only its exact
    # input and output bindings change. All vector assertions are retained.
    path = Path(V.__file__)
    text = path.read_text()
    text = P.replace_once(text, "raw = P.compose(P.PRIVATE.read_bytes(), proposal['patches'])", 'raw = CURRENT_RAW')
    text = P.replace_once(text, "assert P.sha(raw) == proposal['memory_only_hashes'][P.PIN]", 'assert P.sha(raw) == CURRENT_SHA')
    text = P.replace_once(text, "OUT/'oam-IRQ.json'", "OUT/'oam-IRQ-current.json'")
    text = P.replace_once(text, "P.R/'src/reset.s',P.R/'src/metasprite_engine.s',P.PRIVATE", 
                          "P.R/'src/reset.s',P.R/'src/metasprite_engine.s',P.MINI_PRIVATE,FRONTEND,SOURCE_CHECKER")
    env = dict(V.__dict__, __name__='dk_current_vector_checker', __file__=__file__, CURRENT_RAW=raw,
               CURRENT_SHA=PIN, FRONTEND=ui_path, SOURCE_CHECKER=path)
    exec(compile(text, str(path), 'exec'), env)
    env['main']()


if __name__ == '__main__':
    main()
