// Copyright Porret Gaming 2024, All Rights Reserved

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"

#include "./ADBLog/ADBLogLevel.h"
#include "./AndroidLifecycle/AndroidLifecycleEventType.h"
#include "./AndroidBattery/AndroidBatteryInfo.h"
#include "./InternetCheck/InternetCheckResult.h"

#include "AndroidUtilityPackBPLibrary.generated.h"

/*
    Delegate Definitions
*/
DECLARE_DYNAMIC_DELEGATE_OneParam(FAndroidLifecycleEvent_PG_AUP, const EAndroidLifecycleEventType&, LifecycleEvent);
DECLARE_DYNAMIC_DELEGATE_OneParam(FNetworkConnectivityResult_PG_AUP, const FInternetCheckResult&, InternetCheckResult);

UCLASS()
class UAndroidUtilityPackBPLibrary: public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /*
        Delegates
    */
    static FAndroidLifecycleEvent_PG_AUP LifecycleEventCallback;
    static bool RunOnGameThread;

    static FNetworkConnectivityResult_PG_AUP NetworkConnectivityCallback;
    
    /*
        Blueprint Functions
    */
    UFUNCTION(BlueprintCallable, meta = (DisplayName = "ADB Log", Keywords = "ADB Log"), Category = "Android Utility Pack")
    static void ADBLog(EADBLogLevel ADBLogLevel, FString Tag, FString Message);

    UFUNCTION(BlueprintPure, meta = (DisplayName = "Get Android SDK Version", Keywords = "Get Android SDK Version"), Category = "Android Utility Pack")
    static int32 GetAndroidSDKVersion();

    UFUNCTION(BlueprintCallable, meta = (DisplayName = "Setup Lifecycle Event Callbacks", Keywords = "Setup Lifecycle Event Callbacks"), Category = "Android Utility Pack")
    static void SetupLifecycleEventCallbacks(bool bRunOnGameThread, FAndroidLifecycleEvent_PG_AUP OnLifecycleEvent);

    UFUNCTION(BlueprintCallable, meta = (DisplayName = "Get Current Battery Status", Keywords = "Get Current Battery Status"), Category = "Android Utility Pack")
    static FAndroidBatteryInfo GetCurrentBatteryStatus();

    UFUNCTION(BlueprintCallable, meta = (DisplayName = "Is Connected To Internet", Keywords = "Is Connected To Internet"), Category = "Android Utility Pack")
    static FInternetCheckResult IsConnectedToInternet();

    UFUNCTION(BlueprintCallable, meta = (DisplayName = "Setup Network Callbacks", Keywords = "Setup Network Callbacks"), Category = "Android Utility Pack")
    static void SetupNetworkCallbacks(FNetworkConnectivityResult_PG_AUP OnNetworkConnectivityChanged);

    UFUNCTION(BlueprintPure)
    static FString GetAndroidExternalCardPath();
    
    UFUNCTION(BlueprintCallable)
    static void OpenSystemFolder(const FString& FolderPath);

};