from piccolo.table import Table
from piccolo.columns import Varchar, Text

class CulturalSite(Table):
    name = Varchar(length=200)
    description = Text()
