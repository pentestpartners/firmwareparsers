#!/usr/bin/env python3

import argparse
import os
import struct
import sys


class PacHeader:
    FORMAT = '<44sII512s512sIIIIIIII200sIII200I2H'
    SIZE = struct.calcsize(FORMAT)

    def __init__(self, data):
        unpacked_data = struct.unpack(self.FORMAT, data)
        self.szVersion = unpacked_data[0].decode('utf-16le').strip('\x00')
        self.dwHiSize = unpacked_data[1]
        self.dwLoSize = unpacked_data[2]
        self.szPrdName = unpacked_data[3].decode('utf-16le').strip('\x00')
        self.szPrdVersion = unpacked_data[4].decode('utf-16le').strip('\x00')
        self.nFileCount = unpacked_data[5]
        self.dwFileOffset = unpacked_data[6]
        self.dwMode = unpacked_data[7]
        self.dwFlashType = unpacked_data[8]
        self.dwNandStrategy = unpacked_data[9]
        self.dwIsNvBackup = unpacked_data[10]
        self.dwNandPageType = unpacked_data[11]
        self.szPrdAlias = unpacked_data[12]
        self.dwOmaDmProductFlag = unpacked_data[13].decode('ascii').strip('\x00')
        self.dwIsOmaDM = unpacked_data[14]
        self.dwIsPreload = unpacked_data[15]
        self.dwReserved = unpacked_data[16:216]  # Array of 200 uint32_t
        self.dwMagic = unpacked_data[216]
        self.wCRC1 = unpacked_data[217]
        self.wCRC2 = unpacked_data[218]

    def print_header(self, verbose=False):
        print(f"    szVersion: {self.szVersion}")
        print(f"    dwHiSize: {self.dwHiSize}")
        print(f"    dwLoSize: {self.dwLoSize}")
        print(f"    szPrdName: {self.szPrdName}")
        print(f"    szPrdVersion: {self.szPrdVersion}")
        print(f"    nFileCount: {self.nFileCount}")
        print(f"    dwFileOffset: {self.dwFileOffset}")
        print(f"    dwMode: {self.dwMode}")
        print(f"    dwFlashType: {self.dwFlashType}")
        print(f"    dwNandStrategy: {self.dwNandStrategy}")
        print(f"    dwIsNvBackup: {self.dwIsNvBackup}")
        print(f"    dwNandPageType: {self.dwNandPageType}")
        print(f"    szPrdAlias: {self.szPrdAlias}")
        print(f"    dwOmaDmProductFlag: {self.dwOmaDmProductFlag}")
        print(f"    dwIsOmaDM: {self.dwIsOmaDM}")
        print(f"    dwIsPreload: {self.dwIsPreload}")
        print(f"    dwMagic: {self.dwMagic}")
        print(f"    wCRC1: {self.wCRC1}")
        print(f"    wCRC2: {self.wCRC2}")


class Header:
    FORMAT = '<I512s512s504sIIIIIIII5I249I'
    SIZE = struct.calcsize(FORMAT)

    def __init__(self, data):
        unpacked_data = struct.unpack(self.FORMAT, data)
        self.dwSize = unpacked_data[0]
        self.szFileID = unpacked_data[1].decode('utf-16le').strip('\x00')
        self.szFileName = unpacked_data[2].decode('utf-16le').strip('\x00')
        self.szFileVersion = unpacked_data[3].decode('ascii', errors='ignore').strip('\x00')
        self.dwHiFileSize = unpacked_data[4]
        self.dwHiDataOffset = unpacked_data[5]
        self.dwLoFileSize = unpacked_data[6]
        self.nFileFlag = unpacked_data[7]
        self.nCheckFlag = unpacked_data[8]
        self.dwLoDataOffset = unpacked_data[9]
        self.dwCanOmitFlag = unpacked_data[10]
        self.dwAddrNum = unpacked_data[11]
        self.dwAddr = unpacked_data[12:17]  # Array of 5 uint32_t
        self.dwReserved = unpacked_data[17:266]  # Array of 249 uint32_t

    @property
    def nFileSize(self):
        return (self.dwHiFileSize << 32) | self.dwLoFileSize

    @property
    def dwDataOffset(self):
        return (self.dwHiDataOffset << 32) | self.dwLoDataOffset

    def print_header(self, verbose=False):
        if verbose:
            print(f"  dwSize: {self.dwSize}")
            print(f"  szFileID: {self.szFileID}")
            print(f"  szFileName: {self.szFileName}")
            print(f"  szFileVersion: {self.szFileVersion}")
            print(f"  dwHiFileSize: {self.dwHiFileSize}")
            print(f"  dwHiDataOffset: {self.dwHiDataOffset}")
            print(f"  dwLoFileSize: {self.dwLoFileSize}")
            print(f"  nFileFlag: {self.nFileFlag}")
            print(f"  nCheckFlag: {self.nCheckFlag}")
            print(f"  dwLoDataOffset: {self.dwLoDataOffset}")
            print(f"  dwCanOmitFlag: {self.dwCanOmitFlag}")
            print(f"  dwAddrNum: {self.dwAddrNum}")
            print(f"  nFileSize: {self.nFileSize}")
            print(f"  dwDataOffset: {self.dwDataOffset}")
        else:
            print(f"  szFileID: {self.szFileID}")
            print(f"  szFileName: {self.szFileName}")


