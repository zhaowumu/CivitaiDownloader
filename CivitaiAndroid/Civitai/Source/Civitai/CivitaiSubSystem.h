// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Runtime/Online/HTTP/Public/Http.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "CivitaiSubSystem.generated.h"


DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FSyncDataOverDelegate, bool, result, int32, count);

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
	TMap<int32, FString> CurrentUserDataMap;
	UPROPERTY(BlueprintReadOnly)
	FString CurrentPageUrl = FString();
	UPROPERTY(BlueprintReadOnly)
	int32 CurrentJsonCount = 0;

	UPROPERTY(BlueprintAssignable)
	FSyncDataOverDelegate SyncDataOverDelegate;


	UFUNCTION(BlueprintCallable, Category = "Civitai")
	void CreateUserFolder(const FString& InUserName);

	UFUNCTION(BlueprintPure, Category = "Civitai")
	void GetUserDataList(TArray<FString>& InUserDataList);


	UFUNCTION(BlueprintCallable, Category = "Civitai")
	void StartFetchJsonData(const FString& InUserName);

	UFUNCTION(BlueprintCallable, Category = "Civitai")
	void SendDataHttpRequest(const FString& InUrl);

	void HandleCivitaiDataResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);

	UFUNCTION(BlueprintCallable, Category = "Civitai")
	bool SaveJsonData();

	UFUNCTION(BlueprintCallable, Category = "Civitai")
	void ShowUserLocalData(const FString& InUserName);

	UFUNCTION(BlueprintPure, Category = "Civitai")
	FString GetCivitaiUserDir();

	UFUNCTION(BlueprintCallable, Category = "Civitai")
	TMap<int32, FString> GetDownLoadImageData();
};
