# SDK Pullenti Address, version 4.14, september 2022. Copyright (c) 2013, Pullenti. All rights reserved.
# Non-Commercial Freeware and Commercial Software.
# This class is generated using the converter Unisharping (www.unisharping.ru) from Pullenti C# project.
# The latest version of the code is available on the site www.pullenti.ru

import typing
import pathlib
from pullenti.unisharp.Utils import Utils

from pullenti.address.SearchParams import SearchParams
from pullenti.address.AddressService import AddressService

class Program:
    
    @staticmethod
    def main(args : typing.List[str]) -> None:
        # Можно работать через сервер, тогда инициалиация не нужна
        if (AddressService.set_server_connection("http://localhost:2222")): 
            server_version = AddressService.get_server_version("http://localhost:2222")
            print("Server version: {0}".format(Utils.ifNotNull(server_version, "?")), flush=True)
        else: 
            # Обязательная инициализация один раз перед использованием SDK
            print("Initialize SDK Pullenti Address v.{0} ... ".format(AddressService.VERSION), end="", flush=True)
            AddressService.initialize()
            print("OK", flush=True)
            # Указание SDK папки с индексом ГАР
            gar_path = "Gar77"
            if (not pathlib.Path(gar_path).is_dir()): 
                print("Gar path {0} not exists".format(gar_path), flush=True)
                return
            if (not AddressService.set_gar_index_path(gar_path)): 
                print("Gar path {0} - bad index".format(gar_path), flush=True)
                return
        info = AddressService.get_gar_statistic()
        if (info is not None): 
            print(str(info), flush=True)
        # установим по умолчанию город (если явно не указан, то будет использован этот)
        AddressService.set_default_geo_object("Москва")
        print("Root Gar Objects:", flush=True)
        # посмотрим объекты 1-го уровня (в демо-варианте только Москва)
        root_gars = AddressService.get_objects(None, False)
        if (root_gars is not None): 
            for go1 in root_gars: 
                # а вот так можно получить дочерние объекты (по Id родителя)
                children = AddressService.get_objects(go1.id0_, False)
                print("{0} ({1} children)".format(str(go1), (0 if children is None else len(children))), flush=True)
        # поищем по именам
        sp = SearchParams()
        sp.street = "советск"
        sp.max_count = 100
        print("\nSearch {0} ...".format(sp), end="", flush=True)
        sr = AddressService.search_objects(sp)
        if (sr is not None): 
            print(" found {0} object(s)".format(len(sr.objects)), end="", flush=True)
            for o in sr.objects: 
                print("\n{0} ({1})".format(str(o), o.guid), end="", flush=True)
                parent = AddressService.get_object(o.parent_id)
                if (parent is not None): 
                    print(" - {0}".format(str(parent)), end="", flush=True)
        else: 
            print("Fatal search error", flush=True)
        # анализ текстовых фрагментов с адресами
        text = "адрес 16 парковая улица, дом номер два квартира 3 в которой проживает кое-кто"
        print("\n\nAnalyze text: {0}".format(text), flush=True)
        addrs = AddressService.process_text(text)
        if (addrs is not None): 
            for addr in addrs: 
                print("Address: {0}".format(addr.get_full_path(", ")), flush=True)
                # детализируем элементы адреса
                for item in addr.items: 
                    print("  {0}: {1}".format(Utils.enumToString(item.attrs.level), str(item)), flush=True)
                    if (len(item.gars) > 0): 
                        # привязанных объектов ГАР в принципе может быть несколько
                        for gar in item.gars: 
                            print("   Gar: {0} ({1})".format(str(gar), gar.guid), flush=True)
        # а вот анализ текста, который содержит ТОЛЬКО АДРЕС, и ничего более (поле ввода адреса, например)
        # text = "Москва, ул. 16-я Парковая д.2 кв.3 и какой-то мусор"
        # text = "ул. Михневская, д. 8, Москва"
        text = "115547, г Москва, Бирюлево Восточное р-н, ул Михневская, д 8"
        saddr = AddressService.process_single_address_text(text)
        print("\nAnalyze single address: {0}".format(text), flush=True)
        if (saddr is None): 
            print("Fatal process error", flush=True)
        else:
            print("Coefficient: {0}".format(saddr.coef), flush=True)
            if (saddr.error_message is not None): 
                print("Message: {0}".format(saddr.error_message), flush=True)
            for item in saddr.items: 
                print("Item: {0}".format(str(item)), end="", flush=True)
                if (len(item.gars) > 0): 
                    for gar in item.gars: 
                        print(" (Gar: {0}, GUID={1})".format(str(gar), gar.guid), end="", flush=True)
                print("", flush=True)
        print("Bye!", flush=True)

if __name__ == "__main__":
    Program.main(None)
