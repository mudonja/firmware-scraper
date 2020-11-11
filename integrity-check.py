#!/bin/etc/env python

import os
import subprocess
import time
import logging


# import datetime

class Checker:
    def __init__(self, chksum_filename=None, chksum_hash=None, somesortofchksumrecord=None):
        self.chksum_filename = chksum_filename
        self.chksum_hash = chksum_hash
        self.somesortofchksumrecord = somesortofchksumrecord

    # .asc .gpg .pgp
    def check(self, paths):
        # filenames_and_summs = dict()
        for path in paths:
            # Contains file path appended with file name
            print("PATH", path)
            if os.path.isfile(path):
                # contents = subprocess.run(['cat', path], stdout=subprocess.PIPE)
                # TODO: Line bellow was an idea that might be not necessary
                #  if os.path.isfile(path-md5sums/*) and md5summs not in path/*
                #    if md5sum(filename) == filename_and_summs[filename]:
                #        with open("./INTEGRITY", 'w+') as f:
                #            f.write(filename+"  OK!"
                sum_file_name = os.path.split(path)[-1]
                cwdpath = path[:-len(self.chksum_hash + "sums")]
                result = subprocess.Popen([self.chksum_hash + "sum", '-c', sum_file_name], cwd=cwdpath,
                                          stdout=subprocess.PIPE)
                out, err = result.communicate()
                if err is not None:
                    print("ERROR:", err)
                tmp = out.decode()
                tmp2 = tmp.split("\n")
                if tmp2[-1] == "":
                    del tmp2[-1]

                # This result/log mechanism could be written in a better fashion
                log_dir = "log/"
                # log_name = "integrity_check_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".log"
                log_name = self.chksum_filename + "_integrity_check.log"
                with open(log_dir + log_name, 'a+') as f:
                    f.write("\n\n*")
                    f.write(path[25:-len(self.chksum_hash + "sums")].upper())  # .replace("/", "."))
                    f.write("\n")
                    for t in tmp2:
                        f.write(t)
                        f.write("\n")
                f.close()
                print("***DONE with", path, "\n\n")
                # Alternative to Popen
                # result = subprocess.run(['md5sum', '-c', 'md5sums'], cwd=path[:-7], stdout=subprocess.PIPE)
            else:
                print(path, "is not a valid md5 check sum file!")

    def sum_check_from_file(self):
        if self.chksum_hash == 'md5':
            md5sums = subprocess.run(['find', target_dir, '-iname', self.chksum_filename], stdout=subprocess.PIPE)
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
            sha256sums = subprocess.run(['find', target_dir, '-iname', self.chksum_filename], stdout=subprocess.PIPE)
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
        elif self.chksum_hash == 'sha1':
            pass

    def file_check_with_signature(self):
        pass


class Verifier:
    def __init__(self, filename=None, extension=None):
        self.filename = filename
        self.extension = extension

    def verify(self):
        files = subprocess.run(['find', target_dir, '-iname', self.filename+'.'+self.extension], stdout=subprocess.PIPE)
        a = files.stdout.decode()
        b = a.split("\n")

        # logging.basicConfig(filename='./log/verifier.log', encoding='utf-8', level=logging.DEBUG)

        if b[-1] == "":
            del b[-1]
        for ele in b:
            print("***Checking:\n", ele[:-(len(self.extension)+1)])
            # +1 is to include the dot before the extension
            print("***With:\n", ele)
            print("***RESULT:")
            ###verify 256sums and packages
            result = subprocess.Popen(['gpg', '--with-fingerprint', '--verify', ele, ele[:-(len(self.extension)+1)]],
                                      cwd=".", stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = result.communicate()
            if err is not None:
                print('***Error:\n', err.decode(), "\n\n")
            if out is not None:
                print('***Output:\n', out.decode(), "\n\n")




def getKeyRing():
    keyring = 'git://git.openwrt.org/keyring.git'
    # gitcmd == git clone git://git.openwrt.org/keyring.git
    gitcmd = subprocess.Popen(['git', 'clone', keyring], cwd=".",
                              stdout=subprocess.PIPE)
    out, err = gitcmd.communicate()
    if err:
        print("There has been an error:\n", str(err))
    else:
        print("***Done\n", str(out))


def importKeys():
    # gpgcmd == gpg --import ./keyring/gpg/*
    gpgcmd = subprocess.Popen(['gpg', '--import', 'keyring/gpg/*'], cwd=".",
                              stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = gpgcmd.communicate()
    if err:
        print("***ERROR:\n", err.decode())
    else:
        print("***Done\n", out.decode())


if __name__ == '__main__':
    target_dir = "./temp"  # Change to the directory containing the files
    ### Download keyring
    #getKeyRing()
    #time.sleep(10)
    ### Import keys
    #importKeys()


    ### Checks MD5 hashes
    md5check = Checker(chksum_filename='md5sums', chksum_hash="md5")
    ### Checks SHA256 hashes
    sha256check = Checker(chksum_filename='sha256sums', chksum_hash='sha256')
    ### Check for signature files(e.g.  *.gpg *.asc *.sig)
    print("***Verifying sha256 files and Package")
    verifyPackagesASC = Verifier(filename="Packages", extension='asc')
    verifyPackagesGPG = Verifier(filename="Packages", extension='gpg')
    verifySHA256ASC = Verifier(filename="sha256sums", extension='asc')
    verifySAH256GPG = Verifier(filename="sha256sums", extension='gpg')

    verifyPackagesASC.verify()
    verifyPackagesGPG.verify()
    verifySHA256ASC.verify()
    verifySAH256GPG.verify()
    print("check md5")
    md5check.sum_check_from_file()
    print("check sha256")
    sha256check.sum_check_from_file()
