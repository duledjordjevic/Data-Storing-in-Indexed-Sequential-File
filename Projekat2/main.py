import os
from sequential_file import SequentialFile
from serial_file import SerialFile
from record import Record
from primary_zone import PrimaryZone
from index_zone import IndexZone
from zona_prekoracenja import ZonaPrekoracenja
import datetime

ATTRIBUTI = ["id",  "registarska oznaka", "datum i vreme parkiranja", "oznaka parking mesta", "duzina boravka", "status"]
FORMAT = "i10s19s7sii"
CODING = "ascii"

FAKTOR_BLOKIRANJA = 5

ATTRIBUTI2 = ["position"]
FORMAT2 = "i"

ATRIBUTI_INDEX = ["key1", "position1", "key2", "position2"]
FORMAT_INDEX = "iiii"

ATRIBUTI_PREKORACENJA = ["id",  "registarska oznaka", "datum i vreme parkiranja", "oznaka parking mesta", "duzina boravka", "status", "next"]
FORMAT_PREKORACENJA = "i10s19s7siii"

def choice(file):
    option = 0
    while True:
        
        if file != None:
            print("\nTrenutna aktivna datoteka: " + "\033[1m" +file.filename.split("/")[1].split("_dp_ser")[0] + "\033[0;0m")
        else:
            print("\nTrenutna aktivna datoteka:  " + "\033[1m" +"None" + "\033[0;0m")
        print("Izaberite neku od punudjenih opcija:")
        print("1. Formiranje prazne datoteke")
        print("2. Izbor aktivne datoteke")
        print("3. Lista aktivnih datoteka")
        print("4. Unos slogova u serijsku datoteku")
        print("5. Formiranje sekvencijalne datoteke ")
        print("6. Formiranje aktivne datoteke ")
        print("7. Upis novog sloga u aktivnu datoteku ")
        print("8. Trazenje prozivoljnog sloga i prikaz njegovog bloka")
        print("9. Logicko brisanje aktuelnog sloga")
        print("10. Prikaz svih slogova aktivne datoteke")
        print("0. Izlaz")

        option = input(">>  ")
        try:
            option = int(option)
        except:
            print("Molim vas da izaberete neku od ponudjenih opcija! ")
        if option in range(0, 11):
            break
        print("Molim vas da izaberete neku od ponudjenih opcija! ")

    return option

def make_file():
    print("Unesite ime fajla:")
    file_name = input(">>  ")
    file_name = "podaci/" + file_name + "_ser.bin"

    if (os.path.exists(file_name) == False):
        f = open(file_name , "w")
        rec = Record(ATTRIBUTI, FORMAT, CODING)
        binary_file = SerialFile(file_name, rec, FAKTOR_BLOKIRANJA)
        binary_file.init_file()
        print("Uspesno ste kreirali novi fajl. Sada je aktivna datoteka")
        return binary_file
    else:
        print("Ovaj fajl vec postoji. Aktiviran je ovaj fajl.")
        rec = Record(ATTRIBUTI, FORMAT, CODING)

        binary_file = SerialFile(file_name, rec, FAKTOR_BLOKIRANJA)
        return binary_file


def prikaz_datoteka():
    lista = os.listdir("./podaci")
    if len(lista) != 0:
        for file in lista:
            if "_ser.bin" in file:
                print(file.split("_ser")[0])
    else:
        print("Nema ni jedne aktivne datoteke trenutno.")

def izbor_aktivne():
    print("Unesite naziv datoteke koju zelite koristiti:")
    name = input(">>  ")
    name = "podaci/" + name + "_ser.bin"
    if (os.path.exists(name) == True):
        print("Ova datoteka je sada aktivna")
        rec = Record(ATTRIBUTI, FORMAT, CODING)
        binary_file = SerialFile(name, rec, FAKTOR_BLOKIRANJA)
        return binary_file
    else:
        print("Uneli ste datoteku koja ne postoji")
        return None

