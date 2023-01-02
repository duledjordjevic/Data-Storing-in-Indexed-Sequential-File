#!/usr/bin/python

import os
import struct
from binary_file import BinaryFile


class PrimaryZone(BinaryFile):
    def __init__(self, filename, record, record2, blocking_factor, empty_key=-1):
        BinaryFile.__init__(self, filename, record, blocking_factor, empty_key)
        self.record2 = record2 
        self.record_size2 = struct.calcsize(self.record2.format)
        self.block_size = (self.blocking_factor - 1) * self.record_size + self.record_size2
        
    def init_file(self):
        with open(self.filename, "wb") as f:
            block = self.blocking_factor*[self.get_empty_rec()]
            self.write_block(f, block)

    def __find_in_block(self, block, rec):
        for j in range(self.blocking_factor):
            if block[j].get("id") == self.empty_key or block[j].get("id") > rec.get("id"):
                return (True, j)

        return (False, None)

    def insert_record(self, rec):
        # if self.find_by_id(rec.get("id")):  # Svakom upisu prethodi trazenje
        #     print("Already exists with ID {}".format(rec.get("id")))
        #     return

        with open(self.filename, "rb+") as f:
            while True:
                block = self.read_block(f)

                if not block:           # EOF
                    break

                last = self.__is_last(block)
                here, j = self.__find_in_block(block, rec)

                if not here:
                    continue

                # save last record for inserting into next block
                tmp_rec = block[self.blocking_factor-1]
                for k in range(self.blocking_factor-1, j, -1):
                    block[k] = block[k-1]               # move records
                block[j] = rec                          # insert
                rec = tmp_rec                           # new record for insertion

                f.seek(-self.block_size, 1)
                self.write_block(f, block)

                # last block without empty rec?
                if last and block[self.blocking_factor-1].get("id") != self.empty_key:
                    block = self.blocking_factor*[self.get_empty_rec()]
                    self.write_block(f, block)

    def write_block(self, file, block):
        binary_data = bytearray()   # Niz bita koji bi trebalo da se upise u datoteku

        # Svaki slog u bloku serijalizujemo i dodamo u niz bajta
        for rec in block:
            if len(rec) != 1:
                # print(rec)
                rec_binary_data = self.record.dict_to_encoded_values(rec)
            else:
                rec_binary_data = self.record2.dict_to_encoded_values(rec)
                
            binary_data.extend(rec_binary_data)
        
        file.write(binary_data)

    def read_block(self, file):
        # Citanje od trenutne pozicije
        binary_data = file.read(self.block_size)
        block = []
        
        if len(binary_data) == 0:
            return block

        for i in range(self.blocking_factor ):   # slajsingom izdvajamo niz bita za svaki slog, i potom vrsimo otpakivanje
            if i != self.blocking_factor -1:
                begin = self.record_size*i
                end = self.record_size*(i+1)
                block.append(self.record.encoded_tuple_to_dict(
                    binary_data[begin:end]))
                
            else:
                # print()
                begin = self.record_size*i
                end = begin + self.record_size2
                block.append(self.record2.encoded_tuple_to_dict(
                    binary_data[begin:end]))
        
        return block

    def making_primary_zone(self, sorted_list):
        with open(self.filename, "wb") as f:
            empty_dict = {"position": -1}
            for i in range(0, len(sorted_list), self.blocking_factor  -1):
                last = len(sorted_list)-i
                if last < (self.blocking_factor - 1) and last != 0:
                    block = sorted_list[i:(i + last)]
                    for j in range(self.blocking_factor-last - 1):
                        block.append(self.get_empty_rec())
                else:
                    block = sorted_list[i:(i + self.blocking_factor-1)]
                block.append(empty_dict)
                
                self.write_block(f, block)

    

    def __is_last(self, block):
        for i in range(self.blocking_factor):
            if block[i].get("id") == self.empty_key:
                return True
        return False

    def print_file(self):
        i = 0
        with open(self.filename, "rb") as f:
            while True:
                block = self.read_block(f)

                if not block:
                    break

                i += 1
                print("Block {}".format(i))
                self.print_block(block)

    def read_block_by_position(self,  position):
        block = None
        with open(self.filename, "rb") as f:
            f.seek((self.record_size * (self.blocking_factor - 1) + self.record_size2)  * position)
            block = self.read_block(f)

        return block

    def update_position(self, position_of_block, position):
        block = self.read_block_by_position(position_of_block)
        block[-1]["position"] = position
        
        with open(self.filename, "rb+") as f:
            f.seek((self.record_size * (self.blocking_factor - 1) + self.record_size2)  * position_of_block)
            self.write_block(f, block)

        return True

    def update_block(self, position, block):
        with open(self.filename, "rb+") as f:
            f.seek((self.record_size * (self.blocking_factor - 1) + self.record_size2)  * position)
            self.write_block(f, block)
        
        return True

    # def find_by_id(self, id):
    #     i = 0
    #     with open(self.filename, "rb") as f:
    #         while True:
    #             block = self.read_block(f)

    #             if not block:
    #                 return None

    #             for j in range(self.blocking_factor):
    #                 if block[j].get("id") == id:
    #                     return (i, j)
    #                 if block[j].get("id") > id:
    #                     return None

    #             i += 1

    # def delete_by_id(self, id):
    #     found = self.find_by_id(id)

    #     if not found:
    #         return

    #     block_idx = found[0]
    #     rec_idx = found[1]
    #     next_block = None

    #     with open(self.filename, "rb+") as f:
    #         while True:
    #             f.seek(block_idx * self.block_size)  # last block
    #             block = self.read_block(f)

    #             for i in range(rec_idx, self.blocking_factor-1):
    #                 block[i] = block[i+1]       # move records

    #             if self.__is_last(block):              # is last block full?
    #                 f.seek(-self.block_size, 1)
    #                 self.write_block(f, block)
    #                 break

    #             next_block = self.read_block(f)
    #             # first record of next block is now the last of current one
    #             block[self.blocking_factor-1] = next_block[0]
    #             f.seek(-2*self.block_size, 1)
    #             self.write_block(f, block)

    #             block_idx += 1
    #             rec_idx = 0

    #     if next_block and next_block[0].get("id") == self.empty_key:
    #         os.ftruncate(os.open(self.filename, os.O_RDWR),
    #                      block_idx * self.block_size)
