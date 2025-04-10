// Fill out your copyright notice in the Description page of Project Settings.


#include "CivitaiSubSystem.h"
#include "Serialization/JsonTypes.h"    // TJsonArray定义位置
#include "Serialization/JsonWriter.h"   // JSON序列化支持
#include "Serialization/JsonSerializer.h" // JSON编解码器

void UCivitaiSubSystem::StartFetchJsonData(const FString& InUserName)
{
	if (!InUserName.IsEmpty())
	{
		CurrentUser = InUserName;
		CurrentPage = 0;
		CurrentUserDataMap.Empty();
		SendDataHttpRequest();
	}
}

void UCivitaiSubSystem::SendDataHttpRequest()
{
	FString BaseUrl = FString::Printf(
		TEXT("https://civitai.com/api/v1/images?username=%s&page=%d&limit=200&nsfw=X&period=AllTime&sort=Newest"),
		*CurrentUser, CurrentPage);

	TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request = FHttpModule::Get().CreateRequest();
	Request->SetURL(BaseUrl);
	Request->SetHeader(TEXT("Content-Type"), TEXT("application/json"));
	Request->SetHeader("Authorization", "48a2ee64f676a61c94169c95da2f81fc");
	Request->SetVerb("GET"); // 或 "POST"

	// 绑定回调
	Request->OnProcessRequestComplete().BindUObject(this, &UCivitaiSubSystem::HandleCivitaiDataResponse);
	// 发送请求
	Request->ProcessRequest();
}


void UCivitaiSubSystem::HandleCivitaiDataResponse(FHttpRequestPtr Request, FHttpResponsePtr Response,
                                                  bool bWasSuccessful)
{
	if (bWasSuccessful && Response.IsValid())
	{
		// 请求成功，处理响应数据
		FString ResponseString = Response->GetContentAsString();
		//UE_LOG(LogTemp, Warning, TEXT("Response: %s"), *ResponseString);

		TSharedPtr<FJsonObject> JsonObject;
		TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(ResponseString);

		// 解析JSON数据
		if (FJsonSerializer::Deserialize(Reader, JsonObject) && JsonObject.IsValid())
		{
			// 清空旧数据
			CurrentUserDataMap.Empty();

			// 遍历items数组
			const TArray<TSharedPtr<FJsonValue>> Items = JsonObject->GetArrayField(TEXT("items"));
			for (const TSharedPtr<FJsonValue>& ItemValue : Items)
			{
				TSharedPtr<FJsonObject> ItemObject = ItemValue->AsObject();
                
				// 提取关键字段
				int32 ItemId = ItemObject->GetIntegerField(TEXT("id"));
				FString ItemUrl = ItemObject->GetStringField(TEXT("url"));
				
				// 存入映射表
				CurrentUserDataMap.Add(ItemId, ItemUrl);
			}

			UE_LOG(LogTemp, Log, TEXT("成功解析 %d 条数据"), Items.Num());
		}
		else
		{
			UE_LOG(LogTemp, Error, TEXT("JSON解析失败"));
		}


	}
	else
	{
		// 请求失败，处理错误信息
		UE_LOG(LogTemp, Error, TEXT("Response: Error"));
	}
}

bool UCivitaiSubSystem::SaveJsonData()
{

	// 创建JSON对象
	TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject());

	// 遍历TMap并填充JSON对象
	for (const auto& ImgData : CurrentUserDataMap)
	{
		FString KeyStr = FString::Printf(TEXT("%d"), ImgData.Key);
		JsonObject->SetStringField(KeyStr, ImgData.Value);
	}
	

	// 文件保存增强
	FString FilePath = FPaths::ProjectSavedDir() / TEXT("civitai_data.json");
	if (!FFileHelper::SaveStringToFile(OutputString, *FilePath))
	{
		UE_LOG(LogTemp, Error, TEXT("文件保存失败: %s"), *FilePath);
		return false;
	}

	return true;
}
