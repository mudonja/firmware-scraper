#!/bin/etc/env python

import os
import subprocess


class Checker:
    def __init__(self, chksum_filename=None, chksum_hash=None, somesortofchksumrecord=None):
        self.chksum_filename = chksum_filename
        self.chksum_hash = chksum_hash
        self.somesortofchksumrecord = somesortofchksumrecord

    def md5check(self, paths):
        filenames_and_summs=dict()
        for path in paths:
            # Contains file path appended with file name
            print("path", path)
            if os.path.isfile(path):
                print(path, "\nContains:")
                contents = subprocess.run(['cat', path], stdout=subprocess.PIPE)
                # TODO: Line bellow was an idea that might be not necessary
                # if os.path.isfile(path-md5sums/*) and md5summs not in path/*
                #    if md5sum(filename) == filename_and_summs[filename]:
                #        with open("./INTEGRITY", 'w+') as f:
                #            f.write(filename+"  OK!"
                print(contents.stdout.decode())
            else:
                print(path, "is not a valid md5 check sum file!")

    def sum_check_from_file(self):
        if self.chksum_hash == 'md5':
            md5sums = subprocess.run(['find', '.', '-iname', self.chksum_filename], stdout=subprocess.PIPE)
            a = md5sums.stdout.decode()
            b = a.split("\n")
            if b[-1] == "":
                del b[-1]
            md5paths = []
            i = 0

            for ele in b:
                ele.strip()
                print(i, ele)
                md5paths.append(ele)
                i += 1

            self.md5check(md5paths)

            #print("WOHOOOOOO\n", md5paths)
        elif self.chksum_hash == 'sha1':
            pass
        elif self.chksum_hash == 'sha256':
            pass


if __name__ == '__main__':
    check = Checker(chksum_filename='md5sums', chksum_hash="md5")
    check.sum_check_from_file()
