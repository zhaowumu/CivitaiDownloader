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

UAsyncTask_DownloadCivitai* UAsyncTask_DownloadCivitai::DownloadCivitai(FString InUserName, int32 InImageID,
                                                                        FString InSubFolder, FString InURL)
{
	UAsyncTask_DownloadCivitai* BlueprintAsyncTask = NewObject<UAsyncTask_DownloadCivitai>();
	BlueprintAsyncTask->URL = InURL;
	BlueprintAsyncTask->UserName = InUserName;
	BlueprintAsyncTask->ImageID = InImageID;
	BlueprintAsyncTask->SubFolder = InSubFolder.IsEmpty() ? TEXT("Normal") : InSubFolder;
	return BlueprintAsyncTask;
}

void UAsyncTask_DownloadCivitai::Activate()
{
	// ✅ 防止被 GC 提前回收
	AddToRoot(); 
	
	TSharedRef<IHttpRequest, ESPMode::ThreadSafe> HttpRequest = FHttpModule::Get().CreateRequest();
	HttpRequest->OnProcessRequestComplete().BindUObject(this, &UAsyncTask_DownloadCivitai::HandleImageRequest);
	HttpRequest->SetURL(URL);
	HttpRequest->SetVerb(TEXT("GET"));
	HttpRequest->ProcessRequest();

	UE_LOG(LogTemp, Log, TEXT("UAsyncTask_DownloadCivitai::Activate | URL: %s"), *URL);
}

void UAsyncTask_DownloadCivitai::HandleImageRequest(FHttpRequestPtr HttpRequest, FHttpResponsePtr HttpResponse,
                                                    bool bSucceeded)
{
	UE_LOG(LogTemp, Log, TEXT("HandleImageRequest"));
	
	if (bSucceeded && HttpResponse.IsValid() && EHttpResponseCodes::IsOk(HttpResponse->GetResponseCode()) &&
		HttpResponse->GetContentLength() > 0 && HttpResponse->GetContent().Num() > 0)
	{
		// 获取图片二进制数据
		const TArray<uint8>& ImageVideoData = HttpResponse->GetContent();
		SaveToData(ImageVideoData);
	}else
	{
		OnFail.Broadcast(false,TEXT("NullImageRequest"), ImageID);
	}
	
	RemoveFromRoot();
	SetReadyToDestroy();
}

void UAsyncTask_DownloadCivitai::SaveToData(const TArray<uint8>& InData)
{
	// 生成文件名（从URL提取或使用ID）
	FString FileName = FPaths::GetCleanFilename(URL);

	// 确定文件扩展名
	const FString FileExtension = FPaths::GetExtension(FileName);

	if (FileExtension.IsEmpty())
	{
		UE_LOG(LogTemp, Error, TEXT("UAsyncTask_DownloadCivitai::SaveToData 无法确定文件扩展名"));
	}

	if (SubFolder.IsEmpty())
	{
		SubFolder = "Normal";
	}

	// 创建目录
	const FString FolderPath = UCivitaiFunctionLib::GetProjectSavedFolder() / TEXT("CivitaiImageData") / UserName / SubFolder;
	if (!IFileManager::Get().DirectoryExists(*FolderPath))
	{
		IFileManager::Get().MakeDirectory(*FolderPath, true);
	}
	
	// 构建完整文件路径
	const FString FilePath = UCivitaiFunctionLib::GetProjectSavedFolder() / TEXT("CivitaiImageData") / UserName / SubFolder /
		(FString::FromInt(ImageID) + TEXT(".") + FileExtension);

	// 保存文件
	if (FFileHelper::SaveArrayToFile(InData, *FilePath))
	{
		UE_LOG(LogTemp, Log, TEXT("成功保存图片: %s"), *FilePath);
		//UTexture2D* t = UKismetRenderingLibrary::ImportFileAsTexture2D(this, FilePath);
		OnSuccess.Broadcast(true, FilePath, ImageID);
	}
	else
	{
		OnFail.Broadcast(false,TEXT("SaveFail"), ImageID);
		UE_LOG(LogTemp, Error, TEXT("保存图片失败: %s"), *FilePath);
	}
}
