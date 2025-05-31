// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "UObject/ObjectMacros.h"
#include "Interfaces/IHttpRequest.h"
#include "Kismet/BlueprintAsyncActionBase.h"
#include "AsyncTask_DownloadCivitai.generated.h"


DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FDownloadImageDelegate,
                                               UTexture2D*, Texture,
                                               FString, ImageSavePath,
                                               int32, Uid);

UCLASS(BlueprintType, meta = (ExposedAsyncProxy = AsyncTask))
class CIVITAI_API UAsyncTask_DownloadCivitai : public UBlueprintAsyncActionBase
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, meta=(BlueprintInternalUseOnly="true"))
	static UAsyncTask_DownloadCivitai* DownloadCivitai(FString InUserName, FString InURL, int32 InImageID);

public:
	UPROPERTY(BlueprintAssignable)
	FDownloadImageDelegate OnSuccess;

	UPROPERTY(BlueprintAssignable)
	FDownloadImageDelegate OnFail;

public:
	virtual void Activate() override;

private:
	FString URL;
	FString UserName;
	int32 ImageID;

	/** Handles image requests coming from the web */
	void HandleImageRequest(FHttpRequestPtr HttpRequest, FHttpResponsePtr HttpResponse, bool bSucceeded);

	void SaveToData(const TArray<uint8>& InData);
};
