"""Fail closed on build-cache size/file growth, independently of capture limits."""
from pathlib import Path
import os
import time

BUILD=Path(__file__).resolve().parents[2]/'build'
BUILD_BYTES=5_000_000_000
BUILD_FILES=20_000
TASK_BYTES=256_000_000
TASK_FILES=1_000
_cached=None


class BuildStorageExceeded(RuntimeError):
    pass


def inventory(root,byte_cap,file_cap):
    size=count=0
    if not root.exists():return size,count
    pending=[root];directories=0
    while pending:
        directories+=1
        if directories>max(file_cap,64):
            raise BuildStorageExceeded('Build directory count exceeds the bounded storage scan.')
        with os.scandir(pending.pop())as items:
            for item in items:
                st=item.stat(follow_symlinks=False)
                if item.is_symlink()or getattr(st,'st_file_attributes',0)&0x400:
                    raise BuildStorageExceeded('Build storage contains a link/reparse point; inspect before writing.')
                if item.is_dir(follow_symlinks=False):pending.append(Path(item.path))
                elif item.is_file(follow_symlinks=False):count+=1;size+=st.st_size
                if size>byte_cap or count>file_cap:
                    raise BuildStorageExceeded(f'Build storage limit exceeded at {size:,} bytes / {count:,} files. Prune superseded outputs; do not raise the cap.')
    return size,count


def preflight(*,private_root=None,reserved_bytes=0,reserved_files=0,fresh=False):
    global _cached
    if reserved_bytes<0 or reserved_files<0:raise BuildStorageExceeded('Invalid storage reservation.')
    now=time.monotonic()
    if fresh or _cached is None or now-_cached[0]>2:
        size,count=inventory(BUILD,BUILD_BYTES,BUILD_FILES);_cached=(now,size,count)
    _,size,count=_cached
    if size+reserved_bytes>BUILD_BYTES or count+reserved_files>BUILD_FILES:
        raise BuildStorageExceeded('Build reservation would exceed 5 GB / 20,000 files. Prune before creating outputs.')
    if private_root is not None:
        private_root=Path(private_root).resolve()
        if not private_root.is_relative_to(BUILD.resolve())or private_root==BUILD.resolve():
            raise BuildStorageExceeded('Task output must be a proper child of build/.')
        inventory(private_root,TASK_BYTES,TASK_FILES)
    return dict(build_bytes=size,build_files=count,build_byte_cap=BUILD_BYTES,build_file_cap=BUILD_FILES)
