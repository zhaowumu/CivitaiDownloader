// Copyright Porret Gaming 2024, All Rights Reserved

#pragma once

#include "./InternetCheck/InternetCheckResult.h"
#include "./AndroidBattery/AndroidBatteryInfo.h"

#include "AndroidUtilityPackJNIUtils.generated.h"

#if PLATFORM_ANDROID
#include "Android/AndroidJNI.h"
#include "Android/AndroidApplication.h"
#endif

UCLASS()
class UAndroidUtilityPackJNIUtils : public UObject
{
    GENERATED_BODY()

public:

#if PLATFORM_ANDROID
    static FInternetCheckResult BuildInternetCheckResult(JNIEnv* Env, jobject internetCheckResultObj);
    static FAndroidBatteryInfo BuildAndroidBatteryInfo(JNIEnv* Env, jobject BatteryInfoObj);
#endif

};