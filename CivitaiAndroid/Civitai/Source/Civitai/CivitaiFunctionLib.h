// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "CivitaiFunctionLib.generated.h"





/**
 * 
 */
UCLASS()
class CIVITAI_API UCivitaiFunctionLib : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:

	/**
	 * 创建一个文件夹，如果文件夹不存在的话。
	 * @param FolderPath 要创建的文件夹路径（相对于项目内容目录或保存游戏目录）。
	 * @param bRelativeToContentDir 如果为 true，路径将相对于项目内容目录；否则相对于保存游戏目录。
	 * @return 如果文件夹创建成功或已经存在，返回 true；否则返回 false。
	 */
	UFUNCTION(BlueprintCallable, Category = "File")
	static bool CreateFolder(const FString& InFolderName);

	UFUNCTION(BlueprintCallable, Category = "File")
	static TArray<FString> GetAllSubFolders(const FString& InFolderPath);
    
};