def dodavanje_sloga():
    print("Upisite novi slog: ")
    record = None
    try:
        id = input("Unesite id >>  ")
        id = int(id)
        if id > 999999999  or id < 0:
            print("Uneli ste id van opsega!")
            return
        registarska_oznaka = input("Unesite registarsku oznaku >>  ")
        if len(registarska_oznaka) > 10:
            print("Registarska oznaka moze biti najvise 10 karaktera!")
            return
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        oznaka_parking_mesta = input("Unesite oznaku parking mesta >>  ")
        if len(oznaka_parking_mesta) != 7:
            print("Uneli ste oznaku parking mesta u losem formatu")
            return
        duzina_boravka = input("Unesite duzinu boravka u minutima >> ")
        duzina_boravka = int(duzina_boravka)
        if duzina_boravka > 999999999 or duzina_boravka < 0:
            print("Uneli ste duzinu boravka van opsega")
            return
    except:
        print("Pogresan unos!")
        return None

    record = {
        "id" : id,  
        "registarska oznaka": registarska_oznaka,
        "datum i vreme parkiranja" : date,
        "oznaka parking mesta": oznaka_parking_mesta,
        "duzina boravka": duzina_boravka,
        "status": 1
    }

    return record
def dodavanje_sloga_ser(file):
    
    record = dodavanje_sloga()
    if record != None:
        ret = file.insert_record(record)
        if ret:
            print("Uspesno ste uneli novi slog!")


def forimiranje_sek_dat(file):

    file_name = file.filename.replace("ser", "sek")
    f = open(file_name , "w")
    rec = Record(ATTRIBUTI, FORMAT, CODING)
    ser_file = SequentialFile(file_name, rec, FAKTOR_BLOKIRANJA)
    ser_file.init_file()

    lista = []
    with open(file.filename, "rb") as f:
        while True:
            block = file.read_block(f)
            if not block:
                break
            for slog in block:
                if slog["id"] == -1:
                    break
                lista.append(slog)

    lista1 = sorted(lista, key=lambda x: x["id"])
    for slog in lista1:
        ser_file.insert_record(slog)
    
    print("Uspesno ste formirali sekvencijalnu datoteku promene!")
    # ser_file.print_file()

def formiranje_primarne_zone(file):
    file_name = file.filename.replace("ser", "sek")
    f = open(file_name , "w")
    rec = Record(ATTRIBUTI, FORMAT, CODING)
    rec2 = Record(ATTRIBUTI2, FORMAT2, CODING)
    primary_file = PrimaryZone("podaci/aktivna_datoteka.bin", rec,rec2,  FAKTOR_BLOKIRANJA )
    # primary_file.init_file()

    lista = []
    with open(file.filename, "rb") as f:
        while True:
            block = file.read_block(f)
            if not block:
                break
            for slog in block:
                if slog["id"] == -1:
                    break
                lista.append(slog)

    lista1 = sorted(lista, key=lambda x: x["id"])
    primary_file.making_primary_zone(lista1)
    primary_file.print_file()
    
    rec_index = Record(ATRIBUTI_INDEX, FORMAT_INDEX, CODING)
    index_file = IndexZone("podaci/indeksna_datoteka.bin", rec_index, 2, 4, 999999999)
    tf = index_file.making_index_zone(lista1)
    # index_file.print_file()
    if tf:
        rec_zona_prekoracenja = Record(ATRIBUTI_PREKORACENJA, FORMAT_PREKORACENJA, CODING)
        zona_prekoracenja_file = ZonaPrekoracenja("podaci/zona_prekoracenja.bin", rec_zona_prekoracenja, 1)
        tf = zona_prekoracenja_file.making_zona_prekoracnja()
    
    if tf:
        print("\nUspesno ste formirali primarnu zonu!\n")

    return primary_file, index_file, zona_prekoracenja_file


