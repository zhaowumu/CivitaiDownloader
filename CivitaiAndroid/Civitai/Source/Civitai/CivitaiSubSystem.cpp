// Fill out your copyright notice in the Description page of Project Settings.


#include "CivitaiSubSystem.h"

#include "CivitaiFunctionLib.h"
#include "Kismet/BlueprintPathsLibrary.h"
#include "Serialization/JsonTypes.h"
#include "Serialization/JsonWriter.h"
#include "Serialization/JsonSerializer.h"


void UCivitaiSubSystem::CreateUserFolder(const FString& InUserName)
{
	if (!InUserName.IsEmpty())
	{
		FString FolderPath = UCivitaiFunctionLib::GetProjectSavedFolder() / TEXT("CivitaiImageData") / InUserName;
		if (!FPaths::DirectoryExists(FolderPath))
		{
			if (FPlatformFileManager::Get().GetPlatformFile().CreateDirectoryTree(*FolderPath))
			{
				UE_LOG(LogTemp, Log, TEXT("创建文件夹成功: %s"), *FolderPath);
			}
			else
			{
				UE_LOG(LogTemp, Error, TEXT("创建文件夹失败: %s"), *FolderPath);
			}
		}
	}
}

void UCivitaiSubSystem::GetUserDataList(TArray<FString>& InUserDataList)
{
	InUserDataList = UCivitaiFunctionLib::GetAllSubFolders(UCivitaiFunctionLib::GetProjectSavedFolder() / TEXT("CivitaiImageData"));
}

void UCivitaiSubSystem::StartFetchJsonData(const FString& InUserName)
{
	if (!InUserName.IsEmpty())
	{
		// 如果是数字就代表是日期
		if (InUserName.IsNumeric())
		{
			/*CurrentUser = InUserName;
			CurrentUserDataMap.Empty();
			CurrentPageUrl.Empty();

			FString BaseUrl = FString::Printf(
				TEXT("https://civitai.com/api/v1/images?limit=100&nsfw=X&period=Day&sort=Newest"));

			SendDataHttpRequest(BaseUrl);*/
		}
		else
		{
			CurrentUser = InUserName;
			CurrentUserDataMap.Empty();
			CurrentPageUrl.Empty();

			FString BaseUrl = FString::Printf(
				TEXT("https://civitai.com/api/v1/images?username=%s&limit=100&nsfw=X&period=AllTime&sort=Newest"),
				*CurrentUser);

			SendDataHttpRequest(BaseUrl);
		}
	}
}

void UCivitaiSubSystem::SendDataHttpRequest(const FString& InUrl)
{
	CurrentPageUrl = InUrl;
	TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request = FHttpModule::Get().CreateRequest();
	Request->SetURL(InUrl);
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
			// 遍历items数组
			const TArray<TSharedPtr<FJsonValue>> Items = JsonObject->GetArrayField(TEXT("items"));
			for (const TSharedPtr<FJsonValue>& ItemValue : Items)
			{
				TSharedPtr<FJsonObject> ItemObject = ItemValue->AsObject();

				// 提取关键字段
				int32 ItemId = ItemObject->GetIntegerField(TEXT("id"));
				FString ItemUrl = ItemObject->GetStringField(TEXT("url"));
				FString ItemType = ItemObject->GetStringField(TEXT("type"));
				FString ItemNsfwLevel = ItemObject->GetStringField(TEXT("nsfwLevel"));

				// 存入映射表
				CurrentUserDataMap.Add(ItemId, FCivitaiDataInfo(ItemId, ItemUrl, ItemType, ItemNsfwLevel));
			}
			TSharedPtr<FJsonObject> MetaDataJsonObject = JsonObject->GetObjectField(TEXT("metadata"));

			// 还有下一页
			if (MetaDataJsonObject.IsValid())
			{
				// 提取关键字段
				FString nextCursor = MetaDataJsonObject->GetStringField(TEXT("nextCursor"));
				FString nextUrl = MetaDataJsonObject->GetStringField(TEXT("nextPage"));

				if (!nextUrl.IsEmpty())
				{
					SendDataHttpRequest(nextUrl);
				}
				else
				{
					SyncDataOverDelegate.Broadcast(false, CurrentUserDataMap.Num());
					UE_LOG(LogTemp, Error, TEXT("错误下一页"));
				}
			}
			else
			{
				SyncDataOverDelegate.Broadcast(true, CurrentUserDataMap.Num());
				UE_LOG(LogTemp, Log, TEXT("成功解析 %d 条数据"), CurrentUserDataMap.Num());
			}
		}
		else
		{
			SyncDataOverDelegate.Broadcast(false, CurrentUserDataMap.Num());
			UE_LOG(LogTemp, Error, TEXT("JSON解析失败"));
		}
	}
	else
	{
		SyncDataOverDelegate.Broadcast(false, CurrentUserDataMap.Num());
		// 请求失败，处理错误信息
		UE_LOG(LogTemp, Error, TEXT("Response: Error"));
	}
}

