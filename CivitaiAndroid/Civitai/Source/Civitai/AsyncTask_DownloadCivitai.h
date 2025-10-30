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

/**
 * 异步下载图片的蓝图节点
 */
UCLASS(BlueprintType, meta = (ExposedAsyncProxy = AsyncTask))
class CIVITAI_API UAsyncTask_DownloadCivitai : public UBlueprintAsyncActionBase
{
	GENERATED_BODY()

public:
	/** 创建异步下载节点 */
	UFUNCTION(BlueprintCallable, meta=(BlueprintInternalUseOnly="true"))
	static UAsyncTask_DownloadCivitai* DownloadCivitai(FString InUserName, int32 InImageID, FString InSubFolder,FString InURL);

public:
	UPROPERTY(BlueprintAssignable)
	FDownloadImageDelegate OnSuccess;

	UPROPERTY(BlueprintAssignable)
	FDownloadImageDelegate OnFail;

public:
	virtual void Activate() override;

private:
	/** 下载地址 */
	FString URL;

	/** 用户名 */
	FString UserName;

	/** 图片ID */
	int32 ImageID;

	/** 子文件夹 */
	FString SubFolder;

	/** 请求完成回调 */
	void HandleImageRequest(FHttpRequestPtr HttpRequest, FHttpResponsePtr HttpResponse, bool bSucceeded);

	/** 保存数据到文件 */
	void SaveToData(const TArray<uint8>& InData);
};
