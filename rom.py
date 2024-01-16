import Utils
import bsdiff4
from Utils import read_snes_rom, __version__
from worlds.Files import APDeltaPatch

USHASH = 'd69b2115e17d1cf2cb3590d3f75febb9'
ROM_PLAYER_LIMIT = 65535

import hashlib
import os





class LocalRom(object):

    def __init__(self, file, patch=True, vanillaRom=None, name=None, hash=None):
        self.original_file = file
        self.name = name
        self.hash = hash
        self.orig_buffer = None

        with open(file, 'rb') as stream:
            self.buffer = read_snes_rom(stream)
                
        with open(file, 'rb') as file:
            self.rom_data = file.read()
        
    def read_bit(self, address: int, bit_number: int) -> bool:
        bitflag = (1 << bit_number)
        return ((self.buffer[address] & bitflag) != 0)

    def read_byte(self, address: int) -> int:
        return self.buffer[address]

    def read_bytes(self, startaddress: int, length: int) -> bytes:
        return self.buffer[startaddress:startaddress + length]

    def write_byte(self, address: int, value: int):
        self.buffer[address] = value

    def write_bytes(self, startaddress: int, values):
        self.buffer[startaddress:startaddress + len(values)] = values

    def write_to_file(self, file):
        with open(file, 'wb') as outfile:
            outfile.write(self.buffer)

    def write_rom_data_to_file(self, file):
        with open(file, 'wb') as outfile:
            outfile.write(self.rom_data)

    def read_from_file(self, file):
        with open(file, 'rb') as stream:
            self.buffer = bytearray(stream.read())
            
            
    def write_randomizer_asm_to_file(self, basepatch_to_use, temp_patch_path, rompath):
        with open(basepatch_to_use, "rb") as f:
            delta: bytes = f.read()
        self.rom_data = bsdiff4.patch(self.rom_data, delta)
        self.write_rom_data_to_file(rompath)
        self.read_from_file(self.original_file)

        # the following code is taking a .asm file meant to be used with asar
        # and instead manually updates all of the bytes
        
        with open(temp_patch_path,'r') as f:
            data = f.readlines()

        master = {}
        new_loc = 0
        for line in data:
            line = line.split(";")[0]
            if "org" not in line and "db" not in line:
                continue
            
            if "org" in line:
                new_loc = int(line.split("$")[1],base=16) - 12582912
                continue
            if "db" in line:
                each_byte = line.split(" ")[1:]
                each_byte = [i.replace(",","").replace("$","").strip() for i in each_byte if i]
                for b in each_byte:
                    if b:
                        master[new_loc] = int(b, base=16)
                        new_loc += 1
                    
                    
        
        for idx, b in master.items():
            self.buffer[idx] = b

        # dragon
        new_loc = int('C33320', base=16) - 12582912
        self.buffer[new_loc] = 0
        self.buffer[new_loc + 1] = 1
        self.buffer[new_loc + 2] = 0
        self.buffer[new_loc + 3] = 0
        
        b = data[-6].split("dw ")[1].split("\n")[0].replace("$","")
        b1 = b[:2]
        b2 = b[2:]


        
        for i in range(15):
            self.buffer[new_loc + 4 + i * 2] = int(b2,base=16)
            self.buffer[new_loc + 4 + i * 2 + 1] = int(b1,base=16)



def patch_rom(world, rom, player):
    rom.name = bytearray(f'K7{__version__.replace(".", "")[0:3]}_{player}_{world.seed:11}\0', 'utf8')[:21]
    rom.name.extend([0] * (21 - len(rom.name)))
    rom.write_bytes(0x7FC0, rom.name)
    
    
class FFVCDDeltaPatch(APDeltaPatch):
    hash = USHASH
    game = "Final Fantasy V Career Day"
    patch_file_ending = ".apffvcd"

    @classmethod
    def get_source_data(cls) -> bytes:
        return get_base_rom_bytes()


