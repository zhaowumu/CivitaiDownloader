// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Runtime/Online/HTTP/Public/Http.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "CivitaiSubSystem.generated.h"
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnRequestCompleted, FString, FilePath, bool, bSuccess);
/**
 * 
 */
UCLASS()
class CIVITAI_API UCivitaiSubSystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:

	UPROPERTY()
	FString CurrentUser = FString();
	UPROPERTY()
	int32 CurrentPage = 0;
	UPROPERTY()
	TMap<int32,FString> CurrentUserDataMap;

	UFUNCTION(BlueprintCallable, Category = "Civitai")
	void StartFetchJsonData(const FString& InUserName);

	UFUNCTION(BlueprintCallable, Category = "Civitai")
	void SendDataHttpRequest();

	void HandleCivitaiDataResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);
	
	UFUNCTION(BlueprintCallable, Category = "Civitai")
	bool SaveJsonData();

	UPROPERTY(BlueprintAssignable, Category = "Civitai")
	FOnRequestCompleted OnRequestCompleted;
};
