// Fill out your copyright notice in the Description page of Project Settings.


#include "CivitaiInstance.h"

#include "Kismet/KismetSystemLibrary.h"

void UCivitaiInstance::Init()
{
	Super::Init();

	// 获取URL中的参数
	FString CommandLine = FCommandLine::Get();

	UKismetSystemLibrary::PrintString(this, "haha>>" + CommandLine);
}
