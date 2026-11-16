"""Reuse frozen owning full-route/first-injury checker with new inputs only."""
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import replay_dkjr_pipe5_depart_defense_1116 as F
import check_dkjr_backward_stairs_current_root_1116 as Previous

CHECK_SHA='ae09319754023d02b03c18e7f31b394267d54e404e8cb8fd1f9f6499972012dc'
H=lambda value:sha256(value).hexdigest()


def main():
    assert H(Path(Previous.__file__).read_bytes())==CHECK_SHA
    read=Path.read_bytes;parent=read(F.C.BT.ROM);assert H(parent)==F.C.PIN
    def snapshot(path):
        return parent if path.resolve()==F.C.BT.ROM.resolve()else read(path)
    print('DKJR_PIPE5_DEFENSE_SCOPE '+json.dumps(dict(factory_SHA256=H(Path(F.__file__).read_bytes()),
        baseline_factory_SHA256=F.PARENT_FACTORY_SHA,baseline_checker_SHA256=CHECK_SHA,
        actual_parent_SHA256=H(parent),candidate_SHA256=F.C.CANDIDATE,
        new_inputs_only=True,prior_50719_encounter_receipt='48a74141d60e4917c39ba22250b7b153471bd432682e363084613d0f8b686ca3',
        inherited_first_source5_and_native_injury_reporting=True,new_game_bytes=0,new_helpers=0,outputs=0),separators=(',',':')),flush=True)
    with patch.object(Previous,'F',F),patch.object(Path,'read_bytes',snapshot):Previous.main()


if __name__=='__main__':main()
