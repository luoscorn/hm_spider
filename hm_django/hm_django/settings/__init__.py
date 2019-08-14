#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap

try:
    from .locals import *
except Exception as e:
    print(e)
    from .base import *
