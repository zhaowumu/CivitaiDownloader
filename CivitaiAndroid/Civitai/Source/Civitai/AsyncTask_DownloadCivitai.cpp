// Fill out your copyright notice in the Description page of Project Settings.


#include "AsyncTask_DownloadCivitai.h"

#include "AndroidUtilityPackBPLibrary.h"
#include "CivitaiFunctionLib.h"
#include "HttpModule.h"
#include "IImageWrapper.h"
#include "IImageWrapperModule.h"
#include "Engine/Texture2DDynamic.h"
#include "Interfaces/IHttpResponse.h"
#include "Kismet/KismetRenderingLibrary.h"

UAsyncTask_DownloadCivitai* UAsyncTask_DownloadCivitai::DownloadCivitai(FString InUserName, FString InURL,
                                                                        int32 InImageID)
{
	UAsyncTask_DownloadCivitai* BlueprintAsyncTask = NewObject<UAsyncTask_DownloadCivitai>();
	UE_LOG(LogTemp, Log, TEXT("UAsyncTask_DownloadCivitai::DownloadCivitai"));
	BlueprintAsyncTask->URL = InURL;
	BlueprintAsyncTask->UserName = InUserName;
	BlueprintAsyncTask->ImageID = InImageID;
	return BlueprintAsyncTask;
}

void UAsyncTask_DownloadCivitai::Activate()
{
	// Create the Http request and add to pending request list
	TSharedRef<IHttpRequest, ESPMode::ThreadSafe> HttpRequest = FHttpModule::Get().CreateRequest();

	HttpRequest->OnProcessRequestComplete().BindUObject(this, &UAsyncTask_DownloadCivitai::HandleImageRequest);
	HttpRequest->SetURL(URL);
	HttpRequest->SetVerb(TEXT("GET"));
	HttpRequest->ProcessRequest();

	UE_LOG(LogTemp, Log, TEXT("UAsyncTask_DownloadCivitai::Activate"));
}

void UAsyncTask_DownloadCivitai::HandleImageRequest(FHttpRequestPtr HttpRequest, FHttpResponsePtr HttpResponse,
                                                    bool bSucceeded)
{
	UE_LOG(LogTemp, Log, TEXT("HandleImageRequest"));
	RemoveFromRoot();
	UE_LOG(LogTemp, Log, TEXT("HandleImageRequest2"));
	if (bSucceeded && HttpResponse.IsValid() && EHttpResponseCodes::IsOk(HttpResponse->GetResponseCode()) &&
		HttpResponse->GetContentLength() > 0 && HttpResponse->GetContent().Num() > 0)
	{
		UE_LOG(LogTemp, Log, TEXT("HandleImageRequest3"));
		// 获取图片二进制数据
		const TArray<uint8>& VideoData = HttpResponse->GetContent();
		SaveToData(VideoData);
		SetReadyToDestroy();
		return;
	}

	OnFail.Broadcast(nullptr,TEXT("NullSavePath"), ImageID);
	SetReadyToDestroy();
}

void UAsyncTask_DownloadCivitai::SaveToData(const TArray<uint8>& InData)
{
	// 生成文件名（从URL提取或使用ID）
	FString FileName = FPaths::GetCleanFilename(URL);

	// 确定文件扩展名
	FString FileExtension = FPaths::GetExtension(FileName);


	// 构建完整文件路径

	FString FilePath = UCivitaiFunctionLib::GetProjectSavedFolder() / TEXT("CivitaiImageData") / UserName / (
		FString::FromInt(ImageID) + TEXT(".")
		+ FileExtension);

	// 保存文件
	if (FFileHelper::SaveArrayToFile(InData, *FilePath))
	{
		UE_LOG(LogTemp, Log, TEXT("成功保存图片: %s"), *FilePath);
		UTexture2D* t = UKismetRenderingLibrary::ImportFileAsTexture2D(this, FilePath);
		OnSuccess.Broadcast(t, FilePath, ImageID);
	}
	else
	{
		OnSuccess.Broadcast(nullptr, FilePath, ImageID);
		UE_LOG(LogTemp, Error, TEXT("保存图片失败: %s"), *FilePath);
	}
}
