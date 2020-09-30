#!/bin/etc/env python

import os
import subprocess
import datetime

class Checker:
    def __init__(self, chksum_filename=None, chksum_hash=None, somesortofchksumrecord=None):
        self.chksum_filename = chksum_filename
        self.chksum_hash = chksum_hash
        self.somesortofchksumrecord = somesortofchksumrecord
#.asc .gpg .pgp
    def md5check(self, paths):
        filenames_and_summs=dict()
        for path in paths:
            # Contains file path appended with file name
            print("PATH", path)
            if os.path.isfile(path):
                #contents = subprocess.run(['cat', path], stdout=subprocess.PIPE)
                # TODO: Line bellow was an idea that might be not necessary
                #  if os.path.isfile(path-md5sums/*) and md5summs not in path/*
                #    if md5sum(filename) == filename_and_summs[filename]:
                #        with open("./INTEGRITY", 'w+') as f:
                #            f.write(filename+"  OK!"
                sum_file_name = os.path.split(path)[-1]
                result = subprocess.Popen(['md5sum', '-c', sum_file_name], cwd=path[:-7], stdout=subprocess.PIPE)
                out, err = result.communicate()
                if err != None:
                    print("ERROR:", err)
                tmp = out.decode()
                tmp2 = tmp.split("\n")
                if tmp2[-1] == "":
                    del tmp2[-1]

                # This result mechanism could be written in a better fashion
                log_dir = "log/"
                #log_name = "integrity_check_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".log"
                log_name = "integrity_check.log"
                with open(log_dir+log_name, 'a+') as f:
                    f.write("\n\n")
                    f.write(path[20:-7].upper().replace("/", "."))
                    f.write("\n")
                    for t in tmp2:
                        f.write(t)
                        f.write("\n")
                f.close()
                print("***DONE with", path, "\n\n")
                # Alternative to Popen
                #result = subprocess.run(['md5sum', '-c', 'md5sums'], cwd=path[:-7], stdout=subprocess.PIPE)

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
