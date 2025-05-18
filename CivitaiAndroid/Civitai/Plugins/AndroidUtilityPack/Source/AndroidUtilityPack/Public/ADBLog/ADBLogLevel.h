// Copyright Porret Gaming 2024, All Rights Reserved

#pragma once

#include "ADBLogLevel.generated.h"

UENUM(BlueprintType)
enum EADBLogLevel
{
    ADB_LOG_LEVEL_VERBOSE       = 0         UMETA(DisplayName = "VERBOSE"),
    ADB_LOG_LEVEL_DEBUG         = 1         UMETA(DisplayName = "DEBUG"),
    ADB_LOG_LEVEL_INFO          = 2         UMETA(DisplayName = "INFO"),
    ADB_LOG_LEVEL_WARNING       = 3         UMETA(DisplayName = "WARNING"),
    ADB_LOG_LEVEL_ERROR         = 4         UMETA(DisplayName = "ERROR")
};
