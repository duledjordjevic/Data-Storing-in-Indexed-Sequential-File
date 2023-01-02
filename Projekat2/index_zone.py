import os
import struct
from binary_file import BinaryFile
from record import Record
import math 

class IndexZone(BinaryFile):
    def __init__(self, filename, record,  blocking_factor, primary_blocking_factor,max_value,  empty_key=-1):
        BinaryFile.__init__(self, filename, record, blocking_factor, empty_key)
        self.header = Record(["B", "h", "C"], 'iii', "ascii")
        self.header_size = struct.calcsize(self.header.format)
        self.primary_blocking_factor = primary_blocking_factor
        self.max_value = max_value

    def init_file(self):
        with open(self.filename, "wb") as f:
            binary_data = self.header.dict_to_encoded_values({"B": 0, "h": 0, "C" : 0})
            f.write(binary_data)

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

    
    def making_index_zone(self, sorted_list):
        
        B = math.ceil(len(sorted_list) / self.primary_blocking_factor)
        h = math.ceil(math.log(B, self.blocking_factor))
        C = 0
        for i in range(1, h+1):
            C += math.ceil(B/(self.blocking_factor**(h-i+1)))
        head = {"B" : B, "h" : h, "C": C}
        Ch = math.ceil(B/(self.blocking_factor))
        leaves = []
        with open(self.filename, "wb") as f:
            binary_data = self.header.dict_to_encoded_values(head)
            f.write(binary_data)
            
            leaf = {"key1": 0, "position1" : 0, "key2" : 0, "position2" : 0}
            key1 = 0
            key2 = 0
            position1 = 0
            position2 = 0
            for i in range(B):
                if B % 2 == 0:
                    if i % 2 == 0:
                        key1 = sorted_list[(i+1)*(self.primary_blocking_factor) -1]["id"]
                        position1 = i
                    elif i % 2 != 0 and i != B - 1:
                        key2 = sorted_list[(i+1)*(self.primary_blocking_factor) - 1]["id"]
                        position2 = i
                        leaf = {"key1": key1, "position1" : position1, "key2" : key2, "position2" : position2}
                        binary_data = self.record.dict_to_encoded_values(leaf)
                        leaves.append(leaf)
                        f.write(binary_data)
                    elif i % 2 != 0 and i == B - 1:
                        key2 = self.max_value
                        position2 = i
                        leaf = {"key1": key1, "position1" : position1, "key2" : key2, "position2" : position2}
                        binary_data = self.record.dict_to_encoded_values(leaf)
                        leaves.append(leaf)
                        f.write(binary_data)
                else:
                    if i % 2 == 0 and i != B-1:
                        key1 = sorted_list[(i+1)*(self.primary_blocking_factor) -1]["id"]
                        position1 = i
                    elif i % 2 != 0 and i != B - 1:
                        key2 = sorted_list[(i+1)*(self.primary_blocking_factor) - 1]["id"]
                        position2 = i
                        leaf = {"key1": key1, "position1" : position1, "key2" : key2, "position2" : position2}
                        binary_data = self.record.dict_to_encoded_values(leaf)
                        leaves.append(leaf)
                        
                        f.write(binary_data)
                    elif i % 2 == 0 and i == B - 1:
                        key1 = self.max_value
                        position1 = i
                        leaf = {"key1": key1, "position1" : position1, "key2" : -1, "position2" : -1}
                        binary_data = self.record.dict_to_encoded_values(leaf)
                        leaves.append(leaf)
                        
                        f.write(binary_data)

                    

            # i = 0
            # print(Ch)
            original_leaves = leaves
            next_leaves = []
            # print(leaves)
            while True:

                
                if len(leaves) != 1:
                    if len(leaves) % 2 == 0:
                        for i in range(0, len(leaves), 2):
                            leaf1 = leaves[i]
                            leaf2 = leaves[i+1]
                            leaf = None
                            if leaf2["key2"] != -1:
                                leaf = {"key1": leaf1["key2"], "position1" : i, "key2" : leaf2["key2"], "position2" : i+1}
                                next_leaves.append(leaf)
                            else:
                                leaf = {"key1": leaf1["key2"], "position1" : i, "key2" : leaf2["key1"], "position2" : i+1}
                                next_leaves.append(leaf)
                       
                            binary_data = self.record.dict_to_encoded_values(leaf)
                            f.write(binary_data)

                    else:
                        for i in range(0, len(leaves)-1, 2):
                            leaf1 = leaves[i]
                            leaf2 = leaves[i+1]
                            leaf = None
                            # if leaf1["key2"] < leaf2["key2"]:
                            #     leaf = {"key1": leaf1["key2"], "position1" : leaf1["position1"], "key2" : leaf2["key2"], "position2" : leaf2["position1"]}
                            #     next_leaves.append(leaf)
                            # else:
                            #     leaf = {"key1": leaf2["key2"], "position1" : leaf2["position1"], "key2" : leaf1["key2"], "position2" : leaf1["position1"]} 
                            #     next_leaves.append(leaf)
                            if leaf2["key2"] != -1:
                                leaf = {"key1": leaf1["key2"], "position1" : i, "key2" : leaf2["key2"], "position2" : i+1}
                                next_leaves.append(leaf)
                            else:
                                leaf = {"key1": leaf1["key2"], "position1" : i, "key2" : leaf2["key1"], "position2" : i+1}
                                next_leaves.append(leaf)
                            binary_data = self.record.dict_to_encoded_values(leaf)
                            f.write(binary_data)

                        leaf = leaves[-1]
                        leaf["position1"] = len(leaves) - 1
                        next_leaves.append(leaf)  
                        binary_data = self.record.dict_to_encoded_values(leaf)
                        f.write(binary_data)
                        
                else:
                    # if len(original_leaves) != 1:
                    #     binary_data = self.record.dict_to_encoded_values(leaves[0])
                    #     f.write(binary_data)
                    break

                # print(next_leaves)
                leaves = next_leaves
                next_leaves = []
        return True

                
    def find_by_id(self, id):
        header = self.read_header()
        C = header["C"]
        B = header["B"]
        h = header["h"]
        ret_primary_position = 0
        leaf = None
        with open(self.filename, "rb") as f:
            position = 0
            old_c = 0
            for i in range(h):
                if i == 0:
                    f.seek(self.header_size + self.record_size*(C-1))
                    binary_data = f.read(self.record_size)
                    
                    leaf = self.record.encoded_tuple_to_dict(binary_data)
                    # print(leaf)
                    if id <= leaf["key1"]:
                        position = leaf["position1"]
                    else:
                        position = leaf["position2"]
                    old_c += 1

                else:
                    Ch = math.ceil(B/(self.blocking_factor**(h-i)))
                    f.seek(self.header_size + self.record_size * (C-old_c - (Ch - position)) )
                    binary_data = f.read(self.record_size)
                    
                    leaf = self.record.encoded_tuple_to_dict(binary_data)
                    # print(leaf, "Hello")
                    if id <= leaf["key1"]:
                        position = leaf["position1"]
                    else:
                        position = leaf["position2"]
                    old_c += Ch
            if id <= leaf["key1"]:
                ret_primary_position = leaf["position1"]
            else:
                ret_primary_position = leaf["position2"]
            
        
        return ret_primary_position

            

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





            

            


