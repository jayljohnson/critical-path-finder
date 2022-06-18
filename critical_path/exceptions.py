#!/usr/bin/env python

class MissingInputsException(Exception):
    pass


class RunBeforeSaveException(Exception):
    pass


class ClearBeforeLoading(Exception):
    pass


class NodeWeightsDuplicateValues(Exception):
    pass