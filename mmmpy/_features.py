""""""
__all__ = ["MRMSFeatures", "MRMSRegions"]
import re
from functools import lru_cache
from enum import Enum, auto

class _AUTO_NAME(str,Enum):
    
    def _generate_next_value_(name,*_):

        if re.search(r"_M\d{1,2}C", name):
            name = re.sub(r"_M","_-", name)
        elif re.search(r"_\d{1,2}_\d{1,2}", name):
            name = "-".join(v for v in re.split(r"(.+\d)_(\d.+)",name) if v)
        
        return name
    @classmethod
    @property
    @lru_cache(1)
    def __all__(cls):
        return [i for i in cls]
    @classmethod
    @property
    @lru_cache(1)
    def values(cls):
        return [i.value for i in cls]
    @classmethod
    def select(cls, items:list[str]):
        yield from (cls[item] for item in items)

class MRMSFeatures(_AUTO_NAME):
    """
    MULTI-RADAR/MULTI-SENSOR SYSTEM (MRMS)
    The MRMS system was developed to produce severe weather, 
    transportation, and precipitation products for improved decision-making 
    capability to improve hazardous weather forecasts and warnings, 
    along with hydrology, aviation, and numerical weather prediction.

    MRMS is a system with fully-automated algorithms that quickly and 
    intelligently integrate data streams from multiple radars, surface and 
    upper air observations, lightning detection systems, satellite observations, 
    and forecast models. Numerous two-dimensional multiple-sensor products 
    offer assistance for hail, wind, tornado, quantitative precipitation 
    estimations, convection, icing, and turbulence diagnosis.
    """
    ANC_FinalForecast = auto()
    ANC_ConvectiveLikelihood = auto()
    EchoTop_60 = auto()
    RotationTrack240min = auto()
    MultiSensor_QPE_03H_Pass2 = auto()
    RadarOnly_QPE_15M = auto()
    MultiSensor_QPE_48H_Pass1 = auto()
    MultiSensor_QPE_01H_Pass2 = auto()
    RadarOnly_QPE_01H = auto()
    RadarAccumulationQualityIndex_06H = auto()
    MultiSensor_QPE_06H_Pass2 = auto()
    FLASH_SAC_MAXSOILSAT = auto()
    H60_Above_M20C = auto()
    Reflectivity_0C = auto()
    PrecipFlag = auto()
    EchoTop_18 = auto()
    RotationTrack1440min = auto()
    MergedReflectivityQComposite = auto()
    MultiSensor_QPE_24H_Pass2 = auto()
    MergedBaseReflectivityQC = auto()
    GaugeInflIndex_72H_Pass1 = auto()
    RotationTrackML30min = auto()
    Model_SurfaceTemp = auto()
    MultiSensor_QPE_03H_Pass1 = auto()
    RadarAccumulationQualityIndex_03H = auto()
    FLASH_CREST_MAXSOILSAT = auto()
    BREF_1HR_MAX = auto()
    FLASH_QPE_ARI12H = auto()
    EchoTop_50 = auto()
    VIL_Max_120min = auto()
    LayerCompositeReflectivity_High = auto()
    Reflectivity_M15C = auto()
    FLASH_QPE_ARI24H = auto()
    RadarAccumulationQualityIndex_72H = auto()
    FLASH_HP_MAXUNITSTREAMFLOW = auto()
    NLDN_CG_015min_AvgDensity = auto()
    MESH = auto()
    RadarOnly_QPE_06H = auto()
    SHI = auto()
    GaugeInflIndex_01H_Pass2 = auto()
    Reflectivity_M10C = auto()
    LVL3_HREET = auto()
    LVL3_HighResVIL = auto()
    LayerCompositeReflectivity_Super = auto()
    GaugeInflIndex_24H_Pass2 = auto()
    CREF_1HR_MAX = auto()
    H50_Above_0C = auto()
    MultiSensor_QPE_48H_Pass2 = auto()
    GaugeInflIndex_03H_Pass2 = auto()
    LowLevelCompositeReflectivity = auto()
    RadarAccumulationQualityIndex_48H = auto()
    RotationTrackML60min = auto()
    RadarAccumulationQualityIndex_24H = auto()
    FLASH_SAC_MAXUNITSTREAMFLOW = auto()
    MultiSensor_QPE_01H_Pass1 = auto()
    SeamlessHSRHeight = auto()
    WarmRainProbability = auto()
    RotationTrack60min = auto()
    FLASH_CREST_MAXSTREAMFLOW = auto()
    Reflectivity_M5C = auto()
    GaugeInflIndex_24H_Pass1 = auto()
    RotationTrackML360min = auto()
    FLASH_QPE_FFG03H = auto()
    HeightCompositeReflectivity = auto()
    MultiSensor_QPE_72H_Pass1 = auto()
    GaugeInflIndex_12H_Pass1 = auto()
    FLASH_QPE_ARI30M = auto()
    FLASH_QPE_ARIMAX = auto()
    MultiSensor_QPE_12H_Pass1 = auto()
    VII = auto()
    MergedZdr = auto()
    MergedReflectivityQC = auto()
    MESH_Max_240min = auto()
    GaugeInflIndex_01H_Pass1 = auto()
    Model_0degC_Height = auto()
    FLASH_QPE_ARI06H = auto()
    RadarOnly_QPE_12H = auto()
    LayerCompositeReflectivity_Low = auto()
    FLASH_QPE_ARI01H = auto()
    MESH_Max_60min = auto()
    VIL = auto()
    MESH_Max_360min = auto()
    RadarAccumulationQualityIndex_01H = auto()
    MergedAzShear_0_2kmAGL = auto()
    MergedReflectivityComposite = auto()
    FLASH_QPE_FFG06H = auto()
    PrecipRate = auto()
    NLDN_CG_030min_AvgDensity = auto()
    Model_WetBulbTemp = auto()
    POSH = auto()
    RadarOnly_QPE_24H = auto()
    SeamlessHSR = auto()
    VIL_Max_1440min = auto()
    MESH_Max_30min = auto()
    RadarAccumulationQualityIndex_12H = auto()
    NLDN_CG_001min_AvgDensity = auto()
    GaugeInflIndex_12H_Pass2 = auto()
    GaugeInflIndex_48H_Pass2 = auto()
    FLASH_SAC_MAXSTREAMFLOW = auto()
    NLDN_CG_005min_AvgDensity = auto()
    MergedReflectivityQCComposite = auto()
    RotationTrack360min = auto()
    RadarOnly_QPE_48H = auto()
    ReflectivityAtLowestAltitude = auto()
    RadarOnly_QPE_03H = auto()
    MultiSensor_QPE_06H_Pass1 = auto()
    BrightBandBottomHeight = auto()
    H60_Above_0C = auto()
    H50_Above_M20C = auto()
    EchoTop_30 = auto()
    GaugeInflIndex_48H_Pass1 = auto()
    FLASH_QPE_FFG01H = auto()
    GaugeInflIndex_06H_Pass1 = auto()
    LayerCompositeReflectivity_ANC = auto()
    FLASH_QPE_ARI03H = auto()
    Reflectivity_M20C = auto()
    MergedRhoHV = auto()
    BrightBandTopHeight = auto()
    MESH_Max_1440min = auto()
    RadarQualityIndex = auto()
    MergedAzShear_3_6kmAGL = auto()
    RotationTrackML1440min = auto()
    RotationTrack120min = auto()
    HeightLowLevelCompositeReflectivity = auto()
    GaugeInflIndex_72H_Pass2 = auto()
    MergedBaseReflectivity = auto()
    RadarOnly_QPE_Since12Z = auto()
    MultiSensor_QPE_72H_Pass2 = auto()
    FLASH_HP_MAXSTREAMFLOW = auto()
    FLASH_CREST_MAXUNITSTREAMFLOW = auto()
    MESH_Max_120min = auto()
    RotationTrackML240min = auto()
    MultiSensor_QPE_24H_Pass1 = auto()
    RotationTrack30min = auto()
    MultiSensor_QPE_12H_Pass2 = auto()
    GaugeInflIndex_06H_Pass2 = auto()
    SyntheticPrecipRateID = auto()
    MergedReflectivityAtLowestAltitude = auto()
    FLASH_QPE_FFGMAX = auto()
    RadarOnly_QPE_72H = auto()
    VIL_Density = auto()
    GaugeInflIndex_03H_Pass1 = auto()
    RotationTrackML120min = auto()


class MRMSRegions(_AUTO_NAME):
    ANC= auto()
    CONUS= auto()
    ALASKA= auto()
    CARIB= auto()
    GUAM= auto()
    HAWAII= auto()

