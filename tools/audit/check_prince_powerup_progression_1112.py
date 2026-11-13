"""Inspect actual native reveal classification for current Prince cold state."""
import json
from hashlib import sha256
from pathlib import Path
import check_prince_brick_support_1111 as B


def main():
    raw = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    assert sha256(raw).hexdigest() == '6d0346164b7099f8e75cdbe22a9e9f1fd5f4f673116fd1dcb48a3cee620734c2'
    seed, _ = B.cold(raw)
    rows = []
    for status in (0, 1, 2):
        model = B.fixture(seed)
        B.N.put(model, PlayerStatus=status, ObjectOffset=5)
        model[B.N.address(model.bundle, 'PowerUpType')+5] = 0
        B.N.invoke(model, 'PwrUpJmp', x=5)
        rows.append(dict(status=status, revealed=model[B.N.address(model.bundle, 'PowerUpType')+5]))
    print(json.dumps(dict(rows=rows, scope='Controlled native reveal, not earned pickup', output_files=0)))


if __name__ == '__main__':
    main()