def get_base_rom_bytes(file_name: str = "") -> bytes:
    base_rom_bytes = getattr(get_base_rom_bytes, "base_rom_bytes", None)
    if not base_rom_bytes:
        file_name = get_base_rom_path(file_name)
        base_rom_bytes = bytes(read_snes_rom(open(file_name, "rb")))

        basemd5 = hashlib.md5()
        basemd5.update(base_rom_bytes)
        if USHASH != basemd5.hexdigest():
            print("\nSupplied Base Rom does not match known MD5 for J(1.0) with RPGe patch applied.\n")
            raise Exception('Supplied Base Rom does not match known MD5 for J(1.0) with RPGe patch applied.')
        get_base_rom_bytes.base_rom_bytes = base_rom_bytes
    return base_rom_bytes

def get_base_rom_path(file_name: str = "") -> str:
    options = Utils.get_options()
    if not file_name:
        file_name = options["ffvcd_options"]["rom_file"]
    if not os.path.exists(file_name):
        file_name = Utils.user_path(file_name)
    return file_name





crystal_ram_data = {100:["80",0x840],
                    101:["40",0x840],
                    102:["20",0x840],
                    103:["10",0x840],
                    104:["08",0x840],
                    105:["04",0x840],
                    106:["02",0x840],
                    107:["01",0x840],
                    108:["80",0x841],
                    109:["40",0x841],
                    110:["20",0x841],
                    111:["10",0x841],
                    112:["08",0x841],
                    113:["04",0x841],
                    114:["02",0x841],
                    115:["01",0x841],
                    116:["80",0x842],
                    117:["40",0x842],
                    118:["20",0x842],
                    119:["10",0x842],
                    120:["08",0x842],
                    121:["04",0x842]}


magic_ram_data = {201:["40", 0x950],
                    202:["20", 0x950],
                    203:["10", 0x950],
                    204:["08", 0x950],
                    205:["04", 0x950],
                    206:["02", 0x950],
                    207:["01", 0x950],
                    208:["80", 0x951],
                    209:["40", 0x951],
                    210:["20", 0x951],
                    211:["10", 0x951],
                    212:["08", 0x951],
                    213:["04", 0x951],
                    214:["02", 0x951],
                    215:["01", 0x951],
                    216:["80", 0x952],
                    217:["40", 0x952],
                    218:["20", 0x952],
                    219:["10", 0x952],
                    220:["08", 0x952],
                    221:["04", 0x952],
                    222:["02", 0x952],
                    223:["01", 0x952],
                    224:["80", 0x953],
                    225:["40", 0x953],
                    226:["20", 0x953],
                    227:["10", 0x953],
                    228:["08", 0x953],
                    229:["04", 0x953],
                    230:["02", 0x953],
                    231:["01", 0x953],
                    232:["80", 0x954],
                    233:["40", 0x954],
                    234:["20", 0x954],
                    235:["10", 0x954],
                    236:["08", 0x954],
                    237:["04", 0x954],
                    238:["02", 0x954],
                    239:["01", 0x954],
                    240:["80", 0x955],
                    241:["40", 0x955],
                    242:["20", 0x955],
                    243:["10", 0x955],
                    244:["08", 0x955],
                    245:["04", 0x955],
                    246:["02", 0x955],
                    247:["01", 0x955],
                    248:["80", 0x956],
                    249:["40", 0x956],
                    250:["20", 0x956],
                    251:["10", 0x956],
                    252:["08", 0x956],
                    253:["04", 0x956],
                    255:["01", 0x956],
                    256:["80", 0x957],
                    257:["40", 0x957],
                    258:["20", 0x957],
                    259:["10", 0x957],
                    260:["08", 0x957],
                    261:["04", 0x957],
                    263:["01", 0x957],
                    264:["80", 0x958],
                    265:["40", 0x958],
                    266:["20", 0x958],
                    267:["10", 0x958],
                    268:["08", 0x958],
                    269:["04", 0x958],
                    270:["02", 0x958],
                    271:["01", 0x958],
                    272:["80", 0x959],
                    273:["40", 0x959],
                    274:["20", 0x959],
                    275:["10", 0x959],
                    276:["08", 0x959],
                    277:["04", 0x959],
                    278:["02", 0x959],
                    279:["01", 0x959],
                    280:["80", 0x95A],
                    281:["40", 0x95A],
                    282:["20", 0x95A],
                    283:["10", 0x95A],
                    284:["08", 0x95A],
                    285:["04", 0x95A],
                    286:["02", 0x95A],
                    287:["01", 0x95A],
                    288:["80", 0x95B],
                    289:["40", 0x95B],
                    290:["20", 0x95B],
                    291:["10", 0x95B],
                    292:["08", 0x95B],
                    293:["04", 0x95B],
                    294:["02", 0x95B],
                    295:["20", 0x960],
                    296:["10", 0x960],
                    297:["08", 0x960],
                    298:["04", 0x960],
                    299:["02", 0x960],
                    300:["01", 0x960],
                    301:["80", 0x961],
                    302:["40", 0x961],
                    303:["20", 0x961],
                    304:["10", 0x961],
                    305:["08", 0x961],
                    306:["04", 0x961],
                    307:["02", 0x961],
                    308:["01", 0x961],
                    309:["80", 0x962],
                    310:["40", 0x962],
                    311:["20", 0x962],
                    312:["10", 0x962],
                    313:["08", 0x962],
                    314:["04", 0x962],
                    315:["02", 0x962],
                    316:["01", 0x962],
                    317:["80", 0x963],
                    318:["40", 0x963],
                    319:["20", 0x963],
                    320:["10", 0x963],
                    321:["08", 0x963],
                    322:["04", 0x963],
                    323:["02", 0x963],
                    324:["01", 0x963]}

