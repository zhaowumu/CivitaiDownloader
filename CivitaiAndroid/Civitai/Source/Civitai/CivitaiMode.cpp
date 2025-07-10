// Fill out your copyright notice in the Description page of Project Settings.


#include "CivitaiMode.h"

#include "Kismet/KismetSystemLibrary.h"

void ACivitaiMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
	Super::InitGame(MapName, Options, ErrorMessage);

	// 获取URL中的参数
	FString CommandLine = FCommandLine::Get();

	UKismetSystemLibrary::PrintString(this, "CommandLine>>" + CommandLine);

	UKismetSystemLibrary::PrintString(this, "Options>>" + Options);
}
