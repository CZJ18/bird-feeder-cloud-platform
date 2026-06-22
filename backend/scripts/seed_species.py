from __future__ import annotations

from app.models import SpeciesDict

SPECIES = [
    (0, "Black-winged Cuckoo Shrike", "黑翅雀鹎"),
    (1, "Dark Green White-eye", "暗绿绣眼鸟"),
    (2, "White-browed Laughingthrush", "白颊噪鹛"),
    (3, "Light-vented Bulbul", "白头鹎"),
    (4, "Silver Pheasant female", "白鹇（雌）"),
    (5, "Silver Pheasant male", "白鹇（雄）"),
    (6, "Scaly-breasted Munia", "斑文鸟"),
    (7, "Black-throated Bushtit", "银喉长尾山雀"),
    (8, "Red-billed Blue Magpie", "红嘴蓝鹊"),
    (9, "Yellow-bellied Tit", "黄腹山雀"),
    (10, "Yellow-browed Bunting", "黄眉鹀"),
    (11, "Grey-headed Black-faced Bunting", "灰头鹀"),
    (12, "Azure-winged Magpie", "灰喜鹊"),
    (13, "Eurasian Tree Sparrow", "树麻雀"),
    (14, "Blackbird", "乌鸫"),
    (15, "Magpie", "喜鹊"),
    (16, "Little Egret", "白鹭"),
    (17, "Vinous-throated Parrotbill", "红嘴相思鸟"),
]


async def seed_species() -> None:
    for class_id, species_en, species_cn in SPECIES:
        row = await SpeciesDict.get_or_none(class_id=class_id)
        if row:
            row.species_en = species_en
            row.species_cn = species_cn
            await row.save()
        else:
            await SpeciesDict.create(class_id=class_id, species_en=species_en, species_cn=species_cn)
