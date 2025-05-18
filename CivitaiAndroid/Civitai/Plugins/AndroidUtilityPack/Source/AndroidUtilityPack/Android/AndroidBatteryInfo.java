// Copyright Porret Gaming 2024, All Rights Reserved
package com.porretgaming.androidutilitypack;

public final class AndroidBatteryInfo
{
    private final int BatteryStatus;
    private final float BatteryPercentage;
    private final boolean bIsBatteryLow;
    private final boolean bIsBatteryPresent;
    private final int BatteryHealth;
    private final int BatteryPlugType;
    private final float BatteryTemperature;
    private final float BatteryVoltage;
    private final String BatteryTechnology;

    public AndroidBatteryInfo(
        int _BatteryStatus,
        float _BatteryPercentage,
        boolean _bIsBatteryLow,
        boolean _bIsBatteryPresent,
        int _BatteryHealth,
        int _BatteryPlugType,
        float _BatteryTemperature,
        float _BatteryVoltage,
        String _BatteryTechnology)
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

    public int getBatteryStatus() {
        return BatteryStatus;
    }

    public float getBatteryPercentage() {
        return BatteryPercentage;
    }

    public boolean isBatteryLow() {
        return bIsBatteryLow;
    }

    public boolean isBatteryPresent() {
        return bIsBatteryPresent;
    }

    public int getBatteryHealth() {
        return BatteryHealth;
    }

    public int getBatteryPlugType() {
        return BatteryPlugType;
    }

    public float getBatteryTemperature() {
        return BatteryTemperature;
    }

    public float getBatteryVoltage() {
        return BatteryVoltage;
    }

    public String getBatteryTechnology() {
        return BatteryTechnology;
    }
}