// Copyright Porret Gaming 2024, All Rights Reserved

#include "AndroidUtilityPackEditor.h"

#include "AndroidUtilityPackSettings.h"
#include "ISettingsModule.h"

#define LOCTEXT_NAMESPACE "FAndroidUtilityPackEditorModule"

void FAndroidUtilityPackEditorModule::StartupModule()
{
	ISettingsModule* SettingsModule = FModuleManager::GetModulePtr<ISettingsModule>("Settings");

	if (SettingsModule != nullptr)
	{
		SettingsModule->RegisterSettings(TEXT("Project"), TEXT("Plugins"), TEXT("Android Utility Pack"),
			LOCTEXT("AndroidUtilityPackSettingsName", "Android Utility Pack"),
			LOCTEXT("AndroidUtilityPackDescription", "Configure Android Utility Pack."),
			GetMutableDefault<UAndroidUtilityPackSettings>()
		);
	}
}

void FAndroidUtilityPackEditorModule::ShutdownModule()
{
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FAndroidUtilityPackEditorModule, AndroidUtilityPackEditor)