def dodavanje_sloga_aktivna(file_aktivna):
    primary_file = file_aktivna[0]
    index_file = file_aktivna[1]
    zona_prekoracenja_file = file_aktivna[2]

    record = dodavanje_sloga()
   

    if record != None:
        id = record["id"]
        position = index_file.find_by_id(id)

        block = primary_file.read_block_by_position(position)

        tf = False
        is_new = True
        for rec in block:
            if "id" in rec.keys():
                if id < rec["id"]:
                    tf = True
                if rec["id"] == id and rec["status"] != -1:
                    return False
                elif rec["id"] == id and rec["status"] == -1:
                    is_new = False
        #upis u primarnu
        if tf:
            #dodavanje novog
            pop_up_record = None
            if is_new:
                is_last_block = False
                count = 0
                for i in block:
                    if "id" in i.keys():
                        if i["id"] == -1:
                            is_last_block = True
                            count += 1
                if not is_last_block:
                    new_block = block[:-1]
                    new_block.append(record)
                    lista1 = sorted(new_block, key=lambda x: x["id"])
                    pop_up_record = lista1.pop()
                    lista1.append(block[-1])
                    block = lista1
                else:
                    new_block = block[:-(count + 1)]
                    new_block.append(record)
                    lista1 = sorted(new_block, key=lambda x: x["id"])
                    pop_up_record = lista1.pop()
                    for i in range(count):
                        lista1.append(block[-2])
                    lista1.append(block[-1])
                    block = lista1
                    print(block)
                #prvi upis u zonu prekoracenja
                if block[-1]["position"] == -1:
                    E = zona_prekoracenja_file.adding_element_first_time(pop_up_record)
                    block[-1]["position"] = E
                    primary_file.update_block(position, block)
                # upis popup recorda u zonu prekoracenja
                else:
                    position_in_zona = block[-1]["position"]
                    E = zona_prekoracenja_file.adding_popup_record(position_in_zona, pop_up_record)
                    block[-1]["position"] = E
                    primary_file.update_block(position, block)
            #izmena logicki izbrisanog
            else:
                x = 0
                for i in range(len(block)-1):
                    if block[i]["id"] == id:
                        x = i
                block[x] = record
                primary_file.update_block(position, block)
            
        else:
            #upis u zonu prekoracenja
            if block[-1]["position"] == -1:
                E = zona_prekoracenja_file.adding_element_first_time(record)
                block[-1]["position"] = E
                primary_file.update_block(position, block)

            else:
                position_in_zona = block[-1]["position"]
                ret = zona_prekoracenja_file.searching(position_in_zona, id)
                # print(ret, "hello")
                if type(ret) is bool:
                    return False
                elif type(ret) is tuple:
                    #upis umesto logicki obrisanog
                    position = ret[1]
                    zona_prekoracenja_file.dodavanje_logicki_obrisanog(record, position)

                else:
                    if ret[0] == None:
                        E = zona_prekoracenja_file.adding_element_first_time_with_next(record, position_in_zona)
                        block[-1]["position"] = E
                        primary_file.update_block(position, block)
                    else:
                        # ret == before
                        before = ret[0]
                        position_in_zona = ret[1]
                        E = zona_prekoracenja_file.adding_element_first_time_with_next(record, before["next"])
                        zona_prekoracenja_file.update_position(position_in_zona, E)


        print("Uspesno ste dodali slog!")
        primary_file.print_file()
        zona_prekoracenja_file.print_file()
       
        
def search_by_id(file_aktivna, id):
    primary_file = file_aktivna[0]
    index_file = file_aktivna[1]
    zona_prekoracenja_file = file_aktivna[2]

    position = index_file.find_by_id(id)

    block = primary_file.read_block_by_position(position)

    is_in_primary = False
    found = False
    for rec in block:
        if "id" in rec.keys():
            if id < rec["id"]:
                is_in_primary = True
            if rec["id"] == id and rec["status"] != -1:
                found = True

    if found:
        return block, position
    
    if is_in_primary:
        return False
    
    if block[-1]["position"] == -1:
        return False
    else:
        position = block[-1]["position"]
        tf, lista = zona_prekoracenja_file.search_by_id(position, id)
        if tf:
            return lista[0], lista[1]
        else:
            return False

