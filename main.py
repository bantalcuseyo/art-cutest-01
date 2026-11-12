#!/usr/bin/env python3
"""Copy the pre-rendered entry art into the make.fun output directory."""
import os
import shutil

src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
dst_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(dst_dir, exist_ok=True)
shutil.copyfile(src, os.path.join(dst_dir, "entry.png"))
print("wrote", os.path.join(dst_dir, "entry.png"))
