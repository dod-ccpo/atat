from enum import Enum


class AzureApiVersion(Enum):
    # This class serves as the representation of the various REST API versions that Azure uses.
    API_VERSION_2015_07_01 = "2015-07-01"
    API_VERSION_2016_07_01 = "2016-07-01"
    API_VERSION_2019_09_01 = "2019-09-01"
    API_VERSION_2019_11_01 = "2019-11-01"
    API_VERSION_2020_02_01 = "2020-02-01"
    PREVIEW_API_VERSION_2019_10_01 = "2019-10-01-preview"
    PREVIEW_API_VERSION_2020_01_01 = "2020-01-01-preview"

    API_VERSION_7_1 = "7.1"
