"""This module contains custom exception for malvm."""


class BaseImageExists(Exception):
    pass


class VMNotExists(Exception):
    pass
