#!/usr/bin/env python

import sys
from src import main

if "--profile" in sys.argv:
    import profile
    profile.run("main.main()")
else:
    main.main()