def logicko_brisanje(file_aktivna, id):
    primary_file = file_aktivna[0]
    index_file = file_aktivna[1]
    zona_prekoracenja_file = file_aktivna[2]

    ret = search_by_id(file_aktivna, id)
    if isinstance(ret, bool):
        print("Nismo pronasli slog sa tim ID")
        return
    else:
        block = ret[0]
        position = ret[1]

        if len(block) == 1:
            block[0]["status"] = -1
            zona_prekoracenja_file.update_block(position, block)
            
        else:
            index = 0
            for i in range(len(block)):
                if block[i]["id"] == id:
                    index = i
                    break
            block[index]["status"] = -1
            primary_file.update_block(position, block)

        print("Uspesno ste obrisali slog!")


def main():
    print("Dobrodosli!")
    file_ser = None
    file_aktivna = None
    option = choice(file_ser)
    while option != 0:
        if option == 1:
            file_ser = make_file()
        elif option == 2:
            file_ser = izbor_aktivne()
        elif option == 3:
            prikaz_datoteka()
        elif option == 4:
            if file_ser != None:
                while True:
                    dodavanje_sloga_ser(file_ser)
                    x = None
                    while True:
                        print("Da li zelite da nastavite sa dodavanjem?(da ili ne)")
                        x = input(">>  ")
                        if x.strip().lower() == "da" or x.strip().lower() == "ne":
                            break
                    if x != "da":
                        break
            else:
                print("Morate izabrati aktivnu datoteku!")

        elif option == 5:
            if file_ser != None:
                forimiranje_sek_dat(file_ser)
            else:
                print("Morate izabrati aktivnu datoteku!")
        elif option == 6:
            if file_ser != None:
                file_aktivna = formiranje_primarne_zone(file_ser)
            else:
                print("Morate izabrati aktivnu datoteku!")
        elif option == 7:
            if file_aktivna != None:
                ret = dodavanje_sloga_aktivna(file_aktivna)
                if ret == False:
                    print("Slog sa takvim ID vec postoji!")
            else:
                print("Morate izabrati aktivnu datoteku!")
        elif option == 8:
            if file_aktivna != None:
                print("Unesite ID")
                id = input(">>  ")
                if id.isdigit() == True:
                    id = int(id)
                    if id > 0 and id < 999999999:
                        ret = search_by_id(file_aktivna, id)
                        if isinstance(ret, bool):
                            print("Nismo pronasli slog sa tim ID")
                        else:
                            block = ret[0]
                            position = ret[1]

                            print("Blok " + str(position + 1))
                            for i in block:
                                print(i)
                    else:
                        print("Uneti id mora biti u opsegu!")
                else:
                    print("Morate uneti broj!")
            else:
                print("Morate izabrati aktivnu datoteku!")

        elif option == 9:
            if file_aktivna != None:
                print("Unesite ID")
                id = input(">>  ")
                if id.isdigit() == True:
                    id = int(id)
                    if id > 0 and id < 999999999:
                        logicko_brisanje(file_aktivna, id)
                    else:
                        print("Uneti id mora biti u opsegu!")
                else:
                    print("Morate uneti broj!")
                
            else:
                print("Morate izabrati aktivnu datoteku!")
        elif option == 10:
            if file_aktivna != None:
                primary_file = file_aktivna[0]
                zona_prekoracenja_file = file_aktivna[2]

                print("\nPrimarna zona: \n")
                primary_file.print_file()
                print("\nZona prekoracenja: \n")
                zona_prekoracenja_file.print_file()
            else:
                print("Morate izabrati aktivnu datoteku!")
        option = choice(file_ser)


    print("Izlaz iz programa")
main()

# rec = Record(ATTRIBUTI, FORMAT, CODING)
# binary_file = SerialFile("podaci/test_ser.bin", rec, FAKTOR_BLOKIRANJA)

# binary_file.print_file()