import os
import struct
from binary_file import BinaryFile
from record import Record
import math 

class ZonaPrekoracenja(BinaryFile):
    def __init__(self, filename, record,  blocking_factor,  empty_key=-1):
        BinaryFile.__init__(self, filename, record, blocking_factor, empty_key)
        self.header = Record(["E"], 'i', "ascii")
        self.header_size = struct.calcsize(self.header.format)
        

    # def init_file(self):
    #     with open(self.filename, "wb") as f:
    #         binary_data = self.header.dict_to_encoded_values({"B": 0, "h": 0, "C" : 0})
    #         f.write(binary_data)

    def __find_in_block(self, block, rec):
        for j in range(self.blocking_factor):
            if block[j].get("id") == self.empty_key or block[j].get("id") > rec.get("id"):
                return (True, j)

        return (False, None)


    def write_header(self, head):
        with open(self.filename, "rb+") as f:
            binary_data = self.header.dict_to_encoded_values(head)
            f.write(binary_data)

    def read_header(self):
        with open(self.filename, "rb") as f:
            binary_data = f.read(self.header_size)

        return self.header.encoded_tuple_to_dict(binary_data)

    def making_zona_prekoracnja(self):
        head = {"E" : 0}
        with open(self.filename, "wb") as f:
            binary_data = self.header.dict_to_encoded_values(head)
            f.write(binary_data)
        return True


    # def find_next(self, position):
    #     last_element_position = position
    #     with open(self.filename, "rb") as f:
    #         while True:
    #             f.seek(self.header_size + (position) * self.record_size)
    #             binary_data = f.read(self.record_size)
    #             record = self.record.encoded_tuple_to_dict(binary_data)

    #             if record["next"] == -1:
    #                 break
    #             last_element_position = position
    #             position = record["next"]
    #     return position, last_element_position


    def adding_element_first_time(self, record):
        head = self.read_header()
        E = head["E"]
        with open(self.filename, "rb+") as f:
            f.seek(self.header_size + self.record_size*E)
            record["next"] = -1
            binary_data = self.record.dict_to_encoded_values(record)
            f.write(binary_data)
        head["E"] = E +1
        self.write_header(head)


        return E

    
    def find_by_position(self, position, id):
        tf = False
        record = None
        with open(self.filename, "rb") as f:
            while True:
                f.seek(self.header_size + (position) * self.record_size)
                binary_data = f.read(self.record_size)
                record = self.record.encoded_tuple_to_dict(binary_data)
                print(record)
                if record["id"] == id:
                    tf = True
                    break
                if record["next"] == -1:
                    break
                position = record["next"]

        return tf, record, position

    def read_block_by_position(self,  position):
        block = None
        with open(self.filename, "rb") as f:
            f.seek(self.header_size + (self.block_size  * position))
            block = self.read_block(f)

        return block

    def update_position(self, position_of_block, position):
        block = self.read_block_by_position(position_of_block)
        block[0]["next"] = position
        # print(block)
        with open(self.filename, "rb+") as f:
            f.seek(self.header_size + (self.block_size  * position_of_block))
            self.write_block(f, block)


    def adding_popup_record(self, position, record):
        head = self.read_header()
        E = head["E"]
        with open(self.filename, "rb+") as f:
            f.seek(self.header_size + self.record_size*E)
            record["next"] = position
            binary_data = self.record.dict_to_encoded_values(record)
            f.write(binary_data)
        head["E"] = E +1
        self.write_header(head)

        return E

    def searching(self, position, id):
        # tf = False
        before = None
        # after = None
        before_position = 0
        block = self.read_block_by_position(position)
        while True:
            # block = self.read_block_by_position(position)
            if block[0]["id"] == id and block[0]["status"] != -1:
                return True
            elif block[0]["id"] == id and block[0]["status"] == -1:
                return True, position
            elif id < block[0]["id"] :
                lista = [before, before_position]
                return lista
            else:
                before = block[0]
                if before["next"] != -1:
                    before_position = position
                    position = before["next"]
                    block = self.read_block_by_position(position)
                else:
                    lista = [before, before_position]
                    return lista
        


    def adding_element_first_time_with_next(self, record, next):
        head = self.read_header()
        E = head["E"]
        with open(self.filename, "rb+") as f:
            f.seek(self.header_size + self.record_size*E)
            record["next"] = next
            binary_data = self.record.dict_to_encoded_values(record)
            f.write(binary_data)
        head["E"] = E +1
        self.write_header(head)

        return E

    def dodavanje_logicki_obrisanog(self, record, position):
        old_record = self.read_block_by_position(position)[0]
        record["next"] = old_record["next"]
        block = [record]
        with open(self.filename, "rb+") as f:
            f.seek(self.header_size + self.record_size*position)
            self.write_block(f, block)

    def search_by_id(self, position, id):
        while True:
            block = self.read_block_by_position(position)
            if block[0]["id"] == id and block[0]["status"] != -1:
                return True, [block, position]
            if block[0]["next"] == -1:
                return False, None
            
            position = block[0]["next"]

    def update_block(self, position, block):
        with open(self.filename, "rb+") as f:
            f.seek(self.header_size + (self.block_size  * position))
            self.write_block(f, block)


    def print_file(self):
        i = 0
        with open(self.filename, "rb") as f:
            f.read(self.header_size)
            while True:
                block = self.read_block(f)
                
                if not block:
                    break

                i += 1
                print("Block {}".format(i))
                self.print_block(block)
