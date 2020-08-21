from enum import Enum
from LDF_Client import ClientTab
from LDF_HomeInfo import HomeInfoTab
from LDF_Device import DeviceTab
from LDF_Install import InstallationTab
from LDF_DeviceDetection import DeviceDetectionTab
from LDF_Motivations import MotivationsTab
from LDF_PrevLeak import PrevLeakTab
from LDF_Rooms import RoomsTab
from LDF_AppsAndFix import FixAndAppTab
from LDF_People import PeopleTab
from LDF_Economic import EconomicTab
from LDF_RepLeak import RepLeakTab
from LDF_CustKnow import CustomerKnowledgeTab
from LDF_Types import Types, TYPES

# For Database Query Use ONLY
# ---------------------------------------------------------------------
class PhynHourlyCons(Enum):
    PHYN_DATE = "text_1"
    CONSUMPTION = "num_2"
    AP_PHASE_ID = "text_2"

    @property
    def data_type(self):
        for key in TYPES.keys():
            if key in self.value:
                return TYPES[key]

class ExclusiveDbTables(Enum):
    PHYN_HOURLY_CONS = PhynHourlyCons

    @property
    def fields(self):
        return [field.name for field in self.value]
    
    @property
    def table_fields(self):
        return [field for field in self.value]
# ---------------------------------------------------------------------

class Tables(Enum):
    CLIENT = ClientTab()
    HOME_INFO = HomeInfoTab()
    DEVICE = DeviceTab()
    INSTALLATION = InstallationTab()
    DEVICE_DETECTION = DeviceDetectionTab()
    MOTIVATIONS = MotivationsTab()
    PREV_LEAK = PrevLeakTab()
    ROOMS = RoomsTab()
    FIX_AND_APP = FixAndAppTab()
    PEOPLE = PeopleTab()
    ECONOMIC = EconomicTab()
    REP_LEAK = RepLeakTab()
    CUSTOMER_KNOWLEDGE = CustomerKnowledgeTab()
    

    @property
    def fields(self):
        return self.value.getFields()
    
    @property
    def values(self):
        return self.value.getValues()
    
    @property
    def row_data(self):
        return self.value.getFormData()
    
    @property
    def table_fields(self):
        return self.value._table
    

def getFieldNames(table_name):
    field_names = []
    for table in Tables:
        if table.name == table_name:
            return table.fields 

def getAllFieldNames(table_name, normal_table = True):
    field_names = []
    if normal_table:
        field_names.append("ID")
        for table in Tables:
            if table.name == table_name:
                field_names.extend(table.fields)
                return field_names
    else:
        for table in ExclusiveDbTables:
            if table.name == table_name:
                return table.fields 





