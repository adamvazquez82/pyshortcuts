#!/usr/bin/env python
"""
Create desktop shortcuts for Darwin / MacOS
"""
from __future__ import print_function
import os
import sys
import shutil

from .homedir import get_homedir

def fix_anacondapy_pythonw(fname):
    """fix shebang line for scripts using anaconda python
    to use 'pythonw' instead of 'python'
    """
    # print(" fix anaconda py (%s) for %s" % (sys.prefix, script))
    with open(fname, 'r') as fh:
        try:
            lines = fh.readlines()
        except IOError:
            lines = ['-']
    firstline = lines[0][:-1].strip()
    if firstline.startswith('#!') and 'python' in firstline:
        firstline = '#!/usr/bin/env pythonw'
        fh = open(fname, 'w')
        fh.write('%s\n' % firstline)
        fh.write("".join(lines[1:]))
        fh.close()

def make_shortcut(script, name, description=None, icon=None, terminal=False):
    """create minimal Mac App to run script"""
    if description is None:
        description = name

    desktop = os.path.join(get_homedir(), 'Desktop')
    script = os.path.abspath(script)`

    pyexe = sys.executable
    if 'Anaconda' in sys.version:
        pyexe = "{prefix:s}/python.app/Contents/MacOS/python".format(prefix=sys.prefix)
        fix_anacondapy_pythonw(script)
    dest = os.path.join(desktop, name + '.app')
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.mkdir(dest)
    os.mkdir(os.path.join(dest, 'Contents'))
    os.mkdir(os.path.join(dest, 'Contents', 'MacOS'))
    os.mkdir(os.path.join(dest, 'Contents', 'Resources'))
    opts = dict(name=name, desc=description, script=script,
                prefix=sys.prefix, pyexe=pyexe)

    info = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN"
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
  <key>CFBundleGetInfoString</key> <string>{desc:s}</string>
  <key>CFBundleName</key> <string>{name:s}</string>
  <key>CFBundleExecutable</key> <string>{name:s}</string>
  <key>CFBundleIconFile</key> <string>{name:s}</string>
  <key>CFBundlePackageType</key> <string>APPL</string>
  </dict>
</plist>
"""

    header = """#!/bin/bash
## Run script with Python that created this script
export PYTHONEXECUTABLE={prefix:s}/bin/python
export PY={pyexe:s}
export SCRIPT={script:s}
"""
    text = "$PY $SCRIPT"
    if terminal:
        text = """
osascript -e 'tell application "Terminal" to do script "'${{PY}}\ ${{SCRIPT}}'"'
"""

    with open(os.path.join(dest, 'Contents', 'Info.plist'), 'w') as fout:
        fout.write(info.format(**opts))

    ascript_name = os.path.join(dest, 'Contents', 'MacOS', name)
    with open(ascript_name, 'w') as fout:
        fout.write(header.format(**opts))
        fout.write(text.format(**opts))
        fout.write("\n")

    os.chmod(ascript_name, 493) ## = octal 755 / rwxr-xr-x
    if icon is not None:
        icon_dest = os.path.join(dest, 'Contents', 'Resources', name + '.icns')
        shutil.copy(icon, icon_dest)
