// Fill out your copyright notice in the Description page of Project Settings.


#include "CivitaiFunctionLib.h"

#include "ImageUtils.h"

bool UCivitaiFunctionLib::CreateFolder(const FString& InFolderName)
{
	// 获取基础路径
	FString BasePath = FPaths::ProjectSavedDir();

	// 拼接完整路径
	FString FullPath = BasePath / InFolderName;

	// 确保路径以 "/" 结尾
	if (!FullPath.EndsWith("/"))
	{
		FullPath += "/";
	}

	// 获取平台文件接口
	IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();

	// 检查文件夹是否已经存在
	if (PlatformFile.DirectoryExists(*FullPath))
	{
		UE_LOG(LogTemp, Log, TEXT("Folder already exists: %s"), *FullPath);
		return true;
	}

	// 创建文件夹
	bool bCreated = PlatformFile.CreateDirectory(*FullPath);

	if (bCreated)
	{
		UE_LOG(LogTemp, Log, TEXT("Folder created successfully: %s"), *FullPath);
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to create folder: %s"), *FullPath);
	}

	return bCreated;
}

TArray<FString> UCivitaiFunctionLib::GetAllSubFolders(const FString& InFolderPath)
{
	TArray<FString> SubFolderNames;
	IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();

	// 检查基础路径是否存在
	if (!PlatformFile.DirectoryExists(*InFolderPath))
	{
		UE_LOG(LogTemp, Warning, TEXT("Directory does not exist: %s"), *InFolderPath);
		return SubFolderNames;
	}

	// 定义 Lambda 变量（自动推导类型）
	auto DirectoryVisitor = [&SubFolderNames](const TCHAR* Path, bool bIsDirectory) -> bool
	{
		//UE_LOG(LogTemp, Log, TEXT("Path: %s, Is Directory: %s"), Path, bIsDirectory ? TEXT("Yes") : TEXT("No"));
		if (bIsDirectory)
		{
			FString FolderName = FPaths::GetCleanFilename(Path);
			if (FolderName.StartsWith(TEXT("/")))
			{
				FolderName = FolderName.RightChop(1);
				FolderName = FPaths::GetCleanFilename(FolderName);
			}
			// 如果是文件夹就加入ResultFolders列表中
			SubFolderNames.AddUnique(FolderName);
		}
		return true; // 继续遍历
	};

	// 转换为 const TCHAR*
	const TCHAR* PathPtr = *InFolderPath;
	// 遍历目录内容（只包含子目录）
	PlatformFile.IterateDirectory(PathPtr, DirectoryVisitor);

	return SubFolderNames;
}

TArray<FString> UCivitaiFunctionLib::GetAllSubFiles(const FString& InFolderPath)
{
	TArray<FString> SubFileNames;
	IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();

	// 检查基础路径是否存在
	if (!PlatformFile.DirectoryExists(*InFolderPath))
	{
		UE_LOG(LogTemp, Warning, TEXT("Directory does not exist: %s"), *InFolderPath);
		return SubFileNames;
	}

	PlatformFile.FindFiles(SubFileNames, *InFolderPath, TEXT(""));

	return SubFileNames;
}

UTexture2D* UCivitaiFunctionLib::GetVideoThumbnail()
{
	return nullptr;
}
