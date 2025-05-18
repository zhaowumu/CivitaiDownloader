// Copyright Porret Gaming 2024, All Rights Reserved

#pragma once

#include "BatteryStatus.generated.h"

UENUM(BlueprintType)
enum EBatteryStatus
{
    BATTERY_STATUS_ERROR                = 0     UMETA(DisplayName = "BATTERY_STATUS_ERROR"),
    BATTERY_STATUS_UNKNOWN              = 1     UMETA(DisplayName = "BATTERY_STATUS_UNKNOWN"),
    BATTERY_STATUS_CHARGING             = 2     UMETA(DisplayName = "BATTERY_STATUS_CHARGING"),
    BATTERY_STATUS_DISCHARGING          = 3     UMETA(DisplayName = "BATTERY_STATUS_DISCHARGING"),
    BATTERY_STATUS_NOT_CHARGING         = 4     UMETA(DisplayName = "BATTERY_STATUS_NOT_CHARGING"),
    BATTERY_STATUS_FULL                 = 5     UMETA(DisplayName = "BATTERY_STATUS_FULL")
};
