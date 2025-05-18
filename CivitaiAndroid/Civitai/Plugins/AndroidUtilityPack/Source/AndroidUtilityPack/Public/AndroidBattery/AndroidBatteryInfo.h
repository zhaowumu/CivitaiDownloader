// Copyright Porret Gaming 2024, All Rights Reserved

#pragma once

#include "BatteryHealth.h"
#include "BatteryPlugType.h"
#include "BatteryStatus.h"

#include "AndroidBatteryInfo.generated.h"

USTRUCT(BlueprintType)
struct FAndroidBatteryInfo
{
    GENERATED_BODY()

    FAndroidBatteryInfo(): FAndroidBatteryInfo(EBatteryStatus::BATTERY_STATUS_ERROR, 0.f, false, true, EBatteryHealth::BATTERY_HEALTH_ERROR, EBatteryPlugType::BATTERY_UNPLUGGED, 0.f, 0.f, TEXT(""))
    {}

    FAndroidBatteryInfo(
        TEnumAsByte<EBatteryStatus> _BatteryStatus,
        float _BatteryPercentage,
        bool _bIsBatteryLow,
        bool _bIsBatteryPresent,
        TEnumAsByte<EBatteryHealth> _BatteryHealth,
        TEnumAsByte<EBatteryPlugType> _BatteryPlugType,
        float _BatteryTemperature,
        float _BatteryVoltage,
        FString _BatteryTechnology)
    {
        BatteryStatus = _BatteryStatus;
        BatteryPercentage = _BatteryPercentage;
        bIsBatteryLow = _bIsBatteryLow;
        bIsBatteryPresent = _bIsBatteryPresent;
        BatteryHealth = _BatteryHealth;
        BatteryPlugType = _BatteryPlugType;
        BatteryTemperature = _BatteryTemperature;
        BatteryVoltage = _BatteryVoltage;
        BatteryTechnology = _BatteryTechnology; 
    }

    UPROPERTY(BlueprintReadOnly, Category = "AndroidBatteryHealth")
    TEnumAsByte<EBatteryStatus> BatteryStatus;

    UPROPERTY(BlueprintReadOnly, Category = "AndroidBatteryHealth")
    float BatteryPercentage;

    UPROPERTY(BlueprintReadOnly, Category = "AndroidBatteryHealth")
    bool bIsBatteryLow;

    UPROPERTY(BlueprintReadOnly, Category = "AndroidBatteryHealth")
    bool bIsBatteryPresent;

    UPROPERTY(BlueprintReadOnly, Category = "AndroidBatteryHealth")
    TEnumAsByte<EBatteryHealth> BatteryHealth;

    UPROPERTY(BlueprintReadOnly, Category = "AndroidBatteryHealth")
    TEnumAsByte<EBatteryPlugType> BatteryPlugType;

    UPROPERTY(BlueprintReadOnly, Category = "AndroidBatteryHealth")
    float BatteryTemperature;

    UPROPERTY(BlueprintReadOnly, Category = "AndroidBatteryHealth")
    float BatteryVoltage;

    UPROPERTY(BlueprintReadOnly, Category = "AndroidBatteryHealth")
    FString BatteryTechnology;
    
};
