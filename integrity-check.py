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
    def check(self, paths):
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
                cwdpath=path[:-len(self.chksum_hash+"sums")]
                result = subprocess.Popen([self.chksum_hash+"sum", '-c', sum_file_name], cwd=cwdpath, stdout=subprocess.PIPE)
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
                log_name = self.chksum_filename+"_integrity_check.log"
                with open(log_dir+log_name, 'a+') as f:
                    f.write("\n\n*")
                    f.write(path[25:-len(self.chksum_hash+"sums")].upper())  #.replace("/", "."))
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
            self.check(md5paths)
        elif self.chksum_hash == 'sha256':
            sha256sums = subprocess.run(['find', '.', '-iname', self.chksum_filename], stdout=subprocess.PIPE)
            a = sha256sums.stdout.decode()
            b = a.split("\n")
            if b[-1] == "":
                del b[-1]
            sha256paths = []
            i = 0
            for ele in b:
                ele.strip()
                print(i, ele)
                sha256paths.append(ele)
                i += 1
            self.check(sha256paths)
            #print("WOHOOOOOO\n", md5paths)
        elif self.chksum_hash == 'sha1':
            pass
        # elif self.chksum_hash == 'sha256':
        #     pass

# TODO: GPG/PGP Signatures
#       .ASC File
#       .SIG File
#

if __name__ == '__main__':
    # Checks MD5 hashes
    check = Checker(chksum_filename='md5sums', chksum_hash="md5")
    # Checks SHA256 hashes
    check2 = Checker(chksum_filename='sha256sums', chksum_hash='sha256')
    # Check for signature files(e.g. *.pgp *.gpg *.asc *.sig)

    check.sum_check_from_file()
    print("check sha256")
    check2.sum_check_from_file()
