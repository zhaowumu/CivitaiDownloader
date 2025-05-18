// Copyright Porret Gaming 2024, All Rights Reserved

#include "../Public/AndroidUtilityPackBPLibrary.h"

#include "Async/TaskGraphInterfaces.h"

#include "../Public/AndroidUtilityPackJNIUtils.h"

#include "../Public/AndroidBattery/BatteryHealth.h"
#include "../Public/AndroidBattery/BatteryPlugType.h"
#include "../Public/AndroidBattery/BatteryStatus.h"

#if PLATFORM_ANDROID
#include "Android/AndroidJNI.h"
#include "Android/AndroidApplication.h"
#endif

void UAndroidUtilityPackBPLibrary::ADBLog(EADBLogLevel ADBLogLevel, FString Tag, FString Message)
{
#if PLATFORM_ANDROID
	if (JNIEnv* Env = FAndroidApplication::GetJavaEnv())
	{
		// Fetch Method ID
		static jmethodID Method = FJavaWrapper::FindMethod(Env, FJavaWrapper::GameActivityClassID, "AndroidThunkJava_PG_ADBLog", "(ILjava/lang/String;Ljava/lang/String;)V", false);

		jint jLogLevel = static_cast<jint>(ADBLogLevel);
		jstring jTag = Env->NewStringUTF(TCHAR_TO_UTF8(*Tag));
		jstring jMessage = Env->NewStringUTF(TCHAR_TO_UTF8(*Message));

		// Call Method
		FJavaWrapper::CallVoidMethod(Env, FJavaWrapper::GameActivityThis, Method, jLogLevel, jTag, jMessage);
	}
#endif
}

int32 UAndroidUtilityPackBPLibrary::GetAndroidSDKVersion()
{
	int32 SDKVersion = -1;
#if PLATFORM_ANDROID
	if (JNIEnv* Env = FAndroidApplication::GetJavaEnv())
	{
		// Fetch Method ID
		static jmethodID Method = FJavaWrapper::FindMethod(Env, FJavaWrapper::GameActivityClassID, "AndroidThunkJava_PG_GetAndroidSDKVersion", "()I", false);
		// Call Method
		SDKVersion = static_cast<int32>(FJavaWrapper::CallIntMethod(Env, FJavaWrapper::GameActivityThis, Method));
	}
#endif
	return SDKVersion;
}

FAndroidLifecycleEvent_PG_AUP UAndroidUtilityPackBPLibrary::LifecycleEventCallback;
bool UAndroidUtilityPackBPLibrary::RunOnGameThread;

void UAndroidUtilityPackBPLibrary::SetupLifecycleEventCallbacks(bool bRunOnGameThread, FAndroidLifecycleEvent_PG_AUP OnLifecycleEvent)
{
	UAndroidUtilityPackBPLibrary::LifecycleEventCallback = OnLifecycleEvent;
	UAndroidUtilityPackBPLibrary::RunOnGameThread = bRunOnGameThread;

#if PLATFORM_ANDROID
	if (JNIEnv* Env = FAndroidApplication::GetJavaEnv())
	{
		// Fetch Method ID
		static jmethodID Method = FJavaWrapper::FindMethod(Env, FJavaWrapper::GameActivityClassID, "AndroidThunkJava_PG_SetupLifecycleEventCallback", "()V", false);

		// Call Method
		FJavaWrapper::CallVoidMethod(Env, FJavaWrapper::GameActivityThis, Method);
	}
#endif
	
}

FAndroidBatteryInfo UAndroidUtilityPackBPLibrary::GetCurrentBatteryStatus()
{
	FAndroidBatteryInfo BatteryInfo;

#if PLATFORM_ANDROID
	if (JNIEnv* Env = FAndroidApplication::GetJavaEnv())
	{
		// Fetch Method ID
		static jmethodID Method = FJavaWrapper::FindMethod(Env, FJavaWrapper::GameActivityClassID, "AndroidThunkJava_PG_GetCurrentBatteryStatus", "()Lcom/porretgaming/androidutilitypack/AndroidBatteryInfo;", false);
		
		// Call Method and get the returned Java object
        jobject BatteryInfoObj = FJavaWrapper::CallObjectMethod(Env, FJavaWrapper::GameActivityThis, Method);
		BatteryInfo = UAndroidUtilityPackJNIUtils::BuildAndroidBatteryInfo(Env, BatteryInfoObj);

		// Clean up local references
        Env->DeleteLocalRef(BatteryInfoObj);
	}
#endif

	return BatteryInfo;
}

FInternetCheckResult UAndroidUtilityPackBPLibrary::IsConnectedToInternet()
{
	FInternetCheckResult ReturnValue;
#if PLATFORM_ANDROID
	if (JNIEnv* Env = FAndroidApplication::GetJavaEnv())
	{
		// Fetch Method ID
		static jmethodID Method = FJavaWrapper::FindMethod(Env, FJavaWrapper::GameActivityClassID, "AndroidThunkJava_PG_IsConnectedToInternet", "()Lcom/porretgaming/androidutilitypack/InternetCheckResult;", false);
		// Call Method
		jobject internetCheckResultObj = FJavaWrapper::CallObjectMethod(Env, FJavaWrapper::GameActivityThis, Method);

		ReturnValue = UAndroidUtilityPackJNIUtils::BuildInternetCheckResult(Env, internetCheckResultObj);
	}
#endif
	return ReturnValue;
}

