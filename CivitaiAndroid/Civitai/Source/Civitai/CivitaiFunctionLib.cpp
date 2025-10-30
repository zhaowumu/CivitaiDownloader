// Fill out your copyright notice in the Description page of Project Settings.


#include "CivitaiFunctionLib.h"
#include "ImageUtils.h"
#include "AndroidUtilityPackBPLibrary.h"
#if PLATFORM_ANDROID
#include "Android/AndroidApplication.h"
#include "Android/AndroidJNI.h"
#endif

bool UCivitaiFunctionLib::CreateFolder(const FString& InFolderName)
{
	// 获取基础路径
	FString BasePath = GetProjectSavedFolder();

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

	// 2. 定义需要遍历的子文件夹名称
	const TArray<FString> TargetSubFolders = {
		TEXT("None"),
		TEXT("Soft"),
		TEXT("mature"),
		TEXT("X")
	};

	// 3. 遍历目标子文件夹
	for (const FString& SubFolder : TargetSubFolders)
	{
		// 构建完整的子文件夹路径
		// FPaths::Combine 是一个安全且跨平台的路径连接方法，它会自动处理斜杠。
		const FString FullSubFolderPath = FPaths::Combine(InFolderPath, SubFolder);

		// 检查子文件夹是否存在
		if (!PlatformFile.DirectoryExists(*FullSubFolderPath))
		{
			UE_LOG(LogTemp, Log, TEXT("Target sub-directory does not exist: %s"), *FullSubFolderPath);
			// 简单跳过，继续查找下一个文件夹
			continue;
		}

		// 创建一个临时数组来存放当前子文件夹找到的文件
		TArray<FString> CurrentSubFiles;

		// 调用 FindFiles 查找该子文件夹下的所有文件 (TEXT("") 表示所有扩展名)
		PlatformFile.FindFiles(CurrentSubFiles, *FullSubFolderPath, TEXT(""));

		// 将当前子文件夹找到的文件列表添加到总的结果数组中
		SubFileNames.Append(CurrentSubFiles);
	}

	return SubFileNames;
}

UTexture2D* UCivitaiFunctionLib::GetVideoThumbnail()
{
	return nullptr;
}

void UCivitaiFunctionLib::OpenFolderBySystem(const FString& InFolderName)
{
	FPlatformProcess::ExploreFolder(*InFolderName);
}

void UCivitaiFunctionLib::OpenFileBySystem(const FString& InFile)
{
#if PLATFORM_WINDOWS
	// 使用系统默认应用程序打开文件
	FPlatformProcess::LaunchURL(*InFile, nullptr, nullptr);
#endif

#if PLATFORM_ANDROID
	UAndroidUtilityPackBPLibrary::OpenSystemFolder(InFile);
#endif
}

FString UCivitaiFunctionLib::GetProjectSavedFolder()
{
	FString outPath = FString();
#if PLATFORM_WINDOWS
	outPath = FPaths::ProjectSavedDir();
#endif

#if PLATFORM_ANDROID
	outPath = UAndroidUtilityPackBPLibrary::GetAndroidExternalCardPath();
#endif

	return outPath;
}

void UCivitaiFunctionLib::ShowToast(const FString& msg)
{
#if PLATFORM_ANDROID
	if (JNIEnv* Env = FAndroidApplication::GetJavaEnv())
	{

	}

#endif
}
