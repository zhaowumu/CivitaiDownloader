// Copyright Porret Gaming 2024, All Rights Reserved

#pragma once

#include "AndroidUtilityPackSettings.generated.h"

UCLASS(Config=Game, defaultconfig)
class UAndroidUtilityPackSettings : public UObject
{
	GENERATED_BODY()

	/*
		Android SDK API Fixes
	*/
	UPROPERTY(Config, EditAnywhere, Category = "Unreal Engine Source Code Fixes", Meta = (DisplayName = "Enable Android API 33 Fixes", Tooltip = "Fix any Unreal Engine java breaking changes for Android API 33"))
	bool bEnableAndroidAPI33Fixes;

	UPROPERTY(Config, EditAnywhere, Category = "Unreal Engine Source Code Fixes", Meta = (DisplayName = "Enable Android API 34 Fixes", Tooltip = "Fix any Unreal Engine java breaking changes for Android API 34"))
	bool bEnableAndroidAPI34Fixes;

    UPROPERTY(Config, EditAnywhere, Category = "Unreal Engine Source Code Fixes", Meta = (DisplayName = "Update Gradle", Tooltip = "Update Gradle to 7.5 matching latest Unreal Engine versions"))
    bool bUpgradeGradle;

    UPROPERTY(Config, EditAnywhere, Category = "Unreal Engine Source Code Fixes", Meta = (DisplayName = "Update AndroidX Fragment", Tooltip = "Add a constraint to 'androidx.fragment:fragment:1.3.6'"))
    bool bUpdateAndroidXFragement;
   
    /*
        Internet Check Overrides
    */
    UPROPERTY(Config, EditAnywhere, Category = "Internet Check", Meta = (DisplayName = "Override Internet Check", Tooltip = "Override the default Internet Check behavior"))
    bool bOverrideInternetCheck;

    UPROPERTY(Config, EditAnywhere, Category = "Internet Check", Meta = (EditCondition = "bOverrideInternetCheck", DisplayName = "Connection Timeout (ms)", Tooltip = "Set the connection timeout in milliseconds for the Internet Check"))
    int32 ConnectionTimeout = 1500;

    UPROPERTY(Config, EditAnywhere, Category = "Internet Check", Meta = (EditCondition = "bOverrideInternetCheck", DisplayName = "Internet Check URL", Tooltip = "Set the URL to be used for the Internet Check"))
    FString InternetCheckURL = "https://clients3.google.com/generate_204";
};
