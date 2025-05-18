// Copyright Porret Gaming 2024, All Rights Reserved

#pragma once

#include "Modules/ModuleManager.h"

class FToolBarBuilder;
class FMenuBuilder;

class FAndroidUtilityPackEditorModule : public IModuleInterface
{
public:

	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

};