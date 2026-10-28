import os, sys, zipfile
src, out = 'unpacked', sys.argv[1]
if os.path.exists(out): os.remove(out)
z = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
for root, _, files in os.walk(src):
    for f in files:
        full = os.path.join(root, f)
        z.write(full, os.path.relpath(full, src).replace(chr(92), '/'))
z.close(); print('packed', out, os.path.getsize(out))
