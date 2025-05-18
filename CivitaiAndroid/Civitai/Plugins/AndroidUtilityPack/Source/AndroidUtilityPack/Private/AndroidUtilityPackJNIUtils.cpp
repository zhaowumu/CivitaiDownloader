// Copyright Porret Gaming 2024, All Rights Reserved

#include "../Public/AndroidUtilityPackJNIUtils.h"

#include "../Public/InternetCheck/InternetCheckResult.h"

#if PLATFORM_ANDROID
#include "Android/AndroidJNI.h"
#include "Android/AndroidApplication.h"
#endif

#if PLATFORM_ANDROID

FInternetCheckResult UAndroidUtilityPackJNIUtils::BuildInternetCheckResult(JNIEnv* Env, jobject internetCheckResultObj)
{
    if (internetCheckResultObj == nullptr) {
        return FInternetCheckResult();
    }

    // Find the class of the returned object
    jclass InternetCheckResultClass = Env->GetObjectClass(internetCheckResultObj);

    // Get the method IDs for the getters
    jmethodID GetIsConnected = Env->GetMethodID(InternetCheckResultClass, "getIsConnected", "()Z");
    jmethodID GetFailureReason = Env->GetMethodID(InternetCheckResultClass, "getFailureReason", "()Ljava/lang/String;");
    
    // Extract the values from the Java object using the getter methods
    bool bIsConnected = Env->CallBooleanMethod(internetCheckResultObj, GetIsConnected);
    jstring FailureReasonJString = (jstring)Env->CallObjectMethod(internetCheckResultObj, GetFailureReason);

    // Initialize the BatteryInfo struct using its constructor
    FInternetCheckResult Result = FInternetCheckResult(
        bIsConnected,
        FString(UTF8_TO_TCHAR(Env->GetStringUTFChars(FailureReasonJString, NULL))));

    Env->ReleaseStringUTFChars(FailureReasonJString, Env->GetStringUTFChars(FailureReasonJString, NULL));
    Env->DeleteLocalRef(InternetCheckResultClass);

    return Result;
}


FAndroidBatteryInfo UAndroidUtilityPackJNIUtils::BuildAndroidBatteryInfo(JNIEnv* Env, jobject BatteryInfoObj)
{
    if (BatteryInfoObj == nullptr) {
        return FAndroidBatteryInfo();
    }
    // Find the class of the returned object
    jclass BatteryInfoClass = Env->GetObjectClass(BatteryInfoObj);

    // Get the method IDs for the getters
    jmethodID GetBatteryStatus = Env->GetMethodID(BatteryInfoClass, "getBatteryStatus", "()I");
    jmethodID GetBatteryPercentage = Env->GetMethodID(BatteryInfoClass, "getBatteryPercentage", "()F");
    jmethodID GetIsBatteryLow = Env->GetMethodID(BatteryInfoClass, "isBatteryLow", "()Z");
    jmethodID GetIsBatteryPresent = Env->GetMethodID(BatteryInfoClass, "isBatteryPresent", "()Z");
    jmethodID GetBatteryHealth = Env->GetMethodID(BatteryInfoClass, "getBatteryHealth", "()I");
    jmethodID GetBatteryPlugType = Env->GetMethodID(BatteryInfoClass, "getBatteryPlugType", "()I");
    jmethodID GetBatteryTemperature = Env->GetMethodID(BatteryInfoClass, "getBatteryTemperature", "()F");
    jmethodID GetBatteryVoltage = Env->GetMethodID(BatteryInfoClass, "getBatteryVoltage", "()F");
    jmethodID GetBatteryTechnology = Env->GetMethodID(BatteryInfoClass, "getBatteryTechnology", "()Ljava/lang/String;");
    
    // Extract the values from the Java object using the getter methods
    int32 BatteryStatus = static_cast<int32>(Env->CallIntMethod(BatteryInfoObj, GetBatteryStatus));
    float BatteryPercentage = Env->CallFloatMethod(BatteryInfoObj, GetBatteryPercentage);
    bool bIsBatteryLow = Env->CallBooleanMethod(BatteryInfoObj, GetIsBatteryLow);
    bool bIsBatteryPresent = Env->CallBooleanMethod(BatteryInfoObj, GetIsBatteryPresent);
    int32 BatteryHealth = static_cast<int32>(Env->CallIntMethod(BatteryInfoObj, GetBatteryHealth));
    int32 BatteryPlugType = static_cast<int32>(Env->CallIntMethod(BatteryInfoObj, GetBatteryPlugType));
    float BatteryTemperature = Env->CallFloatMethod(BatteryInfoObj, GetBatteryTemperature);
    float BatteryVoltage = Env->CallFloatMethod(BatteryInfoObj, GetBatteryVoltage);
    jstring BatteryTechnologyJString = (jstring)Env->CallObjectMethod(BatteryInfoObj, GetBatteryTechnology);

    // Initialize the BatteryInfo struct using its constructor
    FAndroidBatteryInfo BatteryInfo = FAndroidBatteryInfo(
        static_cast<EBatteryStatus>(BatteryStatus),
        BatteryPercentage,
        bIsBatteryLow,
        bIsBatteryPresent,
        static_cast<EBatteryHealth>(BatteryHealth),
        static_cast<EBatteryPlugType>(BatteryPlugType),
        BatteryTemperature,
        BatteryVoltage,
        FString(UTF8_TO_TCHAR(Env->GetStringUTFChars(BatteryTechnologyJString, NULL)))
    );

    Env->ReleaseStringUTFChars(BatteryTechnologyJString, Env->GetStringUTFChars(BatteryTechnologyJString, NULL));
    Env->DeleteLocalRef(BatteryInfoClass);

    return BatteryInfo;
}

#endif