ability_ram_data = {400:["02",0x8F7],
                    401:["01",0x8F7],
                    402:["80",0x8F8],
                    403:["40",0x8F8],
                    404:["20",0x8F8],
                    405:["10",0x8F8],
                    406:["08",0x8F8],
                    407:["04",0x8F8],
                    408:["02",0x8F8],
                    409:["01",0x8F8],
                    410:["80",0x8F9],
                    411:["40",0x8F9],
                    412:["20",0x8F9],
                    413:["10",0x8F9],
                    414:["08",0x8F9],
                    415:["04",0x8F9],
                    416:["02",0x8F9],
                    417:["01",0x8F9],
                    418:["80",0x8FA],
                    419:["40",0x8FA],
                    420:["20",0x8FA],
                    421:["10",0x8FA],
                    422:["08",0x8FA],
                    423:["02",0x8FA],
                    424:["01",0x8FA],
                    425:["80",0x8FB],
                    426:["40",0x8FB],
                    427:["20",0x8FB],
                    428:["08",0x8FB],
                    429:["01",0x8FB],
                    430:["80",0x8FC],
                    431:["40",0x8FC],
                    432:["20",0x8FC],
                    433:["80",0x8FD],
                    434:["40",0x8FD],
                    435:["20",0x8FD],
                    436:["10",0x8FD],
                    437:["08",0x8FD],
                    438:["04",0x8FD],
                    439:["80",0x8FE],
                    440:["40",0x8FE],
                    441:["20",0x8FE],
                    442:["10",0x8FE],
                    443:["08",0x8FE],
                    444:["04",0x8FE],
                    445:["80",0x8FF],
                    446:["40",0x8FF],
                    447:["20",0x8FF],
                    448:["10",0x8FF],
                    449:["08",0x8FF],
                    450:["04",0x8FF],
                    451:["80",0x900],
                    452:["40",0x900],
                    453:["20",0x900],
                    454:["10",0x900],
                    455:["08",0x900],
                    456:["04",0x900],
                    457:["80",0x901],
                    458:["40",0x901],
                    459:["20",0x901],
                    460:["10",0x901],
                    461:["08",0x901],
                    462:["80",0x902],
                    463:["40",0x902],
                    464:["20",0x902],
                    465:["80",0x903],
                    466:["40",0x903],
                    467:["80",0x904],
                    468:["40",0x904],
                    469:["20",0x904],
                    470:["10",0x904],
                    471:["08",0x904],
                    472:["04",0x904],
                    473:["02",0x904],
                    474:["01",0x904],
                    475:["80",0x905],
                    476:["40",0x905],
                    477:["20",0x905],
                    478:["10",0x905],
                    479:["08",0x905],
                    480:["04",0x905],
                    481:["02",0x905],
                    482:["01",0x905],
                    483:["80",0x906],
                    484:["40",0x906],
                    485:["20",0x906],
                    486:["10",0x906],
                    487:["08",0x906],
                    488:["04",0x906],
                    489:["02",0x906],
                    490:["80",0x907],
                    491:["40",0x907],
                    492:["20",0x907],
                    493:["10",0x907],
                    494:["04",0x907],
                    495:["01",0x907]}


