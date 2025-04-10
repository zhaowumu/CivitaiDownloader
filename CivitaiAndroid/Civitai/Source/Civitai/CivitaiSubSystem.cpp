// Fill out your copyright notice in the Description page of Project Settings.


#include "CivitaiSubSystem.h"

void UCivitaiSubSystem::SendDataHttpRequest()
{
	TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request = FHttpModule::Get().CreateRequest();
	Request->SetURL("https://civitai.com/api/v1/images");
	Request->SetHeader(TEXT("Content-Type"), TEXT("application/json"));
	Request->SetHeader("Authorization", "48a2ee64f676a61c94169c95da2f81fc");
	Request->SetVerb("GET"); // 或 "POST"

	// 绑定回调
	Request->OnProcessRequestComplete().BindUObject(this, &UCivitaiSubSystem::HandleCivtaiDataResponse);

	// 发送请求
	Request->ProcessRequest();
}

void UCivitaiSubSystem::HandleCivtaiDataResponse(FHttpRequestPtr Request, FHttpResponsePtr Response,
	bool bWasSuccessful)
{
	if (bWasSuccessful && Response.IsValid())
	{
		// 请求成功，处理响应数据
		FString ResponseString = Response->GetContentAsString();
		UE_LOG(LogTemp, Warning, TEXT("Response: %s"), *ResponseString);

		// 构建文件路径（项目根目录）
		FString FilePath = FPaths::ProjectSavedDir() / TEXT("data.json");
    
		// 保存字符串到文件（UTF-8编码）
		if (FFileHelper::SaveStringToFile(ResponseString, *FilePath, FFileHelper::EEncodingOptions::AutoDetect))
		{
			UE_LOG(LogTemp, Log, TEXT("JSON文件保存成功：%s"), *FilePath);
			OnRequestCompleted.Broadcast(FilePath, true);
		}
		else
		{
			UE_LOG(LogTemp, Error, TEXT("JSON文件保存失败：%s"), *FilePath);
		}
		
	}
	else
	{
		// 请求失败，处理错误信息
		UE_LOG(LogTemp, Error, TEXT("Response: Error"));
	}
}
