// Copyright Porret Gaming 2024, All Rights Reserved

#pragma once

#include "AndroidLifecycleEventType.generated.h"

UENUM(BlueprintType)
enum EAndroidLifecycleEventType
{
    ANDROID_LIFECYCLE_EVENT_CREATE      = 0     UMETA(DisplayName = "EVENT_CREATE"),
    ANDROID_LIFECYCLE_EVENT_START       = 1     UMETA(DisplayName = "EVENT_START"),
    ANDROID_LIFECYCLE_EVENT_RESUME      = 2     UMETA(DisplayName = "EVENT_RESUME"),
    ANDROID_LIFECYCLE_EVENT_PAUSE       = 3     UMETA(DisplayName = "EVENT_PAUSE"),
    ANDROID_LIFECYCLE_EVENT_STOP        = 4     UMETA(DisplayName = "EVENT_STOP"),
    ANDROID_LIFECYCLE_EVENT_RESTART     = 5     UMETA(DisplayName = "EVENT_RESTART")
};
