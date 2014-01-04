#!/usr/bin/env python2
# coding=utf-8

"""
Represents one of the simplest form of key-value storage to file
"""

import pickle


class KVStore(object):
    def __init__(self, storage_file):
        self.__file = storage_file
        self.__data = dict()
        self.load()

    def load(self):
        try:
            fp = open(self.__file, 'r')
            self.__data = pickle.load(fp)
            fp.close()
        except IOError:
            pass

    def save(self):
        if self.__data is not None:
            try:
                fp = open(self.__file, 'w')
                pickle.dump(self.__data, fp)
                fp.close()
            except IOError:
                return False

            return True

        return False

    def items(self):
        return self.__data.items()

    def get(self, key):
        if key in self.__data:
            return self.__data[key]
        return False

    def set(self, key, value):
        self.__data[key] = value
        return self

    def rm(self, key):
        if key in self.__data:
            del self.__data[key]
        return self

    def has(self, key):
        return key in self.__data

    def empty(self):
        return self.count() == 0

    def count(self):
        return len(self.__data)