item_ram_data = {600:"02",
                601:"03",
                602:"04",
                603:"05",
                604:"06",
                605:"07",
                606:"08",
                607:"09",
                608:"0A",
                609:"0B",
                610:"0C",
                611:"0D",
                612:"0E",
                613:"0F",
                614:"10",
                615:"11",
                616:"12",
                617:"13",
                618:"14",
                619:"15",
                620:"16",
                621:"17",
                622:"18",
                623:"19",
                624:"1A",
                625:"1B",
                626:"1C",
                627:"1D",
                628:"1E",
                629:"1F",
                630:"20",
                631:"21",
                632:"22",
                633:"23",
                634:"24",
                635:"25",
                636:"26",
                637:"27",
                638:"28",
                639:"29",
                640:"2A",
                641:"2B",
                642:"2C",
                643:"2D",
                644:"2E",
                645:"2F",
                646:"30",
                647:"31",
                648:"32",
                649:"33",
                650:"34",
                651:"35",
                652:"36",
                653:"37",
                654:"38",
                655:"39",
                656:"3A",
                657:"3B",
                658:"3C",
                659:"3D",
                660:"3E",
                661:"3F",
                662:"40",
                663:"41",
                664:"42",
                665:"43",
                666:"44",
                667:"45",
                668:"46",
                669:"47",
                670:"48",
                671:"49",
                672:"4A",
                673:"4B",
                674:"4C",
                675:"4D",
                676:"4E",
                677:"4F",
                678:"50",
                679:"51",
                680:"52",
                681:"53",
                682:"55",
                683:"56",
                684:"57",
                685:"58",
                686:"59",
                687:"5A",
                688:"5B",
                689:"5C",
                690:"5D",
                691:"5E",
                692:"5F",
                693:"60",
                694:"61",
                695:"62",
                696:"63",
                697:"64",
                698:"65",
                699:"66",
                700:"67",
                701:"68",
                702:"69",
                703:"6A",
                704:"6B",
                705:"6C",
                706:"6D",
                707:"6E",
                708:"81",
                709:"82",
                710:"83",
                711:"84",
                712:"85",
                713:"86",
                714:"87",
                715:"88",
                716:"89",
                717:"8A",
                718:"8B",
                719:"8C",
                720:"8D",
                721:"8E",
                722:"8F",
                723:"90",
                724:"91",
                725:"92",
                726:"93",
                727:"94",
                728:"95",
                729:"96",
                730:"97",
                731:"98",
                732:"99",
                733:"9A",
                734:"9B",
                735:"9C",
                736:"9D",
                737:"9E",
                738:"9F",
                739:"A0",
                740:"A1",
                741:"A2",
                742:"A3",
                743:"A4",
                744:"A5",
                745:"A6",
                746:"A7",
                747:"A8",
                748:"A9",
                749:"AA",
                750:"AB",
                751:"AC",
                752:"AD",
                753:"AE",
                754:"AF",
                755:"B0",
                756:"B1",
                757:"B2",
                758:"B3",
                759:"B4",
                760:"B5",
                761:"B6",
                762:"B7",
                763:"B8",
                764:"B9",
                765:"BA",
                766:"BB",
                767:"BC",
                768:"BD",
                769:"BE",
                770:"BF",
                771:"C0",
                772:"C1",
                773:"C2",
                774:"C3",
                775:"C4",
                776:"C5",
                777:"C6",
                778:"C7",
                779:"C8",
                780:"C9",
                781:"CA",
                782:"CB",
                783:"CC",
                784:"CD",
                785:"CE",
                786:"CF",
                787:"D0",
                788:"E0",
                789:"E1",
                790:"E2",
                791:"E3",
                792:"E4",
                793:"E5",
                794:"E6",
                795:"E7",
                796:"E8",
                797:"E9",
                798:"EA",
                799:"EB",
                800:"EC",
                801:"ED",
                802:"EF",
                803:"F0",
                804:"F1",
                805:"F2",
                806:"F3",
                807:"F4",
                808:"F5",
                809:"F6",
                810:"F9",
                811:"FA",
                812:"FB",
                813:"FC",
                814:"FD",
                815:"FE"}

