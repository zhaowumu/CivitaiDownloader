// Copyright Porret Gaming 2024, All Rights Reserved

#pragma once

#include "InternetCheckResult.generated.h"

USTRUCT(BlueprintType)
struct FInternetCheckResult
{
    GENERATED_BODY()

    FInternetCheckResult(): FInternetCheckResult(false, TEXT(""))
    {}

    FInternetCheckResult(
        bool _bIsConnected,
        FString _FailureReason)
    {
        bIsConnected = _bIsConnected;
        FailureReason = _FailureReason;
    }

    UPROPERTY(BlueprintReadOnly, Category = "InternetCheckResult")
    bool bIsConnected;

    UPROPERTY(BlueprintReadOnly, Category = "InternetCheckResult")
    FString FailureReason;
    
};
