// Copyright Porret Gaming 2024, All Rights Reserved

#pragma once

#include "BatteryHealth.generated.h"

UENUM(BlueprintType)
enum EBatteryHealth
{
    BATTERY_HEALTH_ERROR                    = 0     UMETA(DisplayName = "BATTERY_HEALTH_ERROR"),
    BATTERY_HEALTH_UNKNOWN                  = 1     UMETA(DisplayName = "BATTERY_HEALTH_UNKNOWN"),
    BATTERY_HEALTH_GOOD                     = 2     UMETA(DisplayName = "BATTERY_HEALTH_GOOD"),
    BATTERY_HEALTH_OVERHEAT                 = 3     UMETA(DisplayName = "BATTERY_HEALTH_OVERHEAT"),
    BATTERY_HEALTH_DEAD                     = 4     UMETA(DisplayName = "BATTERY_HEALTH_DEAD"),
    BATTERY_HEALTH_OVER_VOLTAGE             = 5     UMETA(DisplayName = "BATTERY_HEALTH_OVER_VOLTAGE"),
    BATTERY_HEALTH_UNSPECIFIED_FAILURE      = 6     UMETA(DisplayName = "BATTERY_HEALTH_UNSPECIFIED_FAILURE"),
    BATTERY_HEALTH_COLD                     = 7     UMETA(DisplayName = "BATTERY_HEALTH_COLD")
};