def read_pac_header(file):
    file.seek(0)
    data = file.read(PacHeader.SIZE)
    if len(data) != PacHeader.SIZE:
        return None
    return PacHeader(data)


def read_header(file, offset):
    file.seek(offset)
    data = file.read(Header.SIZE)
    if len(data) != Header.SIZE:
        return None
    return Header(data)


def extract_data(file, offset, size, output_dir, filename):
    file.seek(offset)
    data = file.read(size)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(os.path.join(output_dir, filename), 'wb') as out_file:
        out_file.write(data)


def main():
    parser = argparse.ArgumentParser(description='Process a PAC file and its headers.')
    parser.add_argument('file', help='Path to the PAC file')
    parser.add_argument('--print', '-p', action='store_true', help='Print basic output')
    parser.add_argument('--header', '-t', action='store_true', help='Print .pac header')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print verbose output')
    parser.add_argument('--extract', '-e', metavar='IDENTIFIER', help='Extract a specific partition by szFileID or szFileName')
    parser.add_argument('--export', '-x', action='store_true', help='Export all partitions to a directory')
    parser.add_argument('--output-dir', '-o', metavar='DIR', default='output', help='Output directory for extracted files')

    args = parser.parse_args()

    file_path = args.file
    output_dir = args.output_dir
    offset = 2124
    headers = []

    if len(sys.argv) <= 2:
        parser.print_help()
        sys.exit(1)

    with open(file_path, 'rb') as file:
        pac_header = read_pac_header(file)

        if pac_header is None:
            print("PAC header is not valid")
            return

        if args.header:
            print("PAC header")
            pac_header.print_header(verbose=args.verbose)

        # Read subsequent headers based on nFileCount
        num_headers_to_read = pac_header.nFileCount

        for i in range(num_headers_to_read):
            header = read_header(file, offset)
            if not header:
                print("No more headers found or file too short.")
                break
            headers.append(header)
            offset += Header.SIZE

        # Print headers
        if args.print or args.verbose:
            for idx, header in enumerate(headers):
                print(f"\nHeader {idx + 1}:")
                header.print_header(verbose=args.verbose)

        # Extract a specific partition
        if args.extract:
            for header in headers:
                if header.szFileID == args.extract or header.szFileName == args.extract:
                    identifier = header.szFileID if header.szFileID == args.extract else header.szFileName
                    extract_data(file, header.dwDataOffset, header.nFileSize, output_dir, identifier)
                    print(f"Extracted {identifier} to {output_dir}/{identifier}")
                    break
            else:
                print(f"Partition {args.extract} not found.")

        # Export all partitions
        if args.export:
            for header in headers:
                identifier = header.szFileID if header.szFileID else header.szFileName
                extract_data(file, header.dwDataOffset, header.nFileSize, output_dir, identifier)
                print(f"Exported {identifier} to {output_dir}/{identifier}")


if __name__ == "__main__":
    main()
