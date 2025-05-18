// Copyright Porret Gaming 2024, All Rights Reserved

#pragma once

#include "BatteryPlugType.generated.h"

UENUM(BlueprintType)
enum EBatteryPlugType
{
    BATTERY_UNPLUGGED                       = 0     UMETA(DisplayName = "BATTERY_UNPLUGGED"),
    BATTERY_PLUGGED_AC                      = 1     UMETA(DisplayName = "BATTERY_PLUGGED_AC"),
    BATTERY_PLUGGED_USB                     = 2     UMETA(DisplayName = "BATTERY_PLUGGED_USB"),
    BATTERY_PLUGGED_WIRELESS                = 4     UMETA(DisplayName = "BATTERY_PLUGGED_WIRELESS"),
    BATTERY_PLUGGED_DOCK                    = 8     UMETA(DisplayName = "BATTERY_PLUGGED_DOCK")
};