bool UCivitaiSubSystem::SaveJsonData()
{
	TSharedPtr<FJsonObject> RootObject = MakeShareable(new FJsonObject());

	TArray<TSharedPtr<FJsonValue>> JsonArray;
	// 遍历TMap并填充JSON对象
	for (const auto& ImgData : CurrentUserDataMap)
	{
		// 创建第一个对象
		TSharedPtr<FJsonObject> tmpJsonObj = MakeShareable(new FJsonObject());
		tmpJsonObj->SetNumberField(TEXT("id"), ImgData.Key);
		tmpJsonObj->SetStringField(TEXT("url"), ImgData.Value.Url);
		tmpJsonObj->SetStringField(TEXT("type"), ImgData.Value.Type);
		tmpJsonObj->SetStringField(TEXT("nsfwLevel"), ImgData.Value.NsfwLevel);
		JsonArray.Add(MakeShareable(new FJsonValueObject(tmpJsonObj)));
	}

	RootObject->SetArrayField(TEXT("images"), JsonArray); // "images"为数组字段名

	// 序列化为字符串
	FString OutputString;
	TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
	FJsonSerializer::Serialize(RootObject.ToSharedRef(), Writer);


	// 文件保存增强
	FString FilePath = UCivitaiFunctionLib::GetProjectSavedFolder() / TEXT("CivitaiImageData") / CurrentUser / TEXT("data.json");
	if (!FFileHelper::SaveStringToFile(OutputString, *FilePath))
	{
		UE_LOG(LogTemp, Error, TEXT("文件保存失败: %s"), *FilePath);
		return false;
	}

	CurrentJsonCount = CurrentUserDataMap.Num();

	return true;
}

void UCivitaiSubSystem::ShowUserLocalData(const FString& InUserName)
{
	if (InUserName.IsEmpty())
	{
		return;
	}

	CurrentUser = InUserName;
	CurrentJsonCount = 0;
	CurrentUserDataMap.Empty();

	// 构建本地JSON文件路径
	FString FilePath = UCivitaiFunctionLib::GetProjectSavedFolder() / TEXT("CivitaiImageData") / CurrentUser / TEXT("data.json");

	// 检查文件是否存在
	if (!FPaths::FileExists(FilePath))
	{
		UE_LOG(LogTemp, Warning, TEXT("本地数据文件不存在: %s"), *FilePath);
		return;
	}

	// 读取文件内容
	FString FileContent;
	if (!FFileHelper::LoadFileToString(FileContent, *FilePath))
	{
		UE_LOG(LogTemp, Error, TEXT("读取本地文件失败: %s"), *FilePath);
		return;
	}

	// 解析JSON数据
	TSharedPtr<FJsonObject> JsonObject;
	TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(FileContent);

	if (FJsonSerializer::Deserialize(Reader, JsonObject) && JsonObject.IsValid())
	{
		// 检查是否存在images数组
		if (JsonObject->HasField(TEXT("images")))
		{
			const TArray<TSharedPtr<FJsonValue>> Items = JsonObject->GetArrayField(TEXT("images"));
			UE_LOG(LogTemp, Log, TEXT("Josn有 %d 条本地数据"), Items.Num());
			for (const TSharedPtr<FJsonValue>& ItemValue : Items)
			{
				TSharedPtr<FJsonObject> ItemObject = ItemValue->AsObject();

				// 提取关键字段
				int32 ItemId = ItemObject->GetIntegerField(TEXT("id"));
				FString ItemUrl = ItemObject->GetStringField(TEXT("url"));
				FString ItemType = ItemObject->GetStringField(TEXT("type"));
				FString ItemNsfwLevel = ItemObject->GetStringField(TEXT("nsfwLevel"));

				// 存入映射表
				CurrentUserDataMap.Add(ItemId, FCivitaiDataInfo(ItemId, ItemUrl, ItemType, ItemNsfwLevel));
			}

			CurrentJsonCount = CurrentUserDataMap.Num();

			UE_LOG(LogTemp, Log, TEXT("成功加载 %d 条本地数据"), Items.Num());
		}
		else
		{
			UE_LOG(LogTemp, Warning, TEXT("JSON文件缺少images字段"));
		}
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("JSON解析失败"));
	}
}

FString UCivitaiSubSystem::GetCivitaiUserDir()
{
	return UCivitaiFunctionLib::GetProjectSavedFolder() / TEXT("CivitaiImageData") / CurrentUser;
}

FString UCivitaiSubSystem::GetCivitaiExternalStorageDir()
{
	FString ExternalPath = FPlatformMisc::GetEnvironmentVariable(TEXT("EXTERNAL_STORAGE"));


	FString FilePath = FPaths::Combine(ExternalPath, TEXT("MyGame/Screenshots/Image.jpg"));

	return FilePath;
}

TMap<int32, FString> UCivitaiSubSystem::GetDownLoadImageData()
{
	TMap<int32, FString> ResultMap;
	if (CurrentUser.IsEmpty())
	{
		UE_LOG(LogTemp, Warning, TEXT("当前用户未设置，无法下载图片"));
		return ResultMap;
	}

	// 构建目标文件夹路径
	FString TargetFolder = UCivitaiFunctionLib::GetProjectSavedFolder() / TEXT("CivitaiImageData") / CurrentUser;

	// 确保目标文件夹存在
	if (!FPlatformFileManager::Get().GetPlatformFile().DirectoryExists(*TargetFolder))
	{
		if (!FPlatformFileManager::Get().GetPlatformFile().CreateDirectoryTree(*TargetFolder))
		{
			UE_LOG(LogTemp, Error, TEXT("创建目标文件夹失败: %s"), *TargetFolder);
			return ResultMap;
		}
	}

	if (CurrentUserDataMap.Num() == 0)
	{
		return ResultMap;
	}

	for (const auto& ImgData : CurrentUserDataMap)
	{
		FString ext = FString::FromInt(ImgData.Key) + UBlueprintPathsLibrary::GetExtension(ImgData.Value.Url, true);


		FString FilePath = FPaths::Combine(TargetFolder, ext);

		// 检查文件是否存在
		if (FPlatformFileManager::Get().GetPlatformFile().FileExists(*FilePath))
		{
			UE_LOG(LogTemp, Warning, TEXT("文件已存在，跳过下载: %s"), *FilePath);
			continue;
		}

		UE_LOG(LogTemp, Warning, TEXT("文件已加入下载: %s"), *FilePath);
		ResultMap.Add(ImgData.Key, ImgData.Value.Url);
	}

	return ResultMap;
}