gil_ram_data = {900 : 100,
                901 : 300,
                902 : 1000,
                903 : 5000,
                904 : 9900,
                905 : 8000,
                906 : 4400,
                907 : 10000,
                908 : 5000,
                909 : 8000,
                910 : 5000,
                911 : 9000,
                912 : 18000,
                913 : 2500,
                914 : 4900,
                915 : 9500,
                916 : 9000,
                917 : 8000,
                918 : 10000,
                919 : 12000,
                920 : 12000,
                921 : 9000,
                922 : 12000,
                923 : 5000,
                924 : 15000,
                925 : 20000,
                926 : 25000,
                }

key_item_ram_data = {1000	: [['80', 0x4A, 'ON'], ['20', 0x67, 'OFF'], ['01', 0x68, 'ON']],
                1001	: [['40', 0x4A, 'ON']],
                1002	: [['20', 0x4A, 'ON'], ['03', 0x39, 'ON'],],
                1003	: [['10', 0x4A, 'ON'],['08', 0x1B, 'ON'],],
                1004	: [['08', 0x4A, 'ON']],
                1005	: [['04', 0x4A, 'ON'],['2C', 0xE5, ''],['00', 0xE6, ''],['AC', 0xE7, ''],['A5', 0xE8, ''],],
                1006	: [['02', 0x4A, 'ON'],['30', 0xE9, ''],['00', 0xEA, ''],['AD', 0xEB, ''],['A5', 0xEC, ''],],
                1007	: [['01', 0x4A, 'ON'],['40', 0x1F, 'OFF'],],
                1008	: [['80', 0x4B, 'ON'],['20', 0x3C, 'ON'],],
                1009	: [['10', 0x4B, 'ON']],
                1010	: [['08', 0x4B, 'ON']],
                1011	: [['04', 0x4B, 'ON']],
                1012	: [['02', 0x4B, 'ON']],
                1013	: [['20', 0x4C, 'ON']],
                1014	: [['04', 0x4C, 'ON'],['04', 0x53, 'ON'],['01', 0xAF, 'ON'],],
                1015	: [['02', 0x4C, 'ON'],['10', 0x39, 'ON'],],
                1016	: [['80', 0x4D, 'ON'],['02', 0x22, 'ON'],],
                1017	: [['20', 0x4D, 'ON'],['08', 0x24, 'ON'],],
                1018	: [['10', 0x4D, 'ON'],['40', 0x25, 'ON'],],
                1019	: [['08', 0x4D, 'ON'],['02', 0x26, 'ON'],],
                1020	: [['04', 0x4D, 'ON'],['08', 0x26, 'ON'],],
                }