FNetworkConnectivityResult_PG_AUP UAndroidUtilityPackBPLibrary::NetworkConnectivityCallback;
void UAndroidUtilityPackBPLibrary::SetupNetworkCallbacks(FNetworkConnectivityResult_PG_AUP OnNetworkConnectivityChanged)
{
	UAndroidUtilityPackBPLibrary::NetworkConnectivityCallback = OnNetworkConnectivityChanged;
#if PLATFORM_ANDROID
	if (JNIEnv* Env = FAndroidApplication::GetJavaEnv())
	{
		// Fetch Method ID
		static jmethodID Method = FJavaWrapper::FindMethod(Env, FJavaWrapper::GameActivityClassID, "AndroidThunkJava_PG_SetupNetworkCallbacks", "()V", false);
		// Call Method
		FJavaWrapper::CallVoidMethod(Env, FJavaWrapper::GameActivityThis, Method);
	}
#endif
}

FString UAndroidUtilityPackBPLibrary::GetAndroidExternalCardPath()
{
	FString outPath = FString("Hello");

#if PLATFORM_ANDROID
	if (JNIEnv* Env = FAndroidApplication::GetJavaEnv())
	{
		// 获取 Environment 类
		jclass environmentClass = Env->FindClass("android/os/Environment");
		// 获取 DIRECTORY_DOWNLOADS 静态字段
		jfieldID downloadsDirField = Env->GetStaticFieldID(environmentClass, "DIRECTORY_DOWNLOADS", "Ljava/lang/String;");
		jstring downloadsDir = (jstring)Env->GetStaticObjectField(environmentClass, downloadsDirField);
        
		// 获取 getExternalStoragePublicDirectory 方法
		jmethodID getPublicDirMethod = Env->GetStaticMethodID(environmentClass, 
			"getExternalStoragePublicDirectory", 
			"(Ljava/lang/String;)Ljava/io/File;");
        
		// 调用静态方法获取 File 对象
		jobject publicDirFile = Env->CallStaticObjectMethod(environmentClass, getPublicDirMethod, downloadsDir);
        
		// 获取文件路径
		jmethodID getPathMethod = Env->GetMethodID(Env->FindClass("java/io/File"), "getPath", "()Ljava/lang/String;");
		jstring pathString = (jstring)Env->CallObjectMethod(publicDirFile, getPathMethod);
        
		const char* nativePathString = Env->GetStringUTFChars(pathString, 0);
		outPath = ANSI_TO_TCHAR(nativePathString);
        
		// 释放资源
		Env->ReleaseStringUTFChars(pathString, nativePathString);
	}
#endif

	return outPath;
}

void UAndroidUtilityPackBPLibrary::OpenSystemFolder(const FString& FolderPath)
{
#if PLATFORM_ANDROID

#endif
}

/*
	C++ Callback Function from JVM
*/
#if PLATFORM_ANDROID
JNI_METHOD void Java_com_porretgaming_androidutilitypack_AndroidUtilities_CPPOnLifecycleEvent(JNIEnv* env, jclass clazz, jint jEventType)
{
	if (UAndroidUtilityPackBPLibrary::LifecycleEventCallback.IsBound()) {
		EAndroidLifecycleEventType LifeCycleEvent = static_cast<EAndroidLifecycleEventType>(jEventType);

		if (UAndroidUtilityPackBPLibrary::RunOnGameThread) {
			FSimpleDelegateGraphTask::CreateAndDispatchWhenReady(
				FSimpleDelegateGraphTask::FDelegate::CreateLambda([LifeCycleEvent]()
				{
					UAndroidUtilityPackBPLibrary::LifecycleEventCallback.Execute(LifeCycleEvent);
				}),
				TStatId(), nullptr, ENamedThreads::GameThread);
		} else {
			UAndroidUtilityPackBPLibrary::LifecycleEventCallback.Execute(LifeCycleEvent);
		}
	}
}

JNI_METHOD void Java_com_porretgaming_androidutilitypack_AndroidUtilities_CPPOnInternetStatusChanged(JNIEnv* env, jclass clazz, jobject internetCheckResultObj)
{
	if (UAndroidUtilityPackBPLibrary::NetworkConnectivityCallback.IsBound()) {
		FInternetCheckResult Result = UAndroidUtilityPackJNIUtils::BuildInternetCheckResult(env, internetCheckResultObj);
		if (UAndroidUtilityPackBPLibrary::RunOnGameThread) {
			FSimpleDelegateGraphTask::CreateAndDispatchWhenReady(
				FSimpleDelegateGraphTask::FDelegate::CreateLambda([Result]()
				{
					UAndroidUtilityPackBPLibrary::NetworkConnectivityCallback.Execute(Result);
				}),
				TStatId(), nullptr, ENamedThreads::GameThread);
		} else {
			UAndroidUtilityPackBPLibrary::NetworkConnectivityCallback.Execute(Result);
		}
	}
}
#endif