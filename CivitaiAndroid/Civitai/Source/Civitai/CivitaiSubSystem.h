﻿// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Runtime/Online/HTTP/Public/Http.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "CivitaiSubSystem.generated.h"


DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FSyncDataOverDelegate, bool, result, int32, count);

USTRUCT(Blueprintable)
struct FCivitaiDataInfo
{
	GENERATED_BODY()

public:
	FCivitaiDataInfo()
	{
	};

	// 只保留带参数的构造函数
	FCivitaiDataInfo(int32 InID, const FString& InUrl, const FString& InType, const FString& InNsfwLevel,
	                 const FString& InTime)
		: ID(InID), Url(InUrl), Type(InType), NsfwLevel(InNsfwLevel), Time(InTime)
	{
	};

	UPROPERTY(BlueprintReadOnly)
	int32 ID = 0;
	UPROPERTY(BlueprintReadOnly)
	FString Url = FString();

	UPROPERTY(BlueprintReadOnly)
	FString Type = FString();

	UPROPERTY(BlueprintReadOnly)
	FString NsfwLevel = FString();

	UPROPERTY(BlueprintReadOnly)
	FString Time = FString();
};

/**
 * 
 */
UCLASS()
class CIVITAI_API UCivitaiSubSystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadOnly)
	FString CurrentUser = FString();
	UPROPERTY(BlueprintReadOnly)
	TMap<int32, FCivitaiDataInfo> CurrentUserDataMap;
	UPROPERTY(BlueprintReadOnly)
	FString CurrentPageUrl = FString();
	UPROPERTY(BlueprintReadOnly)
	int32 CurrentJsonCount = 0;
	

	UPROPERTY(BlueprintAssignable)
	FSyncDataOverDelegate SyncDataOverDelegate;


	// 创建用户文件夹
	UFUNCTION(BlueprintCallable, Category = "Civitai")
	void CreateUserFolder(const FString& InUserName);

	// 获取所有子文件夹
	UFUNCTION(BlueprintPure, Category = "Civitai")
	void GetUserDataList(TArray<FString>& InUserDataList);

	// 开始拉取数据
	UFUNCTION(BlueprintCallable, Category = "Civitai")
	void StartFetchJsonData(const FString& InUserName);

	// 发送请求
	UFUNCTION(BlueprintCallable, Category = "Civitai")
	void SendDataHttpRequest(const FString& InUrl);

	// 处理回调
	void HandleCivitaiDataResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);

	UFUNCTION(BlueprintCallable, Category = "Civitai")
	void RecordLastUrl();

	// 保存Json
	UFUNCTION(BlueprintCallable, Category = "Civitai")
	bool SaveJsonData();

	// 显示本地数据
	UFUNCTION(BlueprintCallable, Category = "Civitai")
	void ShowUserLocalData(const FString& InUserName);

	UFUNCTION(BlueprintPure, Category = "Civitai")
	FString GetCivitaiUserDir();

	UFUNCTION(BlueprintPure, Category = "Civitai")
	FString GetCivitaiExternalStorageDir();

	UFUNCTION(BlueprintCallable, Category = "Civitai")
	TMap<int32, FString> GetDownLoadImageData();
};